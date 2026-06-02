"""chunking.py 단위 테스트 (2026-05-29 RAG 심층점검 권고 #4·#7).

PDF 변환·임베딩·네트워크 불요 — 순수 함수만 검증한다. 실행:
    cd ~/workspaces/oz_coding/20project/AI_HealthCare_Final_Project/poc
    source .venv/bin/activate
    python -m pytest ../src/rag_indexing/test_chunking.py -v
    # 또는 pytest 미설치 시: python ../src/rag_indexing/test_chunking.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import chunking as ck
import config as cfg


# ─────────────────────────────────────────────────────────────────────────────
# reference 제거 — 인용번호는 제거하되 단위·권고번호·연도는 보존 (발견 #7)
# ─────────────────────────────────────────────────────────────────────────────
def test_strip_references_removes_citation_cluster():
    src = "slows CKD progression.453,454 In addition, it helps."
    out = ck.strip_references(src)
    assert "453,454" not in out
    assert "In addition" in out


def test_strip_references_preserves_unit_value():
    # 단위 동반 수치는 reference 가 아니므로 보존
    src = "protein intake of 2,000 mg per day in adults"
    out = ck.strip_references(src)
    assert "2,000" in out


def test_strip_references_preserves_recommendation_number():
    src = "Recommendation 3.3.1.1 We suggest maintaining a protein intake"
    out = ck.strip_references(src)
    assert "3.3.1.1" in out


def test_strip_references_preserves_year():
    src = "KDIGO 2024 guideline updates the 2012 version"
    out = ck.strip_references(src)
    assert "2024" in out and "2012" in out


def test_strip_references_preserves_korean_unit():
    src = "하루 2,000mg 미만으로 섭취를 권장합니다"
    out = ck.strip_references(src)
    assert "2,000" in out


# ─────────────────────────────────────────────────────────────────────────────
# pymupdf4llm 노이즈 정리 — 마커 제거, picture text 내용 보존
# ─────────────────────────────────────────────────────────────────────────────
def test_clean_markdown_removes_picture_placeholder():
    src = "본문 시작 **==> picture [438 x 237] intentionally omitted <==** 본문 끝"
    out = ck.clean_markdown(src)
    assert "picture" not in out and "omitted" not in out
    assert "본문 시작" in out and "본문 끝" in out


def test_clean_markdown_keeps_picture_text_content():
    src = "**----- Start of picture text -----** 제1권 투석 전 단계 **----- End of picture text -----**"
    out = ck.clean_markdown(src)
    assert "Start of picture text" not in out
    assert "제1권 투석 전 단계" in out  # OCR 본문은 보존


def test_clean_markdown_br_to_newline():
    src = "첫 줄<br>둘째 줄"
    out = ck.clean_markdown(src)
    assert "<br>" not in out
    assert "첫 줄" in out and "둘째 줄" in out


# ── 인코딩 깨짐 복원 (P0-1) — 실측 검증된 매핑만, 달러·각주는 보존 ──
def test_clean_markdown_m2_unit():
    out = ck.clean_markdown("eGFR <15 ml/min per 1.73 m[2] )")
    assert "m²" in out and "m[2]" not in out


def test_clean_markdown_geq_restore():
    # "$180 mm Hg"·"‡75 years" = ≥ (숫자 동반)
    assert "≥180" in ck.clean_markdown("SBP $180 mm Hg").replace(" ", "")
    assert "≥75" in ck.clean_markdown("Adults ‡75 years").replace(" ", "")


def test_clean_markdown_preserve_dollar():
    # 천단위 콤마 달러는 진짜 화폐 → 보존
    assert "$1,571" in ck.clean_markdown("US Print & Online: $1,571; International")


def test_clean_markdown_footnote_not_geq():
    # ‡ 뒤 숫자 아니면(각주 마커) ≥ 로 바꾸지 않음
    assert "≥" not in ck.clean_markdown("(19% CKD)‡ CKD without diabetes")


# ── 브라켓형 인용 제거 (P0-3) — m² 단위·CKD 단계는 보존 ──
def test_strip_references_bracket_citation():
    assert "[91]" not in ck.strip_references("proteinuria.[91][,][93] In")
    assert "In" in ck.strip_references("proteinuria.[91][,][93] In")


def test_strip_references_preserve_m2():
    # clean_markdown 으로 m² 가 된 단위는 strip_references 가 건드리지 않음
    assert "m²" in ck.strip_references("eGFR <15 ml/min per 1.73 m²")


def test_strip_references_footnote_bracket():
    assert "[§]" not in ck.strip_references("de Galan et al.[12][§] Peralta")


# ── MD scrape 아티팩트 정리 (P0-2) ──
def test_clean_md_scrape_artifacts_ui():
    out = ck.clean_md_scrape_artifacts("불면장애\n선택됨\n질환 정보 모두 펼치기\n정의\n본문")
    assert "선택됨" not in out and "모두 펼치기" not in out
    assert "불면장애" in out and "정의" in out and "본문" in out


def test_clean_md_scrape_artifacts_nbsp():
    assert "\xa0" not in ck.clean_md_scrape_artifacts("정의\xa0내용")


# ─────────────────────────────────────────────────────────────────────────────
# frontmatter 파싱 — polymorphic (nosmokeguide vs alcohol/sleep/stress)
# ─────────────────────────────────────────────────────────────────────────────
def test_parse_frontmatter_nosmoke_full():
    text = (
        "---\n"
        "dataId: 221\n"
        "title: 니코틴 중독의 원인\n"
        "category: 금연방법\n"
        "license: 출처표시 + 상업적 이용금지\n"
        "---\n"
        "\n# 니코틴 중독의 원인\n\n본문 시작."
    )
    meta, body = ck.parse_frontmatter(text)
    assert meta["title"] == "니코틴 중독의 원인"
    assert meta["category"] == "금연방법"
    assert meta["dataId"] == "221"
    assert body.lstrip().startswith("# 니코틴")


def test_parse_frontmatter_minimal():
    text = "---\ntitle: 금주가 힘든 이유\ncategory: 절주\n---\n\n# 금주가 힘든 이유\n본문"
    meta, body = ck.parse_frontmatter(text)
    assert meta["title"] == "금주가 힘든 이유"
    assert meta["category"] == "절주"


def test_parse_frontmatter_no_frontmatter():
    text = "# 제목\n본문만 있음"
    meta, body = ck.parse_frontmatter(text)
    assert meta == {}
    assert body == text


def test_strip_leading_title():
    body = "\n# 불면장애\n\n개요\n정의"
    title, rest = ck._strip_leading_title(body)
    assert title == "불면장애"
    assert "# 불면장애" not in rest
    assert "개요" in rest


# ─────────────────────────────────────────────────────────────────────────────
# 분류 유틸 — doc_type / language / SKIP
# ─────────────────────────────────────────────────────────────────────────────
def test_doc_type_for():
    assert ck._doc_type_for(cfg.DATA_DIR / "kdigo" / "x.pdf") == "clinical"
    assert ck._doc_type_for(cfg.DATA_DIR / "ksn_guideline" / "x.pdf") == "clinical"
    assert ck._doc_type_for(cfg.DATA_DIR / "knsn" / "x.pdf") == "nutrition"
    assert ck._doc_type_for(cfg.DATA_DIR / "lifestyle" / "x.pdf") == "lifestyle"
    assert ck._doc_type_for(cfg.DATA_DIR / "lifestyle" / "sleep" / "x.md") == "lifestyle"


def test_detect_language_english():
    en = (
        "We recommend that adults with CKD and diabetes maintain an HbA1c target "
        "of less than 7.0% to slow progression of kidney disease. " * 5
    )
    assert ck.detect_language(en) == "en"


def test_detect_language_korean():
    ko = (
        "만성콩팥병 환자는 단계에 따라 단백질 섭취를 조절해야 합니다. "
        "투석 전 단계에서는 체중 1kg당 단백질 제한이 권장됩니다. " * 5
    )
    assert ck.detect_language(ko) == "ko"


def test_detect_language_mixed_is_korean():
    # 국문 임상자료에 영문 약어(eGFR·SGLT2i)가 섞여도 한글이 우세하면 ko
    mixed = (
        "eGFR 가 60 미만이면 SGLT2i 투여를 고려합니다. 혈압은 130/80 mmHg 미만으로 "
        "관리하고 나트륨은 하루 2,000mg 미만으로 제한하도록 권고합니다. " * 5
    )
    assert ck.detect_language(mixed) == "ko"


def test_detect_language_no_letters_defaults_korean():
    # 글자(한글·라틴) 없음 → 보수적으로 ko
    assert ck.detect_language("12345 ... !!! ") == "ko"


def test_skip_substrings():
    assert ck._is_skipped(cfg.DATA_DIR / "knsn" / "바로알기_소아청소년편.pdf")
    assert ck._is_skipped(cfg.DATA_DIR / "knsn" / "CKRT_leaflet.pdf")
    assert not ck._is_skipped(cfg.DATA_DIR / "knsn" / "바로알기_건강한성인편.pdf")


# ─────────────────────────────────────────────────────────────────────────────
# parent_id 결정성·child 연결 무결성
# ─────────────────────────────────────────────────────────────────────────────
def test_parent_id_deterministic():
    a = ck._parent_id("src", "h1", "h2", 0)
    b = ck._parent_id("src", "h1", "h2", 0)
    assert a == b
    assert a != ck._parent_id("src", "h1", "h2", 1)


def test_emit_parent_children_integrity():
    parents, children = [], []
    long_text = "CKD 환자의 단백질 섭취 권장량은 단계에 따라 다릅니다. " * 80
    ck._emit_parent_children(
        parents=parents,
        children=children,
        text=long_text,
        source="TEST",
        doc_type="clinical",
        language="ko",
        h1="Chapter",
        h2="Section",
        parent_counter=[0],
    )
    assert len(parents) >= 2  # 2000자 초과 → parent 여러 개
    assert len(children) >= len(parents)
    parent_ids = {p["id"] for p in parents}
    for c in children:
        assert c["payload"]["parent_id"] in parent_ids  # 고아 없음
        assert c["payload"]["doc_type"] == "clinical"
        assert c["payload"]["h1"] == "Chapter"


def test_emit_skips_tiny_text():
    parents, children = [], []
    ck._emit_parent_children(
        parents=parents,
        children=children,
        text="짧음",
        source="T",
        doc_type="clinical",
        language="ko",
        h1="",
        h2="",
        parent_counter=[0],
    )
    assert parents == [] and children == []


# ─────────────────────────────────────────────────────────────────────────────
# 직접 실행 (pytest 미설치 환경 폴백)
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {fn.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{passed}/{len(fns)} passed")
    sys.exit(0 if passed == len(fns) else 1)
