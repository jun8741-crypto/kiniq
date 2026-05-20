from enum import StrEnum

from tortoise import fields, models


class SmokingStatus(StrEnum):
    NEVER = "NEVER"
    PAST = "PAST"
    CURRENT = "CURRENT"


class DrinkingFrequency(StrEnum):
    NEVER = "NEVER"
    OCCASIONALLY = "OCCASIONALLY"
    WEEKLY = "WEEKLY"
    DAILY = "DAILY"


class StressLevel(StrEnum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class LifestyleSurvey(models.Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="lifestyle_surveys")
    surveyed_date = fields.DateField(description="설문 응답일")

    smoking_status = fields.CharEnumField(enum_type=SmokingStatus, description="흡연 상태")
    drinking_frequency = fields.CharEnumField(enum_type=DrinkingFrequency, description="음주 빈도")
    exercise_days_per_week = fields.IntField(description="주당 운동 일수 (0~7)")
    sleep_hours_per_day = fields.FloatField(null=True, description="하루 평균 수면 시간 (시간)")
    daily_water_intake = fields.FloatField(null=True, description="하루 평균 수분 섭취량 (L)")
    stress_level = fields.CharEnumField(enum_type=StressLevel, null=True, description="스트레스 수준")

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "lifestyle_surveys"
        ordering = ["-surveyed_date"]
