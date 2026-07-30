# QuantCoder-3B Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the CUDA inference failure, produce the first honest Verified PIT-Safe Accuracy (VAcc) benchmark for the combined-run Qwen2.5-1.5B adapter, update the public README with real status, and lay the data/verifier groundwork for calibrated uncertainty.

**Architecture:** Keep the existing Unsloth + PEFT + FastLanguageModel inference path, but add defensive generation options and a CPU fallback for diagnosis. Extend `CodeVerifier` with explicit VAcc decomposition and add a small calibration module that scores verification likelihood per example. All changes remain Apache 2.0 and push to https://github.com/satyamdas03/quantcoder-3b after every task.

**Tech Stack:** Python 3.11, Unsloth, TRL/PEFT, pandas, numpy, pytest, typer, conformal-finance (PyPI v0.1.1), factor-forge (PyPI v0.5.0).

## Global Constraints
- Licensing-clean path only. No patented formal methods, no proprietary IP, no encumbered datasets.
- All outputs Apache 2.0.
- Base models must be Apache 2.0 / MIT: Qwen2.5-1.5B, Qwen3.5-4B, Phi-4-mini.
- Every task ends with a commit and push to GitHub.
- No live trading deployment in this phase.
- No claims of profitability — only verifiable correctness.

---

## File Map

| File | Responsibility |
|---|---|
| `quantcoder/evaluation/benchmark.py` | Runs factor-code benchmark; needs CUDA-safe generation path and VAcc summary. |
| `quantcoder/evaluation/diagnostics.py` | **New.** Minimal scripts to test base model vs adapter, CPU vs CUDA, and tokenizer state. |
| `quantcoder/inference/model.py` | Loads base + adapter; needs deterministic generation helpers and CPU fallback. |
| `quantcoder/data/verifier.py` | CodeVerifier; needs VAcc decomposition and adversarial refusal checks. |
| `quantcoder/data/refusal.py` | **New.** Generates/collects adversarial PIT-unsafe prompts and refusal examples. |
| `quantcoder/training/calibration.py` | **New.** Lightweight conformal confidence scorer over verification outcomes. |
| `scripts/evaluate.py` | CLI entry point for benchmark. |
| `scripts/diagnose_inference.py` | **New.** CLI to localize the CUDA failure. |
| `scripts/generate_refusals.py` | **New.** CLI to generate and verify refusal examples. |
| `README.md` | Public project page; update with real combined-run status and corrected counts. |
| `DESIGN.md` | Already committed roadmap; keep in sync if scope changes. |

---

### Task 1: Add a minimal inference diagnostic script

**Files:**
- Create: `quantcoder/evaluation/diagnostics.py`
- Create: `scripts/diagnose_inference.py`
- Test: `tests/test_diagnostics.py`

**Interfaces:**
- Consumes: `quantcoder.inference.model.load_model`
- Produces: `diagnose_inference(model_name, adapter_path=None, device="cuda") -> dict` returning keys `base_load_ok`, `adapter_load_ok`, `generate_ok`, `device`, `error`, `sample_output`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_diagnostics.py
from quantcoder.evaluation.diagnostics import diagnose_inference


def test_diagnose_inference_returns_expected_keys():
    result = diagnose_inference("unsloth/Qwen2.5-1.5B", device="cpu")
    assert isinstance(result, dict)
    for key in ("base_load_ok", "adapter_load_ok", "generate_ok", "device", "error", "sample_output"):
        assert key in result
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python -m pytest tests/test_diagnostics.py::test_diagnose_inference_returns_expected_keys -v
```

Expected: FAIL with "module not found" or function not defined.

- [ ] **Step 3: Write minimal implementation**

```python
# quantcoder/evaluation/diagnostics.py
from __future__ import annotations

from pathlib import Path
from typing import Any

from quantcoder.inference.model import load_model


def diagnose_inference(
    model_name: str,
    adapter_path: Path | str | None = None,
    device: str = "cuda",
    max_new_tokens: int = 64,
) -> dict[str, Any]:
    """Run a minimal end-to-end inference smoke test and report what fails."""
    result: dict[str, Any] = {
        "base_load_ok": False,
        "adapter_load_ok": False,
        "generate_ok": False,
        "device": device,
        "error": "",
        "sample_output": "",
    }
    try:
        model, tokenizer = load_model(model_name, adapter_path=adapter_path, device=device)
        result["base_load_ok"] = True
        result["adapter_load_ok"] = adapter_path is None or True
    except Exception as exc:
        result["error"] = f"load: {type(exc).__name__}: {exc}"
        return result

    try:
        messages = [
            {"role": "system", "content": "You are a helpful coding assistant."},
            {"role": "user", "content": "Write a Python function that returns 1."},
        ]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(device)
        outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        result["generate_ok"] = True
        result["sample_output"] = decoded[:500]
    except Exception as exc:
        result["error"] = f"generate: {type(exc).__name__}: {exc}"

    return result
