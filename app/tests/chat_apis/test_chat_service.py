"""ChatService 통합 테스트.

tortoise.contrib.test.TestCase + fakeredis 패턴 사용.
DB 패턴은 test_chat_repository.py 및 test_streak_protect.py 와 동일.
"""

import asyncio
import json
from datetime import date

import fakeredis.aioredis
from tortoise.contrib.test import TestCase

from app.core import config
from app.models.users import User
from app.services import chat as chat_module
from app.services.chat import ChatService


async def _make_user(email: str = "chat_service_test@example.com") -> User:
    return await User.create(
        email=email,
        hashed_password="$2b$12$dummy",
        name="서비스테스터",
        gender="MALE",
        birthday=date(1990, 1, 1),
        phone_number="01011112222",
    )


class TestChatService(TestCase):
    async def test_ask_returns_answer(self):
        """RAG worker가 응답을 쓰면 ask()가 정상적으로 답변을 반환한다."""
        user = await _make_user()
        fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

        # get_redis를 fakeredis로 대체
        original_get_redis = chat_module.get_redis
        chat_module.get_redis = lambda: fake

        try:
            async def fake_worker():
                # rag_jobs 스트림에 job이 올 때까지 폴링 후 응답 기록
                for _ in range(50):
                    jobs = await fake.xrange(config.RAG_JOBS_STREAM)
                    if jobs:
                        job_id = jobs[0][1]["job_id"]
                        await fake.xadd(
                            f"{config.RAG_RESP_PREFIX}:{job_id}",
                            {"data": json.dumps({"answer": "0.8 g/kg"})},
                        )
                        return
                    await asyncio.sleep(0.05)

            worker_task = asyncio.create_task(fake_worker())
            result = await ChatService().ask(user_id=user.id, question="단백질 권장량?")
            await worker_task

            assert result.answer == "0.8 g/kg"
            assert result.created_at is not None
        finally:
            chat_module.get_redis = original_get_redis

    async def test_ask_timeout(self):
        """RAG worker가 응답하지 않으면 504 HTTPException이 발생한다."""
        user = await _make_user(email="chat_service_timeout@example.com")
        fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

        original_get_redis = chat_module.get_redis
        original_timeout = config.RAG_TIMEOUT_SEC
        chat_module.get_redis = lambda: fake
        config.RAG_TIMEOUT_SEC = 1  # 1초로 단축

        try:
            from fastapi import HTTPException

            with self.assertRaises(HTTPException) as ctx:
                await ChatService().ask(user_id=user.id, question="응답 없음")

            assert ctx.exception.status_code == 504
        finally:
            chat_module.get_redis = original_get_redis
            config.RAG_TIMEOUT_SEC = original_timeout

    async def test_ask_saves_messages_to_db(self):
        """ask() 성공 시 USER·ASSISTANT 메시지가 DB에 저장된다."""
        user = await _make_user(email="chat_service_save@example.com")
        fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

        original_get_redis = chat_module.get_redis
        chat_module.get_redis = lambda: fake

        try:
            async def fake_worker():
                for _ in range(50):
                    jobs = await fake.xrange(config.RAG_JOBS_STREAM)
                    if jobs:
                        job_id = jobs[0][1]["job_id"]
                        await fake.xadd(
                            f"{config.RAG_RESP_PREFIX}:{job_id}",
                            {"data": json.dumps({"answer": "하루 0.8~1.0g/kg 권장"})},
                        )
                        return
                    await asyncio.sleep(0.05)

            worker_task = asyncio.create_task(fake_worker())
            await ChatService().ask(user_id=user.id, question="단백질 하루 권장량?")
            await worker_task

            from app.models.chat import ChatMessage, ChatRole

            messages = await ChatMessage.filter(user_id=user.id).order_by("created_at")
            assert len(messages) == 2
            assert messages[0].role == ChatRole.USER
            assert messages[0].content == "단백질 하루 권장량?"
            assert messages[1].role == ChatRole.ASSISTANT
            assert messages[1].content == "하루 0.8~1.0g/kg 권장"
        finally:
            chat_module.get_redis = original_get_redis

    async def test_ask_timeout_saves_nothing(self):
        """timeout(504) 발생 시 DB에 해당 user의 ChatMessage가 0건이어야 한다 (고아 방지 I-1)."""
        user = await _make_user(email="chat_service_timeout_orphan@example.com")
        fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

        original_get_redis = chat_module.get_redis
        original_timeout = config.RAG_TIMEOUT_SEC
        chat_module.get_redis = lambda: fake
        config.RAG_TIMEOUT_SEC = 1  # 1초로 단축

        try:
            from fastapi import HTTPException

            with self.assertRaises(HTTPException) as ctx:
                await ChatService().ask(user_id=user.id, question="timeout 테스트 질문")

            assert ctx.exception.status_code == 504

            from app.models.chat import ChatMessage

            count = await ChatMessage.filter(user_id=user.id).count()
            assert count == 0, f"고아 메시지가 생겼습니다: {count}건"
        finally:
            chat_module.get_redis = original_get_redis
            config.RAG_TIMEOUT_SEC = original_timeout

    async def test_ask_empty_answer_raises_500(self):
        """worker가 {\"answer\": null, \"error\": null}을 반환하면 500 HTTPException이 발생한다 (C-1 null 가드)."""
        user = await _make_user(email="chat_service_null_answer@example.com")
        fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

        original_get_redis = chat_module.get_redis
        chat_module.get_redis = lambda: fake

        try:
            from fastapi import HTTPException

            async def fake_worker_null():
                for _ in range(50):
                    jobs = await fake.xrange(config.RAG_JOBS_STREAM)
                    if jobs:
                        job_id = jobs[0][1]["job_id"]
                        # answer와 error 모두 null인 비정상 페이로드
                        await fake.xadd(
                            f"{config.RAG_RESP_PREFIX}:{job_id}",
                            {"data": json.dumps({"answer": None, "error": None})},
                        )
                        return
                    await asyncio.sleep(0.05)

            worker_task = asyncio.create_task(fake_worker_null())

            with self.assertRaises(HTTPException) as ctx:
                await ChatService().ask(user_id=user.id, question="null 답변 테스트")

            await worker_task
            assert ctx.exception.status_code == 500
            assert "비어있습니다" in ctx.exception.detail

            # null answer 시에도 DB에 아무것도 저장되지 않아야 함
            from app.models.chat import ChatMessage

            count = await ChatMessage.filter(user_id=user.id).count()
            assert count == 0, f"null 답변인데 메시지가 저장됐습니다: {count}건"
        finally:
            chat_module.get_redis = original_get_redis

    async def test_ask_with_health_check_sends_user_context(self):
        """최신 검진 데이터가 있으면 user_context에 eGFR·risk_group이 포함된다."""
        user = await _make_user(email="chat_service_context@example.com")
        fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

        # 검진 데이터 생성
        from app.models.health_check import CkdStage, HealthCheck

        await HealthCheck.create(
            user_id=user.id,
            checked_date=date(2026, 6, 1),
            systolic_bp=120,
            diastolic_bp=80,
            fasting_glucose=90.0,
            weight=70.0,
            height=175.0,
            bmi=22.9,
            egfr_estimated=55.0,
            ckd_stage=CkdStage.G3A,
        )

        original_get_redis = chat_module.get_redis
        chat_module.get_redis = lambda: fake

        try:
            captured_context: dict = {}

            async def fake_worker():
                for _ in range(50):
                    jobs = await fake.xrange(config.RAG_JOBS_STREAM)
                    if jobs:
                        job_id = jobs[0][1]["job_id"]
                        raw_ctx = jobs[0][1].get("user_context", "{}")
                        captured_context.update(json.loads(raw_ctx))
                        await fake.xadd(
                            f"{config.RAG_RESP_PREFIX}:{job_id}",
                            {"data": json.dumps({"answer": "저단백식이 권장"})},
                        )
                        return
                    await asyncio.sleep(0.05)

            worker_task = asyncio.create_task(fake_worker())
            await ChatService().ask(user_id=user.id, question="식이 권장사항?")
            await worker_task

            assert captured_context.get("eGFR") == 55.0
            assert captured_context.get("risk_group") == "G3A"
        finally:
            chat_module.get_redis = original_get_redis
