# 폴더 구조 가이드 v1.27 (2026-05-18)

> **목적**: 우리 프로젝트 폴더가 어떻게 생겼고, 새 기능을 만들 때 **어디에 어떤 파일을 어떤 패턴으로 만들지** 한 번에 파악
> **버전 근거**: 요구사항 정의서 v0.7 + AI_HealthCare_Final_Project_Template

---

## 0. TL;DR — 한 줄 요약

- 컨테이너 7개(nginx · postgres · redis · fastapi · ai-worker · qdrant · langfuse) 중 **우리가 코드를 쓰는 곳은 fastapi와 ai-worker 둘뿐**
- 새 기능 하나 = `app/` 안의 **6파일 세트** (dtos → models → repositories → services → apis/v1 → tests)
- 도메인 7개 × 6파일 + ai_worker 8개 + src/ckd 신규 8개 ≈ **신규 작성 58개**
- DB는 **PostgreSQL** (이전 MySQL에서 변경, v0.7), ORM은 **Tortoise**, 비밀번호는 **bcrypt**

---

## 1. 큰 그림 — 7컨테이너 아키텍처

`docker-compose.yml`에 정의된 실행 단위 7개 (v1.27 RAG 도입으로 5 → 7):

```
                         ┌──────────────┐
사용자 ──────► nginx ─────►│  fastapi     │ ─── PostgreSQL (사용자·검진·결과·langfuse)
            (리버스        │  (app/)      │ ─── Redis     (큐 push)
            프록시)        └──────┬───────┘
                                │ Redis Stream
                                ▼
                          ┌──────────────┐
                          │  ai-worker   │ ─── Model 1·2 추론 + LLM·RAG
                          │ (ai_worker/) │ ─── Qdrant   (벡터 검색)
                          └──────────────┘ ─── Langfuse (LLM 트레이싱·PII 마스킹)
```

| # | 컨테이너 | 역할 | 코드 위치 |
|---|---|---|---|
| 1 | `nginx` | 리버스 프록시, 정적 파일 | `infra/nginx/` (설정만) |
| 2 | `postgres` | DB (앱 + Langfuse) | (이미지만, 코드 0줄) |
| 3 | `redis` | 메시지 브로커·캐시 | (이미지만, 코드 0줄) |
| 4 | `fastapi` | API 서버 | **`app/`** ⭐ |
| 5 | `ai-worker` | 무거운 AI 추론 (Model 1·2·LLM·RAG) | **`ai_worker/`** ⭐ |
| 6 | `qdrant` 🆕 | **벡터 DB** (RAG 검색, KDIGO·한국 신장학회 인덱싱) | (이미지만) |
| 7 | `langfuse` 🆕 | **LLM 관찰성·트레이싱**, PII 마스킹 (REQ-RAG-003) | (이미지만, PostgreSQL 공유) |

---

## 2. 전체 폴더 트리