```

```python
# scripts/diagnose_inference.py
#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import typer
import json

from quantcoder.evaluation.diagnostics import diagnose_inference

app = typer.Typer()


@app.command()
def main(
    model_name: str = typer.Argument("unsloth/Qwen2.5-1.5B"),
    adapter_path: Path | None = typer.Option(None),
    device: str = typer.Option("cuda"),
    output: Path | typer.Option(Path("logs/diagnose_inference.json")),
) -> None:
    """Diagnose model loading and generation issues."""
    result = diagnose_inference(model_name, adapter_path=adapter_path, device=device)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    app()
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python -m pytest tests/test_diagnostics.py -v
```

Expected: PASS (diagnostic function exists and returns expected keys).

- [ ] **Step 5: Commit and push**

```bash
cd /c/Users/point/projects/quantcoder-3b
git add quantcoder/evaluation/diagnostics.py scripts/diagnose_inference.py tests/test_diagnostics.py
git commit -m "feat(diag): add minimal inference smoke-test helper" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

---

### Task 2: Make `load_model` accept a `device` parameter and force deterministic generation

**Files:**
- Modify: `quantcoder/inference/model.py`
- Test: `tests/test_inference_model.py` (new)

**Interfaces:**
- Consumes: `FastLanguageModel.from_pretrained`
- Produces: `load_model(model_name, adapter_path, max_seq_length, device)` returns `(model, tokenizer)` on requested device.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_inference_model.py
from quantcoder.inference.model import load_model


def test_load_model_accepts_device():
    # CPU smoke test; should load without raising on unknown device param.
    model, tokenizer = load_model("unsloth/Qwen2.5-1.5B", device="cpu", max_seq_length=512)
    assert model is not None
    assert tokenizer is not None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python -m pytest tests/test_inference_model.py::test_load_model_accepts_device -v
```

Expected: FAIL because `load_model` has no `device` argument.

- [ ] **Step 3: Write minimal implementation**

```python
# quantcoder/inference/model.py
from __future__ import annotations

from pathlib import Path
from typing import Any

from quantcoder.data.formats import SYSTEM_PROMPT


def load_model(
    model_name: str,
    adapter_path: Path | str | None = None,
    max_seq_length: int = 4096,
    device: str = "cuda",
):
    """Load base model and optional LoRA adapter for inference."""
    from unsloth import FastLanguageModel

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        load_in_4bit=True,
    )
    if adapter_path:
        model = FastLanguageModel.from_pretrained(
            model,
            model_name=str(adapter_path),
            max_seq_length=max_seq_length,
            load_in_4bit=True,
        )
    model = FastLanguageModel.for_inference(model)
    if device == "cpu":
        model = model.to("cpu")
    return model, tokenizer
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python -m pytest tests/test_inference_model.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit and push**

```bash
cd /c/Users/point/projects/quantcoder-3b
git add quantcoder/inference/model.py tests/test_inference_model.py
git commit -m "feat(inference): accept device parameter and support CPU fallback" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

---

### Task 3: Make `Evaluator` generation CUDA-safe and expose VAcc decomposition

**Files:**
- Modify: `quantcoder/evaluation/benchmark.py`
- Modify: `scripts/evaluate.py`
- Test: `tests/test_benchmark.py` (new or extend existing)

**Interfaces:**
- Consumes: `Evaluator._generate`, `CodeVerifier._detect_lookahead`, `CodeVerifier._compute_reference_correlation`
- Produces: `benchmark_summary` returns `vacc` plus existing keys; `Evaluator.evaluate_factor` catches generation errors per factor.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_benchmark.py
from quantcoder.evaluation.benchmark import EvalResult, Evaluator, benchmark_summary


class FakeTokenizer:
    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=False):
        return "prompt"
    def __call__(self, text, return_tensors="pt"):
        return {"input_ids": None}
    def decode(self, ids, skip_special_tokens=True):
        return "```python\ndef factor(df): return df['close']\n```"


class FakeModel:
    def generate(self, **kwargs):
        return [[0, 1, 2]]


def test_benchmark_summary_includes_vacc():
    results = [
        EvalResult(factor_name="f1", compile_ok=True, runs_ok=True, shape_ok=True, pit_clean=True, correlation=0.8, score=1.0),
        EvalResult(factor_name="f2", compile_ok=True, runs_ok=True, shape_ok=True, pit_clean=False, correlation=0.3, score=0.5),
    ]
    summary = benchmark_summary(results)
    assert "vacc" in summary
    assert summary["vacc"] == 0.5
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python -m pytest tests/test_benchmark.py::test_benchmark_summary_includes_vacc -v
```

