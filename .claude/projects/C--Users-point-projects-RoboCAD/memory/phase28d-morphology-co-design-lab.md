---
name: phase28d-morphology-co-design-lab
description: "Morphology Co-Design Lab shipped — deterministic parametric search, scoring, world-model integration, and brain smoke tests with full test coverage."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1d150b00-d45d-4f43-9acb-a88e059db42e
  modified: 2026-09-10T01:02:20.714Z
---

**Phase 28D — Morphology Co-Design Lab is complete.**

Built and green:
- `ai_cad/morphology.py` — `MorphologySpace`, `MorphologyDimension`, `MorphologyCandidate`, `search_morphologies`, `score_candidate`, `default_space`, `save_search_results`, `load_search_results`.
- Deterministic, seedable search over limb counts, link lengths, joint ranges, and end-effector choices for `humanoid`, `quadruped`, and `manipulator_on_base` templates.
- Composite scoring from stability, reachable workspace, gait feasibility, actuator sizing, and span/height compactness, all via existing Phase 23 analysis modules.
- FastAPI endpoints in `web/backend/main.py`: `/morphology/templates`, `/morphology/search`, `/morphology/{search_id}`, `/morphology/{search_id}/candidates/{candidate_id}/simulate`.
- Frontend `MorphologyPanel.jsx` wired into `App.jsx` with template picker, dimension bounds editor, ranked results table, and brain-training smoke-test runner.
- Tests: `tests/test_morphology.py` (10) + `tests/test_morphology_api.py` (5, one slow).
- Performance fix in `ai_cad/kinematic_tree.py`: `forward_kinematics` now accepts precomputed nominal transforms, so `sample_reachable_workspace` avoids recomputing the zero-pose solve for every joint combination.

Test counts after this phase:
- Default suite: **380 passed**, 224 deselected, 3 warnings.
- Heavy/slow suite: **223 passed**, 1 xfailed, 380 deselected.
- Frontend build passes.

**Why:** Closes the Phase 28 loop by giving users a simulation-first, no-LLM morphology explorer that automatically feeds the world builder and attention-based brain training smoke test.

**How to apply:** Use `default_space(template)` + `search_morphologies(...)` for deterministic sweeps, or call the `/morphology/search` endpoint from the frontend panel. Reuse the same scoring utilities when adding new robot templates.
