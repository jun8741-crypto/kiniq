"""qdrant_uploader.py 단위 테스트 (Qdrant·네트워크 불요 — 순수 로직 + mock client).

point id 변환·age_group 태깅(P1-4)·text-hash dedup(P1-5)·payload 조립을 검증한다.
fixture 미사용으로 pytest·직접 실행 양쪽 지원. 실행:
    cd ~/workspaces/oz_coding/20project/AI_HealthCare_Final_Project_Template/poc
    source .venv/bin/activate
    python ../src/rag_indexing/test_uploader.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config as cfg
import qdrant_uploader as up


def _child(id_, text, **payload):
    base = {"doc_type": "clinical", "source": "X", "language": "ko", "h1": "", "h2": "", "parent_id": "p0"}
    base.update(payload)
    return {"id": id_, "text": text, "payload": base}


# ─────────────────────────────────────────────────────────────────────────────
# point id 변환 (16-hex → u64)
# ─────────────────────────────────────────────────────────────────────────────
def test_point_id_is_deterministic_u64():
    pid = up.point_id("797cb062055e70c7")
    assert pid == 8754065710744760519
    assert 0 <= pid < 2**64
    assert up.point_id("797cb062055e70c7") == pid  # 결정적


def test_point_id_distinct_for_distinct_hex():
    assert up.point_id("0000000000000001") != up.point_id("0000000000000002")


# ─────────────────────────────────────────────────────────────────────────────
# age_group 태깅 (P1-4)
# ─────────────────────────────────────────────────────────────────────────────
def test_age_group_ksn_pediatric_chapter():
    p = {"source": "KSN-2024-Diabetic-Kidney-Disease-Guideline", "h2": "9.1. 소아청소년 당뇨병콩팥병의 진단"}
    assert up.age_group_for(p) == cfg.AGE_GROUP_PEDIATRIC


def test_age_group_kdigo_pediatric_section():
    assert up.age_group_for({"source": "KDIGO-2024-CKD-Guideline", "h2": "Pediatric considerations."}) == "pediatric"
    assert (
        up.age_group_for({"source": "KDIGO-2024-CKD-Guideline", "h2": "Considerations in children and adolescents"})
        == "pediatric"
    )


def test_age_group_adult_default():
    assert up.age_group_for({"source": "KDIGO-2024-CKD-Guideline", "h2": "Dietary protein intake"}) == "adult"
    # KSN 이지만 소아 아님 → adult
    assert up.age_group_for({"source": "KSN-2024-Diabetic-Kidney-Disease-Guideline", "h2": "3.1. 혈당 관리"}) == "adult"


def test_age_group_korean_keyword_only_for_ksn_source():
    # '소아' 가 본문이 아닌 h2 에 있고 source 가 KSN 일 때만 매칭 (오탐 방지)
    assert up.age_group_for({"source": "OTHER", "h2": "소아 관련 일반 언급"}) == "adult"


# ─────────────────────────────────────────────────────────────────────────────
# text-hash dedup (P1-5)
# ─────────────────────────────────────────────────────────────────────────────
def test_dedup_removes_exact_duplicates_keeps_first():
    children = [
        _child("a1", "권고문 동일 텍스트", parent_id="p1"),
        _child("a2", "고유 텍스트", parent_id="p1"),
        _child("a3", "권고문 동일 텍스트", parent_id="p2"),  # a1 과 정확 일치 → 제거
    ]
    kept, removed = up.dedup_children(children)
    assert removed == 1
    assert [c["id"] for c in kept] == ["a1", "a2"]  # 첫 등장 유지·순서 보존


def test_dedup_no_duplicates():
    children = [_child("a1", "t1"), _child("a2", "t2")]
    kept, removed = up.dedup_children(children)
    assert removed == 0 and len(kept) == 2


# ─────────────────────────────────────────────────────────────────────────────
# payload 조립 — age_group·text·원본 chunk_id 부착, 원본 필드 보존
# ─────────────────────────────────────────────────────────────────────────────
def test_build_payload_attaches_fields():
    row = _child(
        "abc123",
        "본문 텍스트",
        source="KSN-2025-Hypertension-CKD-Guideline",
        h2="제8장 소아청소년 고혈압콩팥병의 진단과 치료",
        parent_id="pp1",
        page=12,
    )
    pl = up.build_payload(row)
    assert pl["age_group"] == "pediatric"
    assert pl["text"] == "본문 텍스트"
    assert pl["chunk_id"] == "abc123"
    assert pl["parent_id"] == "pp1" and pl["page"] == 12  # 원본 보존


def test_build_payload_does_not_mutate_source_row():
    row = _child("abc123", "t")
    up.build_payload(row)
    assert "age_group" not in row["payload"]  # 원본 payload 불변 (dict 복사)


# ─────────────────────────────────────────────────────────────────────────────
# mock Qdrant client — collection 생성·upsert 호출 검증
# ─────────────────────────────────────────────────────────────────────────────
class _MockClient:
    def __init__(self, existing=()):
        self._collections = set(existing)
        self.created: list = []
        self.deleted: list = []
        self.upserts: list = []

    def collection_exists(self, name):
        return name in self._collections

    def create_collection(self, collection_name, vectors_config):
        self._collections.add(collection_name)
        self.created.append((collection_name, vectors_config))

    def delete_collection(self, name):
        self._collections.discard(name)
        self.deleted.append(name)

    def upsert(self, collection_name, points, wait):
        self.upserts.append((collection_name, len(points)))


def test_ensure_child_collection_creates_when_absent():
    c = _MockClient()
    up.ensure_child_collection(c, "medical_kb_dev", 1536, recreate=False)
    assert len(c.created) == 1 and c.created[0][0] == "medical_kb_dev"
    assert c.deleted == []  # 부재 시 삭제 없이 생성만


def test_ensure_child_collection_recreate_deletes_first():
    c = _MockClient(existing=["medical_kb_dev"])
    up.ensure_child_collection(c, "medical_kb_dev", 1536, recreate=True)
    assert c.deleted == ["medical_kb_dev"]
    assert c.created and c.created[0][0] == "medical_kb_dev"


def test_upsert_children_batches_and_converts_id():
    c = _MockClient()
    children = [
        {"id": "0000000000000001", "text": "t1", "vector": [0.1] * 4, "payload": _child("x", "t")["payload"]},
        {"id": "0000000000000002", "text": "t2", "vector": [0.2] * 4, "payload": _child("x", "t")["payload"]},
        {"id": "0000000000000003", "text": "t3", "vector": [0.3] * 4, "payload": _child("x", "t")["payload"]},
    ]
    up.upsert_children(c, "medical_kb_dev", children, batch_size=2)
    # 3개 / batch 2 → 2회 upsert (2,1)
    assert [n for _, n in c.upserts] == [2, 1]


def test_upsert_parents_uses_empty_vector():
    c = _MockClient()
    parents = [{"id": "0000000000000010", "text": "pt", "payload": _child("x", "t")["payload"]}]
    up.upsert_parents(c, "medical_kb_parents", parents, batch_size=10)
    assert c.upserts == [("medical_kb_parents", 1)]


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
