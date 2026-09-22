"""Smoke tests for the gold-set evaluator."""
from __future__ import annotations

from pathlib import Path

import eval_against_gold


def test_eval_counts_match_perfect_candidate():
    """A candidate identical to a mandatory gold row counts as a hit."""
    gold = [
        {
            "row_id": "G-001",
            "expected_status": "mandatory",
            "mandatory_requirement": "Responses must be in writing and in English.",
        },
        {
            "row_id": "G-002",
            "expected_status": "out_of_scope",
            "mandatory_requirement": "This is background context.",
        },
    ]
    candidates = [
        {"requirement_text": "Responses must be in writing and in English."},
    ]
    result = eval_against_gold.evaluate(candidates, gold, threshold=0.8)
    assert result["hits"] == 1
    assert result["misses"] == 0
    assert result["false_mandatory"] == 0


def test_eval_counts_miss_and_false():
    """An unmatched candidate is a false-mandatory; an unmatched gold row is a miss."""
    gold = [
        {
            "row_id": "G-001",
            "expected_status": "mandatory",
            "mandatory_requirement": "Respondents must hold public liability cover of $10 million.",
        },
    ]
    candidates = [
        {"requirement_text": "The sky is blue."},
    ]
    result = eval_against_gold.evaluate(candidates, gold, threshold=0.55)
    assert result["hits"] == 0
    assert result["misses"] == 1
    assert result["false_mandatory"] == 1


def test_eval_runs_on_real_gold():
    """The evaluator loads the real pack gold rows without error."""
    project_root = Path(__file__).resolve().parents[1]
    gold = eval_against_gold.load_gold(project_root / "packs/nsw-asc-002-rfq-001/gold-rows.csv")
    assert len(gold) >= 20
