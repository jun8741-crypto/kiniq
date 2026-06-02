"""ai_worker consumer 통합 테스트 — fakeredis + handle_chat_job mock."""

import json

import fakeredis.aioredis
import pytest

import ai_worker.main as worker
from ai_worker.core import config
from ai_worker.schemas.chat import ChatResult

pytestmark = pytest.mark.asyncio


async def test_consume_once_writes_response(monkeypatch):
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(worker, "get_redis", lambda: fake)

    async def fake_handle(job):
        return ChatResult(answer=f"A:{job.question}")

    monkeypatch.setattr(worker, "handle_chat_job", fake_handle)

    await fake.xadd(
        config.RAG_JOBS_STREAM,
        {
            "job_id": "job1",
            "question": "단백질?",
            "user_context": json.dumps({}),
        },
    )
    await worker.ensure_group(fake)
    await worker.consume_once(fake)

    resp = await fake.xrange(f"{config.RAG_RESP_PREFIX}:job1")
    assert resp, "응답 스트림이 비어있음"
    payload = json.loads(resp[0][1]["data"])
    assert payload["answer"] == "A:단백질?"
