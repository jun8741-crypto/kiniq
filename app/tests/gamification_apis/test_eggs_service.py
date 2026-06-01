"""EggService 단위 테스트 (v3 — 3단계 진화 시스템).

명세 docs/gamification-spec-v1.md 갱신:
- 부화 임계: 10회 (1단계 캐릭터 등장)
- 2단계 진화: 40회
- 3단계 최종 진화: 100회
- 3단계 도달 = 완료, 새 알 자동 시작 X
- 보너스 분배: +100 / +400 / +750 (합 1,250pt)
- Goal Gradient: 90회 (=3단계 90% 임박)
"""

from datetime import date

from tortoise.contrib.test import TestCase

from app.models.gamification import UserEgg
from app.models.users import User
from app.repositories.gamification_repository import EggRepository, PointRepository
from app.services.eggs import EggService


async def _make_user(email: str = "e1@test.com") -> User:
    return await User.create(
        email=email,
        hashed_password="$2b$12$dummy",
        name="알테스터",
        gender="MALE",
        birthday=date(1990, 1, 1),
        phone_number="01000000001",
    )


class TestEggProgress(TestCase):
    async def test_first_call_creates_egg_with_progress_1(self) -> None:
        user = await _make_user()
        update = await EggService().progress_and_check(user.id, challenge_id=1)
        assert update.progress_checkins == 1
        assert update.current_stage == 0  # 알 (pre-hatch)
        assert update.stage_bonus == 0
        assert update.hatched is False

    async def test_hatch_at_10(self) -> None:
        """10회 도달 시 부화 (1단계 캐릭터 등장 + 종 추첨 + +100pt)."""
        user = await _make_user()
        es = EggService()
        for _ in range(9):
            await es.progress_and_check(user.id, challenge_id=1)
        egg = await EggRepository().get_current(user.id)
        assert egg.progress_checkins == 9
        assert egg.current_stage == 0
        assert egg.species is None
        assert egg.character_name is None

        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.progress_checkins == 10
        assert update.current_stage == 1
        assert update.hatched is True
        assert update.evolved_to is None
        assert update.species is not None
        assert update.character_name
        assert update.stage_bonus == 100
        assert update.stage_milestone == 10
        bal = await PointRepository().get_balance(user.id)
        assert bal == 100

    async def test_evolve_to_stage_2_at_40(self) -> None:
        """40회 도달 시 2단계 진화 + +400pt."""
        user = await _make_user()
        es = EggService()
        for _ in range(39):
            await es.progress_and_check(user.id, challenge_id=1)
        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.progress_checkins == 40
        assert update.current_stage == 2
        assert update.hatched is False
        assert update.evolved_to == 2
        assert update.stage_bonus == 400
        # 누적: 100 (부화) + 400 (2단계) = 500
        bal = await PointRepository().get_balance(user.id)
        assert bal == 500

    async def test_evolve_to_stage_3_at_100(self) -> None:
        """100회 도달 시 3단계 최종 진화 + +750pt. 새 알 자동 시작 X."""
        user = await _make_user()
        es = EggService()
        for _ in range(99):
            await es.progress_and_check(user.id, challenge_id=1)
        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.current_stage == 3
        assert update.evolved_to == 3
        assert update.stage_bonus == 750
        assert update.new_egg_no is None
        # 누적: 100 + 400 + 750 = 1,250
        bal = await PointRepository().get_balance(user.id)
        assert bal == 1250
        eggs = await UserEgg.filter(user_id=user.id)
        assert len(eggs) == 1

    async def test_no_progress_after_stage_3(self) -> None:
        """3단계 도달 후 추가 체크인해도 진행률·보너스 변화 없음 (freeze)."""
        user = await _make_user()
        es = EggService()
        for _ in range(100):
            await es.progress_and_check(user.id, challenge_id=1)
        bal_before = await PointRepository().get_balance(user.id)
        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.progress_checkins == 100  # freeze
        assert update.stage_bonus == 0
        bal_after = await PointRepository().get_balance(user.id)
        assert bal_after == bal_before

    async def test_stage_bonus_not_paid_twice(self) -> None:
        """같은 단계 임계에서 보너스는 한 번만."""
        user = await _make_user()
        es = EggService()
        for _ in range(10):
            await es.progress_and_check(user.id, challenge_id=1)
        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.stage_bonus == 0
        bal = await PointRepository().get_balance(user.id)
        assert bal == 100

    async def test_goal_gradient_final_at_90(self) -> None:
        """90회 도달 시 '최종 진화 임박' 알림 1회."""
        user = await _make_user()
        es = EggService()
        for _ in range(89):
            await es.progress_and_check(user.id, challenge_id=1)
        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.goal_90_just_alerted is True
        update2 = await es.progress_and_check(user.id, challenge_id=1)
        assert update2.goal_90_just_alerted is False
