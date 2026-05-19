from enum import StrEnum

from tortoise import fields, models


class ChallengeCategory(StrEnum):
    HYDRATION = "HYDRATION"
    EXERCISE = "EXERCISE"
    DIET = "DIET"
    SLEEP = "SLEEP"
    SMOKING = "SMOKING"


class ChallengeTrack(StrEnum):
    A = "A"  # G1~G2 대상
    B = "B"  # G3A~G3B 대상


class UserChallengeStatus(StrEnum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class Challenge(models.Model):
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=100)
    category = fields.CharEnumField(enum_type=ChallengeCategory)
    description = fields.TextField()
    duration_days = fields.IntField(description="챌린지 총 기간 (일)")
    track = fields.CharEnumField(enum_type=ChallengeTrack)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "challenges"
        ordering = ["track", "category"]


class UserChallenge(models.Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="user_challenges")
    challenge = fields.ForeignKeyField("models.Challenge", related_name="participants")
    started_at = fields.DateField(description="챌린지 시작일")
    status = fields.CharEnumField(enum_type=UserChallengeStatus, default=UserChallengeStatus.ACTIVE)
    streak_count = fields.IntField(default=0, description="연속 체크인 일수")
    total_checkins = fields.IntField(default=0, description="누적 체크인 횟수")
    last_checkin_date = fields.DateField(null=True, description="마지막 체크인 날짜")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_challenges"
        unique_together = [("user", "challenge")]
