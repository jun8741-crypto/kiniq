from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import ORJSONResponse as Response

from app.dependencies.security import get_request_user
from app.dtos.gamification import (
    ChargeModeResponse,
    EggHistoryResponse,
    EggResponse,
    InventoryResponse,
    MascotResponse,
)
from app.models.users import User
from app.services.gamification import GamificationService

gamification_router = APIRouter(prefix="/gamification", tags=["gamification"])
inventory_router = APIRouter(prefix="/inventory", tags=["gamification"])


@gamification_router.get(
    "/eggs",
    response_model=EggResponse,
    status_code=status.HTTP_200_OK,
    summary="현재 알 상태",
)
async def get_current_egg(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[GamificationService, Depends(GamificationService)],
) -> Response:
    result = await service.get_current_egg(user.id)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@gamification_router.get(
    "/eggs/history",
    response_model=EggHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="부화 이력 (전설 5% 포함)",
)
async def get_egg_history(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[GamificationService, Depends(GamificationService)],
) -> Response:
    result = await service.get_egg_history(user.id)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@gamification_router.get(
    "/mascot",
    response_model=MascotResponse,
    status_code=status.HTTP_200_OK,
    summary="캐릭터 + 충전 모드 통합",
)
async def get_mascot(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[GamificationService, Depends(GamificationService)],
) -> Response:
    result = await service.get_mascot(user.id, date.today())
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@gamification_router.get(
    "/charge-mode",
    response_model=ChargeModeResponse,
    status_code=status.HTTP_200_OK,
    summary="충전 모드 (쉬어가기 모드) 상태",
)
async def get_charge_mode(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[GamificationService, Depends(GamificationService)],
) -> Response:
    result = await service.get_charge_mode(user.id, date.today())
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@gamification_router.post(
    "/charge-mode/exit",
    response_model=ChargeModeResponse,
    status_code=status.HTTP_200_OK,
    summary="충전 모드 명시적 탈출",
)
async def exit_charge_mode(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[GamificationService, Depends(GamificationService)],
) -> Response:
    result = await service.exit_charge_mode(user.id)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@inventory_router.get(
    "",
    response_model=InventoryResponse,
    status_code=status.HTTP_200_OK,
    summary="보유 아이템 목록",
)
async def list_inventory(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[GamificationService, Depends(GamificationService)],
) -> Response:
    result = await service.get_inventory(user.id)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)
