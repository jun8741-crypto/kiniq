"""Phase 1 PoC — KDIGO 가이드라인 기반 RAG 한 사이클 동작 증명.

목적: 우리 결정 스택(OpenAI + Qdrant + LangChain)이 실제 손에 잡히는지 확인.
운영 코드 아님. 학습 후 폐기 예정. 모듈화·테스트·예외처리 의도적으로 최소화.

흐름 (학습카드 02 + 노트북 nb/07_examples/01_rag_agent 매핑):
  1) KDIGO PDF 로드
  2) RecursiveCharacterTextSplitter로 청킹 (1000/200)
  3)+4) OpenAI 임베딩 → Qdrant 로컬 파일 캐시에 저장 (재실행 시 캐시 재사용)
  5)+6) 질문 → similarity_search_with_score Top-3
  7) GPT-4o-mini 호출 (안전 가드 프롬프트)
  8) 답변 + 출처 + 점수 출력

실행:
  python poc_rag.py                          # 기본 질문 1회
  python poc_rag.py "G3a 환자 운동은?"       # 커스텀 질문 1회
  python poc_rag.py --repl                   # 대화형 모드 (Ctrl+C로 종료)
  python poc_rag.py --reindex                # 캐시 무시하고 재인덱싱
  python poc_rag.py --repl --reindex --k 5   # 조합 가능
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

# ─────────────────────────────────────────────────────────────────────────────
# 0. 환경 설정
# ─────────────────────────────────────────────────────────────────────────────
load_dotenv()
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY 누락 — .env 확인"

PDF_PATH = Path(os.getenv("KDIGO_PDF_PATH", "./data/kdigo_ch5_diet.pdf"))
QDRANT_PATH = Path(os.getenv("QDRANT_LOCAL_PATH", "./qdrant_local"))
DEFAULT_QUESTION = "G2 단계 CKD 환자의 단백질 섭취 권장량은?"
COLLECTION = "medical_kb_poc"
EMBED_DIM = 1536  # text-embedding-3-small

# 안전 가드 시스템 프롬프트 (학습카드 05 요약 + Phase 1 발견점 반영)
SYSTEM_PROMPT = (
    "당신은 신장 건강 상담 어시스턴트입니다.\n"
    "[필수 규칙]\n"
    "1. 반드시 아래 [참고 문서] 범위 안에서만 답하세요.\n"
    "2. 문서에 없는 내용은 '확인된 근거가 없습니다'라고 명시하세요.\n"
    "3. KDIGO 권고가 별도 단계 명시 없이 제시된 경우, 모든 CKD 환자(G1~G5)에 "
    "적용된다고 해석하세요. 사용자의 단계(예: G2)가 권고 범위에 포함되면 "
    "그 권고를 그대로 답변에 활용하세요.\n"
    "4. 진단·처방·확진 표현 금지. '병원 상담을 권장합니다'로 우회.\n"
    "5. 답변 끝에 출처(파일·페이지)를 명시하세요.\n"
    "6. 마지막 줄에 책임 회피 문구를 붙이세요."
)
DISCLAIMER = (
    "\n\nℹ️ 본 정보는 교육·관리 보조 목적의 안내이며, 의학적 진단·처방을 "
    "대체하지 않습니다. 정확한 판단은 주치의·신장내과 전문의와 상담하세요."
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. PDF 로드
# ─────────────────────────────────────────────────────────────────────────────
def load_pdf(path: Path) -> list[tuple[str, int]]:
    """페이지별로 (텍스트, 페이지번호) 튜플 리스트 반환."""
    assert path.exists(), f"PDF 없음: {path} — KDIGO 2024 CKD Guideline PDF 필요"
    reader = PdfReader(str(path))
    pages = [(p.extract_text() or "", i + 1) for i, p in enumerate(reader.pages)]
    total_chars = sum(len(t) for t, _ in pages)
    print(f"[1] PDF 로드: {len(pages)} 페이지, {total_chars:,}자")
    return pages


# ─────────────────────────────────────────────────────────────────────────────
# 2. 청킹 (RecursiveCharacterTextSplitter 1000/200)
# ─────────────────────────────────────────────────────────────────────────────
def chunk_pages(pages: list[tuple[str, int]]) -> list[dict]:
    """페이지별 텍스트를 1000자 청크로 분할 + 메타데이터 보존."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
    )
    chunks = []
    for text, page_num in pages:
        for idx, chunk_text in enumerate(splitter.split_text(text)):
            chunks.append(
                {
                    "text": chunk_text,
                    "metadata": {
                        "source": "KDIGO 2024",
                        "page": page_num,
                        "chunk_idx": idx,
                    },
                }
            )
    print(f"[2] 청킹 완료: {len(chunks)}개 청크 (chunk_size=1000, overlap=200)")
    return chunks


