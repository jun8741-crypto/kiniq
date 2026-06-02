"""전역 에러 핸들러 통합 테스트.

목적: Pydantic 422 / HTTPException / 일반 예외가 한국어 응답으로 변환되는지 검증.
"""

from httpx import ASGITransport, AsyncClient
from tortoise.contrib.test import TestCase

from app.main import app

TEST_URL = "http://test"


class TestValidationErrorHandler(TestCase):
    async def test_invalid_email_format_returns_korean(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_URL) as client:
            resp = await client.post(
                "/api/v1/auth/signup",
                json={
                    "email": "not-an-email",
                    "password": "Pass1234!",
                    "name": "테스트",
                    "gender": "MALE",
                    "birth_date": "1990-01-01",
                    "phone_number": "01000000000",
                },
            )
        assert resp.status_code == 422
        body = resp.json()
        assert "detail" in body
        assert isinstance(body["detail"], list)
        # 이메일 필드에 대한 한국어 메시지
        items = body["detail"]
        email_err = next((i for i in items if i.get("field") == "이메일"), None)
        assert email_err is not None
        assert "이메일" in email_err["message"] or "형식" in email_err["message"]

    async def test_missing_required_returns_korean(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_URL) as client:
            resp = await client.post("/api/v1/auth/signup", json={"email": "test@test.com"})
        assert resp.status_code == 422
        body = resp.json()
        items = body["detail"]
        # 누락 필드 메시지가 "필수 입력 항목입니다." 한국어
        missing_msgs = [i["message"] for i in items if "필수" in i.get("message", "")]
        assert len(missing_msgs) > 0


class TestHTTPExceptionPassthrough(TestCase):
    async def test_404_korean_detail_preserved(self) -> None:
        """존재하지 않는 user_challenge_id 체크인 → 한국어 detail 그대로."""
        # 회원가입 + 로그인
        async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_URL) as client:
            await client.post(
                "/api/v1/auth/signup",
                json={
                    "email": "err@test.com",
                    "password": "Pass1234!",
                    "name": "에러테스터",
                    "gender": "MALE",
                    "birth_date": "1990-01-01",
                    "phone_number": "01099887766",
                },
            )
            login = await client.post("/api/v1/auth/login", json={"email": "err@test.com", "password": "Pass1234!"})
            token = login.json()["access_token"]
            resp = await client.post(
                "/api/v1/user-challenges/99999/checkin",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == 404
        body = resp.json()
        # 한국어 detail (문자열)
        assert isinstance(body["detail"], str)
        assert "찾을 수 없습니다" in body["detail"]
