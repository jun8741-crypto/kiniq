from enum import StrEnum

from tortoise import fields, models


class Gender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class User(models.Model):
    id = fields.BigIntField(primary_key=True)
    email = fields.CharField(max_length=40)
    hashed_password = fields.CharField(max_length=128)
    name = fields.CharField(max_length=20)
    gender = fields.CharEnumField(enum_type=Gender)
    birthday = fields.DateField()
    phone_number = fields.CharField(max_length=11)
    is_active = fields.BooleanField(default=True)
    is_admin = fields.BooleanField(default=False)
    last_login = fields.DatetimeField(null=True)
    active_skin_code = fields.CharField(max_length=20, null=True, description="현재 장착한 스킨 ItemCode (null=기본)")
    # REQ-AUTH-007 비밀번호 오류 잠금
    failed_login_count = fields.IntField(default=0, description="연속 비밀번호 실패 횟수")
    locked_until = fields.DatetimeField(null=True, description="계정 잠금 해제 시각 (null=미잠금)")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"
