"""v3.0 PoC — LangGraph StateGraph 기반 Self-corrective RAG 동작 증명.

목적: 로드맵 v3.0에서 설계만 한 LangGraph 그래프가 실제로 도는지 "되긴 되네?" 검증.
운영 코드 아님. 기존 qdrant_local 캐시(KDIGO, medical_kb_poc) 재사용.

검증 대상 (로드맵 §Phase 4 그래프):
  guard → retrieve → grade ─(not_relevant)→ rewrite → retrieve(재검색 ≤2)
        → generate → hallucination ─(환각)→ 재생성(≤1)
                    → answer_grade ─(미해결)→ rewrite
                    → post_guard → END
  · 노트북 05_agentic_rag §5.8 + 공식 Self-RAG 패턴을 의료 안전에 맞게 조정
  · gen_query/tools_condition/ToolNode 미채택 — guard-first(항상 검색)

실행:
  cd poc && .venv/bin/python poc_langgraph_rag.py
  .venv/bin/python poc_langgraph_rag.py "G3 환자 운동은?"
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient

# ── 0. 환경 ──────────────────────────────────────────────────────────────────
load_dotenv()
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY 누락 — .env 확인"
QDRANT_PATH = Path(os.getenv("QDRANT_LOCAL_PATH", "./qdrant_local"))
COLLECTION = "medical_kb_poc"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
grade_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
client = QdrantClient(path=str(QDRANT_PATH))
vs = QdrantVectorStore(client=client, collection_name=COLLECTION, embedding=embeddings)

DISCLAIMER = (
    "\n\nℹ️ 교육·관리 보조 안내이며 의학적 진단·처방을 대체하지 않습니다. "
    "정확한 판단은 주치의·신장내과 전문의와 상담하세요."
)
EMERGENCY = re.compile(r"(자살|죽고\s*싶|목\s*매|손목\s*긋|쓰러|기절|의식\s*없|숨\s*안)")


# ── State ────────────────────────────────────────────────────────────────────
class RAGState(MessagesState):          # messages 자동 (add_messages reducer) + 의료 필드
    documents: list
    top_score: float
    relevance: str
    grounded: str
    addresses: str
    generation: str
    retry_count: int
    gen_retry_count: int
    blocked: str | None


# ── 평가 스키마 (노트북 §5.8 + 공식 Self-RAG, Literal 통일) ──────────────────
class GradeDocuments(BaseModel):
    relevance: Literal["relevant", "not_relevant"] = Field(description="검색 문서 관련성")


class GradeHallucinations(BaseModel):
    grounded: Literal["grounded", "not_grounded"] = Field(description="답변이 검색 근거에 기반")


class GradeAnswer(BaseModel):
    addresses: Literal["addresses", "not_addresses"] = Field(description="답변이 질문을 해결")


doc_grader = grade_llm.with_structured_output(GradeDocuments)
hall_grader = grade_llm.with_structured_output(GradeHallucinations)
ans_grader = grade_llm.with_structured_output(GradeAnswer)


def _q(state: RAGState) -> str:
    """가장 최근 사용자 질문 (rewrite로 갱신된 경우 그것)."""
    return next((m.content for m in reversed(state["messages"]) if m.type == "human"), "")


# ── 노드 ─────────────────────────────────────────────────────────────────────
def guard_node(state: RAGState) -> dict:
    if EMERGENCY.search(_q(state)):
        print("  [guard] 🚨 응급/자해 키워드 → 차단 (검색 건너뜀)")
        return {"blocked": "긴급한 상황이라면 즉시 119, 자살예방상담 1393으로 연락하세요. "
                           "혼자 견디지 마시고 전문가의 도움을 받으시길 바랍니다."}
    print("  [guard] ✅ 통과")
    return {"blocked": None}


def retrieve_node(state: RAGState) -> dict:
    hits = vs.similarity_search_with_score(_q(state), k=3)
    top = hits[0][1] if hits else 0.0
    print(f"  [retrieve] {len(hits)}청크, top score={top:.3f}")
    return {"documents": [d for d, _ in hits], "top_score": top}


def grade_node(state: RAGState) -> dict:
    # PoC 발견: grade LLM이 정답 청크(score 0.600)도 과필터 → score 사전통과(≥0.5 신뢰)로 보완
    if state.get("top_score", 0.0) >= 0.5:
        print(f"  [grade] relevance=relevant (score {state['top_score']:.3f}≥0.5 사전통과)")
        return {"relevance": "relevant"}
    joined = "\n\n".join(d.page_content for d in state["documents"])
    g = doc_grader.invoke(f"질문: {_q(state)}\n문서:\n{joined}\n이 문서에 답에 도움되는 정보가 있습니까?")
    print(f"  [grade] relevance={g.relevance} (LLM)")
    return {"relevance": g.relevance}


def rewrite_node(state: RAGState) -> dict:
    q = _q(state)
    nq = llm.invoke(f"다음 의료 질문을 벡터 검색에 더 잘 맞게 핵심 의학 용어 중심으로 한 줄로 재작성: {q}").content
    print(f"  [rewrite] 재작성 → {nq}")
    return {"messages": [{"role": "user", "content": nq}], "retry_count": state.get("retry_count", 0) + 1}


def generate_node(state: RAGState) -> dict:
    ctx = "\n\n".join(
        f"[{d.metadata.get('source', '?')} p.{d.metadata.get('page', '?')}]\n{d.page_content}"
        for d in state["documents"]
    )
    sys_p = (
        "당신은 신장 건강 상담 어시스턴트입니다. 아래 [참고 문서]의 권고를 그 적용 범위(CKD 단계)와 "
        "함께 제시하세요. 사용자 단계가 권고 범위에 직접 포함되지 않으면, 그 권고가 어느 단계 대상인지 "
        "명시하고 사용자 단계엔 별도 권고가 명시되지 않았음을 알려주세요(임의로 적용 추론 금지). "
        "진단·처방 표현 금지. 문서와 전혀 무관할 때만 '확인된 근거가 없습니다'라고 답하세요."
    )
    r = llm.invoke([
        {"role": "system", "content": sys_p},
        {"role": "user", "content": f"[참고 문서]\n{ctx}\n\n[질문]\n{_q(state)}"},
    ])
    print(f"  [generate] {len(r.content)}자 생성")
    return {"generation": r.content}


def hallucination_node(state: RAGState) -> dict:
    ctx = "\n\n".join(d.page_content for d in state["documents"])
    g = hall_grader.invoke(f"근거:\n{ctx}\n\n답변:\n{state['generation']}\n답변이 근거에 기반합니까?")
    print(f"  [hallucination] grounded={g.grounded}")
    return {"grounded": g.grounded, "gen_retry_count": state.get("gen_retry_count", 0) + 1}


def answer_node(state: RAGState) -> dict:
    g = ans_grader.invoke(f"질문: {_q(state)}\n답변: {state['generation']}\n답변이 질문을 해결합니까?")
    print(f"  [answer_grade] addresses={g.addresses}")
    return {"addresses": g.addresses}


def post_guard_node(state: RAGState) -> dict:
    ans = state.get("generation") or "확실한 근거를 찾지 못했습니다. 신장내과 전문의와 상담하세요."
    print("  [post_guard] 면책 문구 부착 → END")
    return {"generation": ans + DISCLAIMER}


# ── 라우터 3종 ───────────────────────────────────────────────────────────────
def relevance_router(s: RAGState) -> str:
    if s["relevance"] == "relevant":
        return "generate"
    if s.get("retry_count", 0) < 2:
        return "rewrite"
    return "generate"


def grounded_router(s: RAGState) -> str:
    # gen_retry_count는 hallucination_node에서 +1 → 첫 환각 시 1. <2 라야 1회 재생성 (PoC 발견)
    if s["grounded"] == "not_grounded":
        return "generate" if s.get("gen_retry_count", 0) < 2 else "post_guard"
    return "answer_grade"


def answer_router(s: RAGState) -> str:
    if s["addresses"] == "addresses":
        return "post_guard"
    if s.get("retry_count", 0) < 2:
        return "rewrite"
    return "post_guard"


# ── 그래프 조립 ──────────────────────────────────────────────────────────────
def build_graph():
    b = StateGraph(RAGState)
    for name, fn in [
        ("guard", guard_node), ("retrieve", retrieve_node), ("grade", grade_node),
        ("rewrite", rewrite_node), ("generate", generate_node),
        ("hallucination", hallucination_node), ("answer_grade", answer_node),
        ("post_guard", post_guard_node),
    ]:
        b.add_node(name, fn)
    b.add_edge(START, "guard")
    b.add_conditional_edges("guard", lambda s: "blocked" if s["blocked"] else "retrieve",
                            {"blocked": END, "retrieve": "retrieve"})
    b.add_edge("retrieve", "grade")
    b.add_conditional_edges("grade", relevance_router, {"generate": "generate", "rewrite": "rewrite"})
    b.add_edge("rewrite", "retrieve")
    b.add_edge("generate", "hallucination")
    b.add_conditional_edges("hallucination", grounded_router,
                            {"generate": "generate", "answer_grade": "answer_grade", "post_guard": "post_guard"})
    b.add_conditional_edges("answer_grade", answer_router, {"post_guard": "post_guard", "rewrite": "rewrite"})
    b.add_edge("post_guard", END)
    return b.compile()


graph = build_graph()


def run(q: str) -> None:
    print(f"\n{'=' * 72}\n질문: {q}\n{'─' * 72}")
    init = {"messages": [{"role": "user", "content": q}],
            "documents": [], "retry_count": 0, "gen_retry_count": 0, "blocked": None}
    final = graph.invoke(init)
    print(f"{'─' * 72}\n답변:\n{final.get('blocked') or final.get('generation')}")


if __name__ == "__main__":
    questions = sys.argv[1:] or [
        "G2 단계 CKD 환자의 단백질 섭취 권장량은?",   # 정상 의료 질문 → 전체 흐름
        "나 너무 힘들어서 죽고 싶어",                  # 자해 → guard 차단
    ]
    print(f"[그래프 컴파일 ✅] 노드 8개 + 조건부 엣지 3개")
    for q in questions:
        run(q)
