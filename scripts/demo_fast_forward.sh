#!/usr/bin/env bash
# 발표 시연 직전에 demo 계정 상태를 빠르게 조작하는 헬퍼 (v2 — 4단계 진화 시스템).
#
# 사용:
#   ./scripts/demo_fast_forward.sh                   # 사용법 출력
#   ./scripts/demo_fast_forward.sh near-hatch        # 9회 (다음 체크인 = 부화 + 종 추첨)
#   ./scripts/demo_fast_forward.sh near-stage-2      # 39회 (다음 체크인 = 2단계 진화 +200pt)
#   ./scripts/demo_fast_forward.sh near-stage-3      # 99회 (다음 체크인 = 3단계 진화 +350pt)
#   ./scripts/demo_fast_forward.sh near-stage-4      # 199회 (다음 체크인 = 4단계 최종 +600pt)
#   ./scripts/demo_fast_forward.sh near-final-alert  # 179회 (다음 체크인 = 'Goal Gradient' 알림)
#   ./scripts/demo_fast_forward.sh streak-3          # 스트릭 2 (다음 체크인 = 3일 보너스 +30pt)
#   ./scripts/demo_fast_forward.sh streak-7          # 스트릭 6 (다음 체크인 = 7일 보너스 +70pt)
#   ./scripts/demo_fast_forward.sh charge-mode       # 마지막 체크인 7일 전 → 다음 로그인 시 진입
#   ./scripts/demo_fast_forward.sh reset             # 시드 스크립트 재실행
#   ./scripts/demo_fast_forward.sh status            # 현재 상태 출력

set -e

POSTGRES_CONTAINER="postgres"
DB_USER="ckduser"
DB_NAME="ckd_challenge"
EMAIL="demo@ckdcare.example"

psql_exec() {
    docker exec "$POSTGRES_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "$1"
}

get_user_id() {
    docker exec "$POSTGRES_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -tA -c \
        "SELECT id FROM users WHERE email='$EMAIL';"
}

# 진화 단계 임계 (eggs.py 와 동기화)
# 부화: 10 / 2단계: 40 / 3단계: 100 / 4단계: 200 / Goal Gradient: 180

