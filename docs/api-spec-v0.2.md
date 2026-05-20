# API 명세서 v0.2

> 최종 갱신: 2026-05-20
> Base URL: `https://{host}/api/v1`
> 인증: Bearer JWT (`Authorization: Bearer <access_token>`)
> 응답 형식: `application/json`

---

## 공통

### 에러 응답 형식
```json
{ "detail": "에러 메시지" }
```

### 공통 에러 코드
| 코드 | 의미 |
|------|------|
| 400  | 요청 값 오류 |
| 401  | 인증 필요 (토큰 없음·만료) |
| 404  | 리소스 없음 |
| 409  | 중복 충돌 |
| 422  | 유효성 검사 실패 |

---

## 1. 인증 (`/auth`)

### POST `/auth/signup` — 회원가입
인증 불필요

**요청**
```json
{
  "email": "user@example.com",
  "password": "Password123!",
  "name": "홍길동",
  "gender": "MALE",
  "birth_date": "1985-03-10",
  "phone_number": "01011112222"
}
```

| 필드 | 타입 | 제약 |
|------|------|------|
| email | string | 최대 40자 |
| password | string | 최소 8자, 영문+숫자+특수문자 포함 |
| name | string | 최대 20자 |
| gender | `"MALE"` \| `"FEMALE"` | |
| birth_date | date (YYYY-MM-DD) | |
| phone_number | string | 010-XXXX-XXXX 형식 |

**응답 `201`**
```json
{ "detail": "회원가입이 성공적으로 완료되었습니다." }
```

---

### POST `/auth/login` — 로그인
인증 불필요

**요청**
```json
{ "email": "user@example.com", "password": "Password123!" }
```

**응답 `200`**
```json
{ "access_token": "<JWT>" }
```
> `refresh_token`은 HttpOnly Cookie로 설정됨.

---

### GET `/auth/token/refresh` — 액세스 토큰 갱신
인증 불필요 (refresh_token 쿠키 필요)

**응답 `200`**
```json
{ "access_token": "<새 JWT>" }
```

---

## 2. 사용자 (`/users`)

### GET `/users/me` — 내 정보 조회
인증 필요

**응답 `200`**
```json
{
  "id": 1,
  "name": "홍길동",
  "email": "user@example.com",
  "phone_number": "01011112222",
  "birthday": "1985-03-10",
  "gender": "MALE",
  "created_at": "2026-05-20T00:00:00Z"
}
```

---

### PATCH `/users/me` — 내 정보 수정
인증 필요

**요청** (변경할 필드만 포함)
```json
{
  "name": "김철수",
  "email": "new@example.com",
  "phone_number": "01099998888",
  "birthday": "1985-03-10",
  "gender": "MALE"
}
```

**응답 `200`** — 수정된 사용자 정보 (`GET /users/me`와 동일 형식)

---

## 3. 건강검진 (`/health-checks`)

### POST `/health-checks` — 검진 결과 입력
인증 필요

**요청**
```json
{
  "checked_date": "2026-05-20",
  "systolic_bp": 125,
  "diastolic_bp": 80,
  "fasting_glucose": 98.0,
  "creatinine": 1.1,
  "total_cholesterol": 195.0,
  "hdl_cholesterol": 55.0,
  "triglycerides": 130.0,
  "weight": 72.0,
  "height": 175.0,
  "waist_circumference": 85.0
}
```

| 필드 | 타입 | 필수 | 범위 |
|------|------|------|------|
| checked_date | date | ✅ | |
| systolic_bp | int | ✅ | 60~300 mmHg |
| diastolic_bp | int | ✅ | 40~200 mmHg |
| fasting_glucose | float | ✅ | 50~700 mg/dL |
| creatinine | float \| null | | 0.1~30.0 mg/dL |
| total_cholesterol | float \| null | | 50~700 mg/dL |
| hdl_cholesterol | float \| null | | 10~200 mg/dL |
| triglycerides | float \| null | | 20~2000 mg/dL |
| weight | float | ✅ | 20~300 kg |
| height | float | ✅ | 100~250 cm |
| waist_circumference | float \| null | | 40~200 cm |

**응답 `201`**
```json
{
  "id": 1,
  "user_id": 1,
  "checked_date": "2026-05-20",
  "systolic_bp": 125,
  "diastolic_bp": 80,
  "fasting_glucose": 98.0,
  "creatinine": 1.1,
  "total_cholesterol": 195.0,
  "hdl_cholesterol": 55.0,
  "triglycerides": 130.0,
  "weight": 72.0,
  "height": 175.0,
  "bmi": 23.5,
  "waist_circumference": 85.0,
  "egfr_estimated": 72.3,
  "ckd_risk_score": null,
  "ckd_stage": "G2",
  "safety_warning": null,
  "created_at": "2026-05-20T09:00:00Z"
}
```

