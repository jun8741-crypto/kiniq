from datetime import datetime

from app.dtos.base import BaseSerializerModel
from app.models.notification import NotificationType


class NotificationResponse(BaseSerializerModel):
    id: int
    user_id: int
    type: NotificationType
    title: str
    message: str
    is_read: bool
    related_id: int | None
    created_at: datetime


class NotificationListResponse(BaseSerializerModel):
    total: int
    unread_count: int
    items: list[NotificationResponse]
