from datetime import datetime

from pydantic import BaseModel, Field

from app.dtos.base import BaseSerializerModel
from app.models.gamification import ItemCode, PointReason


class PointBalanceResponse(BaseSerializerModel):
    balance: int
    lifetime_earned: int
    lifetime_spent: int


class PointTransactionItem(BaseSerializerModel):
    id: int
    amount: int
    reason: PointReason
    extra: dict
    created_at: datetime


class PointTransactionListResponse(BaseSerializerModel):
    total: int
    items: list[PointTransactionItem]


class PurchaseRequest(BaseModel):
    item_code: ItemCode = Field(..., description="구매할 아이템 코드")


class PurchaseResponse(BaseSerializerModel):
    item_code: ItemCode
    new_quantity: int
    spent: int
    new_balance: int


class AttendanceResponse(BaseSerializerModel):
    awarded: bool
    awarded_points: int
    balance: int
    message: str
