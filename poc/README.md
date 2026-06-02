# Phase 1 PoC — RAG 한 사이클 동작 증명

> **본 폴더의 코드는 "되긴 되네?" 증명용 일회성 PoC.**
> 운영 코드 아님. Phase 2 진입 시 `src/rag_indexing/` + `ai_worker/rag/`로 모듈화 이관 후 폐기.

---

## 목적

[[Team Plan Docs/21_RAG 구축 로드맵 v2.md]] §"Phase 1" 산출물.

우리 결정 스택 ([[project_rag_decision_v1]])이 실제 손에 잡히는지 확인:
- OpenAI `text-embedding-3-small` (1536차원)
- Qdrant in-memory 모드 (Docker 불필요)
- LangChain v1 + `RecursiveCharacterTextSplitter`
- GPT-4o-mini + 안전 가드 시스템 프롬프트

KDIGO 가이드라인 1챕터를 인덱싱해서 "G2 환자 식단?" 같은 질문에 **출처 있는 답변**이 나오는지 확인.

---

## 사전 준비 2건

### 1) OpenAI API 키 발급 ($5~10 충전)

1. https://platform.openai.com → API keys → Create new
2. 키 발급 후 즉시 복사 (한 번만 보임)
3. `.env`에 저장 (아래 설치 단계 참조)

### 2) KDIGO PDF 1챕터 확보

권장 자료: **KDIGO 2024 CKD Evaluation and Management Guideline**

1. https://kdigo.org/guidelines/ckd-evaluation-and-management/ 접속
2. PDF 무료 다운로드 (Member registration 불필요)
3. PoC는 1챕터만 사용 — Chapter 5 "Diet/Lifestyle"(약 50~80페이지) 추출 권장
   - macOS Preview에서 페이지 추출 가능 (Tools → Show Sidebar → 페이지 선택 → 우클릭 Export)
4. `poc/data/kdigo_ch5_diet.pdf` 위치에 저장

> 전체 PDF(250페이지)를 써도 동작은 하지만, 임베딩 비용·시간이 늘어남.
> PoC 단계는 1챕터로 충분.

---

## 설치 및 실행

```bash
cd poc

# 가상환경 분리 (본 프로젝트 .venv와 격리)
uv venv --python 3.13
source .venv/bin/activate

# 의존성 설치
uv pip install -r requirements_poc.txt

# 환경변수 설정
cp .env.example .env
# .env 열어서 OPENAI_API_KEY 채우기

# ─ 실행 옵션 ───────────────────────────────────────────────────
# (1) 기본 질문 1회
python poc_rag.py

# (2) 커스텀 질문 1회
python poc_rag.py "G3a 단계 환자의 운동 권장 강도는?"

# (3) 대화형 모드 — 인덱싱 1회 후 여러 질문 (권장)
python poc_rag.py --repl

# (4) 캐시 무시하고 재인덱싱 (PDF 바꿨을 때)
python poc_rag.py --reindex

# (5) 옵션 조합 — 검색 Top-5 + 대화형 + 재인덱싱
python poc_rag.py --repl --reindex --k 5
```

### 캐싱 동작

첫 실행 후 `qdrant_local/` 폴더에 인덱싱 결과가 영속화됩니다.
이후 실행은 PDF 재로드·임베딩을 **건너뛰고 캐시 사용** (시간·비용 절약).

| 상황 | 동작 |
|---|---|
| 처음 실행 | PDF → 청킹 → 임베딩 → Qdrant 신규 생성 (5~8분, 약 $0.015) |
| 같은 PDF로 재실행 | 캐시 재사용, 인덱싱 스킵 (~1초, $0) |
| **PDF를 바꾼 경우** | `--reindex` 옵션 필수 (캐시 무시) |
| 청크 사이즈를 바꾼 경우 | `--reindex` 옵션 필수 |
| 캐시 통째로 삭제 | `rm -rf qdrant_local/` |

---

## 예상 출력

