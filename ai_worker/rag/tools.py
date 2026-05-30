"""구조화 출력 스키마 (ai_worker/rag/tools.py).

Self-corrective(GradeDocuments) + Self-RAG 2단계(GradeHallucinations·GradeAnswer) 채점용.
llm_client 의 `with_structured_output(스키마)` 로 LLM이 Literal 값만 반환하도록 강제한다.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class GradeDocuments(BaseModel):
    """검색된 문서가 질문에 답할 정보를 담는지."""
    relevance: Literal["relevant", "not_relevant"] = Field(
        description="검색 문서가 질문에 답하는 데 도움되는 정보를 담으면 relevant"
    )


class GradeHallucinations(BaseModel):
    """생성된 답변이 검색 근거에 기반하는지 (환각 검증)."""
    grounded: Literal["grounded", "not_grounded"] = Field(
        description="답변이 검색된 근거 문서에 기반하면 grounded, 지어냈으면 not_grounded"
    )


class GradeAnswer(BaseModel):
    """생성된 답변이 사용자 질문을 실제로 해결하는지."""
    addresses: Literal["addresses", "not_addresses"] = Field(
        description="답변이 질문을 실제로 해결하면 addresses"
    )
