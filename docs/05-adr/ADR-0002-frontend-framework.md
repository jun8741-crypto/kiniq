# ADR-0002: 프론트 프레임워크 — Vite + React 19 + TypeScript

**Date**: 2026-05-19
**Status**: ✅ Accepted

## Context

프론트엔드 구현 도구를 선정해야 한다. 주요 요구사항:

- 부트캠프 안내: **"바이브 코딩 방식"** (AI 페어 코딩 친화적)
- **타입 안전성** — 의료 정보 다루기 때문에 런타임 에러 최소화
- **빠른 핫리로드** — 부트캠프 일정상 빈번한 시연·반복
- **TanStack Query 같은 검증된 캐싱 라이브러리** 사용 (평가 5-1 P95 충족)
- **고령 사용자 비율 고려** — 가벼운 번들, 접근성

## Decision

**Vite + React 19 + TypeScript + Tailwind CSS v4 + TanStack Query** 선정.

- 빌드 도구: **Vite 6**
- UI 프레임워크: **React 19** (Concurrent features)
- 타입: **TypeScript 5** (strict mode)
- 스타일: **Tailwind CSS v4** (`@import "tailwindcss"`, 새 엔진)
- 상태/캐시: **@tanstack/react-query 5** (서버 상태)
- 라우팅: **react-router-dom 7**
- 아이콘: **lucide-react**

## Alternatives Considered

| 후보 | 장점 | 단점 | 기각 사유 |
|---|---|---|---|
| **Next.js 15 (App Router)** | SSR·SEO·풀스택 | 백엔드 분리 구조와 중복, 학습 비용 | 백엔드는 FastAPI로 분리 |
| **Nuxt 3 (Vue)** | Composition API 깔끔 | React 대비 채용 풀 작음 | AI 페어 코딩 React 답변 더 많음 |
| Svelte/SvelteKit | 가장 빠름, 코드량 적음 | 커뮤니티 작음, 의료 도메인 사례 적음 | 부트캠프 멘토 풀 |
| **CRA (Create React App)** | 가장 보수적 | Deprecated (2023), 느림 | 공식 deprecated |
| **Vite + React** ⭐ | 가장 빠른 dev 서버, React 19 호환, AI 페어 친화 | — | 선택 |

상태 관리:
- **Redux/Zustand**: 클라이언트 상태에 좋음. 하지만 우리는 90% 서버 상태 → 과대
- **TanStack Query** ⭐: 서버 상태 캐싱·재검증 표준, REQ-DASH-004(클라이언트 캐싱) 직접 충족

스타일:
- **Styled Components / Emotion**: 런타임 비용
- **Tailwind v4** ⭐: 빌드 타임, 일관 디자인 시스템, 짧은 코드

## Consequences

### 좋은 점
- Vite HMR(<100ms) → 시연 시 반복 빠름
- React 19 + TanStack Query → 평가 5-1 P95 18ms 달성 (목표 3,000ms의 0.6%)
- TypeScript strict → 의료 데이터 타입 오류 컴파일 차단
- Tailwind v4 → 모든 페이지 디자인 일관 (평가 4-2)
- DisclaimerFooter·CharacterImage·BackgroundImage 등 **공통 컴포넌트 fallback 패턴** 확립

### 트레이드오프
- React 19는 출시 직후라 일부 라이브러리 호환 이슈 가능 (현재 발생 X)
- Tailwind v4는 v3 대비 문서 적음 → 일부 클래스 직접 시험
- SSR 없음 → SEO 약함 (의료 정보 검색 노출 X, 발표용 데모 서비스라 무관)

### 운영 영향
- 빌드: `npm run build` → `dist/` (Vite 기본)
- 배포: nginx 정적 서빙 (`infra/nginx/`)
- 번들 크기: ~500KB gzip (gzip 후 충분히 가벼움)
