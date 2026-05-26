"""EggService 단위 테스트.

명세 docs/gamification-spec-v1.md §1-3 검증.
"""

from datetime import date
from unittest.mock import patch

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
        assert update.current_stage == 1
        assert update.stage_bonus == 0

    async def test_stage_transition_at_25_grants_100pt(self) -> None:
        user = await _make_user()
        es = EggService()
        # 24회까지는 단계 1
        for _ in range(24):
            await es.progress_and_check(user.id, challenge_id=1)
        egg = await EggRepository().get_current(user.id)
        assert egg.progress_checkins == 24
        assert egg.current_stage == 1
        assert egg.stage_25_bonus_paid is False

        # 25회째 → 단계 2 + 보너스 +100
        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.progress_checkins == 25
        assert update.current_stage == 2
        assert update.stage_bonus == 100
        assert update.stage_milestone == 25
        # 잔액에 100pt 적립 확인
        bal = await PointRepository().get_balance(user.id)
        assert bal == 100

    async def test_stage_bonus_not_paid_twice(self) -> None:
        user = await _make_user()
        es = EggService()
        for _ in range(25):
            await es.progress_and_check(user.id, challenge_id=1)
        # 26회째에는 보너스 X
        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.stage_bonus == 0
        bal = await PointRepository().get_balance(user.id)
        assert bal == 100  # 25에서 받은 100만

    async def test_goal_70_alert_once(self) -> None:
        user = await _make_user()
        es = EggService()
        for _ in range(69):
            await es.progress_and_check(user.id, challenge_id=1)
        # 70번째에서 알림 발동
        update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.goal_70_just_alerted is True
        # 71에서는 알림 안 됨
        update2 = await es.progress_and_check(user.id, challenge_id=1)
        assert update2.goal_70_just_alerted is False

    async def test_hatch_at_100_creates_new_egg(self) -> None:
        user = await _make_user()
        es = EggService()
        # 99까지 진행
        for _ in range(99):
            await es.progress_and_check(user.id, challenge_id=1)
        # 100번째 → 부화
        with patch("secrets.SystemRandom.random", return_value=0.5):  # 일반 알 (5% 미달)
            update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.hatched is True
        assert update.is_legendary is False
        assert update.new_egg_no == 2
        # 첫 알은 hatched_at 채워짐, 새 알은 진행 중
        first_egg = await UserEgg.filter(user_id=user.id, egg_no=1).first()
        assert first_egg.hatched_at is not None
        assert first_egg.current_stage == 5
        second_egg = await UserEgg.filter(user_id=user.id, egg_no=2).first()
        assert second_egg.progress_checkins == 0

    async def test_legendary_5_percent_when_lucky(self) -> None:
        user = await _make_user()
        es = EggService()
        for _ in range(99):
            await es.progress_and_check(user.id, challenge_id=1)
        with patch("secrets.SystemRandom.random", return_value=0.03):  # 5% 미만 → 전설
            update = await es.progress_and_check(user.id, challenge_id=1)
        assert update.is_legendary is True
