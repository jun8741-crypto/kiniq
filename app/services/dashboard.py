from datetime import datetime, timezone

from app.dtos.dashboard import (
    ChallengeStats,
    DashboardSummaryResponse,
    EgfrDataPoint,
    EgfrTrendResponse,
    LatestHealthMetrics,
    LatestLifestyleSummary,
)
from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:
    def __init__(self) -> None:
        self._repo = DashboardRepository()

    async def get_summary(self, user_id: int) -> DashboardSummaryResponse:
        health, challenge_stats, lifestyle = await _gather(
            self._repo.get_latest_health_check(user_id),
            self._repo.get_challenge_stats(user_id),
            self._repo.get_latest_lifestyle_survey(user_id),
        )

        latest_health = None
        if health is not None:
            latest_health = LatestHealthMetrics(
                checked_date=health.checked_date,
                systolic_bp=health.systolic_bp,
                diastolic_bp=health.diastolic_bp,
                fasting_glucose=health.fasting_glucose,
                bmi=health.bmi,
                egfr_estimated=health.egfr_estimated,
                ckd_stage=health.ckd_stage,
                ckd_risk_score=health.ckd_risk_score,
            )

        latest_lifestyle = None
        if lifestyle is not None:
            latest_lifestyle = LatestLifestyleSummary(
                surveyed_date=lifestyle.surveyed_date,
                smoking_status=lifestyle.smoking_status,
                drinking_frequency=lifestyle.drinking_frequency,
                exercise_days_per_week=lifestyle.exercise_days_per_week,
                stress_level=lifestyle.stress_level,
            )

        return DashboardSummaryResponse(
            latest_health=latest_health,
            challenge_stats=ChallengeStats(**challenge_stats),
            latest_lifestyle=latest_lifestyle,
            generated_at=datetime.now(tz=timezone.utc),
        )

    async def get_egfr_trend(self, user_id: int, limit: int = 12) -> EgfrTrendResponse:
        records = await self._repo.get_egfr_trend(user_id, limit)
        data_points = [
            EgfrDataPoint(checked_date=r.checked_date, egfr_estimated=r.egfr_estimated)
            for r in reversed(records)  # 오래된 순으로 정렬
        ]
        return EgfrTrendResponse(data_points=data_points)


async def _gather(*coros):
    import asyncio

    return await asyncio.gather(*coros)
