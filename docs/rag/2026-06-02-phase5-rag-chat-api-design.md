# Phase 5 — RAG 챗봇 API 통합 설계 (스펙)

> **작성일**: 2026-06-02 · **브랜치**: `feat/RAG` · **담당**: 주니(RAG 트랙)
> **선행**: Phase 0~4 + LLM 폴백 완료 (`ai_worker/rag/`, `from ai_worker.rag import run`)
> **목표**: 완성된 RAG 추론 파이프라인을 백엔드 API로 노출 — 사용자가 챗봇에 질문하고 답변을 받는다.

---

## 1. 개요

만성콩팥병(CKD) 환자용 RAG 챗봇을 백엔드에 통합한다. 사용자가 `POST /api/v1/chat/messages`로 질문하면,
백엔드가 사용자 의료 컨텍스트를 붙여 Redis Stream으로 ai_worker에 작업을 넘기고, worker가 RAG를 실행해
답변을 돌려주면 백엔드가 한 번에 응답한다.

### 확정된 핵심 결정
| 결정 | 선택 | 이유 |
|---|---|---|
| 응답 표시 | **통째 표시** (토큰 스트리밍 X) | `run()`이 `invoke` 일괄 반환 + 의료 가드가 사후 전체검사라 스트리밍 시 가드 우회 위험 |
| 실행 분배 | **Redis Stream + ai_worker** | 백엔드↔AI 작업 분리, worker 수평 확장 대비 |
| 응답 수신 | **일반 HTTP 동기 응답** | 통째 표시라 SSE/폴링 불필요, 클라 구현 단순 |
| 영속화 | **단발 Q&A** (`ChatMessage`) | `run()`이 단일 질문만 받고 멀티턴 히스토리 인터페이스 없음 |
| worker 구조 | **`rag_task.py` 분리** | 모듈화 원칙 (consumer 루프와 핸들러 책임 분리) |

---

## 2. 아키텍처 · 데이터 흐름

```
[클라이언트]
   │  POST /api/v1/chat/messages   { "question": "..." }
   ▼
[chat_router]  ─ get_request_user (JWT 인증, 기존 의존성 재사용)
   │
   ▼
[ChatService]
   1. 최신 HealthCheck 조회 → user_context = {eGFR, risk_group}   (없으면 {} → RAG "단계 미상" 안전 분기)
   2. job_id = uuid 발급
   3. ChatMessage(role="user", content=question) 저장
   4. Redis  XADD "rag_jobs"  { job_id, question, user_context }
   5. Redis  XREAD "rag_resp:{job_id}"  블로킹 대기 (timeout 60s)
   ▼
[Redis Stream "rag_jobs"]   ← 백엔드와 worker의 유일한 접점
   ▼
[ai_worker/main.py  consumer]
   XREADGROUP "rag_jobs" → rag_task.handle(payload)
   ▼
[ai_worker/tasks/rag_task.py]
   answer = asyncio.to_thread(run, question, user_context)   ← run()은 동기·블로킹이라 오프로딩
   XADD "rag_resp:{job_id}"  { answer }   (실패 시 { error })
   ▼
[ChatService]  resp 수신
   6. ChatMessage(role="assistant", content=answer) 저장
   7. HTTP 200  { answer, created_at }
   ▼
[클라이언트] 로딩 스피너 → 답변 통째 표시
```

**설계 의도**
- **통째 표시**: `answer`는 완성된 답변 1건. 의료 안전 가드(`post_guard`)가 *전체 답변*에 적용된 뒤 전송되어 가드 우회 위험이 없다.
- **user_context는 app(ChatService)에서 빌드**: ai_worker는 app DB에 접근하지 못하므로(컨테이너 볼륨 미마운트), 의료 컨텍스트를 페이로드로 실어 보낸다.
- **job_id별 응답 채널** `rag_resp:{job_id}`: 동시 사용자 응답 격리.

---

## 3. 파일 구조

### 신규 — chat 슬라이스 (app, 수직 슬라이스 패턴)
| 파일 | 책임 (SRP) |
|---|---|
| `app/models/chat.py` | `ChatMessage` ORM — `user_id(FK)·role(user/assistant)·content·created_at` |
| `app/dtos/chat.py` | `ChatMessageCreateRequest{question}` · `ChatMessageResponse{answer, created_at}` |
| `app/repositories/chat_repository.py` | `ChatMessage` 저장·조회 |
| `app/services/chat.py` | user_context 빌드 → Redis XADD → XREAD 대기 → 답변 반환 → DB 저장 |
| `app/apis/v1/chat_routers.py` | `POST /chat/messages` (`get_request_user` 의존성) |

### 신규 — Redis 인프라 & worker
| 파일 | 책임 |
|---|---|
| `app/core/redis_client.py` | `redis.asyncio` 커넥션 (producer + 응답 대기) |
| `ai_worker/core/redis_client.py` | worker 커넥션 (consumer + 결과 전송) |
| `ai_worker/main.py` | consumer 루프 — `XREADGROUP "rag_jobs"` → `rag_task` 디스패치 (얇게) |
| `ai_worker/tasks/rag_task.py` | 핸들러 — `asyncio.to_thread(run, q, ctx)` → `XADD "rag_resp:{job_id}"` |
| `ai_worker/schemas/chat.py` | Stream 페이로드 스키마 — `{job_id, question, user_context}` / `{answer, error}` |