**첫 실행 (인덱싱 포함)**:
```
[1] PDF 로드: 250 페이지, 487,222자
[2] 청킹 완료: 1,624개 청크 (chunk_size=1000, overlap=200)
[3+4] Qdrant 신규 인덱싱 완료: 1,624개 청크 → ./qdrant_local/

질문: G2 단계 CKD 환자의 단백질 섭취 권장량은?
──────────────────────────────────────────────────────────────────────
[5+6] 검색 완료: Top-3 청크 (질문 길이 30자)
      1. [score=0.512] p.45 — Protein intake recommendations for patients...
      2. [score=0.487] p.46 — The KDIGO work group suggests a target of...
      3. [score=0.451] p.52 — Caloric intake should be sufficient to maintain...
[7] LLM 응답 완료: gpt-4o-mini (1,234 tokens)

══════════════════════════════════════════════════════════════════════
답변
══════════════════════════════════════════════════════════════════════
G2 단계 만성콩팥병(CKD) 환자의 단백질 섭취량에 대해 KDIGO 2024 가이드라인은
하루 0.8 g/kg 체중을 권장합니다 ...

📚 출처: KDIGO 2024 p.45, p.46

ℹ️ 본 정보는 교육·관리 보조 목적의 안내이며, 의학적 진단·처방을 대체하지
않습니다. 정확한 판단은 주치의·신장내과 전문의와 상담하세요.
```

**두 번째 실행 (캐시 사용)**:
```
[3+4] Qdrant 캐시 사용: 1,624개 청크 (재인덱싱 스킵)
      └─ 경로: qdrant_local/

질문: G2 단계 CKD 환자의 단백질 섭취 권장량은?
──────────────────────────────────────────────────────────────────────
[5+6] 검색 완료: Top-3 청크 (...)
[7] LLM 응답 완료: gpt-4o-mini (1,234 tokens)
...
```
→ 인덱싱 5~8분이 ~1초로 단축, 비용은 LLM 호출분만 (~$0.001).

---

## 성공 기준 (6개 모두 통과해야 Phase 2 진입)

| # | 항목 | 통과 기준 | 확인 방법 |
|---|---|---|---|
| 1 | PDF 텍스트 추출 | 1챕터 5,000자 이상 | `[1] PDF 로드: ... N자` 출력 |
| 2 | 청크 생성 | 50개 이상 | `[2] 청킹 완료: N개 청크` 출력 |
| 3 | Top-3 검색 관련성 | 사람 판단 최소 1개 관련 | snippet 육안 확인 |
| 4 | LLM 답변 반영 | 검색 청크 내용 인용 | 답변에 "KDIGO" / "가이드라인" 등장 |
| 5 | 출처 명시 | 답변 말미에 출처 (p.번호) | `📚 출처` 줄 확인 |
| 6 | 무관 질문 한계 인정 | "오늘 점심 메뉴?" → 한계 답변 | `python poc_rag.py "오늘 점심 추천해줘"` 실행 |

### 추가 확인 사항

- [ ] 비용 측정: 1회 실행에 약 $0.001~0.003 (인덱싱 1회 + 질문 1회 기준)
- [ ] 시간 측정: 인덱싱 ~30초 (PDF 크기에 따라), 검색+생성 ~3초
- [ ] 한국어 질문 → 영문 KDIGO 검색 동작 (다국어 임베딩 검증)

---

## 회고 항목 (Phase 2 진입 전 작성)

PoC 실행 후 아래 답을 정리해두면 Phase 3·4 설계가 쉬워짐:

1. **청크 size 1000 / overlap 200**이 KDIGO에 잘 맞았나?
   - 청크가 너무 잘게 나뉘었으면 size↑ / 너무 크면 size↓
   - 예시: 학습카드 02·로드맵 v2 §"청크 설계 결정"에 반영
2. **Top-3 검색이 항상 관련 청크를 가져왔나?**
   - 가끔 무관한 청크가 1위로 오면 → Phase 6 Hybrid Search 도입 우선순위 ↑
