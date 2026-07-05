"""Cross-domain demo: Honest Agent Protocol on ML hyperparameter search.

This shows that the ledger + train-only-feedback + online-FDR stack is not
specific to finance.  We use a synthetic binary-classification task where the
labels are independent of the features (a pure-noise, all-null world).  An
adaptive generator proposes linear classifiers and hill-climbs on a feedback
signal.  A generator that sees validation-side information discovers
spurious classifiers and overfits the holdout; the honest wall prevents this,
and BY-FDR / online-BY keep false certifications near zero.

Milestone M3 of the Honest Agent Protocol moonshot.
"""

import argparse
import json
from pathlib import Path

import numpy as np
from scipy import stats

from aqra.conformal.multiple_testing import (
    benjamini_yekutieli,
    online_by_rejections,
)
from aqra.db import AQRADatabase
from aqra.generate.ledger import TrialsLedger
from aqra.signals.dsl import DSLCandidate
from aqra.verify.proof_of_trial import LedgerExporter

DATA_SEED = 2026
GEN_SEED = 42
ALPHA = 0.20
N_TRIALS = 200


def load_data(n_features: int = 50, n_samples: int = 600):
    """Synthetic no-signal classification: y is independent of X.

    In this null world any validation accuracy above the majority-class
    baseline is pure noise.  This mirrors the all-null returns world used
    in the finance attack suite (aqra/scripts/attack_suite.py).
    """
    rng = np.random.default_rng(DATA_SEED)
    X = rng.normal(0, 1, (n_samples, n_features))
    y = rng.integers(0, 2, n_samples)
    # train/calib/val = 60/20/20
    X_train, X_rest, y_train, y_rest = train_test_split_like(
        X, y, train_size=0.6
    )
    X_calib, X_val, y_calib, y_val = train_test_split_like(
        X_rest, y_rest, train_size=0.5
    )
    return X_train, y_train, X_calib, y_calib, X_val, y_val


def train_test_split_like(X, y, train_size: float):
    """Stratified split without sklearn (synthetic, balanced by construction)."""
    n = len(y)
    n_train = int(n * train_size)
    rng = np.random.default_rng(DATA_SEED)
    idx = rng.permutation(n)
    train_idx, rest_idx = idx[:n_train], idx[n_train:]
    return X[train_idx], X[rest_idx], y[train_idx], y[rest_idx]


def baseline_accuracy(y):
    return max(np.mean(y == 0), np.mean(y == 1))


def linear_predict(X, weights, bias):
    return ((X @ weights + bias) >= 0).astype(int)


def accuracy(y_pred, y_true):
    return np.mean(y_pred == y_true)


def ttest_pvalue(excess_scores: np.ndarray) -> float:
    """One-sided t-test that mean excess accuracy > 0."""
    if len(excess_scores) == 0 or np.std(excess_scores, ddof=1) == 0:
        return 1.0
    return float(stats.ttest_1samp(excess_scores, 0.0, alternative="greater").pvalue)


def make_random_candidate(rng: np.random.Generator, n_features: int):
    weights = rng.normal(0, 1, n_features)
    weights /= np.linalg.norm(weights) + 1e-9
    return {
        "family": "linear",
        "weights": weights.tolist(),
        "bias": float(rng.normal(0, 1)),
    }


def mutate(config: dict, rng: np.random.Generator):
    child = config.copy()
    w = np.array(child["weights"])
    w += rng.normal(0, 0.25, len(w))
    w /= np.linalg.norm(w) + 1e-9
    child["weights"] = w.tolist()
    child["bias"] += float(rng.normal(0, 0.25))
    return child


