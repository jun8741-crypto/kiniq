"""부하 테스트 시나리오 — REQ 평가 5-1 (API P95 Latency < 3초).

준비:
1. fastapi 컨테이너 실행 (docker compose up -d fastapi)
2. 사용자 시드: DB_HOST=localhost uv run python scripts/seed_load_test_users.py

실행 (헤드리스, 동시 50명, 5분, HTML 리포트):
    uv run locust -f tests/load/locustfile.py \\
        --host http://localhost:8000 \\
        --users 50 --spawn-rate 10 --run-time 5m --headless \\
        --html docs/load-test-report.html

웹 UI:
    uv run locust -f tests/load/locustfile.py --host http://localhost:8000
    → http://localhost:8089

시나리오:
- on_start: 미리 시드된 load001~load050 중 자동 매칭해 로그인 → access_token 보관
- 각 user가 가중치별로 GET 위주 호출 (대시보드·챌린지·게이미피케이션)
"""

import random
from threading import Lock

from locust import HttpUser, between, events, task

API = "/api/v1"
USER_POOL_SIZE = 50
EMAIL_FMT = "load{:03d}@loadtest.example"
PASSWORD = "LoadTest123!"

_assigned: set[int] = set()
_pool_lock = Lock()


def _claim_user_index() -> int:
    """동시 사용자 풀에서 하나 할당. 사용자 수가 풀을 초과하면 라운드로빈."""
    with _pool_lock:
        for i in range(1, USER_POOL_SIZE + 1):
            if i not in _assigned:
                _assigned.add(i)
                return i
        # 풀 초과 시 라운드로빈 (충돌 허용)
        return random.randint(1, USER_POOL_SIZE)


class CkdCareUser(HttpUser):
    """일반 사용자 시뮬레이션. 로그인 후 대시보드·챌린지 탐색."""

    wait_time = between(1, 3)

    def on_start(self) -> None:
        idx = _claim_user_index()
        self.user_idx = idx
        email = EMAIL_FMT.format(idx)
        with self.client.post(
            f"{API}/auth/login",
            json={"email": email, "password": PASSWORD},
            name="POST /auth/login",
            catch_response=True,
        ) as r:
            if r.status_code != 200:
                r.failure(f"login failed {r.status_code}: {r.text[:120]}")
                self.access_token = None
                return
            self.access_token = r.json().get("access_token")
        self.client.headers.update({"Authorization": f"Bearer {self.access_token}"})

    @task(5)
    def dashboard_summary(self) -> None:
        self.client.get(f"{API}/dashboard/summary", name="GET /dashboard/summary")

    @task(3)
    def egfr_trend(self) -> None:
        self.client.get(f"{API}/dashboard/egfr-trend", name="GET /dashboard/egfr-trend")

    @task(2)
    def egfr_simulation(self) -> None:
        self.client.get(f"{API}/dashboard/egfr-simulation", name="GET /dashboard/egfr-simulation")

    @task(3)
    def heatmap(self) -> None:
        self.client.get(f"{API}/challenges/heatmap?weeks=26", name="GET /challenges/heatmap")

    @task(2)
    def category_progress(self) -> None:
        self.client.get(f"{API}/challenges/category-progress", name="GET /challenges/category-progress")

    @task(2)
    def weekly_emotion(self) -> None:
        self.client.get(f"{API}/challenges/weekly-emotion", name="GET /challenges/weekly-emotion")

    @task(2)
    def list_my_challenges(self) -> None:
        self.client.get(f"{API}/user-challenges", name="GET /user-challenges")

    @task(2)
    def list_challenges(self) -> None:
        self.client.get(f"{API}/challenges", name="GET /challenges")

    @task(2)
    def gamification_eggs(self) -> None:
        self.client.get(f"{API}/gamification/eggs", name="GET /gamification/eggs")

    @task(1)
    def gamification_charge_mode(self) -> None:
        self.client.get(f"{API}/gamification/charge-mode", name="GET /gamification/charge-mode")

    @task(1)
    def notifications(self) -> None:
        self.client.get(f"{API}/notifications", name="GET /notifications")

    @task(1)
    def me(self) -> None:
        self.client.get(f"{API}/users/me", name="GET /users/me")


@events.test_stop.add_listener
def _on_stop(environment, **_kwargs):  # type: ignore[no-untyped-def]
    """테스트 종료 후 P95 < 3000ms 통과 여부 출력."""
    stats = environment.stats.total
    p95 = stats.get_response_time_percentile(0.95)
    rps = stats.total_rps
    fail_pct = (stats.num_failures / stats.num_requests * 100) if stats.num_requests else 0
    print("\n" + "=" * 60)
    print("📊 부하 테스트 결과 요약 (REQ 평가 5-1)")
    print("=" * 60)
    print(f"  총 요청       : {stats.num_requests:,}")
    print(f"  실패 요청     : {stats.num_failures:,} ({fail_pct:.2f}%)")
    print(f"  RPS           : {rps:.2f} req/s")
    print(f"  중앙값 (P50)  : {stats.get_response_time_percentile(0.50):.0f} ms")
    print(f"  P95           : {p95:.0f} ms")
    print(f"  P99           : {stats.get_response_time_percentile(0.99):.0f} ms")
    print(f"  최대          : {stats.max_response_time:.0f} ms")
    print("-" * 60)
    target = 3000
    verdict = "✅ PASS" if p95 < target else "❌ FAIL"
    print(f"  P95 < 3,000ms : {verdict}  (실측 {p95:.0f}ms)")
    print("=" * 60)
