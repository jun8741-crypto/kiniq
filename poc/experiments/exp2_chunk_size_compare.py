"""실험 2 — chunk_size 비교 (500 vs 1000 vs 1500).

목적: 청크 크기가 검색 score·청크 수·답변 품질에 미치는 영향 측정.
      Phase 3 인덱싱 청크 튜닝 결정 근거 데이터 수집.

가설:
  - 작은 청크(500): 정밀 검색, score 높음, but 컨텍스트 부족으로 답변 빈약
  - 중간 청크(1000, baseline): 균형
  - 큰 청크(1500): 풍부한 컨텍스트, but 노이즈 ↑, score 분산

실행:
  python experiments/exp2_chunk_size_compare.py
  python experiments/exp2_chunk_size_compare.py "다른 질문" --reindex

기준점: baseline (chunk_size=1000, [[project_phase1_poc_retrospective]])
  - 청크 수 ~270, G2 질문 score 0.600 / 0.586 / 0.570
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY 누락"

PDF_PATH = Path(os.getenv("KDIGO_PDF_PATH", "./data/kdigo_ch3_progression.pdf"))
QDRANT_PATH = Path(os.getenv("QDRANT_LOCAL_PATH", "./qdrant_local"))
EMBED_DIM = 1536

# 비교할 청크 크기 (overlap은 chunk_size의 20% 유지)
CHUNK_CONFIGS = [
    (500, 100),    # 작은 청크
    (1000, 200),   # baseline
    (1500, 300),   # 큰 청크
]

DEFAULT_QUESTION = "G2 단계 CKD 환자의 단백질 섭취 권장량은?"
SYSTEM_PROMPT = (
    "당신은 신장 건강 상담 어시스턴트입니다.\n"
    "참고 문서를 근거로 간결하게 답변하세요.\n"
    "KDIGO 권고 단계 명시 없으면 모든 CKD 환자에 적용된다고 해석하세요.\n"
    "답변은 3문장 이내. 출처 명시."
)


def load_chunks(chunk_size: int, chunk_overlap: int) -> list:
    reader = PdfReader(str(PDF_PATH))
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = []
    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        for ci, ct in enumerate(splitter.split_text(text)):
            chunks.append({
                "text": ct,
                "metadata": {"source": "KDIGO 2024", "page": page_idx + 1, "chunk_idx": ci,
                             "chunk_size": chunk_size},
            })
    return chunks


def run_one(chunk_size: int, chunk_overlap: int, question: str, reindex: bool) -> dict:
    """한 chunk_size 실험 전체. client lock을 try-finally로 즉시 해제."""
    print(f"\n── chunk_size={chunk_size}, overlap={chunk_overlap} " + "─" * 30)
    collection = f"medical_kb_poc_cs{chunk_size}"
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Qdrant 작업 (lock 잡힘) — 끝나면 close
    client = QdrantClient(path=str(QDRANT_PATH))
    try:
        existing = {c.name for c in client.get_collections().collections}

        if collection in existing and not reindex:
            pass   # 캐시 재사용
        else:
            if collection in existing:
                client.delete_collection(collection)
            chunks = load_chunks(chunk_size, chunk_overlap)
            client.create_collection(
                collection,
                vectors_config=qmodels.VectorParams(size=EMBED_DIM, distance=qmodels.Distance.COSINE),
            )
            vs_for_add = QdrantVectorStore(
                client=client, collection_name=collection, embedding=embeddings,
            )
            vs_for_add.add_texts(
                texts=[c["text"] for c in chunks],
                metadatas=[c["metadata"] for c in chunks],
            )
            print(f"  [인덱싱] cs={chunk_size}/ov={chunk_overlap}: {len(chunks)}개 청크 → '{collection}'")

        # 같은 client에서 count + 검색 (lock 유지 상태)
        vs = QdrantVectorStore(
            client=client, collection_name=collection, embedding=embeddings,
        )
        count = client.count(collection).count
        hits = vs.similarity_search_with_score(question, k=3)
    finally:
        client.close()   # ⭐ lock 즉시 해제

    scores = [s for _, s in hits]
    print(f"  청크 수: {count}, Top-3 score: {[round(s, 3) for s in scores]}")
    for i, (doc, s) in enumerate(hits, 1):
        snippet = doc.page_content.replace("\n", " ")[:60]
        print(f"    {i}. [score={s:.3f}] p.{doc.metadata.get('page')} — {snippet}...")

    # LLM은 Qdrant 무관 — lock 해제 후 호출 OK
    context = "\n\n".join(
        f"[p.{d.metadata['page']}]\n{d.page_content}" for d, _ in hits
    )
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, max_tokens=300)
    resp = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"[참고]\n{context}\n\n[질문]\n{question}"},
    ])
    print(f"  답변 ({(resp.usage_metadata or {}).get('total_tokens', '?')} tok):")
    print(f"  {resp.content[:300]}")
    return {
        "chunk_size": chunk_size,
        "overlap": chunk_overlap,
        "count": count,
        "scores": scores,
        "tokens": (resp.usage_metadata or {}).get("total_tokens", 0),
        "answer": resp.content,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    parser.add_argument("--reindex", action="store_true")
    args = parser.parse_args()

    print(f"질문: {args.question}")
    print(f"PDF: {PDF_PATH.name}")
    results = []
    for cs, ov in CHUNK_CONFIGS:
        results.append(run_one(cs, ov, args.question, args.reindex))

    # 비교표
    print("\n" + "═" * 70 + "\n비교 요약\n" + "═" * 70)
    print(f"{'chunk_size':>10} {'overlap':>8} {'청크수':>8} {'score Top-1':>12} {'tokens':>8}")
    print("─" * 70)
    for r in results:
        print(f"{r['chunk_size']:>10} {r['overlap']:>8} {r['count']:>8} "
              f"{r['scores'][0]:>12.3f} {r['tokens']:>8}")


if __name__ == "__main__":
    main()
