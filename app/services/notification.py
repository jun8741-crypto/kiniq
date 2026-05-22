from fastapi import HTTPException
from starlette import status

from app.dtos.notification import (
    NotificationListResponse,
    NotificationResponse,
    NotificationSettingResponse,
    NotificationSettingUpdateRequest,
)
from app.models.notification import NotificationType
from app.repositories.notification_repository import NotificationRepository
from app.repositories.notification_setting_repository import NotificationSettingRepository


class NotificationService:
    def __init__(self) -> None:
        self._repo = NotificationRepository()
        self._setting_repo = NotificationSettingRepository()

    async def get_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> NotificationListResponse:
        total, unread_count, items = await self._repo.get_by_user(user_id, unread_only, limit, offset)
        return NotificationListResponse(
            total=total,
            unread_count=unread_count,
            items=[NotificationResponse.model_validate(n) for n in items],
        )

    async def mark_read(self, notification_id: int, user_id: int) -> NotificationResponse:
        n = await self._repo.mark_read(notification_id, user_id)
        if n is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="알림을 찾을 수 없습니다.")
        return NotificationResponse.model_validate(n)

    async def mark_all_read(self, user_id: int) -> dict:
        count = await self._repo.mark_all_read(user_id)
        return {"updated": count}

    # ── 내부 트리거 (다른 서비스에서 직접 호출) ────────────────────────────

    async def notify_challenge_joined(self, user_id: int, challenge_name: str, uc_id: int) -> None:
        await self._repo.create(
            user_id=user_id,
            type=NotificationType.CHALLENGE_JOINED,
            title="챌린지 시작!",
            message=f"'{challenge_name}' 챌린지를 시작했습니다. 오늘부터 함께 달려봐요!",
            related_id=uc_id,
        )

    async def notify_checkin_done(self, user_id: int, challenge_name: str, streak: int, uc_id: int) -> None:
        await self._repo.create(
            user_id=user_id,
            type=NotificationType.CHECKIN_DONE,
            title="체크인 완료",
            message=f"'{challenge_name}' 연속 {streak}일째 달성 중입니다. 잘 하고 있어요!",
            related_id=uc_id,
        )

    async def notify_challenge_completed(self, user_id: int, challenge_name: str, total_days: int, uc_id: int) -> None:
        await self._repo.create(
            user_id=user_id,
            type=NotificationType.CHALLENGE_COMPLETED,
            title="챌린지 완료!",
            message=f"'{challenge_name}' {total_days}일 챌린지를 완주했습니다. 축하합니다!",
            related_id=uc_id,
        )

    # ── 알림 설정 ────────────────────────────────────────────────────────────

    async def get_settings(self, user_id: int) -> NotificationSettingResponse:
        setting = await self._setting_repo.get_or_create(user_id)
        return NotificationSettingResponse.model_validate(setting)

    async def update_settings(
        self, user_id: int, data: NotificationSettingUpdateRequest
    ) -> NotificationSettingResponse:
        updates = data.model_dump(exclude_none=True)
        setting = await self._setting_repo.update(user_id, updates)
        return NotificationSettingResponse.model_validate(setting)
