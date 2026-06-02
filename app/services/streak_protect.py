"""스트릭 보호권 자동 소모 서비스.

명세 docs/gamification-spec-v1.md §1-4:
- 보호권 자동 소모 조건: 어제 active 챌린지 체크인 0개 + 보유 1개 이상
- 효과: 보호권 1개 차감 + 각 active 챌린지의 last_checkin_date를 어제로 가상 설정
  → 오늘 체크인 시 streak 자연스럽게 +1 됨 (끊김 없이)
- 멱등: 같은 보호일자(yesterday)에 대한 PROTECT_CONSUME 트랜잭션이 있으면 skip

평가 시점: 로그인 + 체크인 hook 시작 시점에 lazy 평가.
"""

from datetime import date, timedelta

from app.models.challenge import UserChallenge, UserChallengeStatus
from app.models.gamification import ItemCode, PointReason, PointTransaction
from app.models.notification import NotificationType
from app.repositories.gamification_repository import InventoryRepository, PointRepository
from app.repositories.notification_repository import NotificationRepository


class StreakProtectService:
    def __init__(self) -> None:
        self._inv = InventoryRepository()
        self._point_repo = PointRepository()
        self._notif = NotificationRepository()

    async def evaluate(self, user_id: int, today: date) -> bool:
        """어제 체크인 0회 + 보호권 보유 시 자동 소모.

        True 반환 = 보호권 소모됨. False = 조건 미충족.
        """
        yesterday = today - timedelta(days=1)

        # 1. 같은 보호일자에 대한 소모 트랜잭션이 이미 있는지 (멱등)
        already = await PointTransaction.filter(
            user_id=user_id,
            reason=PointReason.PROTECT_CONSUME,
            extra__contains={"protected_date": yesterday.isoformat()},
        ).exists()
        if already:
            return False

        # 2. 어제 체크인 1회라도 있었으면 보호 불필요
        had_checkin = await UserChallenge.filter(user_id=user_id, last_checkin_date=yesterday).exists()
        if had_checkin:
            return False

        # 3. 어제 기준 active 챌린지가 있어야 보호 의미 있음
        active = await UserChallenge.filter(user_id=user_id, status=UserChallengeStatus.ACTIVE)
        protectable = [uc for uc in active if uc.started_at <= yesterday]
        if not protectable:
            return False

        # 4. 보호권 보유?
        qty = await self._inv.get_quantity(user_id, ItemCode.PROTECT)
        if qty == 0:
            return False

        # 5. 소비 처리
        await self._inv.add_quantity(user_id, ItemCode.PROTECT, -1)
        await self._point_repo.create_transaction(
            user_id=user_id,
            amount=0,  # 자체 소비는 0pt (구매 시 -500 이미 차감됨)
            reason=PointReason.PROTECT_CONSUME,
            extra={"protected_date": yesterday.isoformat(), "protected_count": len(protectable)},
        )

        # 6. 가상 체크인: 각 active 챌린지에 last_checkin_date = yesterday 설정
        #    오늘 체크인 시 last == today-1 이므로 streak +1
        #    (기존 last_checkin_date가 yesterday보다 미래면 덮어쓰지 않음)
        for uc in protectable:
            if uc.last_checkin_date is None or uc.last_checkin_date < yesterday:
                uc.last_checkin_date = yesterday
                await uc.save()

        # 7. 알림
        await self._notif.create(
            user_id=user_id,
            type=NotificationType.CHALLENGE_REMINDER,
            title="스트릭 보호권이 사용됐어요",
            message=f"어제({yesterday.isoformat()}) 보호권 1개가 자동 사용되어 연속 일수가 유지됐어요.",
        )
        return True
