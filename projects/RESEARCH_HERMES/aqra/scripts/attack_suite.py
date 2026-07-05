"""Cheating-generator attack suite (Honest Agent Protocol, milestone M2).

Ground truth: ALL candidates are null — strategies are weight vectors over
assets whose returns are pure iid noise. Any certification is a false
discovery by construction.

Attacker: feedback-guided hill climb. It keeps the best candidate under the
feedback signal the defense exposes, mutates it, and resubmits. When the
feedback contains validation-window results, the attacker can steer into the
holdout's noise (the reusable-holdout failure mode of Dwork et al.). A
random no-feedback attacker is the baseline.

Defenses:
  naive     — no correction: certify every trial with validation p < 0.05;
              feedback = validation p (full leak)
  no_wall   — BY-FDR (alpha=0.20) over the full ledger, but feedback still
              exposes validation p: multiplicity is charged, yet adaptivity
              makes the p-values themselves anti-conservative
  metered   — BY-FDR over the full ledger; feedback is ONE BIT per round
              (validation p < 0.05 yes/no). Theorem 2's structured-leak
              regime: <= m bits total budget. Empirically sits between no_wall
              and protocol (m=400: 1.5 vs 74.5 vs 0.05 false certs), showing
              leakage grows slowly but is not zero.
  protocol   — BY-FDR over the full ledger AND train-only feedback: candidates
               are independent of the validation window, p-values valid (t-test)
  conformal  — BY-FDR over the full ledger AND train-only feedback, but the
               validator uses a three-way split (train/calibrate/test) and a
               distribution-free split-conformal p-value. This removes the
               parametric t-test caveat from Theorem 1.
  online_by  — Anytime-valid online FDR: at each audit time t the validator
               applies BY-FDR over the first t ledger entries. Candidates are
               independent of V (train-only wall), so super-uniformity holds at
               every t and the rejection set at any time controls FDR <= alpha.
               This is the immortal-agent version of Theorem 1.
  online_lord— Empirical LORD probe (Javanmard-Montanari spending) under the
               same wall. Not proved under the shared-V dependence, but
               included as a power comparison.

Prediction (kill criterion if it fails): naive false-certification count
explodes with trials; no_wall inflates despite BY; protocol, conformal and
online defenses stay at/below alpha.

Usage: uv run python scripts/attack_suite.py [--trials 400] [--reps 20]
Writes docs/paper/attack_results.{json,md} and attack_fdr.png.
"""

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
from scipy import stats

from aqra.conformal.multiple_testing import (
    benjamini_yekutieli,
    online_by_rejections as _online_by_rejections,
    online_lond_rejections as _online_lond_rejections,
)

T_TRAIN, T_CALIB, T_VAL, D_ASSETS = 252, 252, 252, 50
CERT_ALPHA_NAIVE = 0.05
FDR_ALPHA = 0.20
MUTATE_SD = 0.25


def by_reject(pvals: np.ndarray, alpha: float) -> np.ndarray:
    """Benjamini-Yekutieli rejection mask (arbitrary dependence)."""
    return np.array(benjamini_yekutieli(pvals.tolist(), alpha), dtype=bool)


def online_by_rejections(pvals: np.ndarray, alpha: float) -> np.ndarray:
    """Sequential BY-FDR over prefixes (numpy wrapper)."""
    return np.array(_online_by_rejections(pvals.tolist(), alpha), dtype=bool)


def online_lond_rejections(pvals: np.ndarray, alpha: float) -> np.ndarray:
    """LOND online FDR (numpy wrapper)."""
    return np.array(_online_lond_rejections(pvals.tolist(), alpha), dtype=bool)


def pval(pnl: np.ndarray) -> float:
    """One-sided t-test p for mean > 0."""
    if pnl.std() == 0:
        return 1.0
    return float(stats.ttest_1samp(pnl, 0.0, alternative="greater").pvalue)


def conformal_pval(r_calib: np.ndarray, r_val: np.ndarray) -> float:
    """Split-conformal p-value for positive edge, Bonferroni across val days.

    Score = return itself; small p when validation returns are unusually large.
    Under the null that calibration and validation returns are exchangeable,
    each per-day p_j is super-uniform; min*p Bonferroni gives a valid
    candidate-level p-value.
    """
    n_calib = len(r_calib)
    m_val = len(r_val)
    # p_j = (1 + #{calib returns >= val return j}) / (n_calib + 1)
    p_day = (1 + np.sum(r_calib[:, None] >= r_val[None, :], axis=0)) / (n_calib + 1)
    p_cand = p_day.min() * m_val
    return float(min(p_cand, 1.0))


