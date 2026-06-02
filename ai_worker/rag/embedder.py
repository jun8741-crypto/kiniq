"""query 임베딩 (ai_worker/rag/embedder.py).

추론 시 사용자 질문을 인덱싱과 **동일한 모델**(embed-3-small 1536d)로 벡터화한다.
인덱싱 트랙(`src/rag_indexing/embedder.py`)은 배치 적재용, 이쪽은 단일 query 용 — 책임이 달라 분리.
OpenAIEmbeddings 는 OPENAI_API_KEY 환경변수를 자동 사용한다.
"""
from __future__ import annotations

from langchain_openai import OpenAIEmbeddings

from . import config as cfg

_embeddings: OpenAIEmbeddings | None = None


def get_embeddings() -> OpenAIEmbeddings:
    """lazy 싱글턴 (키 검증을 첫 호출로 미룸)."""
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(model=cfg.EMBEDDING_MODEL)
    return _embeddings


def embed_query(text: str) -> list[float]:
    return get_embeddings().embed_query(text)
