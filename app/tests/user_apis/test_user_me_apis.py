from httpx import ASGITransport, AsyncClient
from starlette import status
from tortoise.contrib.test import TestCase

from app.main import app


class TestUserMeApis(TestCase):
    async def test_get_user_me_success(self):
        # 사용자 등록 및 로그인
        email = "me@example.com"
        signup_data = {
            "email": email,
            "password": "Password123!",
            "name": "내정보테스터",
            "gender": "FEMALE",
            "birth_date": "1992-02-02",
            "phone_number": "01055556666",
        }
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post("/api/v1/auth/signup", json=signup_data)

            login_response = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
            access_token = login_response.json()["access_token"]

            # 내 정보 조회
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == email
        assert response.json()["name"] == "내정보테스터"

    async def test_update_user_me_success(self):
        # 사용자 등록 및 로그인
        email = "update_me@example.com"
        signup_data = {
            "email": email,
            "password": "Password123!",
            "name": "수정전",
            "gender": "MALE",
            "birth_date": "1990-10-10",
            "phone_number": "01077778888",
        }
        update_data = {"name": "수정후"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post("/api/v1/auth/signup", json=signup_data)

            login_response = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
            access_token = login_response.json()["access_token"]

            # 내 정보 수정
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.patch("/api/v1/users/me", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "수정후"

    async def test_get_user_me_unauthorized(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_change_password_success(self):
        email = "pw_change@example.com"
        signup_data = {
            "email": email,
            "password": "OldPass123!",
            "name": "비번변경",
            "gender": "MALE",
            "birth_date": "1988-05-05",
            "phone_number": "01011112222",
        }
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post("/api/v1/auth/signup", json=signup_data)
            login_response = await client.post("/api/v1/auth/login", json={"email": email, "password": "OldPass123!"})
            access_token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}

            response = await client.patch(
                "/api/v1/users/me/password",
                json={"current_password": "OldPass123!", "new_password": "NewPass456@"},
                headers=headers,
            )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_change_password_wrong_current(self):
        email = "pw_wrong@example.com"
        signup_data = {
            "email": email,
            "password": "OldPass123!",
            "name": "비번틀림",
            "gender": "FEMALE",
            "birth_date": "1995-03-15",
            "phone_number": "01033334444",
        }
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post("/api/v1/auth/signup", json=signup_data)
            login_response = await client.post("/api/v1/auth/login", json={"email": email, "password": "OldPass123!"})
            access_token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}

            response = await client.patch(
                "/api/v1/users/me/password",
                json={"current_password": "WrongPass999!", "new_password": "NewPass456@"},
                headers=headers,
            )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_delete_account_success(self):
        email = "delete_me@example.com"
        signup_data = {
            "email": email,
            "password": "Password123!",
            "name": "탈퇴테스터",
            "gender": "MALE",
            "birth_date": "1985-07-20",
            "phone_number": "01099998888",
        }
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post("/api/v1/auth/signup", json=signup_data)
            login_response = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
            access_token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}

            response = await client.delete("/api/v1/users/me", headers=headers)
            assert response.status_code == status.HTTP_204_NO_CONTENT

            # 탈퇴 후 동일 이메일로 재로그인 불가
            login_again = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
        assert login_again.status_code == status.HTTP_400_BAD_REQUEST
