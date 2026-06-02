from app.models.notification_setting import NotificationSetting


class NotificationSettingRepository:
    async def get_or_create(self, user_id: int) -> NotificationSetting:
        setting, _ = await NotificationSetting.get_or_create(user_id=user_id)
        return setting

    async def update(self, user_id: int, data: dict) -> NotificationSetting:
        setting = await self.get_or_create(user_id)
        for key, value in data.items():
            setattr(setting, key, value)
        await setting.save(update_fields=list(data.keys()) + ["updated_at"])
        return setting