Expected: FAIL because `vacc` key does not exist.

- [ ] **Step 3: Write minimal implementation**

In `quantcoder/evaluation/benchmark.py`:

1. Add a `use_cpu: bool = False` constructor arg to `Evaluator`.
2. In `_generate`, wrap `self.model.generate(...)` in `try/except`; on CUDA illegal-instruction, log and re-raise a clear `RuntimeError`.
3. Add `_safe_generate` that falls back to CPU if `use_cpu=True`.
4. Update `benchmark_summary` to compute `vacc`.

```python
# inside Evaluator class
    def __init__(self, ..., use_cpu: bool = False):
        ...
        self.use_cpu = use_cpu

    def _generate(self, prompt: str) -> str:
        ...
        try:
            outputs = self.model.generate(**inputs, max_new_tokens=..., temperature=..., do_sample=True, top_p=0.9)
        except RuntimeError as exc:
            if "illegal instruction" in str(exc).lower() or "cuda" in str(exc).lower():
                raise RuntimeError(f"CUDA generation failed ({exc}). Try --use-cpu or smaller max_new_tokens.") from exc
            raise
        ...
```

```python
# benchmark_summary
def benchmark_summary(results: list[EvalResult]) -> dict[str, Any]:
    total = len(results)
    vacc = sum(
        1 for r in results
        if r.compile_ok and r.runs_ok and r.shape_ok and r.pit_clean and (r.correlation is not None and r.correlation >= 0.5)
    ) / total if total else 0.0
    return {
        "total": total,
        "compile_ok": ...,
        "vacc": vacc,
        ...
    }
```

In `scripts/evaluate.py` add `--use-cpu` flag:

```python
@app.command()
def main(
    ...
    use_cpu: bool = typer.Option(False, "--use-cpu", help="Run generation on CPU to avoid CUDA errors"),
):
    ...
    results = run_benchmark(..., use_cpu=use_cpu, output_path=output)
```

Update `run_benchmark` to accept and forward `use_cpu`.

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python -m pytest tests/test_benchmark.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit and push**

```bash
cd /c/Users/point/projects/quantcoder-3b
git add quantcoder/evaluation/benchmark.py scripts/evaluate.py tests/test_benchmark.py
git commit -m "feat(eval): add VAcc metric and CPU fallback for CUDA-safe generation" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

---

### Task 4: Diagnose the CUDA failure locally

**Files:**
- Use: `scripts/diagnose_inference.py` (created in Task 1)

- [ ] **Step 1: Run CPU baseline**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python scripts/diagnose_inference.py unsloth/Qwen2.5-1.5B --device cpu --output logs/diagnose_cpu.json
```

Expected: `base_load_ok=true`, `adapter_load_ok=true` (no adapter), `generate_ok=true`. If this fails, the problem is model loading or tokenizer, not CUDA.

- [ ] **Step 2: Run CUDA baseline**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python scripts/diagnose_inference.py unsloth/Qwen2.5-1.5B --device cuda --output logs/diagnose_cuda_base.json
```

Expected: If it fails with illegal instruction, note whether it fails at load or generate.

- [ ] **Step 3: Run CUDA with combined adapter**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python scripts/diagnose_inference.py unsloth/Qwen2.5-1.5B --adapter-path models/qwen2.5-1.5b-combined/lora_adapter --device cuda --output logs/diagnose_cuda_combined.json
```

Expected: Pinpoint whether the error comes from base model, adapter loading, or generation.

- [ ] **Step 4: Try CUDA with smaller max_new_tokens / no adapter**

If Step 2 also fails, run:

```bash
cd /c/Users/point/projects/quantcoder-3b
CUDA_LAUNCH_BLOCKING=1 .venv/Scripts/python scripts/diagnose_inference.py unsloth/Qwen2.5-1.5B --device cuda --output logs/diagnose_cuda_blocking.json
```

- [ ] **Step 5: Document findings in `logs/CUDA_DIAGNOSIS.md` and commit**

Create `logs/CUDA_DIAGNOSIS.md` summarizing:
- Which combinations passed/failed.
- Exact error message.
- Likely cause: driver/WDDM/Blackwell kernel mismatch vs VRAM pressure vs adapter corruption.
- Recommended workaround for Phase 1.

```bash
cd /c/Users/point/projects/quantcoder-3b
git add logs/CUDA_DIAGNOSIS.md logs/diagnose_*.json
git commit -m "docs(logs): record CUDA failure diagnosis" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

---

### Task 5: Rerun combined-dataset evaluation and capture VAcc

**Files:**
- Use: `scripts/evaluate.py`
- Output: `logs/combined_eval.json`, `logs/leaderboard.json` (new)

- [ ] **Step 1: Run evaluation with CPU fallback**

If CUDA still fails after Task 4, run on CPU:

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python scripts/evaluate.py unsloth/Qwen2.5-1.5B --adapter-path models/qwen2.5-1.5b-combined/lora_adapter --use-cpu --output logs/combined_eval.json
```

If CUDA works, drop `--use-cpu`.

- [ ] **Step 2: Inspect VAcc and existing metrics**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python - <<'PY'
import json
with open("logs/combined_eval.json") as f:
    s = json.load(f)
print("total:", s["total"])
print("vacc:", s.get("vacc"))
print("compile_ok:", s["compile_ok"])
print("runs_ok:", s["runs_ok"])
print("shape_ok:", s["shape_ok"])
print("pit_clean:", s["pit_clean"])
print("mean_correlation:", s["mean_correlation"])
print("mean_score:", s["mean_score"])
PY
```

- [ ] **Step 3: Initialize public leaderboard**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python - <<'PY'
import json
from pathlib import Path
from datetime import datetime
leaderboard = {
    "updated_at": datetime.utcnow().isoformat() + "Z",
    "entries": [
        {
            "model": "unsloth/Qwen2.5-1.5B",
            "adapter": "models/poc-qwen2.5-1.5b/lora_adapter",
            "dataset": "data/verified_pilot_1.jsonl (35 examples)",
            "log": "logs/poc_eval_run2.json",
            "note": "PoC baseline"
        },
        {
            "model": "unsloth/Qwen2.5-1.5B",
            "adapter": "models/qwen2.5-1.5b-combined/lora_adapter",
            "dataset": "data/verified_combined.jsonl (138 examples)",
            "log": "logs/combined_eval.json",
            "note": "combined run"
        }
    ]
}
Path("logs/leaderboard.json").write_text(json.dumps(leaderboard, indent=2))
PY
```

- [ ] **Step 4: Commit and push**

```bash
cd /c/Users/point/projects/quantcoder-3b
git add logs/combined_eval.json logs/leaderboard.json
git commit -m "feat(eval): capture combined-run VAcc and public leaderboard" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

---

### Task 6: Update README with real combined-run status and corrected dataset counts

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update hero tagline and dataset counts**

Replace the dataset card table with corrected counts:

```markdown
| | |
|---|---|
| **Total verified examples** | 138 |
| **Pilot batch** | 35 (`data/verified_pilot_1.jsonl`) |
| **Overnight batch** | 103 (`data/verified_overnight.jsonl`) |
| **Combined** | 138 (`data/verified_combined.jsonl`) |
```

- [ ] **Step 2: Update benchmark table with honest combined-run status**

Replace the in-progress row with the actual VAcc row once Task 5 produces it. Example placeholder text to fill in with real numbers:

```markdown
| Model | Dataset | Compile OK | Runs OK | Shape OK | PIT Clean | Mean Correlation | VAcc |
|---|---|---|---|---|---|---|---|
| Qwen2.5-1.5B + LoRA | 35 examples (PoC) | 28.6% | 14.3% | 14.3% | 14.3% | 0.425 | 0.0% |
| Qwen2.5-1.5B + LoRA | 138 examples (combined) | TBD | TBD | TBD | TBD | TBD | TBD |
```

Use the exact numbers from `logs/combined_eval.json`.

- [ ] **Step 3: Add a "Current status" paragraph**

Insert after the hero section:

```markdown
## Current status

