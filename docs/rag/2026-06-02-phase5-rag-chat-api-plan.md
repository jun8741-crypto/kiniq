# Phase 5 — RAG 챗봇 API 통합 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 완성된 RAG 추론 파이프라인(`ai_worker/rag`)을 `POST /api/v1/chat/messages` API로 노출 — 사용자가 질문하면 백엔드가 의료 컨텍스트를 붙여 Redis Stream으로 worker에 넘기고, worker가 RAG를 실행해 돌려준 답변을 통째로 응답한다.

**Architecture:** 통째 표시 + Redis Stream(`rag_jobs`/`rag_resp:{job_id}`) worker 분리 + 일반 HTTP 동기 응답. 백엔드는 `redis.asyncio`로 작업을 XADD하고 응답 채널을 블로킹 대기(60s)한다. worker는 `run()`을 `asyncio.to_thread`로 오프로딩한다.

**Tech Stack:** FastAPI · Tortoise ORM(asyncpg) · Redis(redis.asyncio) · pydantic-settings · pytest-asyncio · fakeredis(테스트)

설계 스펙: `docs/rag/2026-06-02-phase5-rag-chat-api-design.md`

---

## 파일 구조

**신규 (app)**: `app/core/redis_client.py` · `app/models/chat.py` · `app/dtos/chat.py` · `app/repositories/chat_repository.py` · `app/services/chat.py` · `app/apis/v1/chat_routers.py`
**신규 (ai_worker)**: `ai_worker/core/redis_client.py` · `ai_worker/schemas/chat.py` · `ai_worker/tasks/rag_task.py` · `ai_worker/main.py`(0줄→작성)
**수정**: `app/core/config.py` · `app/core/db/databases.py` · `app/apis/v1/__init__.py` · `ai_worker/core/config.py` · `ai_worker/Dockerfile` · `docker-compose.yml` · `pyproject.toml`(fakeredis) · 마이그레이션 신규

**실행 전제**: `feat/RAG` 브랜치. 의존성은 `uv sync --all-groups`로 설치. 테스트는 `app/tests` 패턴(PostgreSQL) + fakeredis.

---

## Task 0: 테스트 의존성 + config Redis 상수

**Files:**
- Modify: `pyproject.toml` (dev 그룹에 fakeredis)
- Modify: `app/core/config.py` (Config 클래스에 REDIS_* 추가)
- Modify: `ai_worker/core/config.py`

- [ ] **Step 1: pyproject.toml dev 그룹에 fakeredis 추가**

`[dependency-groups]`의 `dev` 리스트에 한 줄 추가:
```toml
    "fakeredis>=2.40.0",
```

- [ ] **Step 2: 의존성 설치**

Run: `cd ~/workspaces/oz_coding/20project/AI_HealthCare_Final_Project && uv sync --all-groups`
Expected: fakeredis 설치 로그

- [ ] **Step 3: app config에 Redis 상수 추가**

`app/core/config.py`의 `Config` 클래스 안, `DB_CONNECTION_POOL_MAXSIZE` 아래에 추가:
```python
    # Redis (RAG 챗봇 작업 큐 — docker-compose redis 서비스)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    RAG_JOBS_STREAM: str = "rag_jobs"          # 백엔드→worker 작업 스트림
    RAG_JOBS_GROUP: str = "rag_workers"        # consumer group 이름
    RAG_RESP_PREFIX: str = "rag_resp"          # 응답 채널 prefix → rag_resp:{job_id}
    RAG_TIMEOUT_SEC: int = 60                  # 백엔드 응답 대기 상한
```

- [ ] **Step 4: ai_worker config에 동일 상수 추가**

`ai_worker/core/config.py`의 `Config` 클래스 안 `TIMEZONE` 아래에 추가:
```python
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    RAG_JOBS_STREAM: str = "rag_jobs"
    RAG_JOBS_GROUP: str = "rag_workers"
    RAG_RESP_PREFIX: str = "rag_resp"
```

- [ ] **Step 5: 검증 — import + 상수 접근**

