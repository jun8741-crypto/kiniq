# ADR-0004: 브랜치 전략 — Git Flow (main / develop / feature)

**Date**: 2026-05-19
**Updated**: 2026-06-02 (develop → main 1차 PR 후 feature 브랜치 강제)
**Status**: ✅ Accepted

## Context

부트캠프 팀 프로젝트로 5명 내외가 협업하며, 발표·평가용 안정 버전과 개발 중 버전을 분리해야 한다.

요구사항:
- **main 보호**: 발표 시점에 안정 버전이 깨지지 않도록
- **develop 통합**: 팀원들이 동시 작업한 결과 통합
- **feature 분리**: 한 사람이 작업 중일 때 다른 사람 작업에 영향 X
- **PR 리뷰**: 의료 콘텐츠·개인정보 변경 시 최소 1인 리뷰 강제
- **부트캠프 평가 6-2**: PR/이슈 기반 협업 흐름

## Decision

**Git Flow 단순화 버전** 채택.

```
main      ← 발표·배포용 안정 버전 (보호, 최종날 머지)
  ↑
develop   ← 통합 브랜치 (1차 안정 머지 후 직접 작업 금지)
  ↑
feature/* ← 기능별 작업 브랜치 (develop으로 PR)
```

### 브랜치 규칙

| 브랜치 | 용도 | 머지 정책 |
|---|---|---|
| `main` | 발표·배포용 | develop에서만 PR, 최종날·마일스톤 시점 |
| `develop` | 통합 | 1차 PR 전엔 직접 push 허용, **이후엔 feature 브랜치 → PR만** |
| `feature/{name}` | 기능 작업 | develop에서 분기, develop으로 PR |
| `release/{ver}` | 배포 준비 (선택) | main으로 머지 후 develop에도 반영 |
| `hotfix/{name}` | 긴급 수정 (선택) | main·develop 양쪽 |

### 커밋 규칙

**Conventional Commits**:
- `feat:` 새 기능
- `fix:` 버그 수정
- `docs:` 문서
- `refactor:` 리팩터
- `test:` 테스트
- `chore:` 잡일
- `perf:` 성능
- `ci:` CI 설정

### PR 규칙

- 최소 1인 리뷰 + 자동 체크(pre-commit·테스트) 통과
- **`medical-review` 라벨**: 의료 콘텐츠 변경 시 필수
- **`privacy-review` 라벨**: 개인정보 처리 흐름 변경 시 필수
- Squash merge (히스토리 단순화)

## Alternatives Considered

| 후보 | 장점 | 단점 | 기각 사유 |
|---|---|---|---|
| **Trunk-based** | 단순, CI/CD 친화 | 소규모 팀에 과대, 발표 안정성 ↓ | 발표 안정성 우선 |
| **GitHub Flow (main + feature만)** | 간단 | 발표·배포용 분리 X | 안정 버전 보호 필요 |
| **Git Flow (release/hotfix 포함)** | 표준 | 부트캠프 규모에 과대 | release·hotfix는 선택 사용 |
| **단순화 Git Flow** ⭐ | main/develop/feature 3종, 단순·충분 | — | 선택 |

## Consequences

### 좋은 점
- **평가 6-2 만점**: PR 기반 협업 흐름 + Conventional Commits + 라벨 시스템
- main이 항상 시연 가능 상태 유지
- 팀원이 동시 작업해도 충돌 최소
- PR 본문에 변경 의도 명시 → 평가위원이 코드 변화 추적 가능

### 트레이드오프
- 매 작업마다 feature 브랜치 생성 (1차 PR 후) → 초보자에게 학습 부담
- Squash merge로 commit 히스토리 단순화 → 세부 커밋 추적 어려움
- main에 자주 안 머지 → 발표 직전 머지 충돌 가능 (대응: 주기적 develop → main 머지)

### 운영 영향
- 1차 PR (develop → main, v1.0): **2026-06-02 진행 예정**
- 이후 작업: `feature/{name}` 브랜치 → develop PR
- 발표 직전(6/12~6/18) 최종 develop → main 머지

### 적용 시점

- **~ 2026-06-02**: develop 직접 작업 허용 (초기 풀스택 구축 단계)
- **2026-06-02 이후**: 1차 PR 후 **feature 브랜치 강제**
- **2026-06-12**: 배포 권장 마감 (release 머지 시점)
- **2026-06-19**: 발표 마감
