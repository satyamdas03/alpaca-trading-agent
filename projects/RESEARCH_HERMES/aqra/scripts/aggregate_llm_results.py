#!/usr/bin/env python3
"""Aggregate per-defense real-LLM results into a summary table and figure.

Reads docs/paper/*_llm_attack_results.json, writes:
- docs/paper/llm_attack_results.json (combined)
- docs/paper/llm_attack_results.md (combined table)
- docs/paper/llm_attack_results.png (bar plot)
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "paper"


def main() -> None:
    files = sorted(DOCS.glob("*_llm_attack_results.json"))
    if not files:
        raise SystemExit("No per-defense result files found.")

    records = []
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        records.append(data)

    # Sort: models llama3:8b then mistral, defenses in protocol order.
    defense_order = ["naive", "protocol", "metered", "e_bh", "sparse_metered"]
    model_order = ["llama3:8b", "mistral"]

    records.sort(key=lambda r: (model_order.index(r["model"]),
                                defense_order.index(r["defense"])))

    out = {
        "run_date": records[0]["run_date"],
        "records": records,
    }
    (DOCS / "llm_attack_results.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )

    lines = [
        "# Real-LLM Adaptive Experiment (Phase C) — Combined Results",
        "",
        "Ground truth: all null. Any certification = false discovery.",
        "",
        "| Defense | Model | Trials | Reps | Mean false certs | Any-false-cert rate | Std dev |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in records:
        s = r["result"]
        lines.append(
            f"| {s['defense']} | `{s['model']}` | {s['trials']} | {s['reps']} | "
            f"{s['mean_false_certs']:.2f} | {s['any_false_cert_rate']:.0%} | "
            f"{s['std_false_certs']:.2f} |"
        )
    lines += ["", f"Run date: {out['run_date']}"]
    (DOCS / "llm_attack_results.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    # Bar plot.
    models = sorted({r["model"] for r in records}, key=lambda m: model_order.index(m))
    defenses = [d for d in defense_order
                if any(r["defense"] == d for r in records)]
    x = np.arange(len(defenses))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for i, model in enumerate(models):
        means = []
        for d in defenses:
            rec = next((r for r in records if r["model"] == model
                        and r["defense"] == d), None)
            means.append(rec["result"]["mean_false_certs"] if rec else 0.0)
        ax.bar(x + (i - 0.5) * width, means, width, label=model)

    ax.set_ylabel("Mean false certifications")
    ax.set_title("Real-LLM adaptive attack: mean false certs by defense and model")
    ax.set_xticks(x)
    ax.set_xticklabels(defenses, rotation=15, ha="right")
    ax.axhline(0, color="black", linewidth=0.5)
    ax.legend(title="Model")
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    fig.savefig(DOCS / "llm_attack_results.png", dpi=150)
    print(f"wrote {DOCS / 'llm_attack_results.json'}")
    print(f"wrote {DOCS / 'llm_attack_results.md'}")
    print(f"wrote {DOCS / 'llm_attack_results.png'}")


if __name__ == "__main__":
    main()
