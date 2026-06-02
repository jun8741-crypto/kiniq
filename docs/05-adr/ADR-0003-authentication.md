# ADR-0003: 인증 방식 — JWT (Access 15분 / Refresh 7일)

**Date**: 2026-05-19 (v1: Access 60분 / Refresh 14일)
**Updated**: 2026-06-01 (v2: Access 15분 / Refresh 7일, REQ-SEC-003 강화)
**Status**: ✅ Accepted

## Context

CKD 환자의 민감의료 정보(혈압·혈당·eGFR·생활습관·감정)를 다루기 때문에 강력한 인증·인가가 필수.

요구사항:
- **REQ-SEC-003**: Access Token 유효기간 15분 / Refresh Token 7일
- **REQ-AUTH-007**: 비밀번호 5회 실패 시 30분 잠금
- **REQ-SEC-004**: Rate Limit (로그인 5회/분, 일반 60회/분)
- **REQ-SEC-008**: 회원 탈퇴 시 민감의료 즉시 파기
- **REQ-SEC-009**: 회원가입 시 민감의료 별도 동의 체크박스
- 부트캠프 평가 **5-4 인증·인가** 만점 충족
- 외부 OAuth(카카오·구글) 통합 가능성

## Decision

**JWT(JSON Web Token) 기반 무상태 인증** 채택.

토큰 정책:
- **Access Token**: 15분 유효, Bearer 헤더로 전송
- **Refresh Token**: 7일 유효, HttpOnly 쿠키 (secure: 운영, JS 접근 차단)
- 알고리즘: **HS256** (대칭키, SECRET_KEY 환경변수)
- Refresh 흐름: `GET /auth/token/refresh` → 새 Access Token 발급

추가 보안 인프라:
- **bcrypt** 비밀번호 해싱
- **slowapi** Rate Limit (인증 액션 5/분, 일반 60/분)
- **SHA256** 비밀번호 재설정 코드 해시 저장 (평문 X)
- **failed_login_count + locked_until** DB 필드로 잠금 관리
- **소셜 로그인**: Kakao·Google OAuth 2.0 (REQ-AUTH-005/006)

## Alternatives Considered

| 후보 | 장점 | 단점 | 기각 사유 |
|---|---|---|---|
| **세션 기반 인증 (Redis)** | 토큰 무효화 즉시 가능 | 분산 환경 복잡, 무상태 X | 무상태 우선, 7컨테이너 확장성 |
| **OAuth 2.0 자체 발급** | 표준 준수 | 자체 OAuth 서버 구축 부담 | 외부 OAuth(카카오/구글)만 클라이언트로 사용 |
| **API Key** | 단순 | 사용자 인증에 부적합 | 사용자 인증 안 됨 |
| **JWT (긴 만료)** v1 안 | 사용자 편의 | 토큰 도난 시 노출 시간 길음 | 의료 정보 — 보안 우선 |
| **JWT (15분/7일)** ⭐ v2 | 보안↑, Refresh로 자동 갱신 | 15분마다 갱신 호출 | 선택 |

JWT 알고리즘:
- **RS256** (비대칭): 키 관리 복잡, 멀티 서비스에 유리
- **HS256** ⭐ (대칭): 단일 서비스에 충분, 운영 단순 → 선택

## Consequences

### 좋은 점
- **평가 5-4 만점**: JWT + 5회 잠금 + Rate Limit + OAuth + 동의 + 회원 탈퇴 즉시 파기 = 6중 보안
- 무상태 → 7컨테이너 수평 확장 자유로움
- Access 15분 → 도난 시 노출 시간 짧음
- Refresh HttpOnly 쿠키 → XSS 공격 차단
- 비밀번호 재설정도 코드 SHA256 해시 저장 (REQ-AUTH C)

### 트레이드오프
- Access 15분이라 사용자가 15분마다 자동 갱신 호출 발생 (백그라운드, UX 영향 X)
- HS256 대칭키 → 멀티 서비스 확장 시 RS256 전환 필요할 수 있음
- 토큰 무효화 즉시 X (Access 15분 자연 만료 대기)

### 운영 영향
- 환경변수 `SECRET_KEY` 필수 (운영 시 강력한 랜덤)
- `JWT_ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=15`, `REFRESH_TOKEN_EXPIRE_MINUTES=10080`
- HTTPS 필수 (운영) — 쿠키 secure 플래그 의존
- 로그아웃 시 쿠키 삭제 + 클라이언트 토큰 제거
