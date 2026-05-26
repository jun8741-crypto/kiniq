"""발표 시연용 데모 계정 시드.

기존 demo 계정이 있으면 삭제 후 재생성. 다음 상태로 세팅:
- 사용자: demo@ckdcare.example / Demo1234!
- 건강검진: G2 (정상~경증) 1건 → Track A 챌린지 추천
- 챌린지 참여: 3건 (수분·운동·식단)
- 누적 체크인: 약 75회 → 알 4단계 (75~100%) 진행률, 90% Goal Gradient 임박
- 포인트 잔액: 10,000pt
- 인벤토리: 보호권 1개, 미니 부스터 1개 (구매 흐름 시연용)
"""

import asyncio
import sys
from datetime import date, timedelta
from pathlib import Path

# 프로젝트 루트를 import path에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tortoise import Tortoise

from app.core.db.databases import TORTOISE_ORM
from app.core.utils.security import hash_password
from app.models.challenge import (
    Challenge,
    ChallengeTrack,
    UserChallenge,
    UserChallengeStatus,
)
from app.models.gamification import (
    ItemCode,
    PointReason,
    PointTransaction,
    UserChargeMode,
    UserDailyLogin,
    UserEgg,
    UserInventory,
)
from app.models.health_check import AppGroup, CkdStage, HealthCheck
from app.models.notification import Notification
from app.models.users import Gender, User

DEMO_EMAIL = "demo@ckdcare.example"
DEMO_PASSWORD = "Demo1234!"


async def wipe_existing_demo() -> None:
    """기존 demo 계정과 관련 데이터 전부 삭제 (cascade로 정리)."""
    user = await User.filter(email=DEMO_EMAIL).first()
    if user:
        print(f"  기존 demo 계정(id={user.id}) 삭제")
        # ForeignKeyField는 ON DELETE CASCADE이므로 User만 지우면 다 따라옴
        await user.delete()


