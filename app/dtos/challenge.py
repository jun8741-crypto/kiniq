from datetime import date, datetime

from pydantic import BaseModel

from app.dtos.base import BaseSerializerModel
from app.models.challenge import ChallengeCategory, ChallengeTrack, UserChallengeStatus


class ChallengeResponse(BaseSerializerModel):
    id: int
    name: str
    category: ChallengeCategory
    description: str
    duration_days: int
    track: ChallengeTrack


class ChallengeListResponse(BaseSerializerModel):
    total: int
    items: list[ChallengeResponse]


class JoinChallengeRequest(BaseModel):
    challenge_id: int
    started_at: date


class UserChallengeResponse(BaseSerializerModel):
    id: int
    challenge_id: int
    started_at: date
    status: UserChallengeStatus
    streak_count: int
    total_checkins: int
    last_checkin_date: date | None
    created_at: datetime


class UserChallengeListResponse(BaseSerializerModel):
    total: int
    items: list[UserChallengeResponse]


class CheckInResponse(BaseSerializerModel):
    id: int
    streak_count: int
    total_checkins: int
    last_checkin_date: date
    status: UserChallengeStatus
    message: str
