"""embedder.py 단위 테스트 (OpenAI 키·네트워크 불요 — mock client 주입).

Embedder 는 client 를 주입받아 배치 분할·순서 복원·차원 검증을 순수 로직으로 검증한다.
fixture 미사용(인자 없는 함수)으로 pytest·직접 실행 양쪽을 지원한다. 실행:
    cd ~/workspaces/oz_coding/20project/AI_HealthCare_Final_Project_Template/poc
    source .venv/bin/activate
    python -m pytest ../src/rag_indexing/test_embedder.py -v
    # 또는: python ../src/rag_indexing/test_embedder.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import embedder as emb


# ─────────────────────────────────────────────────────────────────────────────
# mock OpenAI client — embeddings.create(model, input) 흉내
# ─────────────────────────────────────────────────────────────────────────────
class _FakeDatum:
    def __init__(self, index: int, embedding: list[float]) -> None:
        self.index = index
        self.embedding = embedding


class _FakeResp:
    def __init__(self, data: list[_FakeDatum]) -> None:
        self.data = data


class _FakeEmbeddings:
    """index 0번 원소에 '전역 입력 순번'을 심어 순서 복원을 검증할 수 있게 한다."""

    def __init__(self, dim: int, *, reverse: bool = False) -> None:
        self.dim = dim
        self.reverse = reverse
        self.calls: list[list[str]] = []   # 배치별 input 기록
        self._seen = 0                      # 누적 입력 개수 (배치 경계 넘어 고유값 부여)

    def create(self, model: str, input: list[str]) -> _FakeResp:  # noqa: A002 — OpenAI 시그니처
        self.calls.append(list(input))
        data = []
        for i in range(len(input)):
            vec = [float(self._seen + i)] + [0.1] * (self.dim - 1)
            data.append(_FakeDatum(i, vec))
        self._seen += len(input)
        if self.reverse:        # 응답 순서가 뒤섞여도 index 로 복원되는지 검증
            data.reverse()
        return _FakeResp(data)


class _FakeClient:
    def __init__(self, dim: int, *, reverse: bool = False) -> None:
        self.embeddings = _FakeEmbeddings(dim, reverse=reverse)


# ─────────────────────────────────────────────────────────────────────────────
# Embedder — 배치 분할
# ─────────────────────────────────────────────────────────────────────────────
def test_embed_texts_batches_by_size():
    client = _FakeClient(dim=4)
    e = emb.Embedder(model="m", dim=4, batch_size=2, client=client)
    e.embed_texts(["a", "b", "c", "d", "e"])
    # 5개 / batch 2 → 3회 호출 (2,2,1)
    assert [len(c) for c in client.embeddings.calls] == [2, 2, 1]


def test_embed_texts_dimension_count():
    client = _FakeClient(dim=4)
    e = emb.Embedder(model="m", dim=4, batch_size=8, client=client)
    out = e.embed_texts(["a", "b", "c"])
    assert len(out) == 3
    assert all(len(v) == 4 for v in out)


def test_embed_texts_preserves_order_even_when_response_shuffled():
    # mock 이 응답을 역순으로 돌려줘도 입력 순서가 유지돼야 한다 (index 복원)
    client = _FakeClient(dim=3, reverse=True)
    e = emb.Embedder(model="m", dim=3, batch_size=10, client=client)
    out = e.embed_texts(["t0", "t1", "t2", "t3"])
    # 각 벡터 첫 원소 = 전역 입력 순번 → 0,1,2,3 순서 보존
    assert [v[0] for v in out] == [0.0, 1.0, 2.0, 3.0]


def test_embed_texts_order_preserved_across_batches():
    client = _FakeClient(dim=3, reverse=True)
    e = emb.Embedder(model="m", dim=3, batch_size=2, client=client)
    out = e.embed_texts(["t0", "t1", "t2", "t3", "t4"])
    assert [v[0] for v in out] == [0.0, 1.0, 2.0, 3.0, 4.0]


def test_embed_texts_rejects_wrong_dimension():
    # 기대 차원 5인데 mock 은 4차원 반환 → AssertionError
    client = _FakeClient(dim=4)
    e = emb.Embedder(model="m", dim=5, batch_size=8, client=client)
    try:
        e.embed_texts(["a"])
        raise AssertionError("차원 불일치인데 통과함")
    except AssertionError as ex:
        assert "차원" in str(ex)


def test_embed_texts_rejects_empty_text():
    client = _FakeClient(dim=4)
    e = emb.Embedder(model="m", dim=4, client=client)
    try:
        e.embed_texts(["ok", "   "])
        raise AssertionError("빈 텍스트인데 통과함")
    except ValueError:
        pass


def test_embed_query_returns_single_vector():
    client = _FakeClient(dim=4)
    e = emb.Embedder(model="m", dim=4, client=client)
    v = e.embed_query("hello")
    assert isinstance(v, list) and len(v) == 4


# ─────────────────────────────────────────────────────────────────────────────
# FakeEmbedder — deterministic 단위 벡터 (dry-run)
# ─────────────────────────────────────────────────────────────────────────────
def test_fake_embedder_is_deterministic():
    fe = emb.FakeEmbedder(dim=16)
    assert fe.embed_query("같은 텍스트") == fe.embed_query("같은 텍스트")


def test_fake_embedder_dimension_and_unit_norm():
    fe = emb.FakeEmbedder(dim=32)
    v = fe.embed_query("x")
    assert len(v) == 32
    norm = sum(c * c for c in v) ** 0.5
    assert abs(norm - 1.0) < 1e-9       # 정규화된 단위 벡터 (0-norm 거부 회피)


def test_fake_embedder_differs_by_text():
    fe = emb.FakeEmbedder(dim=16)
    assert fe.embed_query("a") != fe.embed_query("b")


# ─────────────────────────────────────────────────────────────────────────────
# 토큰 truncate
# ─────────────────────────────────────────────────────────────────────────────
def test_truncate_keeps_short_text():
    enc = emb._get_encoder()
    assert emb._truncate_to_token_limit("짧은 문장", enc) == "짧은 문장"


def test_truncate_without_encoder_uses_char_heuristic():
    long = "x" * 100000
    out = emb._truncate_to_token_limit(long, None, limit=10)
    assert len(out) == 20       # limit(10) × 2 char 휴리스틱


# ─────────────────────────────────────────────────────────────────────────────
# placeholder 키 판별
# ─────────────────────────────────────────────────────────────────────────────
def test_placeholder_key_detection():
    assert emb._is_placeholder_key(None) is True
    assert emb._is_placeholder_key("") is True
    assert emb._is_placeholder_key("sk-REPL") is True            # 너무 짧음
    assert emb._is_placeholder_key("sk-REPLACE-ME-0123456789") is True   # REPLACE 힌트
    assert emb._is_placeholder_key("notakey-0123456789012345") is True   # sk- 아님
    # 형식상 실제 키처럼 보이면 False
    assert emb._is_placeholder_key("sk-proj-" + "a" * 40) is False


def test_resolve_api_key_prefers_env():
    saved = os.environ.get("OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = "sk-env-test-key-0123456789"
    try:
        assert emb._resolve_api_key() == "sk-env-test-key-0123456789"
    finally:
        if saved is None:
            os.environ.pop("OPENAI_API_KEY", None)
        else:
            os.environ["OPENAI_API_KEY"] = saved


# ─────────────────────────────────────────────────────────────────────────────
# 비용 추정
# ─────────────────────────────────────────────────────────────────────────────
def test_estimate_tokens_cost_positive():
    tokens, cost = emb.estimate_tokens_cost(["hello world", "안녕하세요"], "text-embedding-3-small")
    assert tokens > 0
    assert cost >= 0.0
    # 단가 0.02/1M 적용 확인
    assert abs(cost - tokens / 1_000_000 * 0.02) < 1e-12


# ─────────────────────────────────────────────────────────────────────────────
# JSONL roundtrip + 임베딩 파이프라인 (FakeEmbedder 로 vector 키 부착)
# ─────────────────────────────────────────────────────────────────────────────
def test_jsonl_roundtrip_and_vector_attach():
    rows = [
        {"id": "a1", "text": "첫 청크", "payload": {"doc_type": "clinical", "parent_id": "p1"}},
        {"id": "a2", "text": "둘째 청크", "payload": {"doc_type": "nutrition", "parent_id": "p2"}},
    ]
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "child.jsonl"
        emb.dump_jsonl(rows, path)
        loaded = emb.read_jsonl(path)
        assert loaded == rows           # 원본 보존 (ensure_ascii=False 한글 라운드트립)

        fe = emb.FakeEmbedder(dim=8)
        vecs = fe.embed_texts([r["text"] for r in loaded])
        for r, v in zip(loaded, vecs):
            r["vector"] = v
        out = Path(d) / "embedded.jsonl"
        emb.dump_jsonl(loaded, out)
        back = emb.read_jsonl(out)
        assert all("vector" in r and len(r["vector"]) == 8 for r in back)
        assert back[0]["id"] == "a1" and back[0]["payload"]["parent_id"] == "p1"


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
