"""REQ-AUTH-007 비밀번호 5회 실패 30분 잠금 테스트."""

from datetime import UTC, datetime, timedelta

from httpx import ASGITransport, AsyncClient
from tortoise.contrib.test import TestCase

from app.main import app
from app.models.users import User

TEST_URL = "http://test"
_SIGNUP_DATA = {
    "email": "lock_test@example.com",
    "password": "Password123!",
    "name": "잠금테스터",
    "gender": "MALE",
    "birth_date": "1990-01-01",
    "phone_number": "01012345678",
}


async def _signup(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/signup", json=_SIGNUP_DATA)


async def _login(client: AsyncClient, password: str):
    return await client.post("/api/v1/auth/login", json={"email": _SIGNUP_DATA["email"], "password": password})


class TestPasswordLock(TestCase):
    async def test_wrong_password_increments_counter(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_URL) as client:
            await _signup(client)
            resp = await _login(client, "WrongPass!")
        assert resp.status_code == 400
        assert "4회 남음" in resp.json()["detail"]  # 5 - 1 = 4 남음
        user = await User.get(email=_SIGNUP_DATA["email"])
        assert user.failed_login_count == 1
        assert user.locked_until is None

    async def test_5_wrong_attempts_locks_account(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_URL) as client:
            await _signup(client)
            # 4번 틀림
            for _ in range(4):
                await _login(client, "WrongPass!")
            # 5번째 → 잠금
            resp = await _login(client, "WrongPass!")
        assert resp.status_code == 423
        body = resp.json()
        assert "5회 틀렸습니다" in body["detail"]
        assert "30분" in body["detail"]
        user = await User.get(email=_SIGNUP_DATA["email"])
        assert user.locked_until is not None
        assert user.locked_until > datetime.now(UTC)
        # 카운터는 리셋됨 (5회 도달 후)
        assert user.failed_login_count == 0

    async def test_locked_account_rejects_login_with_correct_password(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_URL) as client:
            await _signup(client)
            # 잠금 상태 만들기
            user = await User.get(email=_SIGNUP_DATA["email"])
            user.locked_until = datetime.now(UTC) + timedelta(minutes=15)
            await user.save()
            # 올바른 비번이어도 잠겨 있어 거절
            resp = await _login(client, _SIGNUP_DATA["password"])
        assert resp.status_code == 423
        assert "잠겼습니다" in resp.json()["detail"]
        # 남은 시간 분 표시
        assert "분" in resp.json()["detail"]

    async def test_successful_login_resets_counter(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_URL) as client:
            await _signup(client)
            # 3번 틀림 (잠금 직전)
            for _ in range(3):
                await _login(client, "WrongPass!")
            user = await User.get(email=_SIGNUP_DATA["email"])
            assert user.failed_login_count == 3
            # 올바른 비번으로 성공
            resp = await _login(client, _SIGNUP_DATA["password"])
        assert resp.status_code == 200
        user = await User.get(email=_SIGNUP_DATA["email"])
        # 카운터 리셋
        assert user.failed_login_count == 0
        assert user.locked_until is None

    async def test_expired_lock_allows_login_again(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_URL) as client:
            await _signup(client)
            # 과거 시점으로 잠금 (이미 만료된 잠금)
            user = await User.get(email=_SIGNUP_DATA["email"])
            user.locked_until = datetime.now(UTC) - timedelta(minutes=1)
            user.failed_login_count = 0
            await user.save()
            # 올바른 비번 → 성공
            resp = await _login(client, _SIGNUP_DATA["password"])
        assert resp.status_code == 200
