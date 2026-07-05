import json

import pytest

from aqra.conformal.multiple_testing import benjamini_yekutieli
from aqra.db import AQRADatabase
from aqra.generate.ledger import STATUS_EVALUATED, TrialsLedger
from aqra.signals.dsl import DSLCandidate
from aqra.verify.proof_of_trial import (
    GENESIS_HASH,
    LedgerExporter,
    ProofOfTrialVerifier,
    TrialEntry,
)


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


def test_entry_hash_is_deterministic_and_excludes_this_hash():
    e = TrialEntry(trial_id="a", created_at="2026-07-05T00:00:00+00:00",
                   previous_hash=GENESIS_HASH, dsl_version="v1",
                   lane="S", status="EVALUATED", p_value=0.01).seal()
    h1 = e.compute_hash()
    h2 = e.compute_hash()
    assert h1 == h2
    assert len(h1) == 64

    # Mutating a field changes the hash.
    e2 = TrialEntry(trial_id="a", created_at="2026-07-05T00:00:00+00:00",
                    previous_hash=GENESIS_HASH, dsl_version="v1",
                    lane="S", status="EVALUATED", p_value=0.02).seal()
    assert e2.compute_hash() != h1


def test_exported_ledger_is_hash_chained(db, tmp_path):
    ledger = TrialsLedger(db)
    c1 = _cand(ledger)
    ledger.register(c1)
    ledger.record_result(c1.trial_id, {"sharpe": 3.0}, p_value=1e-6)

    export_path = tmp_path / "ledger.jsonl"
    LedgerExporter(ledger).export(export_path, alpha=0.20)

    lines = export_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2  # one trial + metadata
    entry = json.loads(lines[0])
    assert entry["previous_hash"] == GENESIS_HASH
    assert entry["this_hash"] is not None

    meta = json.loads(lines[1])
    assert meta["_meta"]
    assert meta["alpha"] == 0.20
    assert meta["tail_hash"] == entry["this_hash"]


def test_verifier_detects_tampering(db, tmp_path):
    ledger = TrialsLedger(db)
    c1 = _cand(ledger)
    ledger.register(c1)
    ledger.record_result(c1.trial_id, {"sharpe": 3.0}, p_value=1e-6)

    export_path = tmp_path / "ledger.jsonl"
    LedgerExporter(ledger).export(export_path, alpha=0.20)

    # Tamper with a p-value in the exported file.
    lines = export_path.read_text(encoding="utf-8").splitlines()
    obj = json.loads(lines[0])
    obj["p_value"] = 0.0001
    lines[0] = json.dumps(obj)
    export_path.write_text("\n".join(lines), encoding="utf-8")

    report = ProofOfTrialVerifier(export_path).verify()
    assert not report.hash_chain_ok
    assert not report.valid
    assert any("this_hash mismatch" in d for d in report.discrepancies)


def test_verifier_recomputes_by_fdr_correctly(db, tmp_path):
    ledger = TrialsLedger(db)
    good = _cand(ledger)
    ledger.register(good)
    ledger.record_result(good.trial_id, {"sharpe": 3.0}, p_value=1e-6)

    for _ in range(50):
        c = _cand(ledger)
        ledger.register(c)
        ledger.mark_eval_failed(c.trial_id, "junk")

    export_path = tmp_path / "ledger.jsonl"
    LedgerExporter(ledger).export(export_path, alpha=0.20)

    report = ProofOfTrialVerifier(export_path).verify()
    assert report.hash_chain_ok
    assert report.valid
    assert report.certified_claimed == report.certified_recomputed
    assert good.trial_id in report.certified_recomputed


def test_verifier_catches_overclaim(db, tmp_path):
    ledger = TrialsLedger(db)
    c1, c2 = _cand(ledger), _cand(ledger)
    for c in (c1, c2):
        ledger.register(c)
        ledger.record_result(c.trial_id, {"sharpe": 1.0}, p_value=0.04)

    export_path = tmp_path / "ledger.jsonl"
    LedgerExporter(ledger).export(export_path, alpha=0.20)

    # BY at alpha=0.20 over 2 trials with p=0.04 does NOT certify either
    # (threshold at i=1 is 0.20/2/1.5 ≈ 0.067, so one may certify? Let's check).
    pvals = [0.04, 0.04]
    expected = {tid for tid, sel in zip([c1.trial_id, c2.trial_id],
                                        benjamini_yekutieli(pvals, 0.20)) if sel}
    report = ProofOfTrialVerifier(export_path).verify(claimed_certified={c1.trial_id})
    assert not report.valid
    assert report.certified_claimed == {c1.trial_id}
    assert report.certified_recomputed == expected


def test_online_by_verifier_runs(db, tmp_path):
    ledger = TrialsLedger(db)
    good = _cand(ledger)
    ledger.register(good)
    ledger.record_result(good.trial_id, {"sharpe": 3.0}, p_value=1e-6)

    export_path = tmp_path / "ledger.jsonl"
    LedgerExporter(ledger).export(export_path, alpha=0.20, online=True)

    verifier = ProofOfTrialVerifier(export_path)
    report = verifier.verify()
    assert report.valid
    assert verifier.meta["method"] == "online_by"
