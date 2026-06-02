"""폴백 라우팅 단위 테스트 (LLM·키 불요 — 순수 라우터·정규식·문구).

domain 분류 라우팅, 폴백 전용 post-guard(약물수치·독성·식이수치), 면책/scope/referral 문구,
classify 단계 응급 재검사(blocked 경로)를 검증한다. LLM 분류 자체는 통합 스모크에서 확인.
실행: cd 코드루트 && poc/.venv/bin/python ai_worker/rag/test_fallback.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ai_worker.rag import nodes
from ai_worker.rag import safety_guard as sg


# ── fallback_router (domain → 분기) ────────────────────────────────────────────
def test_router_domain1_to_generate():
    assert nodes.fallback_router({"domain": "DOMAIN_1"}) == "fallback_generate"


def test_router_domain2_kidney_to_generate():
    assert nodes.fallback_router({"domain": "DOMAIN_2_KIDNEY"}) == "fallback_generate"


def test_router_domain2_general_to_referral():
    assert nodes.fallback_router({"domain": "DOMAIN_2_GENERAL"}) == "referral"


def test_router_domain3_to_scope():
    assert nodes.fallback_router({"domain": "DOMAIN_3"}) == "scope"


def test_router_blocked_priority():
    # 응급 재검사로 blocked 되면 domain 무관하게 END(blocked)
    assert nodes.fallback_router({"blocked": "위험", "domain": "DOMAIN_1"}) == "blocked"


def test_router_unknown_defaults_to_scope():
    assert nodes.fallback_router({"domain": ""}) == "scope"


# ── fallback_post_guard (폴백 전용 위험 패턴) ──────────────────────────────────
def test_fallback_guard_drug_dose():
    assert "약물·용량수치" in sg.fallback_post_guard("아세트아미노펜 500mg 정도 복용합니다")


def test_fallback_guard_toxicity():
    assert "독성·과용" in sg.fallback_post_guard("콜히친을 과용하면 독성이 나타납니다")


def test_fallback_guard_diet_value():
    assert "식이제한수치" in sg.fallback_post_guard("칼륨은 하루 2000 mg 이하로 제한합니다")


def test_fallback_guard_safe_passes():
    assert sg.fallback_post_guard("단백뇨란 소변으로 단백질이 빠져나오는 상태입니다") == []


# ── fallback_finalize (위험 시 대체 / 안전 시 면책) ────────────────────────────
def test_finalize_replaces_on_risk():
    out = sg.fallback_finalize("이부프로펜 400mg 드시면 됩니다")
    assert sg.FALLBACK_REPLACED in out and "일반적인 의학 지식" in out


def test_finalize_appends_disclaimer_on_safe():
    out = sg.fallback_finalize("단백뇨는 일반적으로 소변 검사로 확인하는 지표입니다")
    assert "단백뇨" in out and "일반적인 의학 지식" in out
    assert sg.FALLBACK_REPLACED not in out


# ── 문구 ────────────────────────────────────────────────────────────────────────
def test_scope_and_referral_notices():
    assert "범위를 벗어납니다" in sg.SCOPE_NOTICE
    assert "전문과" in sg.REFERRAL_NOTICE


# ── classify 응급 재검사 (키 불요 — blocked 경로, grader 호출 전) ───────────────
def _human_msg(text):
    return type("M", (), {"type": "human", "content": text})()


def test_classify_reblocks_selfharm():
    out = nodes.classify_fallback_node({"messages": [_human_msg("죽고 싶어")], "user_context": {}})
    assert out.get("blocked") == sg.SELFHARM_RESPONSE


def test_classify_reblocks_emergency():
    out = nodes.classify_fallback_node({"messages": [_human_msg("소변이 한 번도 안 나와요")], "user_context": {}})
    assert out.get("blocked") == sg.EMERGENCY_RESPONSE


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