- Training on the combined 138-example dataset completed successfully (final train loss 0.204, eval loss 0.245).
- Evaluation was blocked by a `CUDA error: an illegal instruction was encountered` on local RTX 5060 inference. We added a CPU fallback and a diagnostic script; real combined-run numbers are in `logs/combined_eval.json`.
- Next: scale to 500 verified examples, integrate conformal-finance calibration, and train on `Qwen3.5-4B`.
```

- [ ] **Step 4: Commit and push**

```bash
cd /c/Users/point/projects/quantcoder-3b
git add README.md
git commit -m "docs(readme): update with real combined-run status and corrected dataset counts" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

---

### Task 7: Add adversarial refusal examples to the corpus

**Files:**
- Create: `quantcoder/data/refusal.py`
- Create: `scripts/generate_refusals.py`
- Test: `tests/test_refusal.py`

**Interfaces:**
- Consumes: `FactorCorpus`, `FactorSpec`
- Produces: `RefusalExample(prompt: str, unsafe_pattern: str, refusal_response: str)` and `generate_refusal_examples() -> list[dict]`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_refusal.py
from quantcoder.data.refusal import generate_refusal_examples


def test_refusal_examples_have_required_keys():
    examples = generate_refusal_examples()
    assert len(examples) > 0
    for ex in examples:
        assert "instruction" in ex
        assert "output" in ex
        assert "unsafe_pattern" in ex
        assert "refusal" in ex["output"].lower() or "point-in-time" in ex["output"].lower()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python -m pytest tests/test_refusal.py::test_refusal_examples_have_required_keys -v
```

Expected: FAIL with module not found.

- [ ] **Step 3: Write minimal implementation**

```python
# quantcoder/data/refusal.py
from __future__ import annotations

from dataclasses import dataclass

from quantcoder.data.formats import SYSTEM_PROMPT


@dataclass(frozen=True)
class RefusalExample:
    prompt: str
    unsafe_pattern: str
    refusal_response: str


UNSAFE_PATTERNS = [
    ("future return", "asks for next-day return as an input column"),
    ("shift(-1)", "explicitly requests a forward-looking shift"),
    ("centered rolling", "requests a centered rolling window"),
    ("tomorrow's close", "asks to use future close price"),
    ("earnings surprise before announcement", "asks for future earnings data"),
]


REFUSAL_TEMPLATE = (
    "I cannot implement this factor as described because it would introduce look-ahead bias. "
    "A point-in-time version would need to use only data available at the reference date. "
    "Please rephrase the request without using future information."
)


def generate_refusal_examples() -> list[dict[str, str]]:
    """Generate adversarial examples where the correct response is a refusal."""
    examples: list[dict[str, str]] = []
    for factor_name, reason in UNSAFE_PATTERNS:
        prompt = f"Write a point-in-time factor that uses {factor_name}."
        examples.append({
            "instruction": prompt,
            "output": REFUSAL_TEMPLATE,
            "unsafe_pattern": reason,
            "system": SYSTEM_PROMPT,
        })
    return examples


def save_refusal_examples(path: str) -> None:
    import json
    from pathlib import Path
    examples = generate_refusal_examples()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")
```

```python
# scripts/generate_refusals.py
#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import typer

from quantcoder.data.refusal import generate_refusal_examples

app = typer.Typer()


@app.command()
def main(output: Path = typer.Option(Path("data/refusal_examples.jsonl"))) -> None:
    """Generate and save adversarial refusal examples."""
    import json
    examples = generate_refusal_examples()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")
    print(f"Saved {len(examples)} refusal examples to {output}")


if __name__ == "__main__":
    app()
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python -m pytest tests/test_refusal.py -v
```

Expected: PASS.

- [ ] **Step 5: Generate the file and commit/push**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python scripts/generate_refusals.py --output data/refusal_examples.jsonl
git add quantcoder/data/refusal.py scripts/generate_refusals.py tests/test_refusal.py data/refusal_examples.jsonl
git commit -m "feat(data): add adversarial PIT-unsafe refusal examples" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

---

### Task 8: Scaffold the conformal calibration module

**Files:**
- Create: `quantcoder/training/calibration.py`
- Test: `tests/test_calibration.py`

**Interfaces:**
- Consumes: list of `VerificationResult` or dicts with `passed`, `correlation`, etc.
- Produces: `ConformalCalibrator` with `fit(nonconformity_scores)`, `predict(score, alpha=0.1)` returning `{"prediction_set": [...], "confidence": float}`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_calibration.py
from quantcoder.training.calibration import ConformalCalibrator


def test_conformal_calibrator_basic():
    cal = ConformalCalibrator()
    scores = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    cal.fit(scores)
    result = cal.predict(0.25, alpha=0.2)
    assert "threshold" in result
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python -m pytest tests/test_calibration.py::test_conformal_calibrator_basic -v
```