> `egfr_estimated`, `ckd_stage` — 크레아티닌 입력 시 CKD-EPI 공식으로 즉시 계산.
> `ckd_risk_score` — AI 워커 비동기 처리 후 업데이트 (초기값 null).
> `safety_warning` — 위험 수치 감지 시 의료기관 안내 문구 반환 (혈압 ≥180/120 또는 혈당 ≥400 또는 eGFR<15).

**ckd_stage 값**

| 값 | eGFR 범위 |
|----|-----------|
| `G1` | ≥ 90 |
| `G2` | 60~89 |
| `G3A` | 45~59 |
| `G3B` | 30~44 |
| `G4` | 15~29 |
| `G5` | < 15 |

---

### GET `/health-checks` — 내 검진 이력 목록
인증 필요

**쿼리 파라미터**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| limit | int | 20 | 1~100 |
| offset | int | 0 | |

**응답 `200`**
```json
{
  "total": 5,
  "items": [ /* HealthCheckResponse 배열 */ ]
}
```

---

### GET `/health-checks/{id}` — 검진 결과 단건 조회
인증 필요

**응답 `200`** — HealthCheckResponse
**에러** `404` — 존재하지 않거나 타인 데이터

---

## 4. 생활습관 설문 (`/lifestyle-surveys`)

### POST `/lifestyle-surveys` — 설문 등록
인증 필요

**요청**
```json
{
  "surveyed_date": "2026-05-20",
  "smoking_status": "NEVER",
  "drinking_frequency": "OCCASIONALLY",
  "exercise_days_per_week": 3,
  "sleep_hours_per_day": 7.0,
  "daily_water_intake": 1.5,
  "stress_level": "MODERATE"
}
```

| 필드 | 타입 | 필수 | 값 |
|------|------|------|----|
| surveyed_date | date | ✅ | |
| smoking_status | enum | ✅ | `NEVER` \| `PAST` \| `CURRENT` |
| drinking_frequency | enum | ✅ | `NEVER` \| `OCCASIONALLY` \| `WEEKLY` \| `DAILY` |
| exercise_days_per_week | int | ✅ | 0~7 |
| sleep_hours_per_day | float \| null | | 0~24 |
| daily_water_intake | float \| null | | 0~10 L |
| stress_level | enum \| null | | `VERY_LOW` \| `LOW` \| `MODERATE` \| `HIGH` \| `VERY_HIGH` |

**응답 `201`**
```json
{
  "id": 1,
  "user_id": 1,
  "surveyed_date": "2026-05-20",
  "smoking_status": "NEVER",
  "drinking_frequency": "OCCASIONALLY",
  "exercise_days_per_week": 3,
  "sleep_hours_per_day": 7.0,
  "daily_water_intake": 1.5,
  "stress_level": "MODERATE",
  "created_at": "2026-05-20T09:00:00Z"
}
```

---

### GET `/lifestyle-surveys` — 설문 이력 목록
인증 필요 | 쿼리: `limit` (기본 20), `offset` (기본 0)

**응답 `200`**
```json
{ "total": 3, "items": [ /* LifestyleSurveyResponse 배열 */ ] }
```

---

### GET `/lifestyle-surveys/{id}` — 설문 단건 조회
인증 필요

**응답 `200`** — LifestyleSurveyResponse
**에러** `404` — 존재하지 않거나 타인 데이터

---

## 5. 대시보드 (`/dashboard`)

### GET `/dashboard/summary` — 대시보드 요약
인증 필요

**응답 `200`**
```json
{
  "latest_health": {
    "checked_date": "2026-05-20",
    "systolic_bp": 125,
    "diastolic_bp": 80,
    "fasting_glucose": 98.0,
    "bmi": 23.5,
    "egfr_estimated": 72.3,
    "ckd_stage": "G2",
    "ckd_risk_score": null
  },
  "challenge_stats": {
    "active_count": 2,
    "completed_count": 5,
    "total_checkins": 34,
    "best_streak": 7
  },
  "latest_lifestyle": {
    "surveyed_date": "2026-05-20",
    "smoking_status": "NEVER",
    "drinking_frequency": "OCCASIONALLY",
    "exercise_days_per_week": 3,
    "stress_level": "MODERATE"
  },
  "generated_at": "2026-05-20T09:00:00Z"
}
```

> `latest_health`, `latest_lifestyle` — 데이터 없는 신규 유저는 `null`.