Run: `cd ~/workspaces/oz_coding/20project/AI_HealthCare_Final_Project && ./.venv/bin/python -c "from app.core import config; print(config.REDIS_HOST, config.RAG_JOBS_STREAM)"`
Expected: `localhost rag_jobs`

- [ ] **Step 6: Commit**
```bash
git add pyproject.toml uv.lock app/core/config.py ai_worker/core/config.py
git commit -m "feat(chat): Redis 설정 상수 + fakeredis 테스트 의존성"
```

---

## Task 1: Redis 클라이언트 (app)

**Files:**
- Create: `app/core/redis_client.py`
- Test: `app/tests/chat_apis/test_redis_client.py`

- [ ] **Step 1: 디렉토리·실패 테스트 작성**

`app/tests/chat_apis/__init__.py` (빈 파일) 생성 후 `app/tests/chat_apis/test_redis_client.py`:
```python
import pytest
from app.core.redis_client import get_redis, build_redis_url


def test_build_redis_url():
    assert build_redis_url("localhost", 6379) == "redis://localhost:6379"


@pytest.mark.asyncio
async def test_get_redis_returns_singleton():
    a = get_redis()
    b = get_redis()
    assert a is b   # 같은 커넥션 풀 재사용
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd .../AI_HealthCare_Final_Project && ./.venv/bin/python -m pytest app/tests/chat_apis/test_redis_client.py -v`
Expected: FAIL (ModuleNotFoundError: app.core.redis_client)

- [ ] **Step 3: redis_client 구현**

`app/core/redis_client.py`:
```python
"""RAG 챗봇용 Redis 비동기 클라이언트 (단일 커넥션 풀)."""
from __future__ import annotations

import redis.asyncio as aioredis

from app.core import config

_client: aioredis.Redis | None = None


def build_redis_url(host: str, port: int) -> str:
    return f"redis://{host}:{port}"


def get_redis() -> aioredis.Redis:
    """프로세스 단일 Redis 커넥션 풀 (lazy). decode_responses=True 로 str 반환."""
    global _client
    if _client is None:
        _client = aioredis.from_url(
            build_redis_url(config.REDIS_HOST, config.REDIS_PORT),
            decode_responses=True,
        )
    return _client
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `./.venv/bin/python -m pytest app/tests/chat_apis/test_redis_client.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**
```bash
git add app/core/redis_client.py app/tests/chat_apis/
git commit -m "feat(chat): app Redis 비동기 클라이언트"
```

---

## Task 2: ChatMessage 모델 + 등록 + 마이그레이션

**Files:**
- Create: `app/models/chat.py`
- Modify: `app/core/db/databases.py:6-17` (TORTOISE_APP_MODELS)
- Test: `app/tests/chat_apis/test_chat_model.py`

- [ ] **Step 1: 실패 테스트 작성**

`app/tests/chat_apis/test_chat_model.py`:
```python
from app.models.chat import ChatMessage, ChatRole


def test_chat_role_values():
    assert ChatRole.USER == "user"
    assert ChatRole.ASSISTANT == "assistant"


def test_chat_message_table_name():
    assert ChatMessage.Meta.table == "chat_messages"
```

- [ ] **Step 2: 실패 확인**

Run: `./.venv/bin/python -m pytest app/tests/chat_apis/test_chat_model.py -v`
Expected: FAIL (ModuleNotFoundError: app.models.chat)

- [ ] **Step 3: 모델 구현**

`app/models/chat.py`:
```python
from enum import StrEnum

from tortoise import fields, models


class ChatRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(models.Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="chat_messages")
    role = fields.CharEnumField(enum_type=ChatRole, description="발화 주체 (user/assistant)")
    content = fields.TextField(description="질문 또는 답변 본문")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "chat_messages"
        ordering = ["created_at"]
```

- [ ] **Step 4: databases.py 모델 등록**

`app/core/db/databases.py`의 `TORTOISE_APP_MODELS` 리스트에 추가 (`app.models.password_reset` 다음 줄):
```python
    "app.models.chat",
```

- [ ] **Step 5: 테스트 통과 확인**

Run: `./.venv/bin/python -m pytest app/tests/chat_apis/test_chat_model.py -v`
Expected: PASS

