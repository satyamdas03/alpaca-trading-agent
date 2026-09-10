---
name: phase15a-learning-robotics-handshake
description: Phase 15A LearningRobotics handshake — cross-repo bundle ingestion contract, reference loaders, and capability registry.
metadata:
  node_type: memory
  type: project
  originSessionId: cb75c83a-be7b-4a7b-bc49-b8099018beb3
  modified: 2026-08-27T11:16:22.863Z
---

Date: 2026-08-27.

**Status:** ✅ Complete.

**Goal:** Give `LearningRobotics` a clean, documented, tested way to consume a RoboCAD simulation bundle, load it into a standard scene, and verify physics stability.

**What was built:**
- `docs/BUNDLE_CONTRACT.md` — OpenAPI / JSON-Schema contract for bundle ingestion (manifest layout, `BundlePart`, `InertialData`, loader contract, capability registry, stability handshake test description).
- `ai_cad/geda_bridge/loader.py` — reference Python loader:
  - `load_bundle_manifest(bundle_dir)` — read and validate `manifest.json`.
  - `load_bundle_into_mujoco(bundle_dir, scene_template=None)` — load bundle asset into MuJoCo, optionally composed into a standard scene.
  - `run_stability_rollout(model, data, duration_seconds=10.0)` — run physics steps and report NaNs, max position/velocity, penetration, energy drift.
  - `stability_check_bundle(bundle_dir, scene_template, duration_seconds)` — high-level handshake helper.
  - `load_bundle_into_isaac_sim(bundle_dir, ...)` — conditional stub that fails gracefully when Isaac Sim is not installed.
- `ai_cad/geda_bridge/capabilities.py` — `get_capabilities()` registry.
- Backend endpoints in `web/backend/main.py`: `GET /capabilities`, `POST /designs/{id}/handshake`, `GET /designs/{id}/handshake`.
- Frontend `CapabilitiesPanel.jsx` integrated into `App.jsx`.
- Tests:
  - `tests/test_learningrobotics_handshake.py` — 7 tests covering manifest load, MuJoCo scene load, 10 s rollout, high-level helper, Isaac Sim stub, capabilities registry, MJCF fallback.
  - `tests/test_web_backend.py` — 2 endpoint tests for `/capabilities` and `/designs/{id}/handshake`.
- Full pytest suite: **170 passed**.

**Solvable caveats resolved (2026-08-27):**
- `ai_cad/geda_bridge/loader.py` now has a real Isaac Sim skeleton (`_build_isaac_sim_world`, `_add_isaac_sim_shape`) with local `omni.isaac.core` imports so the module still imports outside Isaac Sim.
- `.github/workflows/learningrobotics_handshake.yml` runs a nightly cross-repo handshake test against `satyamdas03/LearningRobotics`.
- `tests/test_web_backend.py` handshakes now seed a real build123d-scale wedge STL instead of the fake cube, and assert `success is True`.
- Also fixed two bugs uncovered during caveat work:
  - `ai_cad/geda_bridge/exporter.py` now writes STL meshes in meters (manifest declares `length_unit="m"`).
  - `ai_cad/geda_bridge/loader.py` casts rollout metrics to native Python scalars/bools so FastAPI can serialize them.

**Known gaps / next work:**
- Real Isaac Sim loader implementation when an Isaac Sim environment is available.
- RL policy training smoke test (Phase 15B).

**Related:** [[phase14b-scene-templates]] | [[phase14a-geda-bridge]] | [[robocad-end-to-end-roadmap]] | [[robocad-path-analysis]]
