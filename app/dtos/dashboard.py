from datetime import date, datetime

from app.dtos.base import BaseSerializerModel
from app.models.health_check import CkdStage
from app.models.lifestyle_survey import DrinkingFrequency, SmokingStatus, StressLevel


class LatestHealthMetrics(BaseSerializerModel):
    checked_date: date
    systolic_bp: int
    diastolic_bp: int
    fasting_glucose: float
    bmi: float
    egfr_estimated: float | None
    ckd_stage: CkdStage | None
    ckd_risk_score: float | None


class EgfrDataPoint(BaseSerializerModel):
    checked_date: date
    egfr_estimated: float


class EgfrTrendResponse(BaseSerializerModel):
    data_points: list[EgfrDataPoint]


class ChallengeStats(BaseSerializerModel):
    active_count: int
    completed_count: int
    total_checkins: int
    best_streak: int


class LatestLifestyleSummary(BaseSerializerModel):
    surveyed_date: date
    smoking_status: SmokingStatus
    drinking_frequency: DrinkingFrequency
    exercise_days_per_week: int
    stress_level: StressLevel | None


class DashboardSummaryResponse(BaseSerializerModel):
    latest_health: LatestHealthMetrics | None
    challenge_stats: ChallengeStats
    latest_lifestyle: LatestLifestyleSummary | None
    generated_at: datetime