```
project/                             ← 프로젝트 루트
│
├─ app/                              ← 🟢 [코드 작성] FastAPI 컨테이너
│  ├─ apis/v1/                       ← URL 라우터 (URL → 함수)
│  ├─ services/                      ← 비즈니스 로직
│  ├─ repositories/                  ← DB CRUD
│  ├─ models/                        ← Tortoise ORM 테이블 정의
│  ├─ dtos/                          ← 요청/응답 Pydantic schema
│  ├─ dependencies/                  ← FastAPI Depends 주입
│  ├─ core/                          ← 공통 (config·JWT·db·utils·logger)
│  ├─ tests/                         ← pytest 단위·통합 테스트
│  ├─ main.py                        ← FastAPI 진입점
│  └─ Dockerfile
│
├─ ai_worker/                        ← 🟢 [코드 작성] AI Worker 컨테이너
│  ├─ tasks/                         ← Redis Stream consumer 작업들
│  │  ├─ model1_task.py · model2_task.py
│  │  ├─ llm_explain_task.py         ← REQ-LLM-001 (RAG 활용)
│  │  └─ rag_chat_task.py            🆕 REQ-RAG-004 (챗봇)
│  ├─ rag/                           🆕 RAG 전용 모듈 (v1.27)
│  │  ├─ retriever.py · embedder.py · llm_client.py
│  │  ├─ prompt_builder.py · safety_guard.py
│  │  └─ chains.py                   ← LangChain 파이프라인
│  ├─ schemas/                       ← Worker 입출력 DTO (model_io·llm_io·rag_io)
│  ├─ core/                          ← model_loader + 🆕 qdrant·openai·langfuse client
│  ├─ main.py
│  └─ Dockerfile
│
├─ src/                              ← 🟢 [코드 작성] 학습·인덱싱 라이브러리
│  ├─ ckd/                           ← ML 학습 (노트북·ai_worker에서 import)
│  │  ├─ config.py / labels.py / simulate.py / challenges.py  (이미 있음)
│  │  ├─ preprocess.py / features.py / cv.py / metrics.py     (신규)
│  │  ├─ train.py / predict.py / seed.py / risk_score.py      (신규)
│  │  └─ data/challenges_v04.json
│  └─ rag_indexing/                  🆕 RAG 인덱싱 파이프라인 (v1.27)
│     ├─ config.py · chunking.py · embedder.py
│     ├─ qdrant_uploader.py · pii_masker.py
│     ├─ sources/                    ← ingest_kdigo.py · ingest_knsn.py · ingest_pubmed.py
│     └─ data/                       ← kdigo·knsn·pubmed PDF 보관
│
├─ data_pipeline/                    ← 🟡 [1회성 스크립트] 데이터 마트 빌드
│  └─ build_knhanes_unified.py       ← v3 (완료, 추가 없음)
│
├─ data/                             ← 🟡 [데이터 산출물] 코드 아님
│  └─ KNHANES/analytic/master_wide_v3.parquet
│
├─ infra/                            ← 🟡 [설정 파일] 거의 수정 X
│  ├─ docker/docker-compose.prod.yml
│  └─ nginx/{default,prod_http,prod_https}.conf
│
├─ scripts/                          ← 🟡 [CI 셸 스크립트]
│  ├─ ci/{check_mypy,code_fommatting,run_test}.sh
│  ├─ certbot.sh
│  └─ deployment.sh
│
├─ envs/                             ← 🔴 [비밀] .env 파일 (Git 제외)
│  ├─ .local.env / .prod.env
│  └─ example.local.env / example.prod.env
│
├─ frontend/                         ← 🟢 [예정] Vite + React + Recharts
│
├─ docs/                             ← 📄 프로젝트 문서
│  └─ folder-structure-guide.md      ← 이 파일
│
├─ docker-compose.yml                ← 7 컨테이너 정의 (v1.27: qdrant·langfuse 추가)
├─ pyproject.toml                    ← Python 의존성 (uv) + 🆕 RAG: openai·qdrant-client·langchain·langfuse·pypdf
├─ uv.lock
└─ README.md
```

---

## 3. `app/` 안의 3계층 패턴 — 가장 중요

새 기능 하나를 만들 때 **항상 같은 6단계 파일 세트**를 만듭니다.

```
요청 URL ───► apis/v1/        ← 라우터 (URL → 함수 매핑, 얇은 layer)
              │
              ▼
              services/        ← 비즈니스 로직 (도메인 규칙·계산)
              │
              ▼
              repositories/    ← DB 접근 (Tortoise ORM 쿼리)
              │
              ▼
              models/          ← DB 테이블 정의
dtos/        ← 요청/응답 Pydantic schema ("API 계약서")
dependencies/← FastAPI Depends 주입 (현재 user, db session)
core/        ← 공통 (config·JWT·DB 연결·logger·utils)
tests/       ← pytest
```

### 왜 분리하는가? (Service Layer Pattern)

| 만약 모든 코드를 라우터 한 파일에 다 넣으면 | 6파일로 분리하면 |
|---|---|
| 100줄 함수 → 가독성 ↓ | 각 파일 30~50줄로 한 가지 책임만 |
| DB 쿼리·검증·응답 변환 다 섞임 | 변경 사유가 같은 코드끼리 모임 |
| 테스트 어려움 | services만 단위 테스트 쉬움 |
| 같은 비즈니스 로직 여러 라우터에 복붙 | services 한 곳에서 import |

---

## 4. 도메인 한 개 = 6파일 세트 (예시: 검진 결과)

