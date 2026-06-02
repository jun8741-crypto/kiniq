"""RAG 대화형 CLI (ai_worker/rag/chat_cli.py) — 개발·체험용 임시 도구.

Phase 5(API·웹 UI) 전에 터미널에서 RAG 챗봇을 직접 써보기 위한 도구다(운영 코드 아님).
envs/.local.env 에서 OPENAI_API_KEY·QDRANT_URL 을 자동 로드하므로 별도 export 불필요.

실행:
    cd ~/workspaces/oz_coding/20project/AI_HealthCare_Final_Project_Template
    ./poc/.venv/bin/python -m ai_worker.rag.chat_cli

명령:
    질문 입력      → RAG 답변 (검색→생성→안전가드)
    /egfr 25       → eGFR 설정 (G4·G5 자가관리 가드 테스트)
    /egfr clear    → eGFR 해제
    exit / quit    → 종료
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# input() 라인 편집(백스페이스·화살표·히스토리) 활성화 — 미로드 시 한글 백스페이스가 깨져 멈춤.
# GNU readline 에서 한글(UTF-8 멀티바이트) 입력·삭제·표시를 안정화한다.
try:
    import readline  # noqa: F401

    readline.parse_and_bind("set input-meta on")
    readline.parse_and_bind("set output-meta on")
    readline.parse_and_bind("set convert-meta off")
except Exception:  # noqa: BLE001 — readline 없는 환경도 동작은 함(편집만 불가)
    pass

# ── envs/.local.env 자동 로드 (의존성 없이 수동 파싱) ──────────────────────────
_ROOT = Path(__file__).resolve().parents[2]
_ENV = _ROOT / "envs" / ".local.env"
if _ENV.exists():
    for _ln in _ENV.read_text(encoding="utf-8").splitlines():
        _ln = _ln.strip()
        if _ln and not _ln.startswith("#") and "=" in _ln:
            _k, _v = _ln.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

sys.path.insert(0, str(_ROOT))
from ai_worker.rag import run  # noqa: E402


def main() -> None:
    key = os.getenv("OPENAI_API_KEY", "")
    if not key or "REPL" in key or len(key) < 20:
        print("⚠ OPENAI_API_KEY 가 미설정/placeholder 입니다 — envs/.local.env 를 확인하세요.")
        return
    if not os.getenv("QDRANT_URL"):
        os.environ["QDRANT_URL"] = "http://localhost:6333"

    print("=" * 64)
    print(" 🩺 CKD RAG 챗봇 (개발 CLI)")
    print("    질문을 입력하세요. 의료 가이드라인을 검색해 답합니다.")
    print("    /egfr 25   eGFR 설정(G4·G5 가드 테스트)   |   /egfr clear   해제")
    print("    exit       종료")
    print("=" * 64)

    user_context: dict = {}
    while True:
        try:
            q = input("\n질문> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다.")
            break

        if not q or q.lower() in ("exit", "quit", "/exit", "/quit"):
            print("종료합니다.")
            break

        if q.startswith("/egfr"):
            parts = q.split()
            if len(parts) == 2 and parts[1] == "clear":
                user_context.pop("eGFR", None)
                print("  → eGFR 해제됨")
            elif len(parts) == 2 and parts[1].isdigit():
                user_context["eGFR"] = int(parts[1])
                stage = "G5" if user_context["eGFR"] < 15 else "G4" if user_context["eGFR"] < 30 else "G1~3"
                print(f"  → eGFR={user_context['eGFR']} ({stage}) 설정됨")
            else:
                print("  사용법: /egfr 25  또는  /egfr clear")
            continue

        print("\n" + "─" * 64)
        try:
            print(run(q, user_context or None))
        except Exception as e:  # noqa: BLE001
            print(f"⚠ 오류: {type(e).__name__}: {e}")
        print("─" * 64)


if __name__ == "__main__":
    main()
