from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, Field

from app.dtos.base import BaseSerializerModel


class DietSurveyCreateRequest(BaseModel):
    surveyed_date: Annotated[date, Field(description="설문 응답일 (YYYY-MM-DD)")]
    soup_stew_per_day: Annotated[int, Field(ge=0, le=20, description="하루 국·찌개·탕류 횟수")]
    sweet_drink_per_day: Annotated[int, Field(ge=0, le=30, description="하루 단 음료 잔 수")]
    fried_food_per_week: Annotated[int, Field(ge=0, le=21, description="주 튀긴 음식 횟수")]
    vegetables_every_meal: Annotated[bool, Field(description="매 끼 채소 반찬 여부")]


class DietSurveyResponse(BaseSerializerModel):
    id: int
    user_id: int
    surveyed_date: date
    soup_stew_per_day: int
    sweet_drink_per_day: int
    fried_food_per_week: int
    vegetables_every_meal: bool
    created_at: datetime


class DietSurveyListResponse(BaseSerializerModel):
    total: int
    items: list[DietSurveyResponse]


class SurveyStatusResponse(BaseModel):
    lifestyle_survey: bool
    diet_survey: bool