- [ ] **Step 6: 마이그레이션 생성**

Run: `cd .../AI_HealthCare_Final_Project && ./.venv/bin/aerich migrate --name add_chat_message`
Expected: `app/core/db/migrations/models/`에 새 마이그레이션 파일 생성
(aerich 미초기화로 실패 시: 앱 lifespan의 `run_migrations()`가 자동 적용하므로 `aerich migrate`만 시도하고, 실패하면 마이그레이션 파일을 기존 파일 패턴으로 수동 작성 — `chat_messages` 테이블 CREATE)

- [ ] **Step 7: Commit**
```bash
git add app/models/chat.py app/core/db/databases.py app/core/db/migrations/ app/tests/chat_apis/test_chat_model.py
git commit -m "feat(chat): ChatMessage 모델 + 마이그레이션"
```

---

## Task 3: chat DTO

**Files:**
- Create: `app/dtos/chat.py`
- Test: `app/tests/chat_apis/test_chat_dto.py`

- [ ] **Step 1: 실패 테스트 작성**

`app/tests/chat_apis/test_chat_dto.py`:
```python
import pytest
from pydantic import ValidationError

from app.dtos.chat import ChatMessageCreateRequest


def test_request_accepts_question():
    req = ChatMessageCreateRequest(question="단백질 권장량은?")
    assert req.question == "단백질 권장량은?"


def test_request_rejects_empty():
    with pytest.raises(ValidationError):
        ChatMessageCreateRequest(question="")
```

- [ ] **Step 2: 실패 확인**

Run: `./.venv/bin/python -m pytest app/tests/chat_apis/test_chat_dto.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: DTO 구현**

`app/dtos/chat.py`:
```python
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from app.dtos.base import BaseSerializerModel


class ChatMessageCreateRequest(BaseModel):
    question: Annotated[str, Field(min_length=1, max_length=2000, description="사용자 질문")]


class ChatMessageResponse(BaseSerializerModel):
    answer: str
    created_at: datetime
```

- [ ] **Step 4: 통과 확인**

Run: `./.venv/bin/python -m pytest app/tests/chat_apis/test_chat_dto.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/dtos/chat.py app/tests/chat_apis/test_chat_dto.py
git commit -m "feat(chat): chat 요청·응답 DTO"
```

---

## Task 4: chat_repository

**Files:**
- Create: `app/repositories/chat_repository.py`
- Test: `app/tests/chat_apis/test_chat_repository.py` (PostgreSQL 통합 — 기존 conftest fixture 사용)

- [ ] **Step 1: 실패 테스트 작성**

`app/tests/chat_apis/test_chat_repository.py` (기존 `app/tests/*/` 의 DB fixture 패턴을 따른다. 사용자 생성 헬퍼가 conftest에 있으면 재사용):
```python
import pytest

from app.models.chat import ChatRole
from app.repositories.chat_repository import ChatRepository

pytestmark = pytest.mark.asyncio


async def test_add_and_list(create_user):   # create_user: 기존 conftest fixture 가정
    user = await create_user()
    repo = ChatRepository()
    await repo.add(user_id=user.id, role=ChatRole.USER, content="질문")
    await repo.add(user_id=user.id, role=ChatRole.ASSISTANT, content="답변")
    total, items = await repo.get_by_user(user.id, limit=10, offset=0)
    assert total == 2
    assert items[0].content == "질문"   # created_at 오름차순
```
> conftest에 `create_user` fixture가 없으면, 다른 `app/tests/*/conftest.py`에서 사용자 생성 방식을 확인해 동일하게 작성하라.

- [ ] **Step 2: 실패 확인**

Run: `./.venv/bin/python -m pytest app/tests/chat_apis/test_chat_repository.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: repository 구현**

`app/repositories/chat_repository.py`:
```python
from app.models.chat import ChatMessage, ChatRole


class ChatRepository:
    async def add(self, *, user_id: int, role: ChatRole, content: str) -> ChatMessage:
        return await ChatMessage.create(user_id=user_id, role=role, content=content)

    async def get_by_user(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> tuple[int, list[ChatMessage]]:
        qs = ChatMessage.filter(user_id=user_id)
        total = await qs.count()
        items = await qs.order_by("created_at").offset(offset).limit(limit)
        return total, items
```