```python
# 1) dtos/health_check.py  ← 먼저! API 계약을 정한다
class HealthCheckUploadRequest(BaseModel):
    file_id: str
class HealthCheckResponse(BaseModel):
    id: int
    parsed_values: dict
    confidence: float

# 2) models/health_check.py  ← DB 테이블 정의
class HealthCheck(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User")
    image_url = fields.CharField(max_length=500)
    parsed_values = fields.JSONField()
    created_at = fields.DatetimeField(auto_now_add=True)

# 3) repositories/health_check_repository.py  ← DB CRUD만
async def create(user_id: int, data: dict) -> HealthCheck:
    return await HealthCheck.create(user_id=user_id, parsed_values=data)
async def get_by_user(user_id: int) -> list[HealthCheck]:
    return await HealthCheck.filter(user_id=user_id).all()

# 4) services/health_check.py  ← 비즈니스 로직 (OCR 호출·검증·Worker 큐)
async def upload_and_parse(user_id: int, file: UploadFile) -> HealthCheck:
    parsed = await ocr_service.parse(file)
    validate_medical_ranges(parsed)
    health_check = await repo.create(user_id, parsed)
    await redis.xadd("predict_stream", {"hc_id": health_check.id})
    return health_check

# 5) apis/v1/health_check_routers.py  ← URL 매핑
router = APIRouter(prefix="/health-checks")
@router.post("", response_model=HealthCheckResponse)
async def upload(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
):
    return await service.upload_and_parse(current_user.id, file)

# 6) tests/health_check_apis/test_upload.py
async def test_upload_success(client, auth_header):
    response = await client.post("/api/v1/health-checks", ...)
    assert response.status_code == 201
```

→ **이 6파일이 한 도메인의 단위.** 한 도메인 작성 = 한 PR.

---

## 5. 우리가 만들 도메인 매핑 (v0.7 기준)

| # | 도메인 | v0.7 ID | dtos | models | repositories | services | apis | tests | 비고 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **회원관리** | REQ-AUTH (9건) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 템플릿에 이미 골격 있음 |
| 2 | **검진 결과** | REQ-DATA-001~005 (5건) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | OCR 트리거 포함 |
| 3 | **생활습관 설문** | REQ-DATA-006~007 (2건) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 식이 4문항 LLM 전용 |
| 4 | **예측 (Model 1+2)** | REQ-ML (8건) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Worker 큐 push |
| 5 | **대시보드** | REQ-DASH (4건) | ✅ | ⎯ | ⎯ | ✅ | ✅ | ✅ | 7개 차트 데이터 |
| 6 | **챌린지** | REQ-CHAL (9건) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | A/B 트랙·알 부화 포함 |
| 7 | **알림** | REQ-NOTI (6건) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | P1 핵심 + P2 부가 |
| 8 | **챗봇 RAG** | REQ-RAG (5건, P2) | ✅ | ⎯ | ⎯ | ✅ | ✅ | ✅ | Qdrant+OpenAI+LangChain+Langfuse |
| 9 | **LLM 행동 추천** | REQ-LLM (4건, P1) | ✅ | ⎯ | ⎯ | ✅ | ⎯ | ✅ | services만, 라우터는 #5에 흡수 |
| 10 | **OCR 서비스** | REQ-DATA-002~004 | ✅ | ⎯ | ⎯ | ✅ | ⎯ | ✅ | services만, 라우터는 #2에 흡수 |

**추가 모델 (도메인엔 안 잡히지만 필요)**:
- `user_consent` — REQ-AUTH-004 민감정보 동의 이력 (개인정보보호법 §23)
- `audit_log` — REQ-SEC-006 접근 감사 로그

---

## 6. `app/` 폴더 상세 가이드 — 8개 하위 폴더 책임

```
app/
├─ main.py              ← FastAPI 진입점 (거의 안 만짐)
├─ apis/v1/             ← 1. 라우터 (URL → 함수)
├─ services/            ← 2. 비즈니스 로직
├─ repositories/        ← 3. DB 쿼리
├─ models/              ← 4. DB 테이블 정의 (Tortoise)
├─ dtos/                ← 5. 요청/응답 schema (Pydantic)
├─ dependencies/        ← 6. Depends 주입 (인증 등)
├─ core/                ← 7. 공통 인프라 (config·jwt·db·utils·validators·logger)
└─ tests/               ← 8. pytest 테스트
```

### 각 폴더 한 줄 요약