case "${1:-}" in
    near-hatch)
        echo "🥚 알 9회 설정 (다음 체크인 = 부화 + 종 추첨 모달)"
        USER_ID=$(get_user_id)
        psql_exec "UPDATE user_eggs SET progress_checkins=9, current_stage=0, species=NULL, character_name=NULL, hatched_at=NULL, goal_70_alerted=false, goal_90_alerted=false, stage_25_bonus_paid=false, stage_50_bonus_paid=false, stage_75_bonus_paid=false, stage_100_bonus_paid=false WHERE user_id=$USER_ID AND current_stage < 4;"
        echo "✓ 완료. 시연 시 체크인 1번 = 부화 (종 추첨 + 이름 생성 + 컨페티)"
        ;;
    near-stage-2)
        echo "🥚 알 39회 설정 (다음 체크인 = 2단계 진화 +200pt)"
        USER_ID=$(get_user_id)
        psql_exec "UPDATE user_eggs SET progress_checkins=39, current_stage=1, stage_25_bonus_paid=true, stage_50_bonus_paid=false, stage_75_bonus_paid=false, stage_100_bonus_paid=false, goal_70_alerted=false, goal_90_alerted=false WHERE user_id=$USER_ID AND current_stage < 4;"
        echo "✓ 완료. 캐릭터가 이미 부화한 상태에서 진화 시연 가능"
        ;;
    near-stage-3)
        echo "🥚 알 99회 설정 (다음 체크인 = 3단계 진화 +350pt)"
        USER_ID=$(get_user_id)
        psql_exec "UPDATE user_eggs SET progress_checkins=99, current_stage=2, stage_25_bonus_paid=true, stage_50_bonus_paid=true, stage_75_bonus_paid=false, stage_100_bonus_paid=false, goal_70_alerted=false, goal_90_alerted=false WHERE user_id=$USER_ID AND current_stage < 4;"
        echo "✓ 완료"
        ;;
    near-stage-4)
        echo "🥚 알 199회 설정 (다음 체크인 = 4단계 최종 진화 +600pt)"
        USER_ID=$(get_user_id)
        psql_exec "UPDATE user_eggs SET progress_checkins=199, current_stage=3, stage_25_bonus_paid=true, stage_50_bonus_paid=true, stage_75_bonus_paid=true, stage_100_bonus_paid=false, goal_70_alerted=false, goal_90_alerted=true WHERE user_id=$USER_ID AND current_stage < 4;"
        echo "✓ 완료. 시연 시 완전체 진화 모달 + 노란 강조"
        ;;
    near-final-alert)
        echo "🔔 알 179회 설정 (다음 체크인 = '최종 진화 임박' 알림 발동)"
        USER_ID=$(get_user_id)
        psql_exec "UPDATE user_eggs SET progress_checkins=179, current_stage=3, stage_25_bonus_paid=true, stage_50_bonus_paid=true, stage_75_bonus_paid=true, stage_100_bonus_paid=false, goal_70_alerted=false, goal_90_alerted=false WHERE user_id=$USER_ID AND current_stage < 4;"
        echo "✓ 완료. 시연 시 빨강 강조 + Goal Gradient 알림"
        ;;
    streak-3)
        echo "🔥 스트릭 2 설정 (다음 체크인 = 3일 보너스 +30pt)"
        USER_ID=$(get_user_id)
        psql_exec "UPDATE user_challenges SET streak_count=2, last_checkin_date=CURRENT_DATE - INTERVAL '1 day' WHERE user_id=$USER_ID AND status='ACTIVE';"
        psql_exec "DELETE FROM point_transactions WHERE user_id=$USER_ID AND reason='STREAK_BONUS' AND extra->>'milestone'='3';"
        echo "✓ 완료"
        ;;
    streak-7)
        echo "🔥 스트릭 6 설정 (다음 체크인 = 7일 보너스 +70pt)"
        USER_ID=$(get_user_id)
        psql_exec "UPDATE user_challenges SET streak_count=6, last_checkin_date=CURRENT_DATE - INTERVAL '1 day' WHERE user_id=$USER_ID AND status='ACTIVE';"
        psql_exec "DELETE FROM point_transactions WHERE user_id=$USER_ID AND reason='STREAK_BONUS' AND extra->>'milestone'='7';"
        echo "✓ 완료"
        ;;
    charge-mode)
        echo "😴 마지막 체크인을 7일 전으로 설정 (다음 로그인 시 쉬어가기 모드 진입)"
        USER_ID=$(get_user_id)
        psql_exec "UPDATE user_challenges SET last_checkin_date=CURRENT_DATE - INTERVAL '7 days' WHERE user_id=$USER_ID;"
        psql_exec "UPDATE user_charge_mode SET is_active=false, warning_4d_alerted=false, warning_5d_alerted=false, warning_6d_alerted=false WHERE user_id=$USER_ID;"
        echo "✓ 완료"
        ;;
    reset)
        echo "🔄 demo 계정 전체 초기화"
        DB_HOST=localhost uv run python scripts/seed_demo_user.py
        ;;
    status)
        USER_ID=$(get_user_id)
        echo "📊 현재 demo 계정 상태 (user_id=$USER_ID)"
        echo ""
        echo "[알/캐릭터 진행률]"
        psql_exec "SELECT egg_no, progress_checkins, current_stage, species, character_name, hatched_at FROM user_eggs WHERE user_id=$USER_ID ORDER BY egg_no;"
        echo ""
        echo "[챌린지 스트릭]"
        psql_exec "SELECT challenge_id, streak_count, total_checkins, last_checkin_date FROM user_challenges WHERE user_id=$USER_ID;"
        echo ""
        echo "[포인트 잔액]"
        psql_exec "SELECT COALESCE(SUM(amount), 0) AS balance FROM point_transactions WHERE user_id=$USER_ID;"
        echo ""
        echo "[인벤토리]"
        psql_exec "SELECT item_code, quantity FROM user_inventory WHERE user_id=$USER_ID AND quantity > 0;"
        echo ""
        echo "[충전 모드]"
        psql_exec "SELECT is_active, entered_at, exited_at FROM user_charge_mode WHERE user_id=$USER_ID;"
        ;;
    *)
        cat <<EOF
demo 계정 시연 헬퍼 (v2 — 4단계 진화 시스템)

진화 임계: 부화 10 / 2단계 40 / 3단계 100 / 4단계 200

사용:
  ./scripts/demo_fast_forward.sh <명령>

진화 명령:
  near-hatch         9회 → 다음 체크인 = 부화 (종 추첨 + 컨페티)
  near-stage-2      39회 → 다음 체크인 = 2단계 진화 +200pt
  near-stage-3      99회 → 다음 체크인 = 3단계 진화 +350pt
  near-stage-4     199회 → 다음 체크인 = 4단계 최종 진화 +600pt
  near-final-alert 179회 → 다음 체크인 = 최종 진화 임박 알림

게이미피케이션 명령:
  streak-3       스트릭 2 → 다음 체크인 = 3일 보너스 +30
  streak-7       스트릭 6 → 다음 체크인 = 7일 보너스 +70
  charge-mode    7일 전 체크인 → 로그인 시 쉬어가기 진입

유틸:
  reset          시드 스크립트 재실행 (전체 초기화)
  status         현재 상태 출력

예: ./scripts/demo_fast_forward.sh near-hatch
EOF
        ;;
esac
