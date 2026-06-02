from app.models.notification import Notification, NotificationType


class NotificationRepository:
    async def create(
        self,
        user_id: int,
        type: NotificationType,
        title: str,
        message: str,
        related_id: int | None = None,
    ) -> Notification:
        return await Notification.create(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            related_id=related_id,
        )

    async def get_by_user(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[int, int, list[Notification]]:
        qs = Notification.filter(user_id=user_id)
        if unread_only:
            qs = qs.filter(is_read=False)
        total = await qs.count()
        unread_count = await Notification.filter(user_id=user_id, is_read=False).count()
        items = await qs.order_by("-created_at").offset(offset).limit(limit)
        return total, unread_count, items

    async def get_by_id(self, notification_id: int, user_id: int) -> Notification | None:
        return await Notification.get_or_none(id=notification_id, user_id=user_id)

    async def mark_read(self, notification_id: int, user_id: int) -> Notification | None:
        n = await self.get_by_id(notification_id, user_id)
        if n is None:
            return None
        n.is_read = True
        await n.save()
        return n

    async def mark_all_read(self, user_id: int) -> int:
        return await Notification.filter(user_id=user_id, is_read=False).update(is_read=True)
