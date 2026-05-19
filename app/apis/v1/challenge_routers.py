from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import ORJSONResponse as Response

from app.dependencies.security import get_request_user
from app.dtos.challenge import (
    ChallengeListResponse,
    CheckInResponse,
    JoinChallengeRequest,
    UserChallengeListResponse,
    UserChallengeResponse,
)
from app.models.health_check import CkdStage
from app.models.users import User
from app.services.challenge import ChallengeService

challenge_router = APIRouter(prefix="/challenges", tags=["challenges"])
user_challenge_router = APIRouter(prefix="/user-challenges", tags=["user-challenges"])


def _latest_ckd_stage(user: User) -> CkdStage | None:
    """가장 최근 health_check에서 CKD 단계를 가져오는 헬퍼 — 비동기 처리 필요 시 서비스로 이동."""
    return None


@challenge_router.get(
    "",
    response_model=ChallengeListResponse,
    status_code=status.HTTP_200_OK,
    summary="챌린지 카탈로그 조회",
    description=(
        "사용자의 CKD 단계(ckd_stage)에 맞는 챌린지 목록을 반환합니다. "
        "G4/G5 또는 미입력 시 빈 목록을 반환합니다(안전 분기)."
    ),
)
async def list_challenges(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[ChallengeService, Depends(ChallengeService)],
    ckd_stage: Annotated[CkdStage | None, Query(description="사용자 CKD 단계 (예: G1, G2, G3A)")] = None,
) -> Response:
    result = await service.list_challenges(ckd_stage)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@user_challenge_router.post(
    "",
    response_model=UserChallengeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="챌린지 참여",
)
async def join_challenge(
    request: JoinChallengeRequest,
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[ChallengeService, Depends(ChallengeService)],
) -> Response:
    result = await service.join_challenge(user_id=user.id, dto=request)
    return Response(result.model_dump(), status_code=status.HTTP_201_CREATED)


@user_challenge_router.get(
    "",
    response_model=UserChallengeListResponse,
    status_code=status.HTTP_200_OK,
    summary="내 챌린지 목록",
)
async def list_my_challenges(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[ChallengeService, Depends(ChallengeService)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Response:
    result = await service.list_my_challenges(user_id=user.id, limit=limit, offset=offset)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@user_challenge_router.post(
    "/{user_challenge_id}/checkin",
    response_model=CheckInResponse,
    status_code=status.HTTP_200_OK,
    summary="챌린지 체크인",
    description="오늘 하루 챌린지를 완료했음을 기록합니다. 하루 1회만 가능합니다.",
)
async def checkin(
    user_challenge_id: int,
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[ChallengeService, Depends(ChallengeService)],
) -> Response:
    result = await service.checkin(
        user_challenge_id=user_challenge_id,
        user_id=user.id,
        today=date.today(),
    )
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)
