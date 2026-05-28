from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import ORJSONResponse as Response

from app.dependencies.security import get_request_user
from app.dtos.dashboard import DashboardSummaryResponse, EgfrSimulationResponse, EgfrTrendResponse
from app.models.users import User
from app.services.dashboard import DashboardService

dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@dashboard_router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="대시보드 요약",
    description="최신 건강지표, 챌린지 현황, 생활습관 요약을 한 번에 반환합니다.",
)
async def get_summary(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[DashboardService, Depends(DashboardService)],
) -> Response:
    result = await service.get_summary(user_id=user.id)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@dashboard_router.get(
    "/egfr-trend",
    response_model=EgfrTrendResponse,
    status_code=status.HTTP_200_OK,
    summary="eGFR 추이",
    description="최근 N회 검진의 eGFR 시계열 데이터를 오래된 순으로 반환합니다.",
)
async def get_egfr_trend(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[DashboardService, Depends(DashboardService)],
    limit: Annotated[int, Query(ge=1, le=24, description="최대 반환 개수 (기본 12)")] = 12,
) -> Response:
    result = await service.get_egfr_trend(user_id=user.id, limit=limit)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@dashboard_router.get(
    "/egfr-simulation",
    response_model=EgfrSimulationResponse,
    status_code=status.HTTP_200_OK,
    summary="챌린지 반영 예상 eGFR (REQ-DASH-003)",
    description=("실측 eGFR + Σ(카테고리 진행률 × 가중치 × MAX_BOOST). G4~G5(eGFR<30) 사용자에게는 시뮬레이션 미적용."),
)
async def get_egfr_simulation(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[DashboardService, Depends(DashboardService)],
) -> Response:
    result = await service.get_egfr_simulation(user_id=user.id)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)
