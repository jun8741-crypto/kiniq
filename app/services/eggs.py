"""알 부화 시스템 서비스.

명세: docs/gamification-spec-v1.md §1-3
- 부화 목표: 누적 체크인 100회 (= 100% 진행률)
- 5단계 임계값: 25 / 50 / 75 / 100 체크인
- 부화 시 95%/5% 전설 추첨 (random.random() < 0.05)
- Goal Gradient 알림: 70%·90% 첫 도달 시 1회씩
- 스테이지 보너스: 25% +100 / 50% +200 / 75% +350 / 100% +600
- 부화 후 새 알 자동 생성 (egg_no+1, progress=0)
"""

import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.models.gamification import PointReason
from app.models.notification import NotificationType
from app.repositories.gamification_repository import EggRepository, PointRepository
from app.repositories.notification_repository import NotificationRepository

GOAL_CHECKINS = 100
STAGE_THRESHOLDS: dict[int, int] = {25: 100, 50: 200, 75: 350, 100: 600}
GOAL_GRADIENT_ALERTS = [70, 90]
LEGENDARY_PROBABILITY = 0.05


@dataclass
class EggUpdate:
    progress_checkins: int = 0
    current_stage: int = 1
    goal_70_just_alerted: bool = False
    goal_90_just_alerted: bool = False
    stage_bonus: int = 0
    stage_milestone: int = 0
    hatched: bool = False
    is_legendary: bool | None = None
    new_egg_no: int | None = None
    extras: dict = field(default_factory=dict)


class EggService:
    def __init__(self) -> None:
        self._eggs = EggRepository()
        self._points = PointRepository()
        self._notif = NotificationRepository()

    async def progress_and_check(self, user_id: int, challenge_id: int | None = None) -> EggUpdate:
        """체크인 1회마다 호출. 진행률 +1 + 단계 보너스 + 알림 + 부화 처리."""
        egg = await self._eggs.get_or_create_current(user_id)

        # 진행률 +1
        egg.progress_checkins = min(GOAL_CHECKINS, egg.progress_checkins + 1)
        update = EggUpdate(progress_checkins=egg.progress_checkins)

        # 단계 전환 (1: 0~25, 2: 25~50, 3: 50~75, 4: 75~100, 5: 부화)
        new_stage = self._calc_stage(egg.progress_checkins)
        egg.current_stage = new_stage
        update.current_stage = new_stage

        # 스테이지 보너스 (각 임계를 처음 넘은 시점에 1회)
        for threshold, bonus in STAGE_THRESHOLDS.items():
            if egg.progress_checkins >= threshold and not self._is_stage_paid(egg, threshold):
                await self._points.create_transaction(
                    user_id=user_id,
                    amount=bonus,
                    reason=PointReason.STAGE_BONUS,
                    extra={"egg_no": egg.egg_no, "stage_percent": threshold, "challenge_id": challenge_id},
                )
                await self._notif.create(
                    user_id=user_id,
                    type=NotificationType.STAGE_BONUS,
                    title=f"알 {threshold}% 달성!",
                    message=f"{threshold}% 도달 보너스 +{bonus}pt를 받았어요.",
                    related_id=egg.id,
                )
                self._mark_stage_paid(egg, threshold)
                update.stage_bonus = bonus
                update.stage_milestone = threshold

        # Goal Gradient 알림 (70%, 90% 첫 도달 시)
        if egg.progress_checkins >= 70 and not egg.goal_70_alerted:
            await self._notif.create(
                user_id=user_id,
                type=NotificationType.EGG_GOAL_70,
                title="알이 거의 자랐어요",
                message="진행률 70% 도달! 부화까지 30번만 남았어요.",
                related_id=egg.id,
            )
            egg.goal_70_alerted = True
            update.goal_70_just_alerted = True

        if egg.progress_checkins >= 90 and not egg.goal_90_alerted:
            await self._notif.create(
                user_id=user_id,
                type=NotificationType.EGG_GOAL_90,
                title="부화 임박!",
                message="진행률 90% 도달! 10번만 더 체크인하면 부화해요.",
                related_id=egg.id,
            )
            egg.goal_90_alerted = True
            update.goal_90_just_alerted = True

        # 100% 도달 → 부화 처리
        if egg.progress_checkins >= GOAL_CHECKINS and egg.hatched_at is None:
            is_legendary = secrets.SystemRandom().random() < LEGENDARY_PROBABILITY
            now = datetime.now(UTC)
            egg.is_legendary = is_legendary
            egg.hatched_at = now
            egg.current_stage = 5
            await egg.save()

            title = "전설의 알이 부화했어요!" if is_legendary else "알이 부화했어요!"
            message = (
                "5% 확률의 전설 알입니다! 특별한 캐릭터가 함께해요."
                if is_legendary
                else "축하합니다! 새 알이 자동으로 시작됩니다."
            )
            await self._notif.create(
                user_id=user_id,
                type=NotificationType.EGG_HATCHED,
                title=title,
                message=message,
                related_id=egg.id,
            )

            # 새 알 자동 시작
            new_egg = await self._eggs.get_or_create_current(user_id)
            update.hatched = True
            update.is_legendary = is_legendary
            update.new_egg_no = new_egg.egg_no
        else:
            await egg.save()

        return update

    @staticmethod
    def _calc_stage(progress: int) -> int:
        if progress >= 100:
            return 5
        if progress >= 75:
            return 4
        if progress >= 50:
            return 3
        if progress >= 25:
            return 2
        return 1

    @staticmethod
    def _is_stage_paid(egg, threshold: int) -> bool:
        flag_name = f"stage_{threshold}_bonus_paid"
        return getattr(egg, flag_name, False)

    @staticmethod
    def _mark_stage_paid(egg, threshold: int) -> None:
        flag_name = f"stage_{threshold}_bonus_paid"
        setattr(egg, flag_name, True)
