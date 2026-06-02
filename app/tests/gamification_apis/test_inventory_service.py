"""InventoryService 단위 테스트.

명세 docs/gamification-spec-v1.md §1-4 검증.
"""

from datetime import date

from fastapi import HTTPException
from tortoise.contrib.test import TestCase

from app.models.gamification import ItemCode, PointReason
from app.models.users import User
from app.repositories.gamification_repository import InventoryRepository, PointRepository
from app.services.inventory import InventoryService


async def _make_user(email: str = "i1@test.com", points: int = 0) -> User:
    u = await User.create(
        email=email,
        hashed_password="$2b$12$dummy",
        name="인벤테스터",
        gender="MALE",
        birthday=date(1990, 1, 1),
        phone_number="01000000003",
    )
    if points:
        await PointRepository().create_transaction(u.id, points, PointReason.CHECKIN, {"seed": True})
    return u


class TestPurchase(TestCase):
    async def test_insufficient_balance_400(self) -> None:
        user = await _make_user(points=100)
        try:
            await InventoryService().purchase(user.id, ItemCode.PROTECT)
            raise AssertionError("expected HTTPException")
        except HTTPException as e:
            assert e.status_code == 400
            assert "포인트가 부족" in e.detail

    async def test_protect_max_2_cap(self) -> None:
        user = await _make_user(points=2000)
        svc = InventoryService()
        await svc.purchase(user.id, ItemCode.PROTECT)
        await svc.purchase(user.id, ItemCode.PROTECT)
        # 3번째는 409
        try:
            await svc.purchase(user.id, ItemCode.PROTECT)
            raise AssertionError("expected HTTPException")
        except HTTPException as e:
            assert e.status_code == 409
            assert "2개" in e.detail

    async def test_skin_dup_blocked(self) -> None:
        user = await _make_user(points=1000)
        svc = InventoryService()
        await svc.purchase(user.id, ItemCode.SKIN_S_BLUE)
        try:
            await svc.purchase(user.id, ItemCode.SKIN_S_BLUE)
            raise AssertionError("expected HTTPException")
        except HTTPException as e:
            assert e.status_code == 409
            assert "이미 보유" in e.detail

    async def test_successful_purchase_updates_balance_and_inventory(self) -> None:
        user = await _make_user(points=2000)
        new_qty, spent, balance = await InventoryService().purchase(user.id, ItemCode.MINI_BOOSTER)
        assert new_qty == 1
        assert spent == 200
        assert balance == 1800
        inv_qty = await InventoryRepository().get_quantity(user.id, ItemCode.MINI_BOOSTER)
        assert inv_qty == 1

    async def test_booster_max_1_cap(self) -> None:
        user = await _make_user(points=2000)
        svc = InventoryService()
        await svc.purchase(user.id, ItemCode.MINI_BOOSTER)
        # 2번째는 캡 초과 → 409
        try:
            await svc.purchase(user.id, ItemCode.MINI_BOOSTER)
            raise AssertionError("expected HTTPException")
        except HTTPException as e:
            assert e.status_code == 409
            assert "이미 보유" in e.detail or "최대" in e.detail
        qty = await InventoryRepository().get_quantity(user.id, ItemCode.MINI_BOOSTER)
        assert qty == 1
