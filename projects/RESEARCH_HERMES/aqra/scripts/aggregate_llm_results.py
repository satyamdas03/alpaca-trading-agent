#!/usr/bin/env python3
"""Aggregate per-defense real-LLM results into a summary table and figure.

Reads docs/paper/*_llm_attack_results.json, writes:
- docs/paper/llm_attack_results.json (combined)
- docs/paper/llm_attack_results.md (combined table)
- docs/paper/llm_fdr_by_trials.png (bar plot)

Supports multiple model families and the maxleak_metered defense added in
Step 8/10 of the Honest Agent Protocol A+C push.
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
        # Normalize older and newer file formats.
        model = data.get("model") or data["result"].get("model")
        defense = data.get("defense") or data["result"].get("defense")
        if data.get("result") is None:
            # legacy single-defense aggregate format
            result = {k: v for k, v in data.items() if k != "results"}
        else:
            result = data["result"]
        records.append(
            {
                "model": model,
                "defense": defense,
                "trials": data.get("trials", result.get("trials")),
                "reps": data.get("reps", result.get("reps")),
                "run_date": data.get("run_date", result.get("run_date", "unknown")),
                "result": result,
            }
        )

    defense_order = [
        "naive",
        "no_wall",
        "metered",
        "sparse_metered",
        "maxleak_metered",
        "protocol",
        "conformal",
        "online_by",
        "online_lond",
        "e_bh",
        "online_e_bh",
        "dby",
    ]
    model_order = [
        "claude-haiku-4-5-20251001",
        "claude-sonnet-5",
        "claude-fable-5",
        "claude-opus-4-8",
        "llama3:8b",
        "mistral",
        "gemma2:9b",
        "qwen2.5:7b",
        "llama3.1:8b",
    ]

    def sort_key(r: dict) -> tuple:
        mod_idx = model_order.index(r["model"]) if r["model"] in model_order else 999
        def_idx = defense_order.index(r["defense"]) if r["defense"] in defense_order else 999
        return mod_idx, def_idx

    records.sort(key=sort_key)

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

    # Bar plot: grouped by defense, one bar per model.
    models = sorted({r["model"] for r in records}, key=lambda m: model_order.index(m) if m in model_order else 999)
    defenses = [d for d in defense_order if any(r["defense"] == d for r in records)]
    x = np.arange(len(defenses))
    width = 0.8 / max(len(models), 1)

    fig, ax = plt.subplots(figsize=(max(8, 1.2 * len(defenses)), 4.5))
    for i, model in enumerate(models):
        means = []
        for d in defenses:
            rec = next(
                (r for r in records if r["model"] == model and r["defense"] == d), None
            )
            means.append(rec["result"]["mean_false_certs"] if rec else 0.0)
        ax.bar(x + (i - (len(models) - 1) / 2) * width, means, width, label=model)

    ax.set_ylabel("Mean false certifications")
    ax.set_title("Real-LLM adaptive attack: mean false certs by defense and model")
    ax.set_xticks(x)
    ax.set_xticklabels(defenses, rotation=20, ha="right")
    ax.axhline(0, color="black", linewidth=0.5)
    ax.legend(title="Model", loc="upper right")
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    fig.savefig(DOCS / "llm_fdr_by_trials.png", dpi=150)
    print(f"wrote {DOCS / 'llm_attack_results.json'}")
    print(f"wrote {DOCS / 'llm_attack_results.md'}")
    print(f"wrote {DOCS / 'llm_fdr_by_trials.png'}")


if __name__ == "__main__":
    main()
