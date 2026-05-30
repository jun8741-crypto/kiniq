"""프롬프트 조립 (ai_worker/rag/prompt_builder.py).

generate 노드용 메시지를 만든다. Parent-Child 검색 결과에서 **parent 맥락을 우선** 컨텍스트로
쓰고(넓은 맥락), child 청크는 출처 표기에 사용한다. 사용자 risk_group(CKD 단계)을 함께 전달해
권고의 적용 범위를 단계와 함께 답하도록 유도한다 (임의 적용 추론 금지).
"""
from __future__ import annotations

from langchain_core.documents import Document

SYSTEM_PROMPT = (
    "당신은 만성콩팥병(CKD) 환자를 돕는 신장 건강 상담 어시스턴트입니다. "
    "아래 [참고 문서]의 권고를 그 적용 범위(CKD 단계)와 함께 제시하세요. "
    "사용자 단계가 권고 범위에 직접 포함되지 않으면, 그 권고가 어느 단계 대상인지 명시하고 "
    "사용자 단계엔 별도 권고가 명시되지 않았음을 알려주세요(임의로 적용 추론 금지). "
    "진단·처방 표현과 '치료'·'완치'·'예방됩니다' 같은 단정 표현은 절대 쓰지 마세요. "
    "참고 문서와 전혀 무관한 질문일 때만 '확인된 근거가 없습니다'라고 답하세요. "
    "사용자 CKD 단계가 '미상'으로 표시되면, 일반 정보를 제공하되 정확한 적용을 위해 "
    "검진(eGFR 확인)을 받도록 권하세요. "
    "답변은 한국어로, 출처(문서명·페이지)를 함께 제시하세요."
)


def _user_context_line(user_context: dict | None) -> str:
    # user_context 미제공(None) = 테스트·무맥락 → 표기 없음
    if user_context is None:
        return ""
    egfr = user_context.get("eGFR")
    rg = user_context.get("risk_group")
    # 단계·eGFR 둘 다 없음 = 단계 미상 → 검진 권유 유도 (05 명세 §6: NULL 안전 처리)
    if egfr is None and rg is None:
        return "\n[사용자 정보] CKD 단계 미상 — 정확한 적용을 위해 검진(eGFR 확인) 권유 필요"
    parts = []
    if rg is not None:
        parts.append(f"단계={rg}")
    if egfr is not None:
        parts.append(f"eGFR={egfr}")
    return "\n[사용자 정보] " + ", ".join(parts)


def build_generation_messages(
    query: str,
    parent_context: str,
    documents: list[Document],
    user_context: dict | None = None,
) -> list[dict]:
    """generate 노드 입력 메시지. parent 맥락 우선 + child 출처 표기."""
    sources = "\n\n".join(
        f"[{d.metadata.get('source', '?')} p.{d.metadata.get('page', '?')}]\n{d.page_content}"
        for d in documents
    )
    context = parent_context.strip() or sources   # parent 맥락 우선, 없으면 child
    user_msg = (
        f"[참고 문서]\n{context}\n\n"
        f"[출처 청크]\n{sources}"
        f"{_user_context_line(user_context)}\n\n"
        f"[질문]\n{query}"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]
