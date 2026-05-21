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
from app.models.health_check import AppGroup
from app.models.users import User
from app.services.challenge import ChallengeService

challenge_router = APIRouter(prefix="/challenges", tags=["challenges"])
user_challenge_router = APIRouter(prefix="/user-challenges", tags=["user-challenges"])


@challenge_router.get(
    "",
    response_model=ChallengeListResponse,
    status_code=status.HTTP_200_OK,
    summary="챌린지 목록 조회",
    description=(
        "사용자의 App 그룹(app_group)에 맞는 챌린지 목록을 반환합니다. "
        "G1·G2는 Track A(케어), G3·G4는 Track B(일반). "
        "미입력 시 최신 검진의 CKD 단계로 자동 배정 (ML 모델 미실행 fallback)."
    ),
)
async def list_challenges(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[ChallengeService, Depends(ChallengeService)],
    app_group: Annotated[AppGroup | None, Query(description="ML 모델 배정 그룹 (G1~G4)")] = None,
) -> Response:
    # ML 모델 미실행 시: 최신 검진 CKD 단계로 fallback
    if app_group is None:
        from app.models.health_check import CkdStage, HealthCheck
        latest = await HealthCheck.filter(user_id=user.id).order_by("-checked_date").first()
        if latest is None:
            from app.dtos.challenge import ChallengeListResponse
            return Response(ChallengeListResponse(total=0, items=[]).model_dump(), status_code=status.HTTP_200_OK)
        if latest.ckd_stage in (CkdStage.G3A, CkdStage.G3B, CkdStage.G4, CkdStage.G5):
            app_group = AppGroup.G3
        else:
            app_group = AppGroup.G2
    result = await service.list_challenges(app_group)
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
