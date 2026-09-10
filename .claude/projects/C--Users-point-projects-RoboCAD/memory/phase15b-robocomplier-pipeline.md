---
name: phase15b-robocomplier-pipeline
description: "Phase 15B RoboCompiler asset pipeline complete with skill recommendation, variant sweep, and trainable push-policy smoke test."
metadata: 
  node_type: memory
  type: project
  originSessionId: cc84a825-3379-4cbc-8b8e-11c76e9783d4
  modified: 2026-08-27T12:00:42.509Z
---

Phase 15B shipped end-to-end on 2026-08-27. It is the final PATH1 / GEDA Bridge milestone before moving to PATH2 (voice/world-model layers).

**What was built:**
- `ai_cad/geda_bridge/skill_recommend.py` — maps skill descriptions to scene templates + default policy configs.
- `ai_cad/geda_bridge/variant_sweep.py` — sweeps feature-tree parameters, exports each variant as a verified bundle, and reports aggregate validity/stability.
- `ai_cad/geda_bridge/skill_smoke.py` — NumPy-only CEM-trained TinyMLP policy for a `wedge_push_block`-derived push scene.
- Backend endpoints: `POST /designs/{id}/recommend-skill`, `POST /designs/{id}/train-skill`, `GET /designs/{id}/skills`, `POST /designs/{id}/variant-sweep`.
- Frontend: `SimulatePanel.jsx` tabs for bundle, skill training, and variant sweep.
- Tests: `tests/test_geda_bridge_skill.py` (7 tests) + 4 new backend endpoint tests in `tests/test_web_backend.py`.

**Test count:** 187/187 pytest passing.

**Honest scope boundary:** The "video" part of video → custom part → trained skill is not implemented; the milestone proves the part → trained-skill loop in simulation. Video-to-skill embedding remains future work.

**Why it matters:** It closes the AI-CAD → physics-skill loop that PATH2 needs. A generated part can now be exported, placed in a scene, and used to train a policy without leaving the RoboCAD stack.

**How to apply:**
- Use `POST /designs/{id}/recommend-skill` to discover which scene template fits a new task description.
- Use `POST /designs/{id}/variant-sweep` to explore parametric sensitivity before committing to a design.
- Use `POST /designs/{id}/train-skill` as the smoke test before claiming a new asset is "simulation ready."
- Keep the policy training hyperparameters modest in CI to avoid timeouts (default backend uses n_iters=20, pop_size=50; tests use n_iters=5, pop_size=10).

**Related memories:** [[phase15a-learning-robotics-handshake]], [[robocad-end-to-end-roadmap]], [[phase14b-scene-templates]], [[phase14a-geda-bridge]].
