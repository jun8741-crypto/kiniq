from enum import StrEnum

from tortoise import fields, models


class PointReason(StrEnum):
    LOGIN = "LOGIN"
    CHECKIN = "CHECKIN"
    LUCKY = "LUCKY"
    STREAK_BONUS = "STREAK_BONUS"
    STAGE_BONUS = "STAGE_BONUS"
    FULL_PARTICIPATION = "FULL_PARTICIPATION"
    PURCHASE = "PURCHASE"
    PROTECT_CONSUME = "PROTECT_CONSUME"
    REFUND = "REFUND"


class ItemCode(StrEnum):
    PROTECT = "PROTECT"
    MINI_BOOSTER = "MINI_BOOSTER"
    SKIN_S_BLUE = "SKIN_S_BLUE"
    SKIN_S_GREEN = "SKIN_S_GREEN"
    SKIN_M_RED = "SKIN_M_RED"
    SKIN_M_PURPLE = "SKIN_M_PURPLE"
    SKIN_L_GOLD = "SKIN_L_GOLD"


class PointTransaction(models.Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="point_transactions")
    amount = fields.IntField(description="+적립 / -소비")
    reason = fields.CharEnumField(enum_type=PointReason)
    extra = fields.JSONField(default=dict, description="컨텍스트: challenge_id, stage_no, streak_day, item_code 등")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "point_transactions"
        ordering = ["-created_at"]


class UserEgg(models.Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="eggs")
    egg_no = fields.IntField(description="사용자 기준 몇 번째 알 (1부터 시작)")
    progress_checkins = fields.IntField(default=0, description="누적 체크인 수 (0~100)")
    current_stage = fields.IntField(default=1, description="1=0~25%, 2=25~50%, 3=50~75%, 4=75~100%, 5=부화")
    is_legendary = fields.BooleanField(null=True, description="부화 시 5% 추첨 결과. 진행 중엔 NULL")
    goal_70_alerted = fields.BooleanField(default=False)
    goal_90_alerted = fields.BooleanField(default=False)
    stage_25_bonus_paid = fields.BooleanField(default=False)
    stage_50_bonus_paid = fields.BooleanField(default=False)
    stage_75_bonus_paid = fields.BooleanField(default=False)
    stage_100_bonus_paid = fields.BooleanField(default=False)
    started_at = fields.DatetimeField(auto_now_add=True)
    hatched_at = fields.DatetimeField(null=True, description="부화 시각. NULL이면 진행 중")

    class Meta:
        table = "user_eggs"
        unique_together = [("user", "egg_no")]
        ordering = ["user_id", "-egg_no"]


class UserInventory(models.Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="inventory")
    item_code = fields.CharEnumField(enum_type=ItemCode)
    quantity = fields.IntField(default=0, description="보호권은 0~2, 부스터/스킨은 0~∞")
    acquired_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_inventory"
        unique_together = [("user", "item_code")]


class UserChargeMode(models.Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="charge_mode", unique=True)
    is_active = fields.BooleanField(default=False)
    entered_at = fields.DatetimeField(null=True)
    exited_at = fields.DatetimeField(null=True)
    warning_4d_alerted = fields.BooleanField(default=False)
    warning_5d_alerted = fields.BooleanField(default=False)
    warning_6d_alerted = fields.BooleanField(default=False)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_charge_mode"


class UserDailyLogin(models.Model):
    """일일 로그인 보상 중복 지급 방지용 — 사용자 × 날짜 1개 row.

    당일 첫 인증된 요청 시점에 row 생성 + 포인트 적립. 같은 날 두 번째 요청부터는 row가 이미 있어 적립 안 함.
    """

    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="daily_logins")
    login_date = fields.DateField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_daily_logins"
        unique_together = [("user", "login_date")]
