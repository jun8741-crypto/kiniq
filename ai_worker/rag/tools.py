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

    addresses: Literal["addresses", "not_addresses"] = Field(description="답변이 질문을 실제로 해결하면 addresses")


class GradeDomain(BaseModel):
    """검색 실패 질문의 도메인 분류 (LLM 폴백 라우팅 — medical 검증 3계층).

    DOMAIN_1        : 직접 신장 (eGFR·크레아티닌·투석·CKD 스테이지·신장식이) → 폴백 허용
    DOMAIN_2_KIDNEY : 인접질환이지만 신장 연관 ("당뇨가 신장에 미치는 영향") → 폴백 허용
    DOMAIN_2_GENERAL: 인접질환 비신장 ("당뇨 일반 식단"·"고혈압약 일반") → 전문진료 유도
    DOMAIN_3        : 비의료 ("날씨"·"코딩") → scope 안내
    """

    domain: Literal["DOMAIN_1", "DOMAIN_2_KIDNEY", "DOMAIN_2_GENERAL", "DOMAIN_3"] = Field(
        description="질문 도메인 — 직접신장/인접신장연관/인접비신장/비의료"
    )