async def create_demo() -> None:
    print("[1] demo 사용자 생성")
    user = await User.create(
        email=DEMO_EMAIL,
        hashed_password=hash_password(DEMO_PASSWORD),
        name="데모유저",
        gender=Gender.FEMALE,
        birthday=date(1978, 4, 15),  # 47세
        phone_number="01088887777",
    )
    print(f"  ✓ id={user.id} email={user.email}")

    print("[2] 건강검진 입력 (G2 정상~경증, Track A 추천)")
    await HealthCheck.create(
        user_id=user.id,
        checked_date=date.today() - timedelta(days=14),
        systolic_bp=128,
        diastolic_bp=82,
        fasting_glucose=98.0,
        creatinine=1.0,
        total_cholesterol=195.0,
        hdl_cholesterol=58.0,
        triglycerides=130.0,
        weight=64.0,
        height=162.0,
        bmi=24.4,
        waist_circumference=82.0,
        egfr_estimated=78.5,
        ckd_risk_score=0.18,
        ckd_stage=CkdStage.G2,
        app_group=AppGroup.G2,
    )
    print("  ✓ G2 / eGFR 78.5 / 위험도 18%")

    print("[3] 챌린지 3건 참여")
    track_a = await Challenge.filter(track=ChallengeTrack.A, is_active=True).limit(3)
    user_challenges = []
    today = date.today()
    for idx, ch in enumerate(track_a):
        uc = await UserChallenge.create(
            user_id=user.id,
            challenge_id=ch.id,
            started_at=today - timedelta(days=25),
            status=UserChallengeStatus.ACTIVE,
            streak_count=5,
            total_checkins=20 + idx * 5,
            last_checkin_date=today - timedelta(days=1),  # 어제 체크인
        )
        user_challenges.append(uc)
        print(f"  ✓ #{ch.id} {ch.name} — 누적 {uc.total_checkins}회, 연속 5일")

    print("[4] 알 부화 진행률 80% (4단계, 부화 임박)")
    egg = await UserEgg.create(
        user_id=user.id,
        egg_no=1,
        progress_checkins=80,
        current_stage=4,
        is_legendary=None,
        goal_70_alerted=True,
        goal_90_alerted=False,
        stage_25_bonus_paid=True,
        stage_50_bonus_paid=True,
        stage_75_bonus_paid=True,
        stage_100_bonus_paid=False,
    )
    print(f"  ✓ egg_no={egg.egg_no} progress={egg.progress_checkins}/100 stage={egg.current_stage}")

    print("[5] 포인트 트랜잭션으로 잔액 10,000pt 세팅")
    # 누적 적립 분포: login·checkin·streak·stage 다양하게
    txs = [
        (250, PointReason.LOGIN, {"date": "누적"}),  # 로그인 25일치
        (1600, PointReason.CHECKIN, {"누적 체크인": "80회"}),  # 80회 × 20pt
        (300, PointReason.LUCKY, {"럭키": "약 15%"}),  # 럭키 발동분 보너스
        (170, PointReason.STREAK_BONUS, {"milestone": 3}),  # 3일 + 7일 일부
        (650, PointReason.STAGE_BONUS, {"단계": "25/50/75%"}),  # 100+200+350
        (480, PointReason.FULL_PARTICIPATION, {"풀 참여": "12회"}),
        (6550, PointReason.REFUND, {"시연용": "데모 세팅", "note": "발표용 잔액 패딩"}),  # 합계 10000
    ]
    for amt, reason, extra in txs:
        await PointTransaction.create(user_id=user.id, amount=amt, reason=reason, extra=extra)
    total = sum(amt for amt, _, _ in txs)
    print(f"  ✓ 누적 적립 {total:,}pt")

    print("[6] 인벤토리: 보호권 1개 + 부스터 1개 (구매 흐름 시연용)")
    await UserInventory.create(user_id=user.id, item_code=ItemCode.PROTECT, quantity=1)
    await UserInventory.create(user_id=user.id, item_code=ItemCode.MINI_BOOSTER, quantity=1)
    print("  ✓ PROTECT × 1, MINI_BOOSTER × 1")

    print("[7] 충전 모드 상태 (정상 모드)")
    await UserChargeMode.create(user_id=user.id, is_active=False)

    print("[8] 일일 로그인 기록 (어제 분 — 오늘 첫 로그인 보너스 +10 가능)")
    await UserDailyLogin.create(user_id=user.id, login_date=date.today() - timedelta(days=1))

    print("[9] 데모용 알림 3건 (읽지 않음)")
    await Notification.create(
        user_id=user.id,
        type="EGG_GOAL_70",
        title="알이 거의 자랐어요",
        message="진행률 70% 도달! 부화까지 30번만 남았어요.",
        related_id=egg.id,
    )
    await Notification.create(
        user_id=user.id,
        type="STAGE_BONUS",
        title="알 75% 달성!",
        message="75% 도달 보너스 +350pt를 받았어요.",
        related_id=egg.id,
    )
    await Notification.create(
        user_id=user.id,
        type="CHECKIN_DONE",
        title="체크인 완료",
        message="물 1.5L 마시기 연속 5일째 달성 중입니다.",
        related_id=user_challenges[0].id,
    )
    print("  ✓ 알림 3건")

    print("\n" + "=" * 60)
    print("✓ 데모 계정 세팅 완료")
    print("=" * 60)
    print(f"  이메일: {DEMO_EMAIL}")
    print(f"  비밀번호: {DEMO_PASSWORD}")
    print("  포인트 잔액: 10,000pt")
    print("  알 진행률: 80% (부화까지 20회)")
    print("  활성 챌린지: 3개")
    print("  보유 아이템: 보호권 1, 부스터 1")
    print("  미읽음 알림: 3건")
    print("=" * 60)


async def main() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    try:
        await wipe_existing_demo()
        await create_demo()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