- [ ] **Step 4: 통과 확인**

Run: `./.venv/bin/python -m pytest app/tests/chat_apis/test_chat_repository.py -v`
Expected: PASS (DB 연결 필요 — docker compose up -d postgres)

- [ ] **Step 5: Commit**
```bash
git add app/repositories/chat_repository.py app/tests/chat_apis/test_chat_repository.py
git commit -m "feat(chat): ChatRepository (저장·조회)"
```

---

## Task 5: ai_worker 페이로드 스키마

**Files:**
- Create: `ai_worker/schemas/chat.py`
- Test: `ai_worker/schemas/test_chat_schema.py`

- [ ] **Step 1: 실패 테스트 작성**

`ai_worker/schemas/test_chat_schema.py`:
```python
from ai_worker.schemas.chat import ChatJob, ChatResult


def test_chat_job_roundtrip():
    job = ChatJob(job_id="abc", question="q", user_context={"eGFR": 50})
    dumped = job.model_dump_json()
    restored = ChatJob.model_validate_json(dumped)
    assert restored.job_id == "abc"
    assert restored.user_context["eGFR"] == 50


def test_chat_result_error_or_answer():
    assert ChatResult(answer="ok").answer == "ok"
    assert ChatResult(error="boom").error == "boom"
```

- [ ] **Step 2: 실패 확인**

Run: `cd .../AI_HealthCare_Final_Project && ./.venv/bin/python -m pytest ai_worker/schemas/test_chat_schema.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: 스키마 구현**

`ai_worker/schemas/chat.py`:
```python
"""백엔드 ↔ ai_worker Redis Stream 페이로드 스키마."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ChatJob(BaseModel):
    job_id: str
    question: str
    user_context: dict = Field(default_factory=dict)   # {eGFR, risk_group}


class ChatResult(BaseModel):
    answer: str | None = None
    error: str | None = None
```

- [ ] **Step 4: 통과 확인**

Run: `./.venv/bin/python -m pytest ai_worker/schemas/test_chat_schema.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add ai_worker/schemas/chat.py ai_worker/schemas/test_chat_schema.py
git commit -m "feat(chat): ai_worker Stream 페이로드 스키마"
```

---

## Task 6: ai_worker Redis 클라이언트 + rag_task 핸들러

**Files:**
- Create: `ai_worker/core/redis_client.py`
- Create: `ai_worker/tasks/rag_task.py`
- Test: `ai_worker/tasks/test_rag_task.py`

- [ ] **Step 1: 실패 테스트 작성 (run mock)**

`ai_worker/tasks/test_rag_task.py`:
```python
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
```

- [ ] **Step 2: 실패 확인**

Run: `./.venv/bin/python -m pytest ai_worker/tasks/test_rag_task.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: redis_client + rag_task 구현**

`ai_worker/core/redis_client.py`:
```python
"""ai_worker용 Redis 비동기 클라이언트."""
from __future__ import annotations

import redis.asyncio as aioredis

from ai_worker.core import config

_client: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _client
    if _client is None:
        _client = aioredis.from_url(
            f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}",
            decode_responses=True,
        )
    return _client
```

`ai_worker/tasks/rag_task.py`:
```python
"""RAG 작업 핸들러 — Stream 페이로드를 받아 run() 실행 (동기 블로킹 오프로딩)."""
from __future__ import annotations

import asyncio

from ai_worker.rag import run   # 테스트에서 monkeypatch 가능하도록 모듈 속성으로 import
from ai_worker.schemas.chat import ChatJob, ChatResult


async def handle_chat_job(job: ChatJob) -> ChatResult:
    try:
        answer = await asyncio.to_thread(run, job.question, job.user_context)
        return ChatResult(answer=answer)
    except Exception as e:  # noqa: BLE001 — worker는 어떤 예외도 결과로 전달해야 함
        return ChatResult(error=str(e))
```

- [ ] **Step 4: 통과 확인**

Run: `./.venv/bin/python -m pytest ai_worker/tasks/test_rag_task.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add ai_worker/core/redis_client.py ai_worker/tasks/rag_task.py ai_worker/tasks/test_rag_task.py
git commit -m "feat(chat): ai_worker Redis 클라이언트 + rag_task 핸들러"
```

---

## Task 7: ai_worker consumer (main.py)

**Files:**
- Modify: `ai_worker/main.py` (0줄 → consumer 루프)
- Test: `ai_worker/test_consume_once.py` (fakeredis)

- [ ] **Step 1: 실패 테스트 작성 (fakeredis + 핸들러 mock)**

`ai_worker/test_consume_once.py`:
```python
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

    # 작업 1건 투입
    await fake.xadd(config.RAG_JOBS_STREAM, {
        "job_id": "job1", "question": "단백질?", "user_context": json.dumps({}),
    })
    await worker.ensure_group(fake)
    await worker.consume_once(fake)

    resp = await fake.xrange(f"{config.RAG_RESP_PREFIX}:job1")
    assert resp, "응답 스트림이 비어있음"
    payload = json.loads(resp[0][1]["data"])
    assert payload["answer"] == "A:단백질?"
```

- [ ] **Step 2: 실패 확인**

Run: `./.venv/bin/python -m pytest ai_worker/test_consume_once.py -v`
Expected: FAIL (consume_once/ensure_group 없음)

- [ ] **Step 3: consumer 구현**

`ai_worker/main.py`:
```python
"""ai_worker 엔트리포인트 — Redis Stream consumer 루프.

