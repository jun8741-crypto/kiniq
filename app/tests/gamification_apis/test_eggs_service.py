"""EggService 단위 테스트 (v2 — 4단계 진화 시스템).

명세 docs/gamification-spec-v1.md §1-3 갱신:
- 부화 임계: 10회 (1단계 캐릭터 등장)
- 2단계 진화: 40회
- 3단계 진화: 100회
- 4단계 최종 진화: 200회
- 4단계 도달 = 완료, 새 알 자동 시작 X
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
        # 9회까지는 알 상태
        for _ in range(9):
            await es.progress_and_check(user.id, challenge_id=1)
        egg = await EggRepository().get_current(user.id)
        assert egg.progress_checkins == 9
        assert egg.current_stage == 0
        assert egg.species is None  # 아직 부화 X
        assert egg.character_name is None

        # 10회째 → 부화
        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.progress_checkins == 10
        assert update.current_stage == 1
        assert update.hatched is True
        assert update.evolved_to is None  # 진화 아님
        assert update.species is not None
        assert update.character_name
        assert update.stage_bonus == 100
        assert update.stage_milestone == 10
        # 잔액 100pt
        bal = await PointRepository().get_balance(user.id)
        assert bal == 100

    async def test_evolve_to_stage_2_at_40(self) -> None:
        """40회 도달 시 2단계 진화 + +200pt."""
        user = await _make_user()
        es = EggService()
        for _ in range(39):
            await es.progress_and_check(user.id, challenge_id=1)
        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.progress_checkins == 40
        assert update.current_stage == 2
        assert update.hatched is False  # 이미 부화 했었음 (10회에)
        assert update.evolved_to == 2
        assert update.stage_bonus == 200
        # 잔액: 100 (부화) + 200 (2단계) = 300
        bal = await PointRepository().get_balance(user.id)
        assert bal == 300

    async def test_evolve_to_stage_3_at_100(self) -> None:
        """100회 도달 시 3단계 진화 + +350pt."""
        user = await _make_user()
        es = EggService()
        for _ in range(99):
            await es.progress_and_check(user.id, challenge_id=1)
        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.current_stage == 3
        assert update.evolved_to == 3
        assert update.stage_bonus == 350
        # 누적: 100 + 200 + 350 = 650
        bal = await PointRepository().get_balance(user.id)
        assert bal == 650

    async def test_evolve_to_stage_4_at_200(self) -> None:
        """200회 도달 시 4단계 최종 진화 + +600pt. 새 알 자동 시작 X."""
        user = await _make_user()
        es = EggService()
        for _ in range(199):
            await es.progress_and_check(user.id, challenge_id=1)
        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.current_stage == 4
        assert update.evolved_to == 4
        assert update.stage_bonus == 600
        assert update.new_egg_no is None  # 새 알 자동 시작 X
        # 누적: 100 + 200 + 350 + 600 = 1250
        bal = await PointRepository().get_balance(user.id)
        assert bal == 1250
        # 알 row는 여전히 1개만 (4단계 완료 상태)
        eggs = await UserEgg.filter(user_id=user.id)
        assert len(eggs) == 1

    async def test_no_progress_after_stage_4(self) -> None:
        """4단계 도달 후 추가 체크인해도 진행률·보너스 변화 없음 (freeze)."""
        user = await _make_user()
        es = EggService()
        for _ in range(200):
            await es.progress_and_check(user.id, challenge_id=1)
        bal_before = await PointRepository().get_balance(user.id)
        # 추가 체크인
        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.progress_checkins == 200  # freeze
        assert update.stage_bonus == 0  # 더 이상 보너스 없음
        bal_after = await PointRepository().get_balance(user.id)
        assert bal_after == bal_before  # 잔액 변화 없음

    async def test_stage_bonus_not_paid_twice(self) -> None:
        """같은 단계 임계에서 보너스는 한 번만."""
        user = await _make_user()
        es = EggService()
        for _ in range(10):
            await es.progress_and_check(user.id, challenge_id=1)
        # 11회째에는 보너스 X
        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.stage_bonus == 0
        bal = await PointRepository().get_balance(user.id)
        assert bal == 100  # 10에서 받은 100만

    async def test_goal_gradient_final_at_180(self) -> None:
        """180회 도달 시 '최종 진화 임박' 알림 1회."""
        user = await _make_user()
        es = EggService()
        for _ in range(179):
            await es.progress_and_check(user.id, challenge_id=1)
        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.goal_90_just_alerted is True
        # 181에서는 알림 안 됨
        update2 = await es.progress_and_check(user.id, challenge_id=1)
        assert update2.goal_90_just_alerted is False
