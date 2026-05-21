from datetime import datetime

from pydantic import BaseModel

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


class NotificationSettingResponse(BaseSerializerModel):
    challenge_joined_enabled: bool
    checkin_done_enabled: bool
    challenge_completed_enabled: bool
    challenge_reminder_enabled: bool


class NotificationSettingUpdateRequest(BaseModel):
    challenge_joined_enabled: bool | None = None
    checkin_done_enabled: bool | None = None
    challenge_completed_enabled: bool | None = None
    challenge_reminder_enabled: bool | None = None
