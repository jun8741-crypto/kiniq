from datetime import date

from fastapi import HTTPException
from starlette import status

from app.dtos.challenge import (
    ChallengeListResponse,
    ChallengeResponse,
    CheckInResponse,
    JoinChallengeRequest,
    UserChallengeListResponse,
    UserChallengeResponse,
)
from app.models.challenge import ChallengeTrack, UserChallengeStatus
from app.models.health_check import AppGroup
from app.repositories.challenge_repository import ChallengeRepository, UserChallengeRepository
from app.services.notification import NotificationService

_GROUP_TO_TRACK: dict[AppGroup, ChallengeTrack] = {
    AppGroup.G1: ChallengeTrack.A,
    AppGroup.G2: ChallengeTrack.A,
    AppGroup.G3: ChallengeTrack.B,
    AppGroup.G4: ChallengeTrack.B,
}


class ChallengeService:
    def __init__(self) -> None:
        self._repo = ChallengeRepository()
        self._user_repo = UserChallengeRepository()
        self._notif = NotificationService()

    async def list_challenges(self, app_group: AppGroup | None) -> ChallengeListResponse:
        """사용자 App 그룹에 맞는 챌린지 목록 반환. 그룹 미입력 시 빈 목록."""
        if app_group is None:
            return ChallengeListResponse(total=0, items=[])

        track = _GROUP_TO_TRACK[app_group]
        items = await self._repo.list_by_track(track)
        return ChallengeListResponse(
            total=len(items),
            items=[ChallengeResponse.model_validate(c) for c in items],
        )

    async def join_challenge(self, user_id: int, dto: JoinChallengeRequest) -> UserChallengeResponse:
        challenge = await self._repo.get_by_id(dto.challenge_id)
        if challenge is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="챌린지를 찾을 수 없습니다.")

        existing = await self._user_repo.get_active(user_id, dto.challenge_id)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 참여 중인 챌린지입니다.")

        uc = await self._user_repo.create(
            user_id=user_id,
            challenge_id=dto.challenge_id,
            started_at=dto.started_at,
        )
        await self._notif.notify_challenge_joined(user_id, challenge.name, uc.id)
        return UserChallengeResponse.model_validate(uc)

    async def list_my_challenges(
        self,
        user_id: int,
        status_filter: UserChallengeStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> UserChallengeListResponse:
        total, items = await self._user_repo.list_by_user(user_id, status_filter, limit, offset)
        return UserChallengeListResponse(
            total=total,
            items=[UserChallengeResponse.model_validate(uc) for uc in items],
        )

    async def checkin(self, user_challenge_id: int, user_id: int, today: date) -> CheckInResponse:
        uc = await self._user_repo.get_by_id(user_challenge_id, user_id)
        if uc is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="참여 중인 챌린지를 찾을 수 없습니다.")

        if uc.status != UserChallengeStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="완료되거나 포기한 챌린지에는 체크인할 수 없습니다.",
            )

        if uc.last_checkin_date == today:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="오늘은 이미 체크인했습니다.")

        # 스트릭 계산: 어제 체크인 → 연속, 아니면 1로 리셋
        from datetime import timedelta

        if uc.last_checkin_date == today - timedelta(days=1):
            uc.streak_count += 1
        else:
            uc.streak_count = 1

        uc.total_checkins += 1
        uc.last_checkin_date = today

        # 챌린지 완료 체크 (fetch challenge duration_days)
        challenge = await uc.challenge
        if uc.total_checkins >= challenge.duration_days:
            uc.status = UserChallengeStatus.COMPLETED
            message = f"챌린지를 완료했습니다! 총 {uc.total_checkins}일 달성."
        else:
            remaining = challenge.duration_days - uc.total_checkins
            message = f"체크인 완료! 연속 {uc.streak_count}일째입니다. 목표까지 {remaining}일 남았습니다."

        await self._user_repo.save(uc)

        if uc.status == UserChallengeStatus.COMPLETED:
            await self._notif.notify_challenge_completed(user_id, challenge.name, uc.total_checkins, uc.id)
        else:
            await self._notif.notify_checkin_done(user_id, challenge.name, uc.streak_count, uc.id)

        return CheckInResponse(
            id=uc.id,
            streak_count=uc.streak_count,
            total_checkins=uc.total_checkins,
            last_checkin_date=uc.last_checkin_date,
            status=uc.status,
            message=message,
        )