| 폴더 | 책임 한 줄 | 자주 손대는가 |
|---|---|---|
| `main.py` | FastAPI 인스턴스 생성 + 라우터 등록 | ❌ 거의 안 만짐 |
| `apis/v1/` | HTTP URL → 함수 매핑 (얇은 layer) | ✅ 새 도메인마다 |
| `services/` | 도메인 규칙·검증·외부 API 호출·트랜잭션 | ✅ 새 도메인마다 |
| `repositories/` | 한 model에 대한 CRUD 함수 모음 (비즈니스 룰 없음) | ✅ 새 model마다 |
| `models/` | DB 테이블 정의 (Tortoise Model 클래스) | ✅ 새 도메인마다 |
| `dtos/` | API 입출력 schema (타입·검증·자동 문서화) | ✅ 새 API마다 |
| `dependencies/` | 라우터 자동 주입 함수 (인증된 user 등) | 🟡 공통 패턴 등장 시 |
| `core/` | 도메인 무관 공통 인프라 (설정·DB·JWT·utils) | ❌ 초기 셋업 후 안정 |
| `tests/` | 단위 + API 통합 테스트 | ✅ 새 도메인마다 |

---

## 7. 한 도메인 개발 표준 워크플로우

1. **dtos 먼저** — 요청·응답 schema를 정한다 = API 계약
2. **models** — DB 테이블 정의
3. **aerich migrate** — 마이그레이션 생성·적용
4. **repositories** — CRUD 함수 작성
5. **services** — 비즈니스 로직 (외부 호출·검증)
6. **apis/v1** — 라우터 + dependencies
7. **tests** — 단위 + API 테스트
8. **린트·포맷**: `ruff check . && ruff format .`
9. **타입 체크**: `mypy app/`
10. **테스트**: `pytest`
11. **PR 생성** — develop으로 머지

---

## 8. `ai_worker/` 구조

### src/ckd vs ai_worker — 학습 vs 추론 분리

| 항목 | `src/ckd/` (학습) | `ai_worker/` (추론) |
|---|---|---|
| **목적** | 모델 만들기 | 만든 모델 사용 |
| **사용자** | 데이터 사이언티스트 | 운영 (FastAPI가 큐 push) |
| **실행 시점** | 노트북·CLI에서 1회성 실험 | 컨테이너로 24/7 실행 |
| **트리거** | 사람이 직접 | Redis Stream 자동 |

> `src/ckd/` = **요리 학원** (레시피 개발)
> `ai_worker/` = **레스토랑 주방** (검증된 레시피로 손님 음식)

### Redis Stream 흐름 (예: 예측)

```
1. fastapi: services/prediction.py
       └─ redis.xadd("predict_stream", {"user_id": 123, "hc_id": 456})
2. ai-worker: main.py (XREADGROUP, blocking)
       └─ tasks/model1_task.py (그룹 배정)
       └─ tasks/model2_task.py (SHAP)
       └─ redis.publish("result:user:123", json)
3. fastapi: SSE 스트림 → 사용자 화면
```

---

## 9. 인프라 변경 사항 (v0.7)

- **DB**: MySQL → **PostgreSQL 16**
- **ORM**: asyncmy → **asyncpg**
- **비밀번호**: bcrypt (passlib 1.7+)
- **JWT**: Access 15분 / Refresh 7일
- **신규**: Qdrant (벡터 DB) + Langfuse (LLM 관찰성)

### 환경변수 추가 (envs/.local.env)

```bash
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_LLM_MODEL=gpt-4o-mini
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=medical_kb
LANGFUSE_HOST=http://langfuse:3000
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
```

---

## 10. 알려진 함정 (Gotchas)

- **포트 충돌**: FastAPI는 8001로 실행 (`uvicorn main:app --reload --port 8001`)
- **bcrypt 버전**: `bcrypt==4.0.1` 고정 (최신 버전과 passlib 충돌)
- **zsh 대괄호**: `pip install "python-jose[cryptography]"` (따옴표 필수)
- **G4~G5 안전 분기**: 해당 CKD 단계 챌린지 노출 금지 (구현 전까지)
- **SHAP 수치**: 사용자에게 직접 노출 금지 → 행동 언어로 변환 후 표시
- **의료광고법**: "막을 수 있다"·"예방됩니다"·"확진" 금지
