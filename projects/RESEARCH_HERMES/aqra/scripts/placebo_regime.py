"""Placebo tests + regime stress (ICAIF sprint gap 6).

Placebo: destroy the signal-return link by permuting the signal
cross-sectionally within each date, keeping the return panel and the
signal's marginal distribution intact.  A sound gate must certify ZERO
placebo strategies.  Placebo trials run in their own accounting — they are
a control experiment and must not inflate the real ledger's FDR burden.

Regime stress: Sharpe of each library candidate inside crisis windows.
Data horizon starts 2010, so 2008 is unavailable (reported as such);
windows used: 2011 US-downgrade H2, 2020 COVID year, 2022 bear year.

Usage: uv run python scripts/placebo_regime.py
"""

import json
from datetime import date
from pathlib import Path

import numpy as np
from scipy import stats

from aqra.backtest.dsl_bt import DSLBacktest
from aqra.certify.lane_i_cert import LaneICertifier
from aqra.certify.lane_s_cert import LaneSCertifier
from aqra.conformal.multiple_testing import benjamini_yekutieli
from aqra.constants import Lane
from aqra.db import AQRADatabase
from aqra.signals.base import SignalCandidate
from aqra.signals.dsl import DSLCandidate, evaluate, features_for_lane

from run_pipeline import HOLDING, LIBRARY, TRAIN, VALIDATION, daily_from

PLACEBO_SEEDS = (11, 23, 47)
REGIMES = {
    "2011_downgrade_H2": ("2011-07-01", "2011-12-31"),
    "2020_covid": ("2020-01-01", "2020-12-31"),
    "2022_bear": ("2022-01-01", "2022-12-31"),
}


class PlaceboBacktest(DSLBacktest):
    """DSLBacktest with within-date signal permutation."""

    def __init__(self, db, seed: int):
        super().__init__(db)
        self.rng = np.random.default_rng(seed)

    def run(self, cand, start, end, holding_period=21, cost_bps=10.0):
        features = self._features(cand.lane, start, end)
        if features.empty:
            return {}
        features["signal"] = evaluate(cand.ast, features,
                                      features_for_lane(cand.lane))
        # within-date permutation: breaks any signal-return link
        features["signal"] = (
            features.groupby("date")["signal"]
            .transform(lambda s: self.rng.permutation(s.to_numpy()))
        )
        rets = self._daily_returns(start, end, holding_period)
        df = features.merge(rets, on=["ticker", "date"], how="inner")
        if df.empty or df["signal"].dropna().nunique() <= 1:
            return {}
        return self.engine.run_single_signal(df, holding_period=holding_period,
                                             cost_bps=cost_bps)


def main() -> None:
    db = AQRADatabase("data/aqra.duckdb")
    certifiers = {"S": LaneSCertifier(), "I": LaneICertifier()}

    # ---------------- placebo ----------------
    placebo_rows, pvals = [], []
    for seed in PLACEBO_SEEDS:
        bt = PlaceboBacktest(db, seed)
        for cid, lane, ast, rationale in LIBRARY:
            cand = DSLCandidate(trial_id=f"placebo-{seed}-{cid}", lane=lane,
                                ast=ast, rationale=rationale, source="placebo")
            m = bt.run(cand, *VALIDATION, holding_period=HOLDING[lane])
            d = daily_from(m or {})
            if d is None:
                placebo_rows.append({"id": cid, "seed": seed, "status": "EMPTY"})
                pvals.append(1.0)
                continue
            _, p = stats.ttest_1samp(d.to_numpy(), 0.0, alternative="greater")
            m.pop("equity_curve", None)
            if m.get("half_life") is None and lane == "I":
                m["half_life"] = 0.0
            placebo_rows.append({
                "id": cid, "seed": seed, "status": "OK",
                "sharpe": round(float(m["sharpe"]), 3),
                "p_value": round(float(p), 5), "lane": lane, "metrics": m,
            })
            pvals.append(float(p))

    selected = benjamini_yekutieli(pvals, alpha=0.20)
    placebo_certified = 0
    for row, sel in zip(placebo_rows, selected):
        if row["status"] != "OK":
            continue
        lane_enum = Lane.STRUCTURAL if row["lane"] == "S" else Lane.INFORMATIONAL
        sc = SignalCandidate(id=row["id"], lane=lane_enum, name=row["id"],
                             formula="placebo", params={}, rationale="placebo")
        dossier = certifiers[row["lane"]].evaluate(
            sc, row["metrics"], sel, p_value=row["p_value"], coverage=None)
        row["fdr_selected"] = bool(sel)
        row["cert_status"] = dossier.status
        if dossier.status == "CERTIFIED":
            placebo_certified += 1

    # ---------------- regime stress ----------------
    bt = DSLBacktest(db)
    regime_rows = []
    for cid, lane, ast, rationale in LIBRARY:
        cand = DSLCandidate(trial_id=f"regime-{cid}", lane=lane, ast=ast,
                            rationale=rationale, source="regime")
        row = {"id": cid, "lane": lane}
        for regime, (start, end) in REGIMES.items():
            m = bt.run(cand, start, end, holding_period=HOLDING[lane])
            row[regime] = round(float(m["sharpe"]), 3) if m else None
        regime_rows.append(row)
    db.close()

    out = {
        "run_date": date.today().isoformat(),
        "placebo": {
            "design": "within-date signal permutation, validation window, "
                      f"seeds {PLACEBO_SEEDS}, BY alpha=0.20",
            "trials": len(placebo_rows),
            "certified": placebo_certified,
            "rows": placebo_rows,
        },
        "regimes": {
            "note": "data horizon starts 2010-01-04; 2008 GFC unavailable",
            "windows": REGIMES,
            "rows": regime_rows,
        },
    }
    docs = Path("docs/paper")
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "placebo_regime_results.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8")

    lines = [
        "# Placebo + Regime Stress",
        "",
        f"## Placebo ({len(placebo_rows)} trials, {len(PLACEBO_SEEDS)} seeds x "
        f"{len(LIBRARY)} candidates, validation window)",
        "",
        f"**Certified placebo strategies: {placebo_certified} (must be 0).**",
        "",
        "| Candidate | Seed | Sharpe | p | FDR | Cert |",
        "|---|---|---|---|---|---|",
    ]
    for r in placebo_rows:
        lines.append(
            f"| {r['id']} | {r['seed']} | {r.get('sharpe', '-')} "
            f"| {r.get('p_value', '-')} | {r.get('fdr_selected', '-')} "
            f"| {r.get('cert_status', r['status'])} |")
    lines += [
        "",
        "## Regime-conditional Sharpe (library candidates)",
        "",
        "Data horizon starts 2010 — 2008 GFC not coverable; windows: "
        "2011 downgrade H2, 2020 COVID, 2022 bear.",
        "",
        "| Candidate | Lane | 2011 H2 | 2020 | 2022 |",
        "|---|---|---|---|---|",
    ]
    for r in regime_rows:
        lines.append(
            f"| {r['id']} | {r['lane']} | {r['2011_downgrade_H2']} "
            f"| {r['2020_covid']} | {r['2022_bear']} |")
    (docs / "placebo_regime_results.md").write_text("\n".join(lines) + "\n",
                                                    encoding="utf-8")
    print(f"placebo certified: {placebo_certified} (target 0); "
          f"wrote docs/paper/placebo_regime_results.*")


if __name__ == "__main__":
    main()