# ─────────────────────────────────────────────────────────────────────────────
# 3+4. 임베딩 + Qdrant 로컬 파일 캐시 (재실행 시 캐시 재사용)
# ─────────────────────────────────────────────────────────────────────────────
def build_vectorstore(reindex: bool = False) -> QdrantVectorStore:
    """캐시 있으면 재사용, 없으면 PDF→청킹→임베딩→Qdrant 신규 생성."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    QDRANT_PATH.parent.mkdir(parents=True, exist_ok=True)
    client = QdrantClient(path=str(QDRANT_PATH))

    existing = {c.name for c in client.get_collections().collections}

    # 캐시 히트 — 인덱싱 스킵
    if COLLECTION in existing and not reindex:
        count = client.count(COLLECTION).count
        print(f"[3+4] Qdrant 캐시 사용: {count}개 청크 (재인덱싱 스킵)")
        print(f"      └─ 경로: {QDRANT_PATH}/")
        return QdrantVectorStore(
            client=client, collection_name=COLLECTION, embedding=embeddings
        )

    # 캐시 미스 또는 강제 재인덱싱 — 신규 생성
    if COLLECTION in existing:
        client.delete_collection(COLLECTION)
        print("[3+4] 기존 캐시 삭제 후 재인덱싱")

    pages = load_pdf(PDF_PATH)
    chunks = chunk_pages(pages)
    client.create_collection(
        COLLECTION,
        vectors_config=qmodels.VectorParams(size=EMBED_DIM, distance=qmodels.Distance.COSINE),
    )
    vs = QdrantVectorStore(client=client, collection_name=COLLECTION, embedding=embeddings)
    vs.add_texts(
        texts=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )
    print(f"[3+4] Qdrant 신규 인덱싱 완료: {len(chunks)}개 청크 → {QDRANT_PATH}/")
    return vs


# ─────────────────────────────────────────────────────────────────────────────
# 5+6. 검색 (similarity_search_with_score Top-K)
# ─────────────────────────────────────────────────────────────────────────────
def retrieve(vs: QdrantVectorStore, question: str, k: int = 3) -> list[tuple]:
    """질문 벡터화 → Top-k 청크 반환 (score 포함)."""
    hits = vs.similarity_search_with_score(question, k=k)
    print(f"[5+6] 검색 완료: Top-{k} 청크 (질문 길이 {len(question)}자)")
    for i, (doc, score) in enumerate(hits, 1):
        snippet = doc.page_content.replace("\n", " ")[:80]
        print(f"      {i}. [score={score:.3f}] p.{doc.metadata['page']} — {snippet}...")
    return hits


# ─────────────────────────────────────────────────────────────────────────────
# 7. LLM 호출 (GPT-4o-mini)
# ─────────────────────────────────────────────────────────────────────────────
def generate_answer(question: str, hits: list[tuple]) -> str:
    """검색 결과 + 시스템 프롬프트 → 답변 + 책임회피 문구."""
    context = "\n\n".join(
        f"[{d.metadata['source']} p.{d.metadata['page']}]\n{d.page_content}"
        for d, _ in hits
    )
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, max_tokens=800)
    response = llm.invoke(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"[참고 문서]\n{context}\n\n[질문]\n{question}"},
        ]
    )
    usage = response.usage_metadata or {}
    print(f"[7] LLM 응답 완료: gpt-4o-mini ({usage.get('total_tokens', '?')} tokens)")
    return response.content + DISCLAIMER


# ─────────────────────────────────────────────────────────────────────────────
# 8. 메인 진입점 (단발 / REPL 모두 지원)
# ─────────────────────────────────────────────────────────────────────────────
def ask_once(vs: QdrantVectorStore, question: str, k: int) -> None:
    """1회 질의응답 사이클."""
    print(f"\n질문: {question}\n" + "─" * 70)
    hits = retrieve(vs, question, k=k)
    answer = generate_answer(question, hits)
    print("\n" + "═" * 70 + "\n답변\n" + "═" * 70)
    print(answer)


def repl(vs: QdrantVectorStore, k: int) -> None:
    """대화형 모드 — 인덱싱 1회 후 여러 질문."""
    print("\n" + "═" * 70)
    print("대화형 모드 시작 — 빈 입력 또는 Ctrl+C로 종료")
    print("═" * 70)
    while True:
        try:
            q = input("\n질문 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료")
            return
        if not q:
            print("종료")
            return
        ask_once(vs, q, k=k)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 1 RAG PoC")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION,
                        help="단발 모드 질문 (REPL 모드 시 무시)")
    parser.add_argument("--repl", action="store_true",
                        help="대화형 모드 (인덱싱 1회 후 여러 질문)")
    parser.add_argument("--reindex", action="store_true",
                        help="기존 캐시 무시하고 재인덱싱")
    parser.add_argument("--k", type=int, default=3,
                        help="검색 Top-K (기본 3)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    vs = build_vectorstore(reindex=args.reindex)
    if args.repl:
        repl(vs, k=args.k)
    else:
        ask_once(vs, args.question, k=args.k)


if __name__ == "__main__":
    main()