3. **답변 품질 — 검색 청크 그대로 인용?** 아니면 LLM이 의역?
   - 의역이 심하면 시스템 프롬프트 강화 (학습카드 05의 금지 표현 추가)
4. **금지 표현 검출되나?** ("치료됩니다", "확진" 등)
   - 후처리 가드 우선순위 검증
5. **비용·시간 실측치는?**
   - 로드맵 v2 §"비용" 추정($0.6/월 1K 질문)과 비교

---

## 코드 구조 (방금 합의된 설명)

### 디렉토리

```
poc/
├─ poc_rag.py                  ← 메인 baseline (229줄, 단일 파일)
├─ experiments/                ← C단계 청킹 비교 실험
│  ├─ exp1_md_chunking.py     (MarkdownHeader 도입 효과)
│  └─ exp2_chunk_size_compare.py (500/1000/1500 비교)
├─ data/
│  ├─ KDIGO-2024-CKD-Guideline.pdf  (199p, 원본)
│  ├─ kdigo_ch3_progression.pdf     (41p, 추출본 — 실제 사용)
│  └─ kdigo_ch3_progression.md      (pymupdf4llm 변환 결과)
├─ qdrant_local/               ← 벡터 인덱스 영속화 (재실행 시 캐시)
├─ requirements_poc.txt        ← LangChain v1 + OpenAI + Qdrant + pypdf
├─ .env / .env.example         ← OPENAI_API_KEY + PDF/Qdrant 경로
├─ .venv/                      ← 본 프로젝트와 격리 (Phase 2에서 흡수)
└─ README.md                   ← 본 문서
```

**격리 원칙**: PoC는 일회성 학습용이라 본 프로젝트 `.venv` / `pyproject.toml`과 완전 분리. Phase 2 진입 시 모듈화 후 폐기 예정.

### `poc_rag.py` — 8단계 일직선 파이프라인

[[project_rag_llm_essence]]의 검색 6가지 + 패턴 4종을 단일 파일로 압축한 구조.

```
[0] 환경 설정     load_dotenv() + 상수 정의 (PDF 경로, 모델, 프롬프트)
 ↓
[1] load_pdf()           PDF → [(텍스트, 페이지), ...]
 ↓
[2] chunk_pages()        RecursiveCharacterTextSplitter (1000/200)
 ↓                       메타: {source, page, chunk_idx}
[3+4] build_vectorstore() OpenAI 임베딩 → Qdrant 로컬 파일 캐시
 ↓                       (캐시 히트 시 인덱싱 스킵)
[5+6] retrieve()         질문 벡터화 → similarity_search_with_score(k=3)
 ↓
[7] generate_answer()    SYSTEM_PROMPT + Top-K 컨텍스트 → gpt-4o-mini
 ↓
[8] ask_once / repl()    1회 / 대화형 진입점
```

### 핵심 설계 결정

| 함수 | 결정 | Why |
|---|---|---|
| `load_pdf` | `pypdf` 사용 | baseline. 실험 1에서 `pymupdf4llm`(헤더 보존) 비교 |
| `chunk_pages` | `RecursiveCharacterTextSplitter` 단독 | baseline. 실험 1에서 `MarkdownHeader` 도입 결정적 효과 입증 |
| `build_vectorstore` | Qdrant in-memory (파일 경로) | Docker 불필요. `QdrantClient(path=...)`로 로컬 영속화 |
| `retrieve` | `similarity_search_with_score` | score 노출 → 무관 질문(0.18)/관련 질문(0.6) 한계 판별 |
| `generate_answer` | `gpt-4o-mini` + temp 0.3 | 개발 정책 ([[project_api_model_policy]]) |
| `SYSTEM_PROMPT` | 6가지 규칙 | 규칙 3번이 발견 #2의 원인 — Phase 4에서 삭제 의무 |

### 캐싱 메커니즘

```python
existing = {c.name for c in client.get_collections().collections}
if COLLECTION in existing and not reindex:
    return ... # 인덱싱 스킵 (~1초)
```

