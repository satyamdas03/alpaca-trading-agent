"""Monitor progress of concurrent per-defense LLM sweep jobs.

Usage:
    uv run python scripts/monitor_llm_sweeps.py

Reads docs/paper/*_llm_attack_results.json and reports completion.
"""

import json
from pathlib import Path


def main() -> None:
    docs = Path("docs/paper")
    files = sorted(docs.glob("*_llm_attack_results.json"))
    if not files:
        print("no per-defense result files found yet")
        return

    total_mean = 0
    total_reps = 0
    rows = []
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        r = data.get("result", {})
        rows.append(
            (
                data.get("defense", "?"),
                data.get("model", "?"),
                data.get("trials", 0),
                data.get("reps", 0),
                r.get("mean_false_certs", None),
                r.get("any_false_cert_rate", None),
            )
        )
        if r.get("mean_false_certs") is not None:
            total_mean += r["mean_false_certs"]
            total_reps += 1

    print(f"found {len(files)} result file(s):\n")
    print(f"{'defense':<18} {'model':<14} {'trials':>6} {'reps':>4} {'mean_false':>10} {'any_rate':>8}")
    print("-" * 70)
    for defense, model, trials, reps, mean, rate in rows:
        mean_str = f"{mean:.2f}" if mean is not None else "pending"
        rate_str = f"{rate:.0%}" if rate is not None else "pending"
        print(f"{defense:<18} {model:<14} {trials:>6} {reps:>4} {mean_str:>10} {rate_str:>8}")

    if total_reps:
        print(f"\noverall mean false certs across completed runs: {total_mean / total_reps:.2f}")


if __name__ == "__main__":
    main()
