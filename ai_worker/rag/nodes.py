"""StateGraph 노드 (ai_worker/rag/nodes.py) — PoC 8노드 이관 + 실제 모듈 연결.

흐름: guard → retrieve → grade ─(부족)→ rewrite → retrieve(재검색 ≤2)
            → generate → hallucination ─(환각)→ 재생성(≤1)
                        → answer_grade ─(미해결)→ rewrite
                        → post_guard → END
PoC(poc_langgraph_rag)의 노드·라우터 로직을 그대로 옮기되, 검색은 retriever(Parent-Child·age_group),
가드는 safety_guard(05 명세 전체), 프롬프트는 prompt_builder를 쓴다.
"""
from __future__ import annotations

from langchain_core.messages import HumanMessage

from . import config as cfg
from . import llm_client, prompt_builder, retriever, safety_guard
from .state import RAGState


def _q(state: RAGState) -> str:
    """가장 최근 사용자 질문 (rewrite로 갱신됐으면 그것)."""
    for m in reversed(state["messages"]):
        if getattr(m, "type", None) == "human":
            return m.content
        if isinstance(m, dict) and m.get("role") == "user":
            return m["content"]
    return ""


# ── 노드 ───────────────────────────────────────────────────────────────────────
def guard_node(state: RAGState) -> dict:
    blocked = safety_guard.pre_retrieval_guard(_q(state), state.get("user_context"))
    return {"blocked": blocked}


def retrieve_node(state: RAGState) -> dict:
    docs, parent_context, top = retriever.retrieve(_q(state))
    return {"documents": docs, "parent_context": parent_context, "top_score": top}


def grade_node(state: RAGState) -> dict:
    # PoC 보완: top_score≥0.5 면 grade LLM 건너뛰고 relevant (정답 청크 과필터 방지)
    if state.get("top_score", 0.0) >= cfg.SCORE_PREPASS:
        return {"relevance": "relevant"}
    joined = "\n\n".join(d.page_content for d in state["documents"])
    if not joined.strip():
        return {"relevance": "not_relevant"}
    g = llm_client.doc_grader().invoke(
        f"질문: {_q(state)}\n문서:\n{joined}\n이 문서에 질문에 답할 정보가 있습니까?"
    )
    return {"relevance": g.relevance}


def rewrite_node(state: RAGState) -> dict:
    nq = llm_client.get_gen_llm().invoke(
        f"다음 의료 질문을 벡터 검색에 더 잘 맞게 핵심 의학 용어 중심으로 한 줄로 재작성: {_q(state)}"
    ).content
    return {"messages": [HumanMessage(content=nq)], "retry_count": state.get("retry_count", 0) + 1}


def generate_node(state: RAGState) -> dict:
    msgs = prompt_builder.build_generation_messages(
        _q(state), state.get("parent_context", ""), state["documents"], state.get("user_context")
    )
    r = llm_client.get_gen_llm().invoke(msgs)
    return {"generation": r.content}


def hallucination_node(state: RAGState) -> dict:
    ctx = state.get("parent_context") or "\n\n".join(d.page_content for d in state["documents"])
    g = llm_client.hallucination_grader().invoke(
        f"근거:\n{ctx}\n\n답변:\n{state['generation']}\n답변이 근거에 기반합니까?"
    )
    return {"grounded": g.grounded, "gen_retry_count": state.get("gen_retry_count", 0) + 1}


def answer_node(state: RAGState) -> dict:
    g = llm_client.answer_grader().invoke(
        f"질문: {_q(state)}\n답변: {state['generation']}\n답변이 질문을 해결합니까?"
    )
    return {"addresses": g.addresses}


def post_guard_node(state: RAGState) -> dict:
    ans = state.get("generation") or "확실한 근거를 찾지 못했습니다. 신장내과 전문의와 상담하세요."
    if safety_guard.find_forbidden(ans):
        # 금지표현 검출 → 면책 강화 (Phase 4: 면책, 재생성 루프는 Phase 6)
        ans += "\n\n※ 위 내용은 참고용 안내이며 단정적 의미가 아닙니다."
    return {"generation": safety_guard.with_disclaimer(ans)}


# ── 라우터 3종 (PoC 검증값) ────────────────────────────────────────────────────
def relevance_router(s: RAGState) -> str:
    if s["relevance"] == "relevant":
        return "generate"
    if s.get("retry_count", 0) < cfg.MAX_REWRITE:
        return "rewrite"
    return "generate"


def grounded_router(s: RAGState) -> str:
    # gen_retry_count는 hallucination_node에서 +1 → 첫 환각 시 1. <2 라야 1회 재생성
    if s["grounded"] == "not_grounded":
        return "generate" if s.get("gen_retry_count", 0) < cfg.MAX_GEN_RETRY else "post_guard"
    return "answer_grade"


def answer_router(s: RAGState) -> str:
    if s["addresses"] == "addresses":
        return "post_guard"
    if s.get("retry_count", 0) < cfg.MAX_REWRITE:
        return "rewrite"
    return "post_guard"
