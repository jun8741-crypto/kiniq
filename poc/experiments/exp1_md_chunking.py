"""실험 1 — MarkdownHeaderTextSplitter 도입.

목적: PoC 발견 #2 "청킹이 섹션 헤더·적용 범위 손실" 직접 검증.
방법: pymupdf4llm으로 PDF→마크다운 변환 (헤더·볼드 보존) → MarkdownHeaderTextSplitter로
      섹션 헤더(#, ##, ###)를 청크 메타데이터에 포함 → 같은 G2 질문으로 baseline과 비교.

가설:
  - baseline(RecursiveCharacterTextSplitter, 1000/200): "G2 specifically 없음, G3-G5만 명시" 절충 답변
  - exp1(MarkdownHeader + Recursive): 섹션 헤더가 청크와 함께 검색되어 LLM이 적용 범위 추론 가능
       → "KDIGO 3.3.1 권고 0.8 g/kg/day가 G2 환자에 적용된다" 명확한 답변 기대

실행:
  python experiments/exp1_md_chunking.py                       # G2 질문 1회
  python experiments/exp1_md_chunking.py "고칼륨혈증 관리는?"   # 커스텀 질문
  python experiments/exp1_md_chunking.py --reindex             # 재인덱싱

비교 기준점: baseline 결과 [[project_phase1_poc_retrospective]]
  - G2 질문 score: 0.600 / 0.586 / 0.570
  - 답변: "G2 specifically 없음, G3-G5는 0.8g 권장"
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# poc 폴더에서 공통 환경 로드
sys.path.insert(0, str(Path(__file__).parent.parent))

import pymupdf4llm
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

# ─────────────────────────────────────────────────────────────────────────────
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY 누락"

PDF_PATH = Path(os.getenv("KDIGO_PDF_PATH", "./data/kdigo_ch3_progression.pdf"))
QDRANT_PATH = Path(os.getenv("QDRANT_LOCAL_PATH", "./qdrant_local"))
COLLECTION = "medical_kb_poc_md"   # baseline과 분리
EMBED_DIM = 1536
DEFAULT_QUESTION = "G2 단계 CKD 환자의 단백질 섭취 권장량은?"

SYSTEM_PROMPT = (
    "당신은 신장 건강 상담 어시스턴트입니다.\n"
    "[필수 규칙]\n"
    "1. 반드시 아래 [참고 문서] 범위 안에서만 답하세요.\n"
    "2. 문서에 없는 내용은 '확인된 근거가 없습니다'라고 명시하세요.\n"
    "3. KDIGO 권고가 별도 단계 명시 없이 제시된 경우, 모든 CKD 환자(G1~G5)에 "
    "적용된다고 해석하세요.\n"
    "4. 청크의 [Section] 헤더 정보를 활용해 권고의 적용 범위를 판단하세요.\n"
    "5. 진단·처방·확진 표현 금지. '병원 상담을 권장합니다'로 우회.\n"
    "6. 답변 끝에 출처(파일·섹션·페이지)를 명시하세요.\n"
    "7. 마지막 줄에 책임 회피 문구를 붙이세요."
)
DISCLAIMER = (
    "\n\nℹ️ 본 정보는 교육·관리 보조 목적의 안내이며, 의학적 진단·처방을 "
    "대체하지 않습니다."
)


def pdf_to_markdown(path: Path) -> str:
    """pymupdf4llm으로 PDF → 마크다운 변환 (헤더·볼드 보존)."""
    print(f"[1] PDF → Markdown 변환: {path.name}")
    md_text = pymupdf4llm.to_markdown(str(path))
    md_path = path.with_suffix(".md")
    md_path.write_text(md_text)
    print(f"    마크다운 저장: {md_path.name} ({len(md_text):,}자)")
    return md_text


def chunk_by_headers(md_text: str) -> list:
    """MarkdownHeaderTextSplitter로 헤더 보존 분할 + Recursive로 2차 분할."""
    headers_to_split = [
        ("#", "Header_1"),     # Chapter (예: "Chapter 3: Delaying CKD progression")
        ("##", "Header_2"),    # Section (예: "3.3 Diet")
        ("###", "Header_3"),   # Subsection (예: "3.3.1 Protein intake")
    ]
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split)
    md_chunks = md_splitter.split_text(md_text)

    # 2차 분할: 헤더 그룹이 너무 크면 1000자로 재분할
    recursive = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
    )
    final_chunks = []
    for doc in md_chunks:
        # 헤더 메타데이터를 모든 sub-청크에 전파
        sub_chunks = recursive.split_text(doc.page_content)
        for idx, text in enumerate(sub_chunks):
            final_chunks.append({
                "text": text,
                "metadata": {
                    "source": "KDIGO 2024",
                    "header_1": doc.metadata.get("Header_1", ""),
                    "header_2": doc.metadata.get("Header_2", ""),
                    "header_3": doc.metadata.get("Header_3", ""),
                    "chunk_idx": idx,
                },
            })
    print(f"[2] 청킹: {len(md_chunks)}개 헤더 그룹 → {len(final_chunks)}개 최종 청크")
    # 샘플 헤더 분포 출력
    sections = set(c["metadata"]["header_3"] or c["metadata"]["header_2"]
                   for c in final_chunks if c["metadata"]["header_2"])
    print(f"    인식된 섹션 수: {len(sections)}개 (예: {list(sections)[:3]})")
    return final_chunks


def build_vectorstore(reindex: bool = False) -> QdrantVectorStore:
    """헤더 메타 포함 청크를 별도 collection에 저장."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    client = QdrantClient(path=str(QDRANT_PATH))
    existing = {c.name for c in client.get_collections().collections}

    if COLLECTION in existing and not reindex:
        count = client.count(COLLECTION).count
        print(f"[3+4] 캐시 사용: {count}개 청크 (collection='{COLLECTION}')")
        return QdrantVectorStore(client=client, collection_name=COLLECTION, embedding=embeddings)

    if COLLECTION in existing:
        client.delete_collection(COLLECTION)

    md_text = pdf_to_markdown(PDF_PATH)
    chunks = chunk_by_headers(md_text)

    client.create_collection(
        COLLECTION,
        vectors_config=qmodels.VectorParams(size=EMBED_DIM, distance=qmodels.Distance.COSINE),
    )
    vs = QdrantVectorStore(client=client, collection_name=COLLECTION, embedding=embeddings)
    vs.add_texts(
        texts=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )
    print(f"[3+4] 인덱싱 완료: {len(chunks)}개 → collection='{COLLECTION}'")
    return vs


