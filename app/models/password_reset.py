from tortoise import fields, models


class PasswordResetCode(models.Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="password_reset_codes", on_delete=fields.CASCADE)
    code_hash = fields.CharField(max_length=64, description="SHA256 해시 (코드 평문 저장 금지)")
    expires_at = fields.DatetimeField(description="만료 시각 (UTC)")
    attempts = fields.IntField(default=0, description="검증 시도 횟수 (5회 초과 시 무효)")
    used_at = fields.DatetimeField(null=True, description="성공 사용 시각 (이후 재사용 불가)")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "password_reset_codes"
        indexes = [("user_id", "expires_at")]
