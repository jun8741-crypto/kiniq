from httpx import ASGITransport, AsyncClient
from starlette import status
from tortoise.contrib.test import TestCase

from app.main import app

_SIGNUP_DATA = {
    "email": "lifestyle_test@example.com",
    "password": "Password123!",
    "name": "생활습관테스터",
    "gender": "FEMALE",
    "birth_date": "1990-07-20",
    "phone_number": "01033334444",
}
_LOGIN_DATA = {"email": "lifestyle_test@example.com", "password": "Password123!"}

_SURVEY_PAYLOAD = {
    "surveyed_date": "2026-05-20",
    "smoking_status": "NEVER",
    "drinking_frequency": "OCCASIONALLY",
    "exercise_days_per_week": 3,
    "sleep_hours_per_day": 7.0,
    "daily_water_intake": 1.5,
    "stress_level": "MODERATE",
}


async def _get_token(client: AsyncClient) -> str:
    await client.post("/api/v1/auth/signup", json=_SIGNUP_DATA)
    resp = await client.post("/api/v1/auth/login", json=_LOGIN_DATA)
    return resp.json()["access_token"]


class TestLifestyleSurveyCreateAPI(TestCase):
    async def test_create_survey_success(self):
        """정상 설문 입력 → 201, 전체 필드 반환."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await _get_token(client)
            response = await client.post(
                "/api/v1/lifestyle-surveys",
                json=_SURVEY_PAYLOAD,
                headers={"Authorization": f"Bearer {token}"},
            )
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["smoking_status"] == "NEVER"
        assert body["exercise_days_per_week"] == 3
        assert body["stress_level"] == "MODERATE"
        assert body["sleep_hours_per_day"] == 7.0
        assert body["daily_water_intake"] == 1.5

    async def test_create_survey_minimal(self):
        """선택 항목 없이 필수 항목만 → 201."""
        payload = {
            "surveyed_date": "2026-05-20",
            "smoking_status": "CURRENT",
            "drinking_frequency": "DAILY",
            "exercise_days_per_week": 0,
        }
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await _get_token(client)
            response = await client.post(
                "/api/v1/lifestyle-surveys",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["sleep_hours_per_day"] is None
        assert body["daily_water_intake"] is None
        assert body["stress_level"] is None

    async def test_create_survey_unauthorized(self):
        """토큰 없이 요청 → 401."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/lifestyle-surveys", json=_SURVEY_PAYLOAD)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLifestyleSurveyListAPI(TestCase):
    async def test_list_surveys_empty(self):
        """설문 이력 없는 신규 유저 → total=0."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await _get_token(client)
            response = await client.get(
                "/api/v1/lifestyle-surveys",
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
            await client.post("/api/v1/lifestyle-surveys", json=_SURVEY_PAYLOAD, headers=headers)
            response = await client.get("/api/v1/lifestyle-surveys", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] == 1


class TestLifestyleSurveyDetailAPI(TestCase):
    async def test_get_survey_success(self):
        """단건 조회 → 200, 내용 일치."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await _get_token(client)
            headers = {"Authorization": f"Bearer {token}"}
            created = await client.post("/api/v1/lifestyle-surveys", json=_SURVEY_PAYLOAD, headers=headers)
            survey_id = created.json()["id"]
            response = await client.get(f"/api/v1/lifestyle-surveys/{survey_id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == survey_id

    async def test_get_survey_not_found(self):
        """존재하지 않는 ID → 404."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            token = await _get_token(client)
            response = await client.get(
                "/api/v1/lifestyle-surveys/99999",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert response.status_code == status.HTTP_404_NOT_FOUND