def ask(vs: QdrantVectorStore, question: str, k: int = 3) -> None:
    print(f"\n질문: {question}\n" + "─" * 70)
    hits = vs.similarity_search_with_score(question, k=k)
    print(f"[5+6] Top-{k} 검색:")
    for i, (doc, score) in enumerate(hits, 1):
        h2 = doc.metadata.get("header_2", "?")
        h3 = doc.metadata.get("header_3", "")
        section = f"{h2} > {h3}" if h3 else h2
        snippet = doc.page_content.replace("\n", " ")[:70]
        print(f"      {i}. [score={score:.3f}] [{section}] {snippet}...")

    context = "\n\n".join(
        f"[Section: {d.metadata.get('header_2','?')} > {d.metadata.get('header_3','')}]\n"
        f"{d.page_content}"
        for d, _ in hits
    )
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, max_tokens=800)
    resp = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"[참고 문서]\n{context}\n\n[질문]\n{question}"},
    ])
    usage = resp.usage_metadata or {}
    print(f"[7] LLM 응답: {usage.get('total_tokens', '?')} tokens")
    print("\n" + "═" * 70 + "\n답변\n" + "═" * 70)
    print(resp.content + DISCLAIMER)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    parser.add_argument("--reindex", action="store_true")
    parser.add_argument("--k", type=int, default=3)
    args = parser.parse_args()

    vs = build_vectorstore(reindex=args.reindex)
    ask(vs, args.question, k=args.k)


if __name__ == "__main__":
    main()
