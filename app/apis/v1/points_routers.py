from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import ORJSONResponse as Response

from app.dependencies.security import get_request_user
from app.dtos.points import (
    AttendanceResponse,
    PointBalanceResponse,
    PointTransactionItem,
    PointTransactionListResponse,
    PurchaseRequest,
    PurchaseResponse,
)
from app.models.users import User
from app.repositories.gamification_repository import PointRepository
from app.services.inventory import InventoryService
from app.services.points import LOGIN_BONUS, PointService

points_router = APIRouter(prefix="/points", tags=["points"])
attendance_router = APIRouter(prefix="/attendance", tags=["attendance"])


@points_router.get(
    "/balance",
    response_model=PointBalanceResponse,
    status_code=status.HTTP_200_OK,
    summary="포인트 잔액 + 평생 누적",
)
async def get_balance(
    user: Annotated[User, Depends(get_request_user)],
) -> Response:
    repo = PointRepository()
    balance = await repo.get_balance(user.id)
    stats = await repo.get_lifetime_stats(user.id)
    result = PointBalanceResponse(
        balance=balance,
        lifetime_earned=stats["earned"],
        lifetime_spent=abs(stats["spent"]),
    )
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@points_router.get(
    "/transactions",
    response_model=PointTransactionListResponse,
    status_code=status.HTTP_200_OK,
    summary="포인트 적립·소비 이력",
)
async def list_transactions(
    user: Annotated[User, Depends(get_request_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Response:
    repo = PointRepository()
    total, items = await repo.get_transactions(user.id, limit=limit, offset=offset)
    result = PointTransactionListResponse(
        total=total,
        items=[
            PointTransactionItem(id=t.id, amount=t.amount, reason=t.reason, extra=t.extra, created_at=t.created_at)
            for t in items
        ],
    )
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@attendance_router.post(
    "/check-in",
    response_model=AttendanceResponse,
    status_code=status.HTTP_200_OK,
    summary="오늘의 출석체크 (멱등)",
    description="당일 첫 호출이면 +10pt 적립, 이미 했으면 awarded=False 반환. 사용자가 명시적으로 누르는 버튼용.",
)
async def daily_attendance(
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[PointService, Depends(PointService)],
) -> Response:
    today = date.today()
    awarded = await service.award_login(user.id, today)
    balance = await PointRepository().get_balance(user.id)
    message = f"출석체크 완료! +{LOGIN_BONUS}pt 적립됐어요." if awarded else "오늘은 이미 출석체크 했어요."
    result = AttendanceResponse(
        awarded=awarded, awarded_points=LOGIN_BONUS if awarded else 0, balance=balance, message=message
    )
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)


@points_router.post(
    "/purchase",
    response_model=PurchaseResponse,
    status_code=status.HTTP_200_OK,
    summary="아이템 구매 (보호권/부스터/스킨)",
)
async def purchase(
    request: PurchaseRequest,
    user: Annotated[User, Depends(get_request_user)],
    service: Annotated[InventoryService, Depends(InventoryService)],
) -> Response:
    new_qty, spent, new_balance = await service.purchase(user.id, request.item_code)
    result = PurchaseResponse(item_code=request.item_code, new_quantity=new_qty, spent=spent, new_balance=new_balance)
    return Response(result.model_dump(), status_code=status.HTTP_200_OK)