def run_cell(defense: str, attacker: str, n_trials: int,
             rng: np.random.Generator) -> dict:
    """One (defense, attacker) cell on one fresh world. Returns cert counts."""
    Z_train = rng.normal(0, 0.01, (T_TRAIN, D_ASSETS))     # generator's data
    Z_calib = rng.normal(0, 0.01, (T_CALIB, D_ASSETS))   # validator calibration
    Z_val = rng.normal(0, 0.01, (T_VAL, D_ASSETS))       # held-out test

    train_p, val_p = np.empty(n_trials), np.empty(n_trials)
    best_a, best_score = None, np.inf
    certified_naive = np.zeros(n_trials, dtype=bool)

    for i in range(n_trials):
        if attacker == "random" or best_a is None:
            a = rng.normal(0, 1, D_ASSETS)
        else:  # hill climb: mutate the best-under-feedback candidate
            a = best_a + rng.normal(0, MUTATE_SD, D_ASSETS)
        a = a / np.linalg.norm(a)

        r_train, r_calib, r_val_vec = Z_train @ a, Z_calib @ a, Z_val @ a
        tp = pval(r_train)
        vp = pval(r_val_vec)
        cp = conformal_pval(r_calib, r_val_vec)
        train_p[i], val_p[i] = tp, (cp if defense == "conformal" else vp)

        # feedback channel differs by defense
        if attacker == "hillclimb":
            if defense == "metered":
                # one bit: attacker only learns accept/reject; on accept it
                # re-bases the climb, otherwise keeps the current base
                if vp < CERT_ALPHA_NAIVE:
                    best_a = a.copy()
                elif best_a is None:
                    pass  # keep sampling randomly until first accept
            else:
                score = tp if defense in ("protocol", "conformal", "online_by", "online_lond") else vp
                if score < best_score:
                    best_score, best_a = score, a.copy()

        if defense == "naive":
            certified_naive[i] = vp < CERT_ALPHA_NAIVE

    if defense == "naive":
        n_cert = int(certified_naive.sum())
    elif defense == "online_by":
        n_cert = int(online_by_rejections(val_p, FDR_ALPHA).sum())
    elif defense == "online_lond":
        n_cert = int(online_lond_rejections(val_p, FDR_ALPHA).sum())
    else:  # ledgered batch defenses: BY over ALL trials at the end of the campaign
        n_cert = int(by_reject(val_p, FDR_ALPHA).sum())
    return {"n_certified_false": n_cert, "min_val_p": float(val_p.min())}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=400)
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    checkpoints = [25, 50, 100, 200, args.trials]
    defenses = ["naive", "no_wall", "metered", "protocol", "conformal",
                "online_by", "online_lond"]
    attackers = ["hillclimb", "random"]

    results = {d: {a: {str(m): [] for m in checkpoints} for a in attackers}
               for d in defenses}
    rng_master = np.random.default_rng(args.seed)
    for rep in range(args.reps):
        for d in defenses:
            for a in attackers:
                for m in checkpoints:
                    rng = np.random.default_rng(rng_master.integers(2**63))
                    cell = run_cell(d, a, m, rng)
                    results[d][a][str(m)].append(cell["n_certified_false"])

    summary = {
        d: {a: {m: {
            "mean_false_certs": float(np.mean(v)),
            "any_false_cert_rate": float(np.mean(np.array(v) > 0)),
        } for m, v in results[d][a].items()} for a in attackers}
        for d in defenses
    }

    out = {
        "run_date": date.today().isoformat(),
        "design": {"t_train": T_TRAIN, "t_calib": T_CALIB, "t_val": T_VAL,
                   "assets": D_ASSETS, "naive_alpha": CERT_ALPHA_NAIVE,
                   "fdr_alpha": FDR_ALPHA, "reps": args.reps,
                   "ground_truth": "all null"},
        "summary": summary,
    }
    docs = Path("docs/paper")
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "attack_results.json").write_text(json.dumps(out, indent=2),
                                              encoding="utf-8")

    lines = [
        "# Cheating-Generator Attack Suite (M2)",
        "",
        f"All-null world ({args.reps} reps). Any certification = false discovery.",
        "Cells: mean false certifications (rate of >=1 false cert).",
        "",
        "| Defense | Attacker | " + " | ".join(f"m={m}" for m in checkpoints) + " |",
        "|---|---|" + "---|" * len(checkpoints),
    ]
    for d in defenses:
        for a in attackers:
            cells = []
            for m in checkpoints:
                s = summary[d][a][str(m)]
                cells.append(f"{s['mean_false_certs']:.2f} ({s['any_false_cert_rate']:.0%})")
            lines.append(f"| {d} | {a} | " + " | ".join(cells) + " |")
    (docs / "attack_results.md").write_text("\n".join(lines) + "\n",
                                            encoding="utf-8")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 4.5))
        styles = {"naive": "tab:red", "no_wall": "tab:orange",
                  "metered": "tab:blue", "protocol": "tab:green",
                  "conformal": "tab:purple", "online_by": "tab:cyan",
                  "online_lond": "tab:pink"}
        for d in defenses:
            ys = [summary[d]["hillclimb"][str(m)]["mean_false_certs"]
                  for m in checkpoints]
            ax.plot(checkpoints, ys, marker="o", color=styles[d],
                    label=f"{d} (hill-climb attacker)")
        ax.axhline(FDR_ALPHA, ls="--", lw=1, color="gray",
                   label=f"FDR target {FDR_ALPHA}")
        ax.set_xlabel("trials by the adversarial generator")
        ax.set_ylabel("mean false certifications (all-null world)")
        ax.set_title("The wall is what holds: false discoveries vs adaptivity")
        ax.legend()
        fig.tight_layout()
        fig.savefig(docs / "attack_fdr.png", dpi=150)
    except Exception as e:  # plot is a bonus, numbers are the artifact
        print(f"plot skipped: {e}")

    for d in ["naive", "protocol", "conformal", "online_by", "online_lond"]:
        print(f"--- {d} hillclimb ---")
        print(json.dumps(summary[d]["hillclimb"], indent=1))
    print("wrote docs/paper/attack_results.{json,md} + attack_fdr.png")


if __name__ == "__main__":
    main()
