"""LLM 클라이언트 (ai_worker/rag/llm_client.py).

생성(temp 0.3)·채점(temp 0) 두 ChatOpenAI 를 lazy 싱글턴으로 공유한다.
채점기는 `with_structured_output(스키마)` 로 Literal 값만 반환하도록 강제한다 (Self-RAG).
OPENAI_API_KEY 환경변수를 자동 사용.
"""

from __future__ import annotations

from langchain_openai import ChatOpenAI

from . import config as cfg
from .tools import GradeAnswer, GradeDocuments, GradeDomain, GradeHallucinations

_gen_llm: ChatOpenAI | None = None
_grade_llm: ChatOpenAI | None = None


def get_gen_llm() -> ChatOpenAI:
    global _gen_llm
    if _gen_llm is None:
        _gen_llm = ChatOpenAI(model=cfg.LLM_MODEL, temperature=cfg.GEN_TEMPERATURE)
    return _gen_llm


def get_grade_llm() -> ChatOpenAI:
    global _grade_llm
    if _grade_llm is None:
        _grade_llm = ChatOpenAI(model=cfg.LLM_MODEL, temperature=cfg.GRADE_TEMPERATURE)
    return _grade_llm


# 채점기 (호출 시점에 grade_llm 바인딩 — 키 검증을 첫 사용으로 미룸)
def doc_grader():
    return get_grade_llm().with_structured_output(GradeDocuments)


def hallucination_grader():
    return get_grade_llm().with_structured_output(GradeHallucinations)


def answer_grader():
    return get_grade_llm().with_structured_output(GradeAnswer)


def domain_grader():
    """검색 실패 질문의 도메인 분류기 (LLM 폴백 라우팅)."""
    return get_grade_llm().with_structured_output(GradeDomain)
