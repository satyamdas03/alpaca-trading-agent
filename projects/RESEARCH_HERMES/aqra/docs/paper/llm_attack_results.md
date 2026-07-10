# Real-LLM Adaptive Experiment (Phase C) — Combined Results

Ground truth: all null. Any certification = false discovery.

| Defense | Model | Trials | Reps | Mean false certs | Any-false-cert rate | Std dev |
|---|---|---|---|---|---|---|
| naive | `claude-haiku-4-5-20251001` | 200 | 10 | 6.60 | 80% | 5.46 |
| naive | `llama3:8b` | 200 | 10 | 6.60 | 80% | 5.46 |
| metered | `llama3:8b` | 50 | 5 | 0.00 | 0% | 0.00 |
| sparse_metered | `llama3:8b` | 50 | 5 | 0.00 | 0% | 0.00 |
| maxleak_metered | `llama3:8b` | 200 | 10 | 0.00 | 0% | 0.00 |
| protocol | `llama3:8b` | 200 | 10 | 0.00 | 0% | 0.00 |
| e_bh | `llama3:8b` | 50 | 5 | 0.00 | 0% | 0.00 |
| naive | `mistral` | 30 | 3 | 1.00 | 67% | 1.00 |
| metered | `mistral` | 30 | 3 | 0.00 | 0% | 0.00 |
| sparse_metered | `mistral` | 30 | 3 | 0.00 | 0% | 0.00 |
| protocol | `mistral` | 30 | 3 | 0.00 | 0% | 0.00 |
| e_bh | `mistral` | 30 | 3 | 0.00 | 0% | 0.00 |

Run date: 2026-07-10
