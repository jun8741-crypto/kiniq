"""rag_task.handle_chat_job 단위 테스트."""

import pytest

from ai_worker.schemas.chat import ChatJob
from ai_worker.tasks import rag_task

pytestmark = pytest.mark.asyncio


async def test_handle_success(monkeypatch):
    monkeypatch.setattr(rag_task, "run", lambda q, ctx: f"답변:{q}")
    result = await rag_task.handle_chat_job(ChatJob(job_id="1", question="단백질?", user_context={}))
    assert result.answer == "답변:단백질?"
    assert result.error is None


async def test_handle_exception(monkeypatch):
    def boom(q, ctx):
        raise RuntimeError("LLM 실패")

    monkeypatch.setattr(rag_task, "run", boom)
    result = await rag_task.handle_chat_job(ChatJob(job_id="1", question="q", user_context={}))
    assert result.answer is None
    assert "LLM 실패" in result.error
