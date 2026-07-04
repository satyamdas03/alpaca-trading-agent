"""Full AQRA pipeline run (ICAIF sprint gap 5).

candidates (library-as-DSL + generated) -> train backtest (feedback stats)
-> validation backtest -> conformal coverage + p-values -> BY-FDR over the
FULL trials ledger -> lane certifiers -> BEAR review -> registry.

The train/validation wall: generator feedback sees TRAIN stats only;
certification p-values come from the VALIDATION window only.

Usage:
    uv run python scripts/run_pipeline.py [--llm]   (--llm needs ANTHROPIC_API_KEY)
"""

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
from scipy import stats

from aqra.backtest.dsl_bt import DSLBacktest
from aqra.bear.chamber import BEARChamber
from aqra.certify.lane_i_cert import LaneICertifier
from aqra.certify.lane_s_cert import LaneSCertifier
from aqra.conformal.validator import ConformalValidator
from aqra.constants import Lane
from aqra.db import AQRADatabase
from aqra.generate.ledger import TrialsLedger
from aqra.generate.llm_generator import LLMGenerator
from aqra.registry.registry import StrategyRegistry
from aqra.signals.base import SignalCandidate
from aqra.signals.dsl import DSLCandidate

TRAIN = ("2012-01-01", "2018-12-31")
VALIDATION = ("2019-01-01", "2024-12-31")
HOLDING = {"S": 21, "I": 5}

# The hand-written Phase 1a library, re-expressed in the DSL so every
# candidate — library or generated — lives in the same trials ledger.
LIBRARY = [
    ("S_MOM_12_1", "S", {"op": "rank", "arg": {"feature": "mom_12_1"}},
     "Jegadeesh-Titman cross-sectional momentum"),
    ("S_VALUE", "S", {"op": "rank", "arg": {"op": "add",
                                            "left": {"feature": "pe_rank"},
                                            "right": {"feature": "pb_rank"}}},
     "Fama-French value premium (cheap on E/P + B/P)"),
    ("S_QUALITY", "S", {"op": "rank", "arg": {"feature": "quality_score"}},
     "Novy-Marx gross profitability quality"),
    ("S_LOW_VOL", "S", {"op": "rank", "arg": {"feature": "low_vol_score"}},
     "Ang et al. low-volatility anomaly"),
    ("I_GAP", "I", {"op": "rank", "arg": {"feature": "overnight_gap"}},
     "Overnight gap continuation"),
    ("I_VOLUME", "I", {"op": "rank", "arg": {"feature": "volume_zscore"}},
     "Abnormal volume as information arrival"),
]


