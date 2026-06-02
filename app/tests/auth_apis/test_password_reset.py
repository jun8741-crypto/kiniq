from httpx import ASGITransport, AsyncClient
from starlette import status
from tortoise.contrib.test import TestCase

from app.main import app

SIGNUP_PAYLOAD = {
    "email": "reset_test@example.com",
    "password": "Password123!",
    "name": "리셋테스터",
    "gender": "MALE",
    "birth_date": "1990-01-01",
    "phone_number": "01099887766",
}


class TestPasswordResetAPI(TestCase):
    async def _signup(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
        assert resp.status_code == status.HTTP_201_CREATED

    async def test_request_password_reset_demo_mode_returns_code(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await self._signup(client)
            resp = await client.post(
                "/api/v1/auth/password-reset/request",
                json={"email": SIGNUP_PAYLOAD["email"]},
            )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["sent"] is True
        assert data["mode"] == "demo"
        assert data["demo_code"] is not None
        assert len(data["demo_code"]) == 6
        assert data["demo_code"].isdigit()
        assert data["expires_in_seconds"] >= 60

    async def test_request_password_reset_unknown_email(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/auth/password-reset/request",
                json={"email": "nobody@example.com"},
            )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "등록된 이메일이 없습니다" in resp.json()["detail"]

    async def test_verify_password_reset_happy_path(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await self._signup(client)
            req = await client.post(
                "/api/v1/auth/password-reset/request",
                json={"email": SIGNUP_PAYLOAD["email"]},
            )
            code = req.json()["demo_code"]
            resp = await client.post(
                "/api/v1/auth/password-reset/verify",
                json={"email": SIGNUP_PAYLOAD["email"], "code": code},
            )
        assert resp.status_code == status.HTTP_200_OK
        temp_pw = resp.json()["temp_password"]
        assert len(temp_pw) == 12

        # 임시 비밀번호로 로그인 가능
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            login = await client.post(
                "/api/v1/auth/login",
                json={"email": SIGNUP_PAYLOAD["email"], "password": temp_pw},
            )
        assert login.status_code == status.HTTP_200_OK

    async def test_verify_password_reset_wrong_code_decrements_attempts(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await self._signup(client)
            await client.post(
                "/api/v1/auth/password-reset/request",
                json={"email": SIGNUP_PAYLOAD["email"]},
            )
            resp = await client.post(
                "/api/v1/auth/password-reset/verify",
                json={"email": SIGNUP_PAYLOAD["email"], "code": "000000"},
            )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "일치하지 않습니다" in resp.json()["detail"]

    async def test_verify_password_reset_max_attempts_exceeded(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await self._signup(client)
            req = await client.post(
                "/api/v1/auth/password-reset/request",
                json={"email": SIGNUP_PAYLOAD["email"]},
            )
            correct = req.json()["demo_code"]
            # 5회 잘못된 시도
            for _ in range(5):
                wrong = "000000" if correct != "000000" else "111111"
                await client.post(
                    "/api/v1/auth/password-reset/verify",
                    json={"email": SIGNUP_PAYLOAD["email"], "code": wrong},
                )
            # 6번째는 코드가 맞아도 차단
            blocked = await client.post(
                "/api/v1/auth/password-reset/verify",
                json={"email": SIGNUP_PAYLOAD["email"], "code": correct},
            )
        assert blocked.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "초과" in blocked.json()["detail"]

    async def test_verify_without_request_returns_error(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await self._signup(client)
            resp = await client.post(
                "/api/v1/auth/password-reset/verify",
                json={"email": SIGNUP_PAYLOAD["email"], "code": "123456"},
            )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "발급된 인증 코드" in resp.json()["detail"]

    async def test_request_password_reset_invalid_email_format(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/auth/password-reset/request",
                json={"email": "not-an-email"},
            )
        # Pydantic 422 → 한국어 미들웨어
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        body = resp.json()
        assert isinstance(body["detail"], list)
        assert "이메일" in body["detail"][0]["message"]
