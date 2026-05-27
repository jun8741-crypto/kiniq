#!/usr/bin/env bash
# 발표 시연 직전에 demo 계정 상태를 빠르게 조작하는 헬퍼.
#
# 사용:
#   ./scripts/demo_fast_forward.sh                # 사용법 출력
#   ./scripts/demo_fast_forward.sh near-hatch     # 알 99% (다음 체크인 1번 = 부화)
#   ./scripts/demo_fast_forward.sh stage-25       # 알 24/100 (다음 체크인 = 25% 보너스 시연)
#   ./scripts/demo_fast_forward.sh stage-50       # 알 49/100 (50% 보너스)
#   ./scripts/demo_fast_forward.sh stage-75       # 알 74/100 (75% 보너스)
#   ./scripts/demo_fast_forward.sh streak-3       # 스트릭 2 (다음 체크인 = 3일 보너스 +30pt)
#   ./scripts/demo_fast_forward.sh streak-7       # 스트릭 6 (다음 체크인 = 7일 보너스 +70pt)
#   ./scripts/demo_fast_forward.sh charge-mode    # 마지막 체크인을 7일 전으로 → 다음 로그인 시 충전 모드 진입
#   ./scripts/demo_fast_forward.sh reset          # 시드 스크립트 재실행 (모든 상태 초기화)
#   ./scripts/demo_fast_forward.sh status         # 현재 상태 출력

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

case "${1:-}" in
    near-hatch)
        echo "🥚 알 진행률 99% 설정 (다음 체크인 1번 = 부화)"
        USER_ID=$(get_user_id)
        psql_exec "UPDATE user_eggs SET progress_checkins=99, current_stage=4, goal_70_alerted=true, goal_90_alerted=true, stage_25_bonus_paid=true, stage_50_bonus_paid=true, stage_75_bonus_paid=true WHERE user_id=$USER_ID AND hatched_at IS NULL;"
        echo "✓ 완료. 시연 시 체크인 1번 누르면 부화 모달 + 종 추첨 표시"
        ;;
    stage-25)
        echo "🥚 알 진행률 24/100 설정 (다음 체크인 = 25% 보너스 +100pt)"
        USER_ID=$(get_user_id)
        psql_exec "UPDATE user_eggs SET progress_checkins=24, current_stage=1, goal_70_alerted=false, goal_90_alerted=false, stage_25_bonus_paid=false WHERE user_id=$USER_ID AND hatched_at IS NULL;"
        echo "✓ 완료"
        ;;
    stage-50)
        echo "🥚 알 진행률 49/100 설정 (다음 체크인 = 50% 보너스 +200pt)"
        USER_ID=$(get_user_id)
        psql_exec "UPDATE user_eggs SET progress_checkins=49, current_stage=2, goal_70_alerted=false, goal_90_alerted=false, stage_25_bonus_paid=true, stage_50_bonus_paid=false WHERE user_id=$USER_ID AND hatched_at IS NULL;"
        echo "✓ 완료"
        ;;
    stage-75)
        echo "🥚 알 진행률 74/100 설정 (다음 체크인 = 75% 보너스 +350pt, 70% 알림 발동)"
        USER_ID=$(get_user_id)
        psql_exec "UPDATE user_eggs SET progress_checkins=74, current_stage=3, goal_70_alerted=false, goal_90_alerted=false, stage_25_bonus_paid=true, stage_50_bonus_paid=true, stage_75_bonus_paid=false WHERE user_id=$USER_ID AND hatched_at IS NULL;"
        echo "✓ 완료"
        ;;
    streak-3)
        echo "🔥 스트릭 2 설정 (다음 체크인 = 3일 보너스 +30pt)"
        USER_ID=$(get_user_id)
        psql_exec "UPDATE user_challenges SET streak_count=2, last_checkin_date=CURRENT_DATE - INTERVAL '1 day' WHERE user_id=$USER_ID AND status='ACTIVE';"
        echo "✓ 완료. 단, 스트릭 보너스는 챌린지×마일스톤 멱등이라 이전에 받은 적 있으면 안 받음"
        echo "  포인트 이력에서 PROTECT_CONSUME 이외의 STREAK_BONUS milestone=3 row 미리 삭제 권장:"
        echo "  docker exec postgres psql -U ckduser -d ckd_challenge -c \"DELETE FROM point_transactions WHERE user_id=$USER_ID AND reason='STREAK_BONUS' AND extra->>'milestone'='3';\""
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
        echo "✓ 완료. 시연 시 로그인 또는 체크인 호출 시 자동 진입"
        ;;
    reset)
        echo "🔄 demo 계정 전체 초기화 (시드 스크립트 재실행)"
        DB_HOST=localhost uv run python scripts/seed_demo_user.py
        ;;
    status)
        USER_ID=$(get_user_id)
        echo "📊 현재 demo 계정 상태 (user_id=$USER_ID)"
        echo ""
        echo "[알 진행률]"
        psql_exec "SELECT egg_no, progress_checkins, current_stage, hatched_at, species, character_name FROM user_eggs WHERE user_id=$USER_ID ORDER BY egg_no;"
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
        echo "demo 계정 시연 헬퍼"
        echo ""
        echo "사용법:"
        echo "  ./scripts/demo_fast_forward.sh <명령>"
        echo ""
        echo "명령:"
        echo "  near-hatch    알 99% → 다음 체크인 = 부화 시연"
        echo "  stage-25      알 24/100 → 다음 체크인 = 25% 보너스 +100"
        echo "  stage-50      알 49/100 → 다음 체크인 = 50% 보너스 +200"
        echo "  stage-75      알 74/100 → 다음 체크인 = 75% 보너스 +350 + 70% 알림"
        echo "  streak-3      스트릭 2 → 다음 체크인 = 3일 보너스 +30"
        echo "  streak-7      스트릭 6 → 다음 체크인 = 7일 보너스 +70"
        echo "  charge-mode   마지막 체크인 7일 전 → 로그인 시 쉬어가기 진입"
        echo "  reset         시드 스크립트 재실행 (전체 초기화)"
        echo "  status        현재 상태 출력"
        echo ""
        echo "예: ./scripts/demo_fast_forward.sh near-hatch"
        ;;
esac