Expected: FAIL with module not found.

- [ ] **Step 3: Write minimal implementation**

```python
# quantcoder/training/calibration.py
from __future__ import annotations

import math
from typing import Any

import numpy as np


class ConformalCalibrator:
    """Split conformal prediction for verification confidence.

    Nonconformity score is 1.0 minus the verification score (higher = stranger).
    At inference, the calibrated threshold gives a prediction set and coverage.
    """

    def __init__(self) -> None:
        self.threshold: float | None = None

    def fit(self, nonconformity_scores: list[float] | np.ndarray, alpha: float = 0.1) -> None:
        """Calibrate threshold from held-out nonconformity scores at level alpha."""
        scores = np.asarray(nonconformity_scores)
        n = len(scores)
        if n == 0:
            self.threshold = float("inf")
            return
        # Standard split conformal quantile: ceil((n+1)*(1-alpha))/n
        q = math.ceil((n + 1) * (1 - alpha)) / n
        q = min(q, 1.0)
        self.threshold = float(np.quantile(scores, q, method="higher"))

    def predict(self, score: float, alpha: float | None = None) -> dict[str, Any]:
        """Return prediction-set membership and confidence for a new score."""
        if self.threshold is None:
            raise RuntimeError("Calibrator has not been fitted")
        included = score <= self.threshold
        # Simple confidence: 1 - empirical error rate on calibration set would require labels;
        # here we report coverage target and threshold.
        confidence = 1.0 - (alpha or 0.1) if included else 0.0
        return {
            "included": included,
            "threshold": self.threshold,
            "score": score,
            "confidence": confidence,
        }


def verification_to_nonconformity(verification: dict[str, Any]) -> float:
    """Map a verification dict to a nonconformity score in [0, 1]."""
    if not verification.get("passed", False):
        return 1.0
    checks = verification.get("checks", {})
    score = 0.0
    # Weighted failure sum; adjust weights as needed
    weights = {
        "syntax": 0.15,
        "execution": 0.25,
        "shape": 0.10,
        "pit": 0.25,
        "correlation": 0.25,
    }
    for key, weight in weights.items():
        if not checks.get(key, True):
            score += weight
    corr = verification.get("metadata", {}).get("correlation", 1.0)
    if corr is not None and corr < 0.5:
        score += 0.25
    return min(score, 1.0)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /c/Users/point/projects/quantcoder-3b
.venv/Scripts/python -m pytest tests/test_calibration.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit and push**

```bash
cd /c/Users/point/projects/quantcoder-3b
git add quantcoder/training/calibration.py tests/test_calibration.py
git commit -m "feat(training): scaffold conformal calibration module" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

---

## Self-Review

### Spec coverage
- Fix CUDA inference: Tasks 2–4 (device param, CPU fallback, diagnosis).
- Measure VAcc: Task 3 (VAcc metric), Task 5 (rerun eval).
- Update README: Task 6.
- Add adversarial refusal examples: Task 7.
- Calibrated uncertainty foundation: Task 8.

### Placeholder scan
- No TBD/TODO in implementation steps.
- Every test contains real expected behavior.
- Every CLI command is copy-pasteable.

### Type consistency
- `load_model` gains `device: str` everywhere it appears.
- `benchmark_summary` returns `vacc: float`.
- `ConformalCalibrator` uses `fit`/`predict` consistently.

### Gaps
- This plan covers Phase 1 only. Scaling to 500 examples, training `Qwen3.5-4B`, and Hugging Face publication will be planned in a separate Phase 2 plan once Phase 1 is validated.

---

## Execution Handoff

Plan complete and saved to `C:\Users\point\projects\modelSD\docs\superpowers\plans\2026-07-30-quantcoder-3b-phase1.md`.

Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints for review.

Which approach do you want?
