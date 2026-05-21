from tortoise import fields, models


class NotificationSetting(models.Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.OneToOneField("models.User", related_name="notification_setting", on_delete=fields.CASCADE)
    challenge_joined_enabled = fields.BooleanField(default=True)
    checkin_done_enabled = fields.BooleanField(default=True)
    challenge_completed_enabled = fields.BooleanField(default=True)
    challenge_reminder_enabled = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "notification_settings"
