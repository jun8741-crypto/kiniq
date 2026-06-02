"""Phase 3 인덱싱 — 통합 실행 진입점 (run_indexing.py).

원본 자료를 data/ 에 넣은 뒤 이 스크립트 하나로 청킹→임베딩→업로드 3단을 순차 실행한다.
각 단계는 기존 모듈(chunking.py·embedder.py·qdrant_uploader.py)을 별도 프로세스로 호출하므로
(SRP·진입점 분리 유지) 한 단계가 실패하면 거기서 멈춘다.

자료 추가 워크플로우 (2026-06-02 자동화):
  1. data/{kdigo|ksn_guideline|knsn|lifestyle}/ 에 PDF/MD 를 넣는다.
  2. python run_indexing.py  ← 끝. (언어 ko/en 자동 판정 · PDF 개수 동적 카운트)
  ※ 완전히 새로운 카테고리 폴더만 config.DOC_TYPE_BY_FOLDER 매핑 1줄 추가가 필요하다
    (폴더명만으론 clinical/nutrition 을 의미적으로 구분할 수 없어 자동화 대상에서 제외).

실행 (poc/.venv 활성화 상태):
    cd ~/workspaces/oz_coding/20project/AI_HealthCare_Final_Project/poc
    source .venv/bin/activate
    python ../src/rag_indexing/run_indexing.py                 # 청킹→임베딩→업로드 (전체 재구축)
    python ../src/rag_indexing/run_indexing.py --dry-run       # 키·Docker 불요, 구조만 검증 (실제 파일 보존)
    python ../src/rag_indexing/run_indexing.py --stage chunk   # 청킹만
    python ../src/rag_indexing/run_indexing.py --yes           # 임베딩 비용 확인 생략
    python ../src/rag_indexing/run_indexing.py --prod          # prod 모델·collection
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

try:
    from . import config as cfg
except ImportError:
    import config as cfg

_HERE = Path(__file__).resolve().parent
_CHUNKING = _HERE / "chunking.py"
_EMBEDDER = _HERE / "embedder.py"
_UPLOADER = _HERE / "qdrant_uploader.py"

# dry-run 임베딩 출력 — 실제 embedded_child_chunks.jsonl(대용량 진짜 벡터) 보존용 임시 파일
_DRYRUN_EMBED_OUT = cfg.CHUNKS_DIR / "embedded_child_chunks.DRYRUN.jsonl"

_STAGES = ("chunk", "embed", "upload")


def _run(script: Path, flags: list[str]) -> None:
    """단일 단계를 같은 인터프리터의 별도 프로세스로 실행. 실패 시 CalledProcessError 전파."""
    cmd = [sys.executable, str(script), *flags]
    print(f"\n{'─' * 70}\n▶ {script.name} {' '.join(flags)}\n{'─' * 70}")
    subprocess.run(cmd, check=True)


def _confirm_cost() -> bool:
    """실제 임베딩 직전 비용 확인. 비대화형(EOF)이면 안전하게 거부."""
    try:
        resp = input("\n실제 임베딩은 OpenAI 비용이 발생합니다 (dev 전체 ≈ $0.03). 계속할까요? [y/N] ")
    except EOFError:
        return False
    return resp.strip().lower() in ("y", "yes")


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG 인덱싱 3단 통합 실행 (청킹→임베딩→업로드)")
    parser.add_argument(
        "--stage",
        choices=("all", *_STAGES),
        default="all",
        help="실행 단계 (기본 all). chunk|embed|upload 로 부분 실행",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="전 단계 dry-run 전파 (OpenAI 키·Docker 불요, 실제 산출물 보존)"
    )
    parser.add_argument(
        "--prod", action="store_true", help="embedder·uploader 에 --prod 전파 (large 3072d, medical_kb_prod)"
    )
    parser.add_argument(
        "--no-recreate", action="store_true", help="업로드 시 collection 재생성 생략 (기본은 전체 재구축 = --recreate)"
    )
    parser.add_argument("--yes", "-y", action="store_true", help="임베딩 비용 확인 프롬프트 생략")
    args = parser.parse_args()

    run_chunk = args.stage in ("all", "chunk")
    run_embed = args.stage in ("all", "embed")
    run_upload = args.stage in ("all", "upload")

    common = ["--dry-run"] if args.dry_run else []
    prod = ["--prod"] if args.prod else []

    print("=" * 70)
    print(
        "RAG 인덱싱 파이프라인 — stage={}{}{}".format(
            args.stage,
            "  [dry-run]" if args.dry_run else "",
            "  [prod]" if args.prod else "",
        )
    )
    print("=" * 70)

    try:
        if run_chunk:
            _run(_CHUNKING, common)

        if run_embed:
            if not args.dry_run and not args.yes and not _confirm_cost():
                print("\n중단 — 임베딩을 건너뜁니다.")
                return
            embed_flags = common + prod
            if args.dry_run:
                # dry-run 가짜 벡터가 실제 embedded_child_chunks.jsonl 을 덮어쓰지 않도록 임시 출력
                embed_flags = embed_flags + ["--out", str(_DRYRUN_EMBED_OUT)]
            _run(_EMBEDDER, embed_flags)

        if run_upload:
            upload_flags = common + prod
            if not args.no_recreate:
                upload_flags = upload_flags + ["--recreate"]
            _run(_UPLOADER, upload_flags)
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"\n✗ 단계 실패 (exit {e.returncode}) — 위 출력 확인 후 해당 단계부터 재실행하세요.") from e

    print(
        "\n{}\n✓ 완료 (stage={}){}\n{}".format(
            "=" * 70,
            args.stage,
            f"  ※ dry-run — 실제 적재 안 됨 (임시 파일 {_DRYRUN_EMBED_OUT.name})" if args.dry_run else "",
            "=" * 70,
        )
    )


if __name__ == "__main__":
    main()
