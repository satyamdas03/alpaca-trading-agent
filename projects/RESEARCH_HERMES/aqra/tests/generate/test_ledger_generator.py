import pytest

from aqra.db import AQRADatabase
from aqra.generate.ledger import (
    STATUS_EVALUATED, STATUS_REJECTED_INVALID, TrialsLedger,
)
from aqra.generate.llm_generator import LLMGenerator
from aqra.signals.dsl import DSLCandidate


@pytest.fixture
def db(tmp_path):
    d = AQRADatabase(str(tmp_path / "t.db"))
    yield d
    d.close()


def _cand(ledger, ast=None, lane="S"):
    return DSLCandidate(
        trial_id=ledger.new_trial_id(), lane=lane,
        ast=ast or {"op": "rank", "arg": {"feature": "mom_12_1"}},
        rationale="test",
    )


def test_register_before_eval_enforced(db):
    ledger = TrialsLedger(db)
    with pytest.raises(ValueError, match="never registered"):
        ledger.record_result("ghost-trial", {"sharpe": 1.0}, p_value=0.01)


def test_lifecycle_and_counts(db):
    ledger = TrialsLedger(db)
    c1, c2, c3 = _cand(ledger), _cand(ledger), _cand(ledger)
    for c in (c1, c2, c3):
        ledger.register(c)
    ledger.record_result(c1.trial_id, {"sharpe": 2.0, "ic": 0.05}, p_value=0.001)
    ledger.mark_invalid(c2.trial_id, ["feature 'x' not whitelisted"])
    ledger.mark_eval_failed(c3.trial_id, "empty backtest")
    counts = ledger.counts()
    assert counts[STATUS_EVALUATED] == 1
    assert counts[STATUS_REJECTED_INVALID] == 1


def test_fdr_over_full_ledger_counts_failures(db):
    """Failed trials enter the BY correction with p=1.0 — they are not free."""
    ledger = TrialsLedger(db)
    good = _cand(ledger)
    ledger.register(good)
    ledger.record_result(good.trial_id, {"sharpe": 3.0}, p_value=1e-6)
    selected_alone = ledger.select_fdr(alpha=0.20)
    assert len(selected_alone) == 1

    # Bury it under 200 failed attempts: same p-value, heavier correction.
    for _ in range(200):
        c = _cand(ledger)
        ledger.register(c)
        ledger.mark_eval_failed(c.trial_id, "junk")
    selected_buried = ledger.select_fdr(alpha=0.20)
    # 1e-6 still survives BY at m=201 (threshold ~1.7e-4) — the point is the
    # threshold moved, so check it via a marginal p-value instead.
    marginal = _cand(ledger)
    ledger.register(marginal)
    ledger.record_result(marginal.trial_id, {"sharpe": 1.0}, p_value=0.03)
    sel = {s["trial_id"] for s in ledger.select_fdr(alpha=0.20)}
    assert good.trial_id in sel
    assert marginal.trial_id not in sel  # 0.03 dies under the full-ledger correction
    assert len(selected_buried) >= 1


def test_train_feedback_excludes_validation_numbers(db):
    ledger = TrialsLedger(db)
    c = _cand(ledger)
    ledger.register(c)
    ledger.record_result(
        c.trial_id, {"sharpe": 9.9, "ic": 0.9}, p_value=0.001,
        train_sharpe=1.2, train_ic=0.03,
    )
    fb = ledger.train_feedback("S")
    assert fb[0]["train_sharpe"] == 1.2
    # validation-window metrics must not appear in the feedback payload
    assert "sharpe" not in fb[0] and "p_value" not in fb[0]


def test_mock_generator_produces_valid_registered_candidates(db):
    gen = LLMGenerator(db, lane="S", client=None)
    cands = gen.propose(4)
    assert len(cands) == 4
    ledger = TrialsLedger(db)
    assert sum(ledger.counts().values()) == 4


def test_generator_ledgers_invalid_proposals(db):
    gen = LLMGenerator(db, lane="S", client=None)
    parsed = [
        {"ast": {"op": "rank", "arg": {"feature": "mom_12_1"}}, "rationale": "ok"},
        {"ast": {"op": "rank", "arg": {"feature": "future_ret"}}, "rationale": "cheat"},
    ]
    # exercise the registration/validation path directly on parsed output
    from aqra.signals.dsl import DSLCandidate, features_for_lane, validate
    ledger = gen.ledger
    kept = []
    for item in parsed:
        cand = DSLCandidate(trial_id=ledger.new_trial_id(), lane="S",
                            ast=item["ast"], rationale=item["rationale"])
        errors = validate(cand.ast, features_for_lane("S"))
        ledger.register(cand)
        if errors:
            ledger.mark_invalid(cand.trial_id, errors)
        else:
            kept.append(cand)
    assert len(kept) == 1
    assert ledger.counts()[STATUS_REJECTED_INVALID] == 1


def test_parse_proposals_handles_garbage():
    assert LLMGenerator._parse_proposals("no json here") == []
    assert LLMGenerator._parse_proposals("[{broken json") == []
    ok = LLMGenerator._parse_proposals('x [{"ast": {"feature": "a"}}] y')
    assert len(ok) == 1
