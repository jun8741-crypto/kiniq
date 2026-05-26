"""게이미피케이션 조회용 서비스 (라우터가 호출).

알 진행률·캐릭터 상태·충전 모드 상태를 조회용 DTO로 직렬화. 적립·소비 로직은 PointService/EggService/ChargeModeService에 분리.
"""

from datetime import date

from fastapi import HTTPException
from starlette import status

from app.dtos.gamification import (
    ChargeModeResponse,
    EggHistoryItem,
    EggHistoryResponse,
    EggResponse,
    InventoryItem,
    InventoryResponse,
    MascotResponse,
)
from app.models.challenge import UserChallenge
from app.models.gamification import ItemCode
from app.repositories.gamification_repository import (
    ChargeModeRepository,
    EggRepository,
    InventoryRepository,
)


class GamificationService:
    def __init__(self) -> None:
        self._eggs = EggRepository()
        self._inv = InventoryRepository()
        self._charge = ChargeModeRepository()

    async def get_current_egg(self, user_id: int) -> EggResponse:
        egg = await self._eggs.get_or_create_current(user_id)
        return EggResponse(
            egg_no=egg.egg_no,
            progress_checkins=egg.progress_checkins,
            current_stage=egg.current_stage,
            progress_percent=egg.progress_checkins,
            goal_70_alerted=egg.goal_70_alerted,
            goal_90_alerted=egg.goal_90_alerted,
            is_legendary=egg.is_legendary,
            species=egg.species,
            character_name=egg.character_name,
            started_at=egg.started_at,
        )

    async def get_egg_history(self, user_id: int) -> EggHistoryResponse:
        items = await self._eggs.get_history(user_id)
        legendary_count = sum(1 for e in items if e.is_legendary)
        return EggHistoryResponse(
            total=len(items),
            legendary_count=legendary_count,
            items=[
                EggHistoryItem(
                    egg_no=e.egg_no,
                    is_legendary=e.is_legendary,
                    species=e.species,
                    character_name=e.character_name,
                    started_at=e.started_at,
                    hatched_at=e.hatched_at,
                )
                for e in items
            ],
        )

    async def rename_character(self, user_id: int, egg_id: int, new_name: str) -> EggHistoryItem:
        """부화된 알의 캐릭터 이름 변경."""
        from app.models.gamification import UserEgg

        egg = await UserEgg.filter(id=egg_id, user_id=user_id).first()
        if egg is None:
            from fastapi import HTTPException

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="캐릭터를 찾을 수 없습니다.")
        if egg.hatched_at is None:
            from fastapi import HTTPException

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="아직 부화하지 않은 알입니다.")
        egg.character_name = new_name.strip()
        await egg.save()
        return EggHistoryItem(
            egg_no=egg.egg_no,
            is_legendary=egg.is_legendary,
            species=egg.species,
            character_name=egg.character_name,
            started_at=egg.started_at,
            hatched_at=egg.hatched_at,
        )

    async def get_charge_mode(self, user_id: int, today: date) -> ChargeModeResponse:
        cm = await self._charge.get_or_create(user_id)
        latest = (
            await UserChallenge.filter(user_id=user_id, last_checkin_date__not_isnull=True)
            .order_by("-last_checkin_date")
            .first()
        )
        days_since = (today - latest.last_checkin_date).days if latest and latest.last_checkin_date else None
        return ChargeModeResponse(
            is_active=cm.is_active,
            entered_at=cm.entered_at,
            exited_at=cm.exited_at,
            days_since_last_checkin=days_since,
            warning_4d_alerted=cm.warning_4d_alerted,
            warning_5d_alerted=cm.warning_5d_alerted,
            warning_6d_alerted=cm.warning_6d_alerted,
        )

    async def get_inventory(self, user_id: int) -> InventoryResponse:
        rows = await self._inv.list_for_user(user_id)
        return InventoryResponse(
            total=len(rows),
            items=[InventoryItem(item_code=r.item_code, quantity=r.quantity, acquired_at=r.acquired_at) for r in rows],
        )

    async def get_mascot(self, user_id: int, today: date) -> MascotResponse:
        current_egg = await self.get_current_egg(user_id)
        charge = await self.get_charge_mode(user_id, today)
        history = await self._eggs.get_history(user_id)
        legendary_unlocked = any(e.is_legendary for e in history)

        # 스킨: 보유한 것 중 가장 비싼 거 (단순화) — 없으면 None
        from app.services.inventory import ITEM_PRICE

        owned = await self._inv.list_for_user(user_id)
        skin_codes = [
            ItemCode.SKIN_S_BLUE,
            ItemCode.SKIN_S_GREEN,
            ItemCode.SKIN_M_RED,
            ItemCode.SKIN_M_PURPLE,
            ItemCode.SKIN_L_GOLD,
        ]
        owned_skins = [r.item_code for r in owned if r.item_code in skin_codes and r.quantity > 0]
        skin_active = max(owned_skins, key=lambda c: ITEM_PRICE[c]) if owned_skins else None

        return MascotResponse(
            current_egg=current_egg,
            charge_mode=charge,
            legendary_unlocked=legendary_unlocked,
            skin_active=skin_active,
        )

    async def exit_charge_mode(self, user_id: int) -> ChargeModeResponse:
        """명시적 탈출 (UI 버튼용). 체크인 한 적 없으면 400."""
        cm = await self._charge.get_or_create(user_id)
        if not cm.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 정상 모드입니다.")
        from datetime import UTC, datetime

        cm.is_active = False
        cm.exited_at = datetime.now(UTC)
        cm.warning_4d_alerted = False
        cm.warning_5d_alerted = False
        cm.warning_6d_alerted = False
        await cm.save()
        return await self.get_charge_mode(user_id, date.today())
