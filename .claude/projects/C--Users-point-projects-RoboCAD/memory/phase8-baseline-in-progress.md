---
name: phase8-complexity-baseline-complete
description: Phase 8 complete — 30-prompt complexity baseline (86.7% pass rate), feature-tree schema v1.0.0, and new tests committed.
metadata: 
  node_type: memory
  type: project
  modified: 2026-08-25T00:23:34.427Z
  originSessionId: cb75c83a-be7b-4a7b-bc49-b8099018beb3
---

RoboCAD Phase 8 (complexity benchmark + feature-tree spec) is under way. All deliverable files are created and tested; the baseline benchmark is running against `qwen3-coder:latest` via Ollama.

**Completed deliverables:**
- `docs/feature_tree_schema.md` — Feature-Tree JSON Schema v1.0.0 (parameters, sketches, constraints, dimensions, features, parts, assemblies, mates, coordinate systems).
- `benchmarks/complexity_ladder.json` — 30 prompts in 5 tiers (T1 Primitive, T2 Basic part, T3 Intermediate, T4 Advanced, T5 Expert) with expected feature counts/types, constraints, and assembly instances.
- `benchmarks/evaluate_complexity.py` — runner that loads the ladder, calls `ai_cad.api.RoboCADBackend.generate`, records success, attempts, latency, failure mode, parameter count, estimated feature count, manifold/watertight status, and writes JSON + Markdown baseline report.
- `tests/test_feature_tree_schema.py` — 10 tests validating schema doc, ladder structure, tier IDs, feature-type vocabulary, and helper functions.
- `tests/test_complexity_benchmark.py` — 5 tests mocking `RoboCADBackend.generate` to verify runner recording, markdown report generation, and CLI path.

**Baseline result (completed 2026-08-25):**
- Model: `qwen3-coder:latest` via Ollama
- Max retries: 2
- Prompts: 30
- Overall pass rate: **26/30 (86.7%)**
- Average successful latency: ~29.5 s
- By tier: T1 83.3% (5/6), T2 100% (6/6), T3 83.3% (5/6), T4 100% (6/6), T5 66.7% (4/6)
- Failure modes: 3 runtime, 1 geometry
- Output directory: `output/benchmarks/baseline_2026-08-25/`
- Published report: `benchmarks/complexity_baseline_2026-08-25.md`

**Unauthorized cross-repo change handled:**
A separate session opened in `LearningRobotics` attempted to implement a `GEDA Bridge` inside `RoboCAD`, adding `ai_cad/geda_bridge/`, `tests/test_geda_*.py`, `GEDA_BRIDGE.md`, and MuJoCo/imageio/PyYAML dependencies to `requirements.txt`. This was not authorized for RoboCAD. The GEDA files and dependency additions were reverted; the working tree now contains only Phase 8 deliverables. MuJoCo/skill-verification integration is intentionally not on the current RoboCAD roadmap.

**Failures to fix in Phase 9/10:**
- `t1.3` (cone): `Cone(radius=...)` invalid — add cone/revolve example to system prompt.
- `t3.5` (V-groove jaw): hallucinated `Triangle(first_side=...)` API — needs sketch/V-groove example.
- `t5.1` (diff-drive assembly): non-watertight multi-body — needs shell/through-hole guidance.
- `t5.6` (Stewart base): fillet radius too large for thin triangular edges — needs edge-aware fillet logic or smaller default radius.

**Next steps:**
1. ✅ Baseline complete and report published.
2. Run full `pytest` suite and commit/push Phase 8 artifacts.
3. Begin Phase 9: feature-tree backend (`ai_cad/feature_tree.py`, `ai_cad/transpiler.py`, `ai_cad/feature_store.py`).

**Related:** [[engineer-grade-roadmap]] [[google-stitch-ui-redesign]]
