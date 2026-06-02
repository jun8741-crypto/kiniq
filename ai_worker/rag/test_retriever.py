"""retriever.py 단위 테스트 (Qdrant·키 불요 — mock client + query_vector 주입).

age_group 필터 적용·Parent-Child 조회·parent_id 중복제거·빈 결과를 순수 로직으로 검증.
실행: cd 코드루트 && poc/.venv/bin/python ai_worker/rag/test_retriever.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 코드루트 (ai_worker 패키지)

from ai_worker.rag import retriever


# ── mock Qdrant client ────────────────────────────────────────────────────────
class _Hit:
    def __init__(self, payload, score):
        self.payload = payload
        self.score = score


class _QResp:
    def __init__(self, points):
        self.points = points


class _Parent:
    def __init__(self, payload):
        self.payload = payload


class _MockClient:
    def __init__(self, hits, parents):
        self._hits = hits
        self._parents = parents
        self.last_filter = None
        self.last_limit = None
        self.retrieved_ids = None

    def query_points(self, collection_name, query, limit, query_filter):
        self.last_collection = collection_name
        self.last_limit = limit
        self.last_filter = query_filter
        return _QResp(self._hits[:limit])

    def retrieve(self, collection_name, ids):
        self.retrieved_ids = ids
        self.last_parent_collection = collection_name
        return [_Parent(p) for p in self._parents]


def _hit(text, parent_hex, score, age="adult", source="KDIGO-2024-CKD-Guideline"):
    return _Hit(
        {
            "text": text,
            "parent_id": parent_hex,
            "source": source,
            "page": 3,
            "doc_type": "clinical",
            "h2": "Diet",
            "age_group": age,
        },
        score,
    )


# ── 테스트 ────────────────────────────────────────────────────────────────────
def test_retrieve_maps_documents_and_parent_context():
    c = _MockClient(
        [_hit("child A", "00000000000000a1", 0.68), _hit("child B", "00000000000000b2", 0.60)],
        [{"text": "parent A"}, {"text": "parent B"}],
    )
    docs, pctx, top = retriever.retrieve("질문", client=c, query_vector=[0.1] * 4)
    assert len(docs) == 2
    assert docs[0].page_content == "child A"
    assert docs[0].metadata["parent_id"] == "00000000000000a1"
    assert docs[0].metadata["source"] == "KDIGO-2024-CKD-Guideline"
    assert top == 0.68
    assert "parent A" in pctx and "parent B" in pctx


def test_retrieve_applies_age_group_filter():
    c = _MockClient([_hit("x", "00000000000000a1", 0.5)], [{"text": "p"}])
    retriever.retrieve("q", client=c, query_vector=[0.1] * 4)
    must = c.last_filter.must
    assert any(getattr(cond, "key", None) == "age_group" for cond in must)
    # MatchValue 가 adult 인지
    cond = next(c for c in must if getattr(c, "key", None) == "age_group")
    assert cond.match.value == "adult"


def test_retrieve_dedupes_parent_ids():
    # 두 child 가 같은 parent → parent 조회는 1번만
    c = _MockClient(
        [_hit("a", "00000000000000a1", 0.6), _hit("b", "00000000000000a1", 0.55)],
        [{"text": "parent1"}],
    )
    retriever.retrieve("q", client=c, query_vector=[0.1] * 4)
    assert len(c.retrieved_ids) == 1


def test_retrieve_empty_hits():
    c = _MockClient([], [])
    docs, pctx, top = retriever.retrieve("q", client=c, query_vector=[0.1] * 4)
    assert docs == [] and pctx == "" and top == 0.0


def test_parent_point_id_matches_uploader_rule():
    # 인덱싱 uploader.point_id 와 동일한 16-hex → int 변환
    assert retriever._parent_point_id("09e87917d8608f74") == int("09e87917d8608f74", 16)


def test_retrieve_respects_top_k_limit():
    hits = [_hit(f"c{i}", f"{i:016x}", 0.9 - i * 0.1) for i in range(5)]
    c = _MockClient(hits, [{"text": "p"}])
    retriever.retrieve("q", client=c, query_vector=[0.1] * 4, top_k=2)
    assert c.last_limit == 2


# ── 직접 실행 ──────────────────────────────────────────────────────────────────
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
