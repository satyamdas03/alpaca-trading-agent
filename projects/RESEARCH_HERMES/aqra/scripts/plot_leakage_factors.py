#!/usr/bin/env python3
"""Plot SparseValidate vs maximal-leakage correction factors across trial counts.

Used for Honest Agent Protocol Step 10/10: theoretical tightening figure.
"""
import math
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

from aqra.conformal.multiple_testing import (
    candidacy_threshold,
    maximal_leakage_bound,
    sparse_validate_transfer_bound,
)

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "paper"


def main() -> None:
    alpha = 0.20
    trials = list(range(50, 1001, 50))
    sv_factors = []
    ml_factors = []
    for m in trials:
        lam = candidacy_threshold(alpha, m)
        k = max(1, int(round(m * lam)))
        sv = sparse_validate_transfer_bound(m, k)
        ml = 2.0 ** maximal_leakage_bound(lam)
        sv_factors.append(sv)
        ml_factors.append(ml)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(trials, sv_factors, marker="o", label="SparseValidate factor")
    ax.plot(trials, ml_factors, marker="s", label="Maximal-leakage factor")
    ax.set_yscale("log")
    ax.set_xlabel("Number of trials $m$")
    ax.set_ylabel("Leakage correction factor (log scale)")
    ax.set_title("SparseValidate vs maximal-leakage pricing: metered channel")
    ax.legend()
    ax.grid(True, which="both", ls="--", lw=0.5)
    fig.tight_layout()
    fig.savefig(DOCS / "leakage_factors.png", dpi=150)
    print(f"wrote {DOCS / 'leakage_factors.png'}")


if __name__ == "__main__":
    main()