---

### GET `/dashboard/egfr-trend` — eGFR 추이
인증 필요

**쿼리 파라미터**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| limit | int | 12 | 1~24, 최근 N회 검진 |

**응답 `200`**
```json
{
  "data_points": [
    { "checked_date": "2026-03-01", "egfr_estimated": 68.5 },
    { "checked_date": "2026-04-15", "egfr_estimated": 70.1 },
    { "checked_date": "2026-05-20", "egfr_estimated": 72.3 }
  ]
}
```

> 크레아티닌 미입력 검진은 제외. 오래된 순으로 정렬.

---

## 6. 챌린지 (`/challenges`)

### GET `/challenges` — 챌린지 목록 조회
인증 필요

**쿼리 파라미터**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| app_group | enum | | `G1` \| `G2` \| `G3` \| `G4` |

> `app_group` 미입력 시 빈 목록 반환.
> G1·G2 → Track A (케어), G3·G4 → Track B (일반)

**응답 `200`**
```json
{
  "total": 50,
  "items": [
    {
      "id": 1,
      "name": "아침 첫 물 한 컵",
      "category": "HYDRATION",
      "description": "기상 직후 물 한 컵(200ml) 마시기",
      "duration_days": 7,
      "track": "A",
      "stage": 1,
      "is_active": true
    }
  ]
}
```

**category 값**: `HYDRATION` \| `EXERCISE` \| `DIET` \| `SLEEP` \| `STRESS`
**stage 값**: `1`=입문(7일) \| `2`=초보(14일) \| `3`=중급(21일) \| `4`=숙련(30일)

---

## 7. 사용자 챌린지 (`/user-challenges`)

### POST `/user-challenges` — 챌린지 참여
인증 필요

**요청**
```json
{
  "challenge_id": 1,
  "started_at": "2026-05-20"
}
```

**응답 `201`**
```json
{
  "id": 1,
  "challenge_id": 1,
  "status": "ACTIVE",
  "started_at": "2026-05-20",
  "streak_count": 0,
  "total_checkins": 0,
  "last_checkin_date": null
}
```

**에러**
- `404` — 존재하지 않는 챌린지
- `409` — 이미 참여 중인 챌린지

---

### GET `/user-challenges` — 내 챌린지 목록
인증 필요 | 쿼리: `limit` (기본 20), `offset` (기본 0)

**응답 `200`**
```json
{ "total": 3, "items": [ /* UserChallengeResponse 배열 */ ] }
```

---

### POST `/user-challenges/{id}/checkin` — 챌린지 체크인
인증 필요

**응답 `200`**
```json
{
  "id": 1,
  "streak_count": 3,
  "total_checkins": 3,
  "last_checkin_date": "2026-05-20",
  "status": "ACTIVE",
  "message": "체크인 완료! 연속 3일째입니다. 목표까지 4일 남았습니다."
}
```

> `duration_days` 달성 시 `status`가 `"COMPLETED"`로 변경됨.

**에러**
- `400` — 이미 완료/포기된 챌린지
- `404` — 참여 중인 챌린지 없음
- `409` — 오늘 이미 체크인함

---

## 부록 — 전체 엔드포인트 목록

| 메서드 | URL | 인증 | 설명 |
|--------|-----|------|------|
| POST | `/auth/signup` | ❌ | 회원가입 |
| POST | `/auth/login` | ❌ | 로그인 |
| GET | `/auth/token/refresh` | ❌ | 액세스 토큰 갱신 |
| GET | `/users/me` | ✅ | 내 정보 조회 |
| PATCH | `/users/me` | ✅ | 내 정보 수정 |
| POST | `/health-checks` | ✅ | 검진 결과 입력 |
| GET | `/health-checks` | ✅ | 검진 이력 목록 |
| GET | `/health-checks/{id}` | ✅ | 검진 결과 단건 조회 |
| POST | `/lifestyle-surveys` | ✅ | 생활습관 설문 등록 |
| GET | `/lifestyle-surveys` | ✅ | 설문 이력 목록 |
| GET | `/lifestyle-surveys/{id}` | ✅ | 설문 단건 조회 |
| GET | `/dashboard/summary` | ✅ | 대시보드 요약 |
| GET | `/dashboard/egfr-trend` | ✅ | eGFR 추이 |
| GET | `/challenges` | ✅ | 챌린지 목록 |
| POST | `/user-challenges` | ✅ | 챌린지 참여 |
| GET | `/user-challenges` | ✅ | 내 챌린지 목록 |
| POST | `/user-challenges/{id}/checkin` | ✅ | 챌린지 체크인 |
