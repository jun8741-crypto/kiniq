"""충전 모드 (쉬어가기 모드) 서비스.

명세: docs/gamification-spec-v1.md §1-5
- 진입 조건: 7일 연속 체크인 0회 (부스터 보유 시 9일로 연장)
- 경고 버퍼: 진입 4·5·6일째 알림 1회씩
- 진입 효과: 스트릭 동결, entered_at 저장, 부스터 보유 시 1개 자동 소모
- 탈출 조건: 체크인 1회로 즉시 정상화

언어 대체표 (절대 준수):
- "강등" → "쉬어가기 모드"
- "레벨 다운" → "충전 모드"
- "실패" → "잠시 멈춤"
- "벌점" 단어 금지

평가 시점: 일일 로그인 + 체크인 hook 시점에 lazy 평가.
"""

from dataclasses import dataclass
from datetime import UTC, date, datetime

from app.models.challenge import UserChallenge
from app.models.gamification import ItemCode
from app.models.notification import NotificationType
from app.repositories.gamification_repository import ChargeModeRepository, InventoryRepository
from app.repositories.notification_repository import NotificationRepository

THRESHOLD_DAYS_DEFAULT = 7
THRESHOLD_DAYS_WITH_BOOSTER = 9
WARNING_DAYS = [4, 5, 6]


@dataclass
class ChargeModeEvent:
    entered: bool = False
    exited: bool = False
    booster_consumed: bool = False
    warning_days: list[int] | None = None

    def __post_init__(self) -> None:
        if self.warning_days is None:
            self.warning_days = []


class ChargeModeService:
    def __init__(self) -> None:
        self._charge = ChargeModeRepository()
        self._inv = InventoryRepository()
        self._notif = NotificationRepository()

    async def evaluate(self, user_id: int, today: date) -> ChargeModeEvent:
        """충전 모드 진입/탈출/경고 평가. 이벤트 dataclass 반환."""
        event = ChargeModeEvent()
        cm = await self._charge.get_or_create(user_id)

        # 사용자의 가장 최근 체크인 날짜 (모든 챌린지 통합)
        latest = (
            await UserChallenge.filter(user_id=user_id, last_checkin_date__not_isnull=True)
            .order_by("-last_checkin_date")
            .first()
        )
        last_date: date | None = latest.last_checkin_date if latest else None

        if last_date is None:
            # 챌린지 시작 전이거나 한 번도 체크인 안 함 → 평가 안 함
            return event

        days_since = (today - last_date).days

        # 이미 충전 모드이고 오늘 체크인했다면 (days_since == 0) → 탈출
        if cm.is_active and days_since == 0:
            cm.is_active = False
            cm.exited_at = datetime.now(UTC)
            cm.warning_4d_alerted = False
            cm.warning_5d_alerted = False
            cm.warning_6d_alerted = False
            await cm.save()
            await self._notif.create(
                user_id=user_id,
                type=NotificationType.CHARGE_MODE_OUT,
                title="다시 시작!",
                message="잠시 쉬어가기 모드에서 돌아왔어요. 오늘 체크인 환영합니다.",
            )
            event.exited = True
            return event

        # 부스터 보유 여부에 따라 임계 결정
        booster_qty = await self._inv.get_quantity(user_id, ItemCode.MINI_BOOSTER)
        threshold = THRESHOLD_DAYS_WITH_BOOSTER if booster_qty > 0 else THRESHOLD_DAYS_DEFAULT

        if not cm.is_active:
            # 4·5·6일 경고
            for d in WARNING_DAYS:
                flag = f"warning_{d}d_alerted"
                if days_since == d and not getattr(cm, flag):
                    await self._notif.create(
                        user_id=user_id,
                        type=NotificationType.CHALLENGE_REMINDER,
                        title=f"{d}일째 쉬는 중이에요",
                        message="지금 1번만 체크인하면 정상으로 돌아갑니다.",
                    )
                    setattr(cm, flag, True)
                    event.warning_days.append(d)

            # 진입 평가
            if days_since >= threshold:
                cm.is_active = True
                cm.entered_at = datetime.now(UTC)
                if booster_qty > 0:
                    await self._inv.add_quantity(user_id, ItemCode.MINI_BOOSTER, -1)
                    event.booster_consumed = True
                await cm.save()
                await self._notif.create(
                    user_id=user_id,
                    type=NotificationType.CHARGE_MODE_IN,
                    title="쉬어가기 모드 시작",
                    message=(
                        "부스터 효과로 진입이 늦춰졌어요."
                        if event.booster_consumed
                        else "잠시 쉬는 동안 스트릭은 보존됩니다."
                    ),
                )
                event.entered = True
                return event

            await cm.save()
        return event
