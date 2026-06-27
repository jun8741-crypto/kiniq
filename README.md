# 🩺 KiniQ — 만성콩팥병(CKD) 생활습관 관리 웹서비스

> 건강검진 결과로 CKD(만성콩팥병) 위험을 예측하고, 맞춤형 생활습관 챌린지와 RAG 챗봇으로 행동 변화를 돕는 AI 헬스케어 웹서비스
>
> **오즈코딩 헬스케어AI 3기 기업연계 최종 프로젝트 (Talos)** · 주강사 **"상용 서비스 수준"** 평가

| 역할 | 맥락 | 기간 | 성과 |
|---|---|---|---|
| **팀장 (4인)** · RAG·풀스택·CI/CD | 오즈코딩 헬스케어AI 3기 기업연계 (Talos) | 2026.05 ~ 06 | 주강사 '상용 수준' 평가 · 부하테스트 P95 **15ms**(동시 50명·실패율 0%) |

> 📄 발표자료(결과보고서): [presentation.pdf](./presentation.pdf)

---

## TL;DR

- 건강검진 데이터로 **CKD 위험을 예측**하고, 위험군을 그룹(G1~G4)으로 나눠 **맞춤 생활습관 챌린지 + RAG 의료 상담 챗봇**으로 연결한 풀스택 AI 헬스케어 웹앱 (4인 팀, **팀장**).
- **내 핵심 기여 3가지**
  1. **LangGraph 기반 Self-corrective RAG 챗봇** 설계·구현 (Grader·Rewrite·Hallucination 검증 + 의료 가드레일 이중 안전장치)
  2. **FastAPI · Redis Stream 비동기 아키텍처**(컨테이너 분리) · **SSE 토큰 스트리밍**
  3. **풀스택**(React 대시보드) · **Docker · CI/CD** 배포 총괄
- **ML 예측 모델**(CKD AUROC 0.906, KNHANES 국가통계 학습)은 **팀원이 담당** — 나는 그 추론 결과를 서비스·RAG·인프라로 엮어 상용 수준으로 완성.
- 결과: **주강사 "상용 서비스 수준" 평가** · 부하테스트 P95 15ms.

---

## 1. 문제 (Problem)

만성콩팥병(CKD)은 **초기 자각 증상이 거의 없어** 상당수가 늦게 발견됩니다. 위험을 **조기에 알리는 것**만으로는 부족하고, 환자가 **실제 생활습관을 바꾸도록 동기를 유지**시켜야 합니다.

- **타겟**: 40세 이상 성인, CKD 위험군
- **핵심 흐름**: 건강검진 결과 입력 → ML 위험 예측 → 그룹 배정(G1~G4) → 맞춤 생활습관 챌린지 → 대시보드 → RAG 챗봇 상담
- **도전 과제**: ① 예측 결과를 **사용자가 이해·신뢰**하게 만들기(SHAP 설명) ② 의료 정보를 **환각 없이 안전하게** 전달하는 챗봇 ③ 실시간 응답성과 안정성을 갖춘 **운영 가능한 아키텍처**

→ 단순 모델이 아니라, **예측 → 설명 → 행동 변화 → 안전한 상담**까지 잇는 **서비스 엔지니어링**이 본질.

---

## 2. 솔루션 · 아키텍처

```
사용자 ──► nginx ──► fastapi (app/, Producer)
                         │ Redis Stream (ckd_jobs / rag_jobs)
                         ▼
                    ai-worker (ai_worker/, Consumer)
                         ├── PostgreSQL  (검진·예측결과·SHAP·AI가이드)
                         ├── Redis       (작업 큐·응답 스트림 rag_resp)
                         └── Qdrant      (RAG 벡터 DB)
```

| 컨테이너 | 역할 |
|---|---|
| `nginx` | 리버스 프록시 (80→8000) |
| `fastapi` ⭐ | API 서버(Producer)·SSE 스트리밍 |
| `ai-worker` ⭐ | ML 추론(SHAP) + RAG 챗봇 (Consumer) |
| `postgres` · `redis` · `qdrant` | DB · 메시지 브로커 · 벡터 DB |

> 무거운 ML 추론·RAG 생성을 **Redis Stream으로 비동기 분리**(Producer/Consumer)해 API 응답성을 확보. 운영(prod)은 위 6개 + `certbot`(SSL 자동 갱신) = **7컨테이너**.

---

