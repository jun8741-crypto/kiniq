from datetime import date, datetime

from tortoise.functions import Sum

from app.models.gamification import (
    ItemCode,
    PointReason,
    PointTransaction,
    UserChargeMode,
    UserDailyLogin,
    UserEgg,
    UserInventory,
)


class PointRepository:
    async def create_transaction(
        self, user_id: int, amount: int, reason: PointReason, extra: dict | None = None
    ) -> PointTransaction:
        return await PointTransaction.create(user_id=user_id, amount=amount, reason=reason, extra=extra or {})

    async def get_balance(self, user_id: int) -> int:
        result = await PointTransaction.filter(user_id=user_id).annotate(total=Sum("amount")).first().values("total")
        return int(result["total"] or 0) if result else 0

    async def get_transactions(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> tuple[int, list[PointTransaction]]:
        total = await PointTransaction.filter(user_id=user_id).count()
        items = await PointTransaction.filter(user_id=user_id).order_by("-created_at").offset(offset).limit(limit)
        return total, items

    async def get_lifetime_stats(self, user_id: int) -> dict[str, int]:
        earned = (
            await PointTransaction.filter(user_id=user_id, amount__gt=0)
            .annotate(total=Sum("amount"))
            .first()
            .values("total")
        )
        spent = (
            await PointTransaction.filter(user_id=user_id, amount__lt=0)
            .annotate(total=Sum("amount"))
            .first()
            .values("total")
        )
        return {
            "earned": int((earned or {}).get("total") or 0),
            "spent": int((spent or {}).get("total") or 0),
        }


class EggRepository:
    async def get_current(self, user_id: int) -> UserEgg | None:
        return await UserEgg.filter(user_id=user_id, hatched_at=None).first()

    async def get_or_create_current(self, user_id: int) -> UserEgg:
        egg = await self.get_current(user_id)
        if egg:
            return egg
        last = await UserEgg.filter(user_id=user_id).order_by("-egg_no").first()
        next_no = (last.egg_no + 1) if last else 1
        return await UserEgg.create(user_id=user_id, egg_no=next_no)

    async def increment_progress(self, egg: UserEgg, delta: int = 1) -> UserEgg:
        egg.progress_checkins = min(100, egg.progress_checkins + delta)
        await egg.save()
        return egg

    async def mark_hatched(self, egg: UserEgg, is_legendary: bool, hatched_at: datetime) -> UserEgg:
        egg.is_legendary = is_legendary
        egg.hatched_at = hatched_at
        egg.current_stage = 5
        await egg.save()
        return egg

    async def get_history(self, user_id: int) -> list[UserEgg]:
        return await UserEgg.filter(user_id=user_id, hatched_at__not_isnull=True).order_by("-egg_no")


class InventoryRepository:
    async def get_quantity(self, user_id: int, item_code: ItemCode) -> int:
        row = await UserInventory.filter(user_id=user_id, item_code=item_code).first()
        return row.quantity if row else 0

    async def list_for_user(self, user_id: int) -> list[UserInventory]:
        return await UserInventory.filter(user_id=user_id, quantity__gt=0)

    async def add_quantity(self, user_id: int, item_code: ItemCode, delta: int) -> UserInventory:
        row = await UserInventory.filter(user_id=user_id, item_code=item_code).first()
        if row:
            row.quantity = max(0, row.quantity + delta)
            await row.save()
            return row
        return await UserInventory.create(user_id=user_id, item_code=item_code, quantity=max(0, delta))


class ChargeModeRepository:
    async def get_or_create(self, user_id: int) -> UserChargeMode:
        row = await UserChargeMode.filter(user_id=user_id).first()
        if row:
            return row
        return await UserChargeMode.create(user_id=user_id, is_active=False)


class DailyLoginRepository:
    async def exists_today(self, user_id: int, login_date: date) -> bool:
        return await UserDailyLogin.filter(user_id=user_id, login_date=login_date).exists()

    async def record(self, user_id: int, login_date: date) -> UserDailyLogin:
        return await UserDailyLogin.create(user_id=user_id, login_date=login_date)
