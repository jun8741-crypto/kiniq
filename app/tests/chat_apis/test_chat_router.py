"""POST /api/v1/chat/messages 라우터 테스트.

패턴: tortoise.contrib.test.TestCase + httpx AsyncClient(ASGITransport)
인증: signup → login → Bearer 토큰 (기존 health_check / lifestyle_survey 테스트와 동일)
ChatService.ask: monkeypatch (Redis/worker 없이 라우터만 검증)
"""
from datetime import datetime, timezone

from httpx import ASGITransport, AsyncClient
from starlette import status
from tortoise.contrib.test import TestCase

from app.main import app
from app.services import chat as chat_module

_SIGNUP_DATA = {
    "email": "chat_router_test@example.com",
    "password": "Password123!",
    "name": "챗라우터테스터",
    "gender": "MALE",
    "birth_date": "1990-01-01",
    "phone_number": "01055556666",
}
_LOGIN_DATA = {
    "email": "chat_router_test@example.com",
    "password": "Password123!",
}


async def _get_token(client: AsyncClient) -> str:
    """회원가입 후 access_token 반환 헬퍼."""
    await client.post("/api/v1/auth/signup", json=_SIGNUP_DATA)
    resp = await client.post("/api/v1/auth/login", json=_LOGIN_DATA)
    return resp.json()["access_token"]


class TestChatRouterAuth(TestCase):
    async def test_post_message_requires_auth(self):
        """인증 없이 POST → 401."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat/messages",
                json={"question": "인증 없이 질문"},
            )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestChatRouterAnswer(TestCase):
    async def test_post_message_returns_answer(self):
        """인증된 요청 + ChatService.ask monkeypatch → 200 + answer 반환."""
        from app.dtos.chat import ChatMessageResponse

        fake_answer = "하루 단백질 0.8 g/kg 권장합니다."
        fake_created_at = datetime(2026, 6, 2, 12, 0, 0, tzinfo=timezone.utc)

        # ChatService.ask를 가짜 응답으로 교체 (Redis/worker 의존 없이)
        original_ask = chat_module.ChatService.ask

        async def fake_ask(self, user_id: int, question: str) -> ChatMessageResponse:  # noqa: ARG001
            return ChatMessageResponse(answer=fake_answer, created_at=fake_created_at)

        chat_module.ChatService.ask = fake_ask
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                token = await _get_token(client)
                response = await client.post(
                    "/api/v1/chat/messages",
                    json={"question": "단백질 권장량이 얼마인가요?"},
                    headers={"Authorization": f"Bearer {token}"},
                )
        finally:
            chat_module.ChatService.ask = original_ask

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["answer"] == fake_answer
        assert "created_at" in body
