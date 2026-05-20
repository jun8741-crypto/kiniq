from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, Field

from app.dtos.base import BaseSerializerModel
from app.models.lifestyle_survey import DrinkingFrequency, SmokingStatus, StressLevel


class LifestyleSurveyCreateRequest(BaseModel):
    surveyed_date: Annotated[date, Field(description="설문 응답일 (YYYY-MM-DD)")]
    smoking_status: Annotated[SmokingStatus, Field(description="흡연 상태")]
    drinking_frequency: Annotated[DrinkingFrequency, Field(description="음주 빈도")]
    exercise_days_per_week: Annotated[int, Field(ge=0, le=7, description="주당 운동 일수")]
    sleep_hours_per_day: Annotated[
        float | None,
        Field(None, ge=0.0, le=24.0, description="하루 평균 수면 시간 (시간)"),
    ]
    daily_water_intake: Annotated[
        float | None,
        Field(None, ge=0.0, le=10.0, description="하루 평균 수분 섭취량 (L)"),
    ]
    stress_level: Annotated[StressLevel | None, Field(None, description="스트레스 수준")]


class LifestyleSurveyResponse(BaseSerializerModel):
    id: int
    user_id: int
    surveyed_date: date
    smoking_status: SmokingStatus
    drinking_frequency: DrinkingFrequency
    exercise_days_per_week: int
    sleep_hours_per_day: float | None
    daily_water_intake: float | None
    stress_level: StressLevel | None
    created_at: datetime


class LifestyleSurveyListResponse(BaseSerializerModel):
    total: int
    items: list[LifestyleSurveyResponse]
