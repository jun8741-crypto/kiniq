"""Phase 3 인덱싱 — child 임베딩 (embedder.py).

chunking.py 산출물 chunks/child_chunks.jsonl 의 각 text 를 OpenAI Embeddings API 로
임베딩해 chunks/embedded_child_chunks.jsonl (원본 row + "vector" 키) 로 덤프한다.
parent 는 벡터 없이 텍스트만 저장하므로 임베딩 대상이 아니다 (Parent-Child 구조).

임베딩(OpenAI 키·비용 필요)과 Qdrant 업로드(Docker 필요)를 두 단계로 분리한다. 한쪽이
실패해도 다른 쪽을 독립 재실행할 수 있고, qdrant_uploader.py 는 embedded_child_chunks.jsonl
만 읽으므로 OpenAI 키가 필요 없다 (SRP·진입점 분리).

모델 정책 (project_api_model_policy):
  • dev  = text-embedding-3-small (1536d) → medical_kb_dev
  • prod = text-embedding-3-large (3072d) → medical_kb_prod (차원 변경 시 collection 재구축 필수)

핵심:
  • 배치 호출(input 리스트) + 응답 index 로 순서 복원 (네트워크 왕복·비용 절감)
  • OpenAI SDK 내장 max_retries(지수 백오프)로 RateLimit·일시 오류 자동 재시도
  • tiktoken 으로 8191 토큰 초과 청크 truncate (child 400자라 드물지만 방어)
  • 차원 검증(응답 len == EMBEDDING_DIM) + 빈 텍스트 가드

실행 (poc/.venv 에 openai·tiktoken·tqdm 설치됨):
    cd .../poc && source .venv/bin/activate
    export OPENAI_API_KEY=sk-...               # 또는 envs/.local.env 에 입력 (자동 탐색)
    python ../src/rag_indexing/embedder.py                # 전체(child 약 13,220개) 임베딩
    python ../src/rag_indexing/embedder.py --limit 50     # 앞 50개만 (스모크·비용 절감)
    python ../src/rag_indexing/embedder.py --dry-run      # 키 없이 deterministic 가짜 벡터로 구조 검증
    python ../src/rag_indexing/embedder.py --prod         # large(3072d)로 임베딩
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
from pathlib import Path

try:
    from . import config as cfg
except ImportError:
    import config as cfg


# ─────────────────────────────────────────────────────────────────────────────
# 상수
# ─────────────────────────────────────────────────────────────────────────────
_MAX_INPUT_TOKENS = 8191        # text-embedding-3 계열 입력당 토큰 상한
_DEFAULT_BATCH_SIZE = 128       # 요청당 input 개수 (128 × ~250토큰 ≈ 32K ≪ 300K/req 한도)
_DEFAULT_MAX_RETRIES = 6        # OpenAI SDK 내장 재시도 횟수 (지수 백오프)
# USD / 1M tokens (project_api_model_policy — 비용 추정 출력용, 청구 기준은 OpenAI 대시보드)
_PRICE_PER_1M = {
    "text-embedding-3-small": 0.02,
    "text-embedding-3-large": 0.13,
}


# ─────────────────────────────────────────────────────────────────────────────
# tiktoken 토큰 가드 (선택적 — 미설치 시 길이 휴리스틱으로 폴백)
# ─────────────────────────────────────────────────────────────────────────────
def _get_encoder():
    """text-embedding-3 계열 인코더(cl100k_base). tiktoken 미설치 시 None."""
    try:
        import tiktoken
        return tiktoken.get_encoding("cl100k_base")
    except Exception:  # noqa: BLE001 — tiktoken 부재/네트워크는 치명적이지 않음
        return None


def _truncate_to_token_limit(text: str, encoder, limit: int = _MAX_INPUT_TOKENS) -> str:
    """8191 토큰 초과 시 잘라낸다. encoder 없으면 보수적 문자수(토큰≈chars/2) 휴리스틱."""
    if encoder is None:
        max_chars = limit * 2  # 한글 1토큰≈1자, 영문 1토큰≈4자 → 안전하게 ×2
        return text[:max_chars] if len(text) > max_chars else text
    ids = encoder.encode(text)
    if len(ids) <= limit:
        return text
    return encoder.decode(ids[:limit])


# ─────────────────────────────────────────────────────────────────────────────
# Embedder — 순수 임베딩 책임 (배치·재시도·차원검증·순서보존)
# ─────────────────────────────────────────────────────────────────────────────
class Embedder:
    """OpenAI Embeddings API 래퍼. client 주입 가능(테스트 mock).

    embed_texts 는 입력 순서를 보존하고 각 벡터 차원을 검증한다.
    실제 OpenAI 호출은 첫 임베딩 시점에 lazy 하게 client 를 만든다(키 검증 전 import OK).
    """

    def __init__(
        self,
        model: str = cfg.EMBEDDING_MODEL_DEV,
        dim: int = cfg.EMBEDDING_DIM_DEV,
        *,
        batch_size: int = _DEFAULT_BATCH_SIZE,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        api_key: str | None = None,
        client=None,
    ) -> None:
        self.model = model
        self.dim = dim
        self.batch_size = batch_size
        self.max_retries = max_retries
        self._api_key = api_key
        self._client = client
        self._encoder = _get_encoder()

    # client lazy 생성 (주입 client 우선 — 테스트는 mock 주입)
    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self._api_key, max_retries=self.max_retries)
        return self._client

    def _prepare(self, text: str) -> str:
        """빈 텍스트 가드 + 토큰 상한 truncate."""
        if not text or not text.strip():
            raise ValueError("빈 텍스트는 임베딩할 수 없습니다 (chunking 의 _MIN_CHUNK_CHARS 가드 확인).")
        return _truncate_to_token_limit(text, self._encoder)

    def embed_texts(self, texts: list[str], *, progress: bool = False) -> list[list[float]]:
        """텍스트 리스트를 배치로 임베딩. 입력 순서·차원 보존.

        progress=True 면 tqdm(있으면)으로 배치 진행률 표시. 라이브러리 호출 기본은 False.
        """
        prepared = [self._prepare(t) for t in texts]
        client = self._get_client()
        vectors: list[list[float]] = [None] * len(prepared)  # type: ignore[list-item]

        batches = range(0, len(prepared), self.batch_size)
        if progress:
            batches = _maybe_tqdm(batches, total_items=len(prepared), batch_size=self.batch_size)

        for start in batches:
            batch = prepared[start:start + self.batch_size]
            resp = client.embeddings.create(model=self.model, input=batch)
            # 응답은 input 순서대로지만 index 로 복원해 순서를 명시적으로 보장
            for item in resp.data:
                vec = list(item.embedding)
                if len(vec) != self.dim:
                    raise AssertionError(
                        f"임베딩 차원 {len(vec)} ≠ 기대 {self.dim} (model={self.model}). "
                        "config.EMBEDDING_DIM 과 모델이 일치하는지 확인."
                    )
                vectors[start + item.index] = vec

        if any(v is None for v in vectors):
            raise RuntimeError("일부 텍스트가 임베딩되지 않았습니다 (응답 누락).")
        return vectors

    def embed_query(self, text: str) -> list[float]:
        """단일 텍스트 임베딩 (추론 단계 query 임베딩에서도 재사용 가능)."""
        return self.embed_texts([text])[0]


# ─────────────────────────────────────────────────────────────────────────────
# dry-run 가짜 임베딩 — 키 없이 파이프라인·uploader 구조 검증
# ─────────────────────────────────────────────────────────────────────────────
class FakeEmbedder:
    """text 해시 시드의 deterministic 단위 벡터. OpenAI 호출 없이 차원·흐름만 검증.

    cosine 거리를 쓰는 Qdrant 가 0-norm 벡터를 거부할 수 있어 비영(非零) 정규화 벡터를 만든다.
    """

    def __init__(self, model: str = cfg.EMBEDDING_MODEL_DEV, dim: int = cfg.EMBEDDING_DIM_DEV) -> None:
        self.model = model
        self.dim = dim

    def _vector(self, text: str) -> list[float]:
        seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)
        rng = random.Random(seed)
        raw = [rng.gauss(0.0, 1.0) for _ in range(self.dim)]
        norm = sum(x * x for x in raw) ** 0.5 or 1.0
        return [x / norm for x in raw]

    def embed_texts(self, texts: list[str], *, progress: bool = False) -> list[list[float]]:
        items = _maybe_tqdm(texts, total_items=len(texts), batch_size=1) if progress else texts
        return [self._vector(t) for t in items]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)


# ─────────────────────────────────────────────────────────────────────────────
# JSONL I/O (uploader 도 read_jsonl 필요 시 io 모듈로 승격 예정 — 현재 단일 사용처)
# ─────────────────────────────────────────────────────────────────────────────
def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def dump_jsonl(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# 진행률 (tqdm optional — chunking.py 가 print 만 쓰므로 부재 시 침묵 폴백)
# ─────────────────────────────────────────────────────────────────────────────
def _maybe_tqdm(iterable, *, total_items: int, batch_size: int):
    try:
        from tqdm import tqdm
        total = (total_items + batch_size - 1) // batch_size
        return tqdm(iterable, total=total, desc="embedding", unit="batch")
    except Exception:  # noqa: BLE001
        return iterable


# ─────────────────────────────────────────────────────────────────────────────
# 키 해석 — 환경변수 우선, 없으면 envs/.local.env 자동 탐색
# ─────────────────────────────────────────────────────────────────────────────
_PLACEHOLDER_HINTS = ("REPLACE", "YOUR", "XXXX", "CHANGEME")


def _resolve_api_key() -> str | None:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        # 편의: repo_root/envs/.local.env 에서 OPENAI_API_KEY 파싱 시도
        env_file = cfg.PKG_ROOT.parent.parent / "envs" / ".local.env"
        if env_file.exists():
            for ln in env_file.read_text(encoding="utf-8").splitlines():
                ln = ln.strip()
                if ln.startswith("OPENAI_API_KEY="):
                    key = ln.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    return key or None


def _is_placeholder_key(key: str | None) -> bool:
    if not key or len(key) < 20 or not key.startswith("sk-"):
        return True
    upper = key.upper()
    return any(h in upper for h in _PLACEHOLDER_HINTS)


# ─────────────────────────────────────────────────────────────────────────────
# 비용 추정 (tiktoken 토큰 합 × 단가)
# ─────────────────────────────────────────────────────────────────────────────
def estimate_tokens_cost(texts: list[str], model: str) -> tuple[int, float]:
    encoder = _get_encoder()
    if encoder is None:
        total = sum(len(t) for t in texts) // 2  # 휴리스틱
    else:
        total = sum(len(encoder.encode(t)) for t in texts)
    price = _PRICE_PER_1M.get(model, 0.0)
    return total, total / 1_000_000 * price


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="child_chunks.jsonl → 임베딩 → embedded_child_chunks.jsonl")
    parser.add_argument("--in", dest="in_path", default=None, help="입력 JSONL (기본 chunks/child_chunks.jsonl)")
    parser.add_argument("--out", dest="out_path", default=None, help="출력 JSONL (기본 chunks/embedded_child_chunks.jsonl)")
    parser.add_argument("--limit", type=int, default=None, help="앞 N개만 임베딩 (스모크·비용 절감)")
    parser.add_argument("--batch-size", type=int, default=_DEFAULT_BATCH_SIZE, help="요청당 input 개수")
    parser.add_argument("--prod", action="store_true", help="prod 모델(text-embedding-3-large, 3072d) 사용")
    parser.add_argument("--dry-run", action="store_true", help="키 없이 deterministic 가짜 벡터로 구조 검증")
    args = parser.parse_args()

    model = cfg.EMBEDDING_MODEL_PROD if args.prod else cfg.EMBEDDING_MODEL_DEV
    dim = cfg.EMBEDDING_DIM_PROD if args.prod else cfg.EMBEDDING_DIM_DEV

    in_path = Path(args.in_path) if args.in_path else cfg.CHUNKS_DIR / "child_chunks.jsonl"
    out_path = Path(args.out_path) if args.out_path else cfg.CHUNKS_DIR / "embedded_child_chunks.jsonl"

    if not in_path.exists():
        raise SystemExit(f"입력 없음: {in_path}\n  먼저 chunking.py 를 실행해 child_chunks.jsonl 을 생성하세요.")

    rows = read_jsonl(in_path)
    if args.limit:
        rows = rows[:args.limit]
    texts = [r["text"] for r in rows]
    print(f"입력: {in_path.name} → {len(rows)}개 child" + (f" (--limit {args.limit})" if args.limit else ""))
    print(f"모델: {model} ({dim}d)" + ("  [dry-run 가짜 벡터]" if args.dry_run else ""))

    tokens, cost = estimate_tokens_cost(texts, model)
    print(f"예상 토큰: {tokens:,} → 추정 비용 ${cost:.4f} ({model})")

    # 임베더 선택 — dry-run 은 키 없이 FakeEmbedder
    if args.dry_run:
        embedder: Embedder | FakeEmbedder = FakeEmbedder(model=model, dim=dim)
    else:
        key = _resolve_api_key()
        if _is_placeholder_key(key):
            raise SystemExit(
                "⚠ OPENAI_API_KEY 가 placeholder/미설정입니다.\n"
                "  → envs/.local.env 의 OPENAI_API_KEY 에 실제 키를 입력하거나 `export OPENAI_API_KEY=sk-...`\n"
                "  → 키 없이 파이프라인 구조만 검증하려면: --dry-run"
            )
        embedder = Embedder(model=model, dim=dim, batch_size=args.batch_size, api_key=key)

    vectors = embedder.embed_texts(texts, progress=True)

    for r, v in zip(rows, vectors):
        r["vector"] = v

    dump_jsonl(rows, out_path)
    print(f"\n덤프 완료: {out_path}  ({len(rows)}개 × {dim}d)")
    if args.dry_run:
        print("※ dry-run 가짜 벡터 — 검색 품질 무의미. 실제 키로 재실행 후 uploader 진행.")


if __name__ == "__main__":
    main()
