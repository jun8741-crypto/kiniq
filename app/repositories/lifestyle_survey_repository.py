from datetime import date

from app.models.lifestyle_survey import (
    DrinkingFrequency,
    LifestyleSurvey,
    SmokingStatus,
    StressLevel,
)


class LifestyleSurveyRepository:
    async def create(
        self,
        user_id: int,
        surveyed_date: date,
        smoking_status: SmokingStatus,
        drinking_frequency: DrinkingFrequency,
        exercise_days_per_week: int,
        sleep_hours_per_day: float | None = None,
        daily_water_intake: float | None = None,
        stress_level: StressLevel | None = None,
    ) -> LifestyleSurvey:
        return await LifestyleSurvey.create(
            user_id=user_id,
            surveyed_date=surveyed_date,
            smoking_status=smoking_status,
            drinking_frequency=drinking_frequency,
            exercise_days_per_week=exercise_days_per_week,
            sleep_hours_per_day=sleep_hours_per_day,
            daily_water_intake=daily_water_intake,
            stress_level=stress_level,
        )

    async def get_by_user(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[int, list[LifestyleSurvey]]:
        qs = LifestyleSurvey.filter(user_id=user_id)
        total = await qs.count()
        items = await qs.order_by("-surveyed_date").offset(offset).limit(limit)
        return total, items

    async def get_latest(self, user_id: int) -> LifestyleSurvey | None:
        return await LifestyleSurvey.filter(user_id=user_id).order_by("-surveyed_date").first()

    async def get_by_id(self, survey_id: int, user_id: int) -> LifestyleSurvey | None:
        return await LifestyleSurvey.get_or_none(id=survey_id, user_id=user_id)

    async def exists_by_user(self, user_id: int) -> bool:
        return await LifestyleSurvey.filter(user_id=user_id).exists()

    async def upsert(
        self,
        user_id: int,
        surveyed_date: date,
        smoking_status: SmokingStatus,
        drinking_frequency: DrinkingFrequency,
        exercise_days_per_week: int,
        sleep_hours_per_day: float | None = None,
        daily_water_intake: float | None = None,
        stress_level: StressLevel | None = None,
    ) -> LifestyleSurvey:
        """기존 사용자 설문 있으면 갱신, 없으면 생성. 최신 1건만 유지하는 정책."""
        existing = await self.get_latest(user_id)
        if existing:
            existing.surveyed_date = surveyed_date
            existing.smoking_status = smoking_status
            existing.drinking_frequency = drinking_frequency
            existing.exercise_days_per_week = exercise_days_per_week
            existing.sleep_hours_per_day = sleep_hours_per_day
            existing.daily_water_intake = daily_water_intake
            existing.stress_level = stress_level
            await existing.save()
            return existing
        return await self.create(
            user_id=user_id,
            surveyed_date=surveyed_date,
            smoking_status=smoking_status,
            drinking_frequency=drinking_frequency,
            exercise_days_per_week=exercise_days_per_week,
            sleep_hours_per_day=sleep_hours_per_day,
            daily_water_intake=daily_water_intake,
            stress_level=stress_level,
        )
