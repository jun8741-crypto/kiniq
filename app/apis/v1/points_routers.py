from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import ORJSONResponse as Response

from app.dependencies.security import get_request_user
from app.dtos.points import (
    PointBalanceResponse,
    PointTransactionItem,
    PointTransactionListResponse,
    PurchaseRequest,
    PurchaseResponse,
)
from app.models.users import User
from app.repositories.gamification_repository import PointRepository
from app.services.inventory import InventoryService

points_router = APIRouter(prefix="/points", tags=["points"])


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
