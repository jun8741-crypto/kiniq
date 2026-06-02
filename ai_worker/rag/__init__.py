"""RAG 추론 파이프라인 (ai_worker/rag/) — LangGraph StateGraph Self-corrective RAG.

사용:
    from ai_worker.rag import run, get_graph
    answer = run("만성콩팥병 환자 단백질 권장량은?", user_context={"eGFR": 50})

Phase 5에서 ai_worker task가 get_graph().invoke(...) 로 호출한다.
"""

from .graph import build_graph, get_graph, run

__all__ = ["build_graph", "get_graph", "run"]