def daily_from(metrics: dict):
    eq = metrics.get("equity_curve")
    if eq is None or len(eq) < 3:
        return None
    return eq.pct_change().dropna()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", action="store_true",
                        help="use the Anthropic API for generation (default: mock)")
    parser.add_argument("--db", default="data/aqra.duckdb")
    parser.add_argument("--n-generated", type=int, default=4)
    args = parser.parse_args()

    db = AQRADatabase(args.db)
    ledger = TrialsLedger(db)
    bt = DSLBacktest(db)
    bear = BEARChamber()  # mock until keys rotated
    certifiers = {"S": LaneSCertifier(), "I": LaneICertifier()}
    registry = StrategyRegistry(db)

    client = None
    if args.llm:
        import os
        import anthropic
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit("--llm requires ANTHROPIC_API_KEY in env")
        client = anthropic.Anthropic()

    # ---- assemble candidates (register everything) ----
    candidates: list[DSLCandidate] = []
    for cid, lane, ast, rationale in LIBRARY:
        cand = DSLCandidate(trial_id=ledger.new_trial_id(), lane=lane,
                            ast=ast, rationale=rationale, source="library")
        ledger.register(cand)
        cand.display_id = cid
        candidates.append(cand)
    for lane in ("S", "I"):
        gen = LLMGenerator(db, lane=lane, client=client,
                           holding_period=HOLDING[lane])
        for cand in gen.propose(args.n_generated):  # generator registers
            cand.display_id = f"GEN_{lane}_{cand.trial_id[:8]}"
            candidates.append(cand)

    # ---- evaluate ----
    records = []
    for cand in candidates:
        hp = HOLDING[cand.lane]
        rec = {"id": cand.display_id, "trial_id": cand.trial_id,
               "lane": cand.lane, "source": cand.source,
               "formula": cand.formula, "rationale": cand.rationale}
        try:
            m_train = bt.run(cand, *TRAIN, holding_period=hp)
            m_val = bt.run(cand, *VALIDATION, holding_period=hp)
        except Exception as e:
            ledger.mark_eval_failed(cand.trial_id, repr(e))
            rec.update(status="EVAL_ERROR", error=repr(e))
            records.append(rec)
            continue
        d_train, d_val = daily_from(m_train or {}), daily_from(m_val or {})
        if not m_train or not m_val or d_train is None or d_val is None:
            ledger.mark_eval_failed(cand.trial_id, "empty backtest window")
            rec.update(status="EVAL_EMPTY")
            records.append(rec)
            continue

        # conformal coverage: calibrate on train dailies, test on validation
        validator = ConformalValidator(np.zeros(len(d_train)),
                                       d_train.to_numpy(), alpha=0.10)
        inside = sum(1 for a in d_val.to_numpy()
                     if validator.predict_interval(0.0)[0] <= a
                     <= validator.predict_interval(0.0)[1])
        coverage = inside / len(d_val)
        # one-sided t-test on VALIDATION dailies (pipeline proxy, see paper)
        _, p_value = stats.ttest_1samp(d_val.to_numpy(), 0.0,
                                       alternative="greater")
        p_value = float(p_value)

        m_val.pop("equity_curve", None)
        m_train.pop("equity_curve", None)
        ledger.record_result(cand.trial_id, m_val, p_value,
                             train_sharpe=m_train.get("sharpe"),
                             train_ic=m_train.get("ic"))
        rec.update(status="EVALUATED", p_value=round(p_value, 5),
                   coverage=round(coverage, 3),
                   train_sharpe=round(m_train["sharpe"], 3),
                   val_sharpe=round(m_val["sharpe"], 3),
                   val_ic=round(m_val["ic"], 4),
                   val_maxdd=round(m_val["max_drawdown"], 3),
                   val_turnover=round(m_val["turnover"], 2),
                   metrics=m_val)
        records.append(rec)

    # ---- BY-FDR over FULL ledger, then certify + BEAR + registry ----
    selected_ids = {s["trial_id"] for s in ledger.select_fdr(alpha=0.20)}
    certified, rejected = [], []
    for rec in records:
        if rec["status"] != "EVALUATED":
            rejected.append({**rec, "rejection": rec["status"]})
            continue
        lane_enum = Lane.STRUCTURAL if rec["lane"] == "S" else Lane.INFORMATIONAL
        sc = SignalCandidate(id=rec["id"], lane=lane_enum, name=rec["id"],
                             formula=rec["formula"], params={},
                             rationale=rec["rationale"])
        dossier = certifiers[rec["lane"]].evaluate(
            sc, rec["metrics"], rec["trial_id"] in selected_ids,
            p_value=rec["p_value"], coverage=rec["coverage"])
        review = bear.review(dossier)
        rec["fdr_selected"] = rec["trial_id"] in selected_ids
        rec["cert_status"] = dossier.status
        rec["bear_passed"] = review.passed
        rec["rejection"] = dossier.rejection_reason
        if dossier.status == "CERTIFIED" and review.passed:
            registry.register(dossier)
            certified.append(rec)
        else:
            rejected.append(rec)

    counts = ledger.counts()
    db.close()

    # ---- report ----
    out = {
        "run_date": date.today().isoformat(),
        "train_window": TRAIN, "validation_window": VALIDATION,
        "generation_mode": "llm" if args.llm else "mock",
        "ledger_counts": counts,
        "fdr_alpha": 0.20,
        "certified": certified,
        "rejected": rejected,
    }
    docs = Path("docs/paper")
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "pipeline_run_results.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8")

    lines = [
        "# AQRA Full Pipeline Run",
        "",
        f"Run {out['run_date']} | train {TRAIN[0]}..{TRAIN[1]} | "
        f"validation {VALIDATION[0]}..{VALIDATION[1]} | generation: {out['generation_mode']} | "
        f"BY-FDR alpha 0.20 over the FULL trials ledger ({sum(counts.values())} trials).",
        "",
        f"**Certified: {len(certified)} / {len(records)} evaluated candidates.**",
        "",
        "| ID | Lane | Source | Formula | Train Sharpe | Val Sharpe | p | FDR | Cert | BEAR | Rejection |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for rec in records:
        lines.append(
            f"| {rec['id']} | {rec['lane']} | {rec['source']} | `{rec['formula']}` "
            f"| {rec.get('train_sharpe', '-')} | {rec.get('val_sharpe', '-')} "
            f"| {rec.get('p_value', '-')} | {rec.get('fdr_selected', '-')} "
            f"| {rec.get('cert_status', rec['status'])} | {rec.get('bear_passed', '-')} "
            f"| {rec.get('rejection') or ''} |"
        )
    (docs / "pipeline_run_results.md").write_text("\n".join(lines) + "\n",
                                                  encoding="utf-8")
    print(f"\nCertified {len(certified)}/{len(records)}; "
          f"ledger counts {counts}; wrote docs/paper/pipeline_run_results.*")


if __name__ == "__main__":
    main()
