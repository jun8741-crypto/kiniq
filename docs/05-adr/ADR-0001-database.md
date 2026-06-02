# ADR-0001: DB 선정 — PostgreSQL + Tortoise ORM

**Date**: 2026-05-19
**Status**: ✅ Accepted

## Context

만성신부전(CKD) 위험군 조기 발굴 서비스의 백엔드 데이터베이스를 선정해야 한다. 주요 요구사항:

- 의료 데이터(혈압·혈당·eGFR·생활습관)의 **트랜잭션 무결성**
- 사용자별 시계열 데이터(체크인·진화 단계·검진 이력) 빈번한 조회
- **JSONB 컬럼**(PointTransaction.extra 등 가변 메타데이터) 필요
- 부트캠프 평가 5-1 P95 < 3초 충족
- AI/ML 결과 저장·검색 시 향후 벡터 확장 고려

## Decision

**PostgreSQL 16 + Tortoise ORM (asyncpg 드라이버)** 선정.

마이그레이션 도구는 **aerich** 사용 (Tortoise 공식 도구).

## Alternatives Considered

| 후보 | 장점 | 단점 | 기각 사유 |
|---|---|---|---|
| **MySQL 8.0** | 사용 인구 많음, 부트캠프 권장안 v0.6까지 | JSONB 부족 (JSON만 지원), 한국어 정렬 약함 | JSONB 필요·시계열 쿼리 성능 |
| **MongoDB** | 스키마 유연, JSON 네이티브 | 트랜잭션 약함, 의료 무결성 부적합 | 의료 데이터 트랜잭션 요구 |
| SQLite | 가볍고 빠름 | 동시 쓰기 약함, 운영 부적합 | 다중 사용자 동시 접속 |
| **PostgreSQL** ⭐ | JSONB, 트랜잭션, 시계열 인덱스, pgvector 확장 가능 | MySQL 대비 운영 경험 적음 | — (선택) |

ORM 선택:
- **SQLAlchemy**: 동기 기본, async 별도 설정 → 학습 곡선 ↑
- **Tortoise ORM** ⭐: 비동기 우선 설계, FastAPI와 자연스러움, aerich 마이그레이션 통합 → 선택

## Consequences

### 좋은 점
- JSONB로 `PointTransaction.extra`·`UserChallenge.last_emotion` 등 가변 메타데이터 유연 저장
- asyncpg + Tortoise async → FastAPI 비동기 처리 일관 (평가 5-5)
- aerich 자동 마이그레이션 생성 + 적용 (16개 마이그레이션 누적 운영)
- 향후 pgvector 확장으로 RAG 임베딩 저장 가능

### 트레이드오프
- MySQL 대비 부트캠프 멘토 사용 경험 적음 → 학습·디버깅 시간
- Tortoise ORM은 SQLAlchemy 대비 커뮤니티 작음 → 일부 고급 쿼리는 직접 SQL
- PostgreSQL JSONB 인덱싱 비용 (점진 최적화로 해결)

### 운영 영향
- 데모·운영 환경 모두 PostgreSQL 16 Docker 이미지 사용
- 마이그레이션: `aerich migrate --name xxx` → `aerich upgrade` (자동)
- 현재 16개 마이그레이션 누적, 무중단 적용