## 3. 내 역할 · 기여 (팀 4인 중 팀장)

> 자기표현 정확성을 위해 **내가 직접 한 일과 팀원이 한 일을 구분**해 적습니다.

| 영역 | 내 기여 |
|---|---|
| **RAG 챗봇** ⭐ | LangGraph 기반 **Self-corrective RAG** 설계·구현 — 검색 적합성 평가(Grader)·질의 재작성(Rewrite)·환각 검증(Hallucination grader) + **의료 가드레일**(확진·치료 표현 차단) |
| **백엔드 아키텍처** ⭐ | FastAPI · **Redis Stream 비동기**(Producer/Consumer) · **SSE 토큰 스트리밍** · PostgreSQL |
| **풀스택** | React 대시보드(예측 결과·SHAP·챌린지) 연동 |
| **인프라·CI/CD** | Docker 컨테이너 구성 · CI 파이프라인(ruff·mypy·pytest) · 배포 총괄 · 부하테스트(Locust) |
| **팀 리딩** | 팀장으로 일정·컨벤션·코드리뷰 주도 (저장소 최다 커밋) |

| 팀원 담당 (참고) | |
|---|---|
| **ML 예측 모델** | CKD 위험 예측 모델 학습·튜닝(AUROC 0.906, KNHANES) — 팀원 담당. 나는 추론 결과를 서비스에 연결 |

---

## 4. RAG 챗봇 — 핵심 기여 상세

의료 상담은 **환각이 곧 위험**이라, 일반 RAG가 아니라 **스스로 점검·교정하는 Self-corrective RAG**로 설계했습니다.

1. **검색(Retrieve)** — Qdrant 벡터 DB에서 CKD 가이드라인(KDIGO 등) 문서 검색
2. **적합성 평가(Grade)** — 검색 문서가 질문에 맞는지 LLM이 채점, 부적합 시 **질의 재작성(Rewrite)** 후 재검색
3. **생성(Generate)** — 근거 문서 기반 답변 생성
4. **환각 검증(Hallucination grade)** — 답변이 근거에서 벗어나면 재생성
5. **의료 가드레일** — "확진·치료·예방됩니다" 표현 차단, "관리·위험을 낮출 수 있다"로만, 면책 고지

> LLM 응답은 **SSE 토큰 스트리밍**으로 화면에 실시간 출력 — 긴 의료 답변에서도 첫 글자까지의 체감 지연 최소화.

---

## 5. 기술 스택

| 구분 | 기술 |
|---|---|
| **AI / RAG** | LangGraph · Qdrant · LLM (Self-corrective RAG) |
| **백엔드** | FastAPI · Redis Stream · SSE · PostgreSQL · Tortoise ORM/Aerich |
| **프런트엔드** | React · Vite |
| **인프라** | Docker Compose · Nginx · Locust(부하테스트) · GitHub Actions(CI) |
| **품질** | ruff · mypy · pytest · pre-commit |

---

## 6. 결과

- **주강사 "상용 서비스 수준" 평가** (오즈코딩 헬스케어AI 3기 기업연계 최종 프로젝트)
- CKD 위험 예측 **AUROC 0.906** (ML 모델, 팀원 담당)
- 부하테스트 **P95 15ms** (GET API, 동시 50명, 실패율 0%)
- 예측 → SHAP 설명 → 맞춤 챌린지 → RAG 상담까지 **end-to-end 동작하는 풀스택 서비스** 완성

---

## 실행 / 셋업

> 개발 환경 셋업(대용량 ML 모델·벡터DB·환경변수 포함)은 **[SETUP.md](./SETUP.md)** 참고.
> 이 저장소는 팀 원본 저장소(`AI-HealthCare-03/AH_03_02`)의 **포크**이며, 본 README는 포트폴리오용으로 재작성했습니다.

```bash
cp envs/example.local.env envs/.local.env   # 환경변수
uv sync                                       # 의존성
docker-compose up -d --build                  # 전체 스택 → http://localhost/api/docs
```

---

## 🔒 보안 · 의료 주의

- 혈압·혈당 등 **민감 건강정보**는 로그·평문 저장·외부 전송 금지, LLM 전달 시 요약·범주화
- "확진·치료·예방됩니다" 표현 금지 — "위험을 낮출 수 있다·관리"로만
- **이 서비스는 임상적 의사결정 도구가 아닙니다** (정보 제공·생활습관 관리 목적)
