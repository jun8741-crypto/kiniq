"""RAG 작업 핸들러 — Stream 페이로드를 받아 run() 실행 (동기 블로킹 오프로딩)."""

from __future__ import annotations

import asyncio

from ai_worker.rag import run  # 테스트에서 monkeypatch 가능하도록 모듈 속성으로 import
from ai_worker.schemas.chat import ChatJob, ChatResult


async def handle_chat_job(job: ChatJob) -> ChatResult:
    try:
        answer = await asyncio.to_thread(run, job.question, job.user_context)
        return ChatResult(answer=answer)
    except Exception as e:  # noqa: BLE001 — worker는 어떤 예외도 결과로 전달해야 함
        return ChatResult(error=str(e))
