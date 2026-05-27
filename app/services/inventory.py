"""인벤토리 / 구매 서비스.

명세: docs/gamification-spec-v1.md §1-4
- 스트릭 보호권 500pt, 최대 2개 캡
- 회복 미니알 부스터 200pt, 무제한
- 스킨 (소) 300pt / (중) 700pt / (대) 1,200pt — 중복 구매 차단
"""

from fastapi import HTTPException
from starlette import status

from app.models.gamification import ItemCode, PointReason
from app.repositories.gamification_repository import InventoryRepository, PointRepository
from app.services.points import PointService

ITEM_PRICE: dict[ItemCode, int] = {
    ItemCode.PROTECT: 500,
    ItemCode.MINI_BOOSTER: 200,
    ItemCode.SKIN_S_BLUE: 300,
    ItemCode.SKIN_S_GREEN: 300,
    ItemCode.SKIN_M_RED: 700,
    ItemCode.SKIN_M_PURPLE: 700,
    ItemCode.SKIN_L_GOLD: 1200,
}

# 보유 한도 (없으면 무제한)
ITEM_MAX_QUANTITY: dict[ItemCode, int] = {
    ItemCode.PROTECT: 2,
    # 부스터는 1개 캡 — 사용 후 재방문 유도 (자주 사두는 패턴 차단)
    ItemCode.MINI_BOOSTER: 1,
    # 스킨은 1개씩 (중복 구매 차단)
    ItemCode.SKIN_S_BLUE: 1,
    ItemCode.SKIN_S_GREEN: 1,
    ItemCode.SKIN_M_RED: 1,
    ItemCode.SKIN_M_PURPLE: 1,
    ItemCode.SKIN_L_GOLD: 1,
}


class InventoryService:
    def __init__(self) -> None:
        self._inv = InventoryRepository()
        self._points = PointService()
        self._point_repo = PointRepository()

    async def purchase(self, user_id: int, item_code: ItemCode) -> tuple[int, int, int]:
        """아이템 구매. 반환: (new_quantity, spent, new_balance)."""
        price = ITEM_PRICE.get(item_code)
        if price is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 아이템 코드입니다.")

        # 보유 한도 검증
        current_qty = await self._inv.get_quantity(user_id, item_code)
        max_qty = ITEM_MAX_QUANTITY.get(item_code)
        if max_qty is not None and current_qty >= max_qty:
            if max_qty == 1:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 보유한 아이템입니다.")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"최대 {max_qty}개까지만 보유할 수 있습니다.",
            )

        # 잔액 검증
        balance = await self._point_repo.get_balance(user_id)
        if balance < price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"포인트가 부족합니다. (잔액 {balance}pt / 필요 {price}pt)",
            )

        # 트랜잭션 — 잔액 검증·차감·인벤토리 추가는 순차 처리
        await self._points.deduct(
            user_id=user_id, amount=price, reason=PointReason.PURCHASE, extra={"item_code": item_code.value}
        )
        row = await self._inv.add_quantity(user_id, item_code, +1)
        new_balance = balance - price
        return row.quantity, price, new_balance

    async def list_items(self, user_id: int) -> list:
        return await self._inv.list_for_user(user_id)