rag_jobs 스트림을 consumer group 으로 읽어 rag_task 에 위임하고, 결과를
rag_resp:{job_id} 스트림에 기록한다. 실행: python -m ai_worker.main
"""
from __future__ import annotations

import asyncio
import json

from redis.exceptions import ResponseError

from ai_worker.core import config
from ai_worker.core.logger import setup_logger
from ai_worker.core.redis_client import get_redis
from ai_worker.schemas.chat import ChatJob
from ai_worker.tasks.rag_task import handle_chat_job

logger = setup_logger("ai_worker")
_CONSUMER = "worker-1"


async def ensure_group(redis) -> None:
    """consumer group 생성 (이미 있으면 무시). 스트림이 없어도 mkstream 으로 생성."""
    try:
        await redis.xgroup_create(
            config.RAG_JOBS_STREAM, config.RAG_JOBS_GROUP, id="0", mkstream=True
        )
    except ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise


async def consume_once(redis) -> int:
    """대기 중인 작업을 한 번 읽어 처리. 처리한 메시지 수 반환 (테스트·루프 공용)."""
    resp = await redis.xreadgroup(
        config.RAG_JOBS_GROUP, _CONSUMER,
        {config.RAG_JOBS_STREAM: ">"}, count=10, block=2000,
    )
    if not resp:
        return 0
    handled = 0
    for _stream, messages in resp:
        for msg_id, fields in messages:
            job = ChatJob(
                job_id=fields["job_id"],
                question=fields["question"],
                user_context=json.loads(fields.get("user_context", "{}")),
            )
            result = await handle_chat_job(job)
            await redis.xadd(
                f"{config.RAG_RESP_PREFIX}:{job.job_id}",
                {"data": result.model_dump_json()},
            )
            await redis.xack(config.RAG_JOBS_STREAM, config.RAG_JOBS_GROUP, msg_id)
            handled += 1
    return handled


async def main() -> None:
    redis = get_redis()
    await ensure_group(redis)
    logger.info("RAG consumer 시작 (stream=%s group=%s)", config.RAG_JOBS_STREAM, config.RAG_JOBS_GROUP)
    while True:
        try:
            await consume_once(redis)
        except Exception:  # noqa: BLE001 — 루프는 죽지 않아야 함
            logger.exception("consume 루프 오류 — 계속 진행")
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 4: 통과 확인**

Run: `./.venv/bin/python -m pytest ai_worker/test_consume_once.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add ai_worker/main.py ai_worker/test_consume_once.py
git commit -m "feat(chat): ai_worker Redis Stream consumer"
```

---

## Task 8: ChatService (핵심 — XADD + 응답 대기)

**Files:**
- Create: `app/services/chat.py`
- Test: `app/tests/chat_apis/test_chat_service.py` (fakeredis + DB)

- [ ] **Step 1: 실패 테스트 작성**

`app/tests/chat_apis/test_chat_service.py`:
```python
import asyncio
import json

import fakeredis.aioredis
import pytest

from app.core import config
from app.services import chat as chat_module
from app.services.chat import ChatService

pytestmark = pytest.mark.asyncio


async def test_ask_returns_answer(monkeypatch, create_user):
    user = await create_user()
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(chat_module, "get_redis", lambda: fake)

    service = ChatService()

    # worker 역할: job 들어오면 즉시 응답 채널에 기록
    async def fake_worker():
        for _ in range(50):
            jobs = await fake.xrange(config.RAG_JOBS_STREAM)
            if jobs:
                job_id = jobs[0][1]["job_id"]
                await fake.xadd(f"{config.RAG_RESP_PREFIX}:{job_id}",
                                {"data": json.dumps({"answer": "0.8 g/kg"})})
                return
            await asyncio.sleep(0.05)

    worker_task = asyncio.create_task(fake_worker())
    result = await service.ask(user_id=user.id, question="단백질 권장량?")
    await worker_task

    assert result.answer == "0.8 g/kg"


async def test_ask_timeout(monkeypatch, create_user):
    user = await create_user()
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(chat_module, "get_redis", lambda: fake)
    monkeypatch.setattr(config, "RAG_TIMEOUT_SEC", 1)   # 빠른 타임아웃
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await ChatService().ask(user_id=user.id, question="응답 없음")
    assert exc.value.status_code == 504
```

- [ ] **Step 2: 실패 확인**

Run: `./.venv/bin/python -m pytest app/tests/chat_apis/test_chat_service.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: ChatService 구현**

`app/services/chat.py`:
```python
"""RAG 챗봇 서비스 — user_context 빌드 → Redis 작업 투입 → 응답 대기 → 영속화."""
from __future__ import annotations

import json
import uuid

from fastapi import HTTPException
from starlette import status

from app.core import config
from app.core.redis_client import get_redis
from app.dtos.chat import ChatMessageResponse
from app.models.chat import ChatRole
from app.models.health_check import HealthCheck
from app.repositories.chat_repository import ChatRepository


class ChatService:
    def __init__(self) -> None:
        self._repo = ChatRepository()

    async def _build_user_context(self, user_id: int) -> dict:
        """최신 검진에서 RAG 가 쓰는 eGFR·risk_group 추출. 없으면 {} (RAG 안전 분기)."""
        hc = await HealthCheck.filter(user_id=user_id).order_by("-checked_date").first()
        if hc is None:
            return {}
        ctx: dict = {}
        if hc.egfr_estimated is not None:
            ctx["eGFR"] = hc.egfr_estimated
        if hc.ckd_stage is not None:
            ctx["risk_group"] = str(hc.ckd_stage)
        return ctx

    async def ask(self, user_id: int, question: str) -> ChatMessageResponse:
        redis = get_redis()
        user_context = await self._build_user_context(user_id)
        job_id = uuid.uuid4().hex

        await self._repo.add(user_id=user_id, role=ChatRole.USER, content=question)
        await redis.xadd(config.RAG_JOBS_STREAM, {
            "job_id": job_id,
            "question": question,
            "user_context": json.dumps(user_context),
        })

        resp_key = f"{config.RAG_RESP_PREFIX}:{job_id}"
        # 응답 채널 블로킹 대기 (밀리초). 타임아웃 시 빈 결과.
        result = await redis.xread({resp_key: "0"}, count=1, block=config.RAG_TIMEOUT_SEC * 1000)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="답변 생성이 지연되고 있습니다. 잠시 후 다시 시도해주세요.",
            )
        payload = json.loads(result[0][1][0][1]["data"])
        if payload.get("error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="답변 생성 중 오류가 발생했습니다.",
            )
        answer = payload["answer"]
        saved = await self._repo.add(user_id=user_id, role=ChatRole.ASSISTANT, content=answer)
        return ChatMessageResponse(answer=answer, created_at=saved.created_at)
```

- [ ] **Step 4: 통과 확인**

Run: `./.venv/bin/python -m pytest app/tests/chat_apis/test_chat_service.py -v`
Expected: PASS (DB + fakeredis)

- [ ] **Step 5: Commit**
```bash
git add app/services/chat.py app/tests/chat_apis/test_chat_service.py
git commit -m "feat(chat): ChatService — Redis 작업 투입·응답 대기·영속화"
```

---

## Task 9: chat_router + 라우터 등록

**Files:**
- Create: `app/apis/v1/chat_routers.py`
- Modify: `app/apis/v1/__init__.py` (import + include_router)
- Test: `app/tests/chat_apis/test_chat_router.py` (인증 + run/redis mock)

- [ ] **Step 1: 실패 테스트 작성**

`app/tests/chat_apis/test_chat_router.py` (기존 `app/tests/*/` 의 인증 클라이언트 fixture 패턴 사용 — 토큰 발급·헤더 주입 방식을 다른 라우터 테스트에서 확인해 동일하게):
```python
import pytest

pytestmark = pytest.mark.asyncio


async def test_post_message_requires_auth(client):   # client: 기존 conftest httpx fixture
    resp = await client.post("/api/v1/chat/messages", json={"question": "단백질?"})
    assert resp.status_code in (401, 403)


async def test_post_message_returns_answer(monkeypatch, auth_client):   # auth_client: 인증된 fixture
    from app.services import chat as chat_module
    from app.dtos.chat import ChatMessageResponse
    from datetime import datetime

    async def fake_ask(self, user_id, question):
        return ChatMessageResponse(answer="0.8 g/kg", created_at=datetime.now())
    monkeypatch.setattr(chat_module.ChatService, "ask", fake_ask)

    resp = await auth_client.post("/api/v1/chat/messages", json={"question": "단백질?"})
    assert resp.status_code == 200
    assert resp.json()["answer"] == "0.8 g/kg"
```
> `client`/`auth_client` fixture가 없으면 `app/tests/auth_apis/` 등에서 사용하는 fixture 이름·생성 방식을 확인해 맞춰라.

- [ ] **Step 2: 실패 확인**

Run: `./.venv/bin/python -m pytest app/tests/chat_apis/test_chat_router.py -v`
Expected: FAIL (404 — 라우터 미등록)

- [ ] **Step 3: 라우터 구현**

`app/apis/v1/chat_routers.py`:
```python
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import ORJSONResponse as Response

from app.dependencies.security import get_request_user
from app.dtos.chat import ChatMessageCreateRequest, ChatMessageResponse
from app.models.users import User
from app.services.chat import ChatService

chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.post(
    "/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="RAG 챗봇에 질문",
)
async def create_message(
    request: ChatMessageCreateRequest,
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[ChatService, Depends(ChatService)],
) -> Response:
    result = await service.ask(user_id=user.id, question=request.question)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)
```

- [ ] **Step 4: __init__.py 등록**

`app/apis/v1/__init__.py`에 import 추가 (lifestyle_survey import 근처):
```python
from app.apis.v1.chat_routers import chat_router
```
그리고 `v1_routers.include_router(...)` 블록에 추가:
```python
v1_routers.include_router(chat_router)
```

- [ ] **Step 5: 통과 확인**

Run: `./.venv/bin/python -m pytest app/tests/chat_apis/test_chat_router.py -v`
Expected: PASS

- [ ] **Step 6: Commit**
```bash
git add app/apis/v1/chat_routers.py app/apis/v1/__init__.py app/tests/chat_apis/test_chat_router.py
git commit -m "feat(chat): POST /chat/messages 라우터 + 등록"
```

---

## Task 10: 컨테이너 설정 (worker 기동)

**Files:**
- Modify: `ai_worker/Dockerfile:18`
- Modify: `docker-compose.yml` (ai-worker 서비스)
- Modify: `envs/.local.env`, `envs/example.local.env`

- [ ] **Step 1: Dockerfile CMD 교체**

`ai_worker/Dockerfile`의 `CMD ["echo", "'hello world'"]` 를 교체:
```dockerfile
CMD ["python", "-m", "ai_worker.main"]
```

- [ ] **Step 2: docker-compose ai-worker command·env 확인**

`docker-compose.yml`의 `ai-worker` 서비스에 `command`가 없으면 추가하고, REDIS/QDRANT/OPENAI env가 주입되는지 확인:
```yaml
  ai-worker:
    # ... 기존 build/depends_on 유지 ...
    command: ["python", "-m", "ai_worker.main"]
    environment:
      REDIS_HOST: redis
      QDRANT_URL: http://qdrant:6333
    env_file:
      - envs/.local.env   # OPENAI_API_KEY 등 (기존 경로 확인)
```

- [ ] **Step 3: env 예시에 REDIS 추가**

`envs/.local.env` 와 `envs/example.local.env` 에 추가 (없을 때):
```
REDIS_HOST=localhost
REDIS_PORT=6379
```
> docker 내부 실행 시 `REDIS_HOST=redis`는 compose의 environment가 우선.

- [ ] **Step 4: 검증 — compose 문법**

Run: `cd .../AI_HealthCare_Final_Project && docker compose config >/dev/null && echo OK`
Expected: OK (문법 오류 없음)

- [ ] **Step 5: Commit**
```bash
git add ai_worker/Dockerfile docker-compose.yml envs/.local.env envs/example.local.env
git commit -m "feat(chat): ai-worker 컨테이너 기동 설정 + REDIS env"
```

---

## Task 11: 전체 검증 (단위 + 통합 스모크)

**Files:** (없음 — 검증만)

- [ ] **Step 1: chat 단위 테스트 전체 통과**

Run: `cd .../AI_HealthCare_Final_Project && ./.venv/bin/python -m pytest app/tests/chat_apis/ ai_worker/tasks/test_rag_task.py ai_worker/schemas/test_chat_schema.py ai_worker/test_consume_once.py -v`
Expected: ALL PASS

- [ ] **Step 2: 기존 테스트 회귀 없음**

Run: `./.venv/bin/python -m pytest app/tests/ -q`
Expected: 기존 테스트 PASS 유지 (chat 추가로 깨진 것 없음)

- [ ] **Step 3: import 스모크 (app 전체 + chat 라우터 마운트)**

Run: `./.venv/bin/python -c "import app.main; routes=[r.path for r in app.main.app.routes if hasattr(r,'path')]; assert '/api/v1/chat/messages' in routes, routes; print('chat 라우터 마운트 OK')"`
Expected: `chat 라우터 마운트 OK`

- [ ] **Step 4: (선택) 실제 E2E 스모크 — docker 필요**

```bash
docker compose up -d postgres redis qdrant ai-worker fastapi
# OPENAI_API_KEY 가 envs/.local.env 에 설정돼 있어야 함
# 로그인 → 토큰 → POST /api/v1/chat/messages {"question":"만성콩팥병 단백질 권장량?"}
# 기대: 200 + answer 에 "0.8 g/kg" 류 + 출처/면책 포함
```
Expected: 실제 RAG 답변 반환 (Qdrant·OpenAI 연결 시)

- [ ] **Step 5: feat/RAG push + PR 준비**
```bash
git push -u origin feat/RAG
# GitHub에서 PR: feat/RAG → develop
```

---

## 완료 기준 (Definition of Done)
- chat 단위·통합 테스트 전체 통과 + 기존 테스트 회귀 0
- `/api/v1/chat/messages` 가 app에 마운트됨
- worker가 `python -m ai_worker.main` 으로 기동되어 작업 처리
- (docker 가용 시) 실제 질문에 RAG 답변 통째 반환 + 의료 가드 적용
- `feat/RAG` → `develop` PR 생성

## 주의 (점검 리포트 연계)
- 본 계획은 chat 슬라이스만 추가하며, 백엔드 점검(`260602_백엔드_코드점검_리포트.md`)의 보안 이슈(JWT 타입 검증 등)는 **백엔드 담당자 트랙**이라 본 계획 범위 밖이다. 단 chat_router도 동일 `get_request_user`를 쓰므로 그 수정의 영향을 받는다.
