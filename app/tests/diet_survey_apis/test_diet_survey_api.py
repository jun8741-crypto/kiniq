from httpx import ASGITransport, AsyncClient
from starlette import status
from tortoise.contrib.test import TestCase

from app.main import app

_SIGNUP_DATA = {
    "email": "diet_test@example.com",
    "password": "Password123!",
    "name": "식이설문테스터",
    "gender": "MALE",
    "birth_date": "1985-03-15",
    "phone_number": "01055556666",
}
_LOGIN_DATA = {"email": "diet_test@example.com", "password": "Password123!"}

_SURVEY_PAYLOAD = {
    "surveyed_date": "2026-05-21",
    "soup_stew_per_day": 2,
    "sweet_drink_per_day": 1,
    "fried_food_per_week": 3,
    "vegetables_every_meal": True,
}


async def _get_token(client: AsyncClient) -> str:
    await client.post("/api/v1/auth/signup", json=_SIGNUP_DATA)
    resp = await client.post("/api/v1/auth/login", json=_LOGIN_DATA)
    return resp.json()["access_token"]


class TestDietSurveyCreateAPI(TestCase):
    async def test_create_survey_success(self):
        """정상 설문 입력 → 201, 전체 필드 반환."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await _get_token(client)
            response = await client.post(
                "/api/v1/diet-surveys",
                json=_SURVEY_PAYLOAD,
                headers={"Authorization": f"Bearer {token}"},
            )
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["soup_stew_per_day"] == 2
        assert body["sweet_drink_per_day"] == 1
        assert body["fried_food_per_week"] == 3
        assert body["vegetables_every_meal"] is True
        assert body["surveyed_date"] == "2026-05-21"
        assert "id" in body
        assert "user_id" in body

    async def test_create_survey_unauthorized(self):
        """토큰 없이 요청 → 401."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/diet-surveys", json=_SURVEY_PAYLOAD)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_survey_invalid_range(self):
        """범위 초과 값 → 422."""
        payload = {**_SURVEY_PAYLOAD, "soup_stew_per_day": 99}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await _get_token(client)
            response = await client.post(
                "/api/v1/diet-surveys",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDietSurveyListAPI(TestCase):
    async def test_list_surveys_empty(self):
        """설문 이력 없는 신규 유저 → total=0."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await _get_token(client)
            response = await client.get(
                "/api/v1/diet-surveys",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["total"] == 0
        assert body["items"] == []

    async def test_list_surveys_after_create(self):
        """설문 입력 후 목록 조회 → total=1."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await _get_token(client)
            headers = {"Authorization": f"Bearer {token}"}
            await client.post("/api/v1/diet-surveys", json=_SURVEY_PAYLOAD, headers=headers)
            response = await client.get("/api/v1/diet-surveys", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] == 1

    async def test_list_surveys_unauthorized(self):
        """토큰 없이 목록 요청 → 401."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/diet-surveys")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSurveyStatusAPI(TestCase):
    async def test_status_both_false(self):
        """설문 미완료 신규 유저 → 둘 다 false."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await _get_token(client)
            response = await client.get(
                "/api/v1/surveys/status",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["lifestyle_survey"] is False
        assert body["diet_survey"] is False

    async def test_status_diet_true_after_create(self):
        """식이 설문 입력 후 → diet_survey=true."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await _get_token(client)
            headers = {"Authorization": f"Bearer {token}"}
            await client.post("/api/v1/diet-surveys", json=_SURVEY_PAYLOAD, headers=headers)
            response = await client.get("/api/v1/surveys/status", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["diet_survey"] is True
        assert body["lifestyle_survey"] is False

    async def test_status_unauthorized(self):
        """토큰 없이 상태 요청 → 401."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/surveys/status")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