### 수정 (기존 파일)
| 파일 | 변경 |
|---|---|
| `app/apis/v1/__init__.py` | `chat_router` 등록 |
| `app/core/db/databases.py` | `TORTOISE_APP_MODELS`에 `app.models.chat` 추가 |
| `app/core/db/migrations/` | `ChatMessage` aerich 마이그레이션 신규 |
| `app/core/config.py` | `REDIS_HOST·REDIS_PORT·RAG_JOBS_STREAM·RAG_RESP_PREFIX·RAG_TIMEOUT_SEC` |
| `envs/.local.env`·`example.local.env` | `REDIS_HOST=redis`·`REDIS_PORT=6379` |
| `ai_worker/Dockerfile` | `CMD` → `python -m ai_worker.main` |
| `docker-compose.yml` | `ai-worker` 서비스 `command` 확인 |

---

## 4. 인터페이스 계약

### RAG 진입점 (변경 없음 — 재사용)
```python
from ai_worker.rag import run
answer: str = run(question: str, user_context: dict | None)   # 완성 답변 문자열 (가드 적용 완료)
# user_context 소비 키: eGFR(float), risk_group(str) — 둘 다 선택, 없으면 안전 분기
```

### Redis Stream 페이로드
```
rag_jobs            (요청)  { "job_id": uuid, "question": str, "user_context": {eGFR, risk_group} }
rag_resp:{job_id}   (응답)  { "answer": str }  또는  { "error": str }
```

### REST API
```
POST /api/v1/chat/messages   (인증 필요)
  요청   { "question": "만성콩팥병 환자 단백질 권장량은?" }
  응답   200 { "answer": "...", "created_at": "..." }
        504 (worker 타임아웃) / 500 (run 예외) / 503 (Redis 불가)
```

### user_context 빌드 규칙
```python
hc = 최신 HealthCheck(user_id)        # challenge_routers 패턴: order_by("-checked_date").first()
user_context = {"eGFR": hc.egfr_estimated, "risk_group": hc.ckd_stage} if hc else {}
```

---

## 5. 에러 처리 · 안전 · 동시성

| 상황 | 처리 |
|---|---|
| worker 응답 지연 | `XREAD` 블로킹 timeout **60초** → `504` "잠시 후 다시 시도" |
| `run()` 내부 예외 | worker가 `{error}` 전송 → 백엔드 `500` + 안내 (스택 비노출) |
| Redis 연결 실패 | `503` |
| 검진 없음 (user_context `{}`) | 정상 — RAG "단계 미상" 안전 분기 |
| 응급·자해·금지표현 | **RAG `run()` 가드가 이미 처리**(119·1393·차단) → 백엔드 그대로 전달, 추가 가공 금지 |

- **동시성**: `rag_resp:{job_id}` 채널로 사용자별 응답 격리. `XREADGROUP` consumer group으로 worker 다중화 시 중복 방지 + ACK.
- **이벤트 루프**: 백엔드는 `redis.asyncio`(비동기)로 대기해 워커를 막지 않음. worker는 `run()`을 `asyncio.to_thread`로 오프로딩.

---

## 6. 테스트 전략

기존 `app/tests` 패턴(PostgreSQL 통합 + fixture) 준수. 외부 의존은 mock.

| 대상 | 검증 | 도구 |
|---|---|---|
| `ChatService` | user_context 빌드 · XADD · XREAD 대기 · DB 저장 | fakeredis + run mock |
| `chat_router` | 인증 + POST → 응답 | 통합 + run mock |
| `rag_task` | XREAD → run → XADD resp | fakeredis + run mock |
| 안전 전달 | run mock "1393 안내" 반환 시 그대로 전달 | mock |
| 타임아웃 | resp 없을 때 504 | fakeredis |

---

## 7. 범위 밖 (YAGNI — 향후 확장)

- **멀티턴 대화**: `run()`이 단일 질문만 받음. `Conversation` 묶음·히스토리 주입은 RAG 인터페이스 확장 후.
- **토큰 스트리밍(SSE)**: 통째 표시로 충분. 타이핑 효과가 필요하면 RAG `astream` + 가드 재설계 후.
- **slowapi Redis 백엔드 전환**: 현재 인메모리. 다중 인스턴스 필요 시.
- **출처 메타데이터 구조화 응답**: 현재 `run()`이 문자열에 출처 포함. 별도 필드가 필요하면 `run()` 반환 확장.

---

## 8. 참고

- 백엔드 통합 분석 출처: `260602_백엔드_코드점검_리포트.md` (RAG 통합 §)
- RAG 파이프라인: `src/rag_indexing/README.md`, `ai_worker/rag/`
- 기존 API 스펙의 `/rag/chat`(P2, `api-spec-v0.8.md:851`)와 경로 상이 → 본 스펙 `/chat/messages` 로 통일 (스펙 문서 갱신 필요)