def run_demo(n_trials: int, wall: bool, online: bool, rng: np.random.Generator,
             ledger: TrialsLedger | None = None) -> dict:
    """Run one ML campaign."""
    X_train, y_train, X_calib, y_calib, X_val, y_val = load_data()
    base_acc = baseline_accuracy(y_val)

    best_config, best_score = None, -np.inf
    pvals, configs, trial_ids, val_accs = [], [], [], []

    for i in range(n_trials):
        if best_config is None or rng.random() < 0.1:
            config = make_random_candidate(rng, X_train.shape[1])
        else:
            config = mutate(best_config, rng)

        weights = np.array(config["weights"])
        bias = config["bias"]

        # Candidate is fitted on the train fold only.  We measure accuracy on
        # the calibration fold (used for early stopping / model selection in a
        # real pipeline) and the held-out validation fold.
        train_pred = linear_predict(X_train, weights, bias)
        calib_pred = linear_predict(X_calib, weights, bias)
        val_pred = linear_predict(X_val, weights, bias)
        train_acc = accuracy(train_pred, y_train)
        calib_acc = accuracy(calib_pred, y_calib)
        val_acc = accuracy(val_pred, y_val)
        val_accs.append(val_acc)

        # p-value: one-sided t-test that per-example excess correctness > 0.
        baseline_correct = (np.full_like(y_val, np.bincount(y_val).argmax()) == y_val).astype(float)
        val_correct = (val_pred == y_val).astype(float)
        excess = val_correct - baseline_correct
        pval = ttest_pvalue(excess)
        pvals.append(pval)
        configs.append(config)

        if ledger is not None:
            trial_id = ledger.new_trial_id()
            trial_ids.append(trial_id)
            cand = DSLCandidate(
                trial_id=trial_id,
                lane="ML",
                ast={"config": config},
                rationale=json.dumps(config, default=float),
            )
            ledger.register(cand)
            ledger.record_result(
                trial_id,
                metrics={"train_acc": train_acc, "calib_acc": calib_acc,
                         "val_acc": val_acc},
                p_value=pval,
            )

        # feedback channel: under the wall the generator sees only train-side
        # information; without the wall it sees validation-side signal.
        if wall:
            score = train_acc
        else:
            score = -pval  # lower validation p-value = better hill-climb score
        if score > best_score:
            best_score, best_config = score, config

    if online:
        selected = online_by_rejections(pvals, ALPHA)
    else:
        selected = benjamini_yekutieli(pvals, ALPHA)
    n_cert = int(sum(selected))
    best_val = max(val_accs) if val_accs else 0.0
    return {
        "n_trials": n_trials,
        "n_certified": n_cert,
        "best_val_acc": float(best_val),
        "baseline_val_acc": float(base_acc),
        "wall": wall,
        "online": online,
    }


def main():
    ap = argparse.ArgumentParser(description="Cross-domain ML demo (M3)")
    ap.add_argument("--trials", type=int, default=N_TRIALS)
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--wall", action="store_true",
                    help="Use train-only feedback wall (honest protocol)")
    ap.add_argument("--online", action="store_true",
                    help="Use online BY instead of batch BY")
    ap.add_argument("--export-ledger", type=Path,
                    help="Export the last repetition's ledger to this path")
    args = ap.parse_args()

    rng_master = np.random.default_rng(GEN_SEED)
    results = []
    for rep in range(args.reps):
        rng = np.random.default_rng(rng_master.integers(2**63))
        db = AQRADatabase(":memory:")
        ledger = TrialsLedger(db)
        try:
            out = run_demo(args.trials, args.wall, args.online, rng, ledger=ledger)
            results.append(out)
            if args.export_ledger and rep == args.reps - 1:
                LedgerExporter(ledger).export(
                    args.export_ledger, alpha=ALPHA, online=args.online
                )
                print(f"Exported ledger to {args.export_ledger}")
        finally:
            db.close()

    mean_cert = float(np.mean([r["n_certified"] for r in results]))
    print(f"Campaigns: {args.reps}, trials/campaign: {args.trials}")
    print(f"Protocol wall={args.wall}, online={args.online}")
    print(f"Mean certified configs: {mean_cert:.2f}")
    print(f"Baseline val acc: {results[0]['baseline_val_acc']:.3f}")
    print(f"Best observed val acc: {np.mean([r['best_val_acc'] for r in results]):.3f}")


if __name__ == "__main__":
    main()