- 첫 실행: PDF→청킹→임베딩→Qdrant (5~8분, ~$0.015)
- 재실행: 캐시 재사용 (~1초, $0)
- `--reindex` 플래그로 강제 재구축

### `experiments/` — C단계 청킹 비교

PoC 회고 발견 #2를 본질 검증한 두 실험:

**`exp1_md_chunking.py`**
- 가설: PDF→Markdown 변환 + 헤더 인식 청킹이 baseline보다 정확할 것
- 구현: `pymupdf4llm.to_markdown()` → `MarkdownHeaderTextSplitter` → `RecursiveCharacterTextSplitter`
- payload: `header_1/2/3` 추가
- 결과: G2 질문 답변이 절충("G2도 고려 가능") → 정확("G3-G5 대상, G2 명시 없음")으로 전환 ✅

**`exp2_chunk_size_compare.py`**
- 가설: chunk_size 튜닝(500/1000/1500)이 답변 품질 좌우할 것
- 구현: 같은 PDF·임베딩·검색 조건에서 3개 collection 생성 후 같은 질문
- 결과: 3배 차이에도 답변 품질 결정적 변화 X → "튜닝의 핵심은 글자 수가 아니라 구조 인식" ❌

### PoC의 본질적 가치

1. **"되긴 되네?" 증명 → 그 다음 질문으로 진행**: 6/6 통과로 동작 확인 후, 진짜 가치는 발견 5가지 ([[project_phase1_poc_retrospective]])
2. **운영 코드와 분리**: 단일 파일·예외처리 최소·모듈화 의도적 회피 → Phase 2에서 `src/rag_indexing/` + `ai_worker/rag/`로 이관 후 폐기
3. **청킹 실험의 기준점**: `qdrant_local/` 캐시 4개(baseline·md·cs500/1000/1500)가 Phase 3 비교 baseline 역할

---

## 한계 (의식적 단순화)

PoC는 다음을 의도적으로 안 함 (Phase 3~5에서 해결):

- ❌ 한 줄짜리 검색 도구 (`@tool(response_format="content_and_artifact")` 패턴)
- ❌ ReAct 에이전트 (`create_agent`) — PoC는 단순 체인
- ❌ 미들웨어 (`ModelCallLimitMiddleware`·`ToolRetryMiddleware`)
- ❌ Langfuse 추적
- ❌ Safety Guard 4단계 파이프라인 (응급·자해·약물 별도 패턴)
- ❌ payload 풍부한 메타필터 (`stage`·`section`)
- ❌ Qdrant Docker (로컬 파일 캐시 모드 사용 — `path=./qdrant_local`)
- ❌ 인덱싱·추론 폴더 분리

→ 모두 [[Team Plan Docs/21_RAG 구축 로드맵 v2.md]]의 Phase 2~6에서 단계적 도입.

---

## 다음 단계

PoC 6개 성공 기준 통과 시:
1. 본 README에 회고 5개 항목 작성
2. 로드맵 v2 §"Phase 1" 체크박스 갱신
3. `project_rag_roadmap` 메모리 갱신 (Phase 1 ✅ + 실측치)
4. Phase 2 진입 — `docker-compose.yml` 7컨테이너 확장

---

## 관련 자료

- 로드맵: `../Team Plan Docs/21_RAG 구축 로드맵 v2.md` §Phase 1
- 학습카드: `../Team Plan Docs/20_RAG 학습카드/01_openai_api.md` · `02_qdrant_essentials.md`
- 노트북 참조:
  - `~/workspaces/langchain-langgraph-deepagents-notebooks/02_langchain/09_custom_workflow_and_rag.ipynb`
  - `~/workspaces/langchain-langgraph-deepagents-notebooks/07_examples/01_rag_agent.ipynb`
  - `~/workspaces/langchain-langgraph-deepagents-notebooks/08_integration/03_vectorstores/05_qdrant.ipynb`
