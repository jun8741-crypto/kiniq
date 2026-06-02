"""Phase 3 진입 게이트 — 헤더 추출 진단 probe (2026-05-29 RAG 심층점검 발견 #2·#3).

PoC는 영문 KDIGO PDF 하나로만 MarkdownHeader 청킹을 검증했다. 실제 인덱싱 자료의
대부분(47 MD + 국문 PDF)은 헤더 구조가 다를 수 있다. 이 스크립트는 청킹 분기
(MarkdownHeader vs Recursive 폴백) 설계 근거를 만들기 위해 헤더 추출 가능성을 측정한다.

- PDF: pymupdf4llm.to_markdown → 변환된 마크다운의 #/##/### 개수
- MD : 본문(frontmatter 제외)의 #/##/### 개수

키·Docker·Qdrant 불요. 실행:
    uv run --no-project --with pymupdf4llm python src/rag_indexing/probe_headers.py
"""

from __future__ import annotations

import re
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"


def count_headers(text: str, strip_frontmatter: bool = False) -> dict[int, int]:
    """마크다운 텍스트에서 #(1)·##(2)·###(3) 헤더 개수를 센다."""
    lines = text.splitlines()
    if strip_frontmatter and lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is not None:
            lines = lines[end + 1 :]
    counts = {1: 0, 2: 0, 3: 0}
    in_fence = False
    for ln in lines:
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,3})\s+\S", ln)
        if m:
            counts[len(m.group(1))] += 1
    return counts


def probe_pdf(path: Path) -> tuple[dict[int, int], int]:
    import pymupdf4llm

    md = pymupdf4llm.to_markdown(str(path), show_progress=False)
    return count_headers(md), len(md)


PDFS = [
    ("[영문 대조] KDIGO 2024 CKD", DATA / "kdigo/KDIGO-2024-CKD-Guideline.pdf"),
    ("[국문] KSN 당뇨병콩팥병 진료지침 2024", DATA / "ksn_guideline/KSN-2024-Diabetic-Kidney-Disease-Guideline.pdf"),
    ("[국문] KSN 영양 1권(투석 전)", DATA / "knsn/1권 투석 전 단계의 만성콩팥병 환자를 위한 영양-식생활 관리.pdf"),
    (
        "[국문] 질병관리청 바로알기 건강한성인",
        DATA / "knsn/[질병관리본부] 일반인을 위한 만성콩팥병 바로알기_건강한성인편.pdf",
    ),
    ("[영문] ISN 2024 운동 합의문", DATA / "lifestyle/ISN-2024-Exercise-CKD-consensus.pdf"),
]

MD_SUBDIRS = ["nosmokeguide", "alcohol", "sleep", "stress"]


def main() -> None:
    print("=" * 64)
    print("PDF 헤더 진단 (pymupdf4llm → markdown)")
    print("=" * 64)
    for name, p in PDFS:
        if not p.exists():
            print(f"  MISSING: {name}\n           {p}")
            continue
        try:
            h, n = probe_pdf(p)
            verdict = "OK" if (h[1] + h[2] + h[3]) >= 5 else "⚠ 헤더 빈약 → Recursive 폴백 필요"
            print(f"  {name}: #={h[1]} ##={h[2]} ###={h[3]} (md {n:,}자) → {verdict}")
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {name}: {type(e).__name__}: {e}")

    print()
    print("=" * 64)
    print("MD 헤더 진단 (lifestyle 47개 — frontmatter 제외 본문)")
    print("=" * 64)
    grand = {1: 0, 2: 0, 3: 0}
    grand_files = 0
    grand_nohdr = 0
    for sub in MD_SUBDIRS:
        d = DATA / "lifestyle" / sub
        mds = sorted(d.glob("*.md"))
        tot = {1: 0, 2: 0, 3: 0}
        nohdr = 0
        for m in mds:
            h = count_headers(m.read_text(encoding="utf-8"), strip_frontmatter=True)
            for k in tot:
                tot[k] += h[k]
            if h[1] + h[2] + h[3] == 0:
                nohdr += 1
        print(
            f"  {sub:14s}: {len(mds):3d}개 | 합계 #={tot[1]} ##={tot[2]} ###={tot[3]} | 헤더0 파일={nohdr}/{len(mds)}"
        )
        for k in grand:
            grand[k] += tot[k]
        grand_files += len(mds)
        grand_nohdr += nohdr
    print("-" * 64)
    print(
        f"  {'합계':14s}: {grand_files:3d}개 | #={grand[1]} ##={grand[2]} ###={grand[3]} | 헤더0 파일={grand_nohdr}/{grand_files}"
    )
    print()
    print("판정: MD 헤더0 비율이 높으면 → MD는 MarkdownHeader 불가, frontmatter 주입/단락분할 경로 필요")


if __name__ == "__main__":
    main()
