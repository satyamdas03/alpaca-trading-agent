---
name: phase14a-geda-bridge
description: Phase 14A GEDA Bridge implementation progress — simulation-ready MJCF/URDF bundle exporter for RoboCAD parts and assemblies.
metadata: 
  node_type: memory
  type: project
  originSessionId: cb75c83a-be7b-4a7b-bc49-b8099018beb3
  modified: 2026-08-27T10:10:05.340Z
---

Date: 2026-08-27.

**Status:** ✅ Complete — MuJoCo runtime validation included.

**What was built:**
- `ai_cad/geda_bridge/` package:
  - `exporter.py` — `export_bundle_from_tree()` and `export_bundle_from_shape()`; shape tessellation via `build123d.Shape.tessellate()`; trimesh-based inertial computation with mm→m and density conversion; URDF and MJCF writers.
  - `packager.py` — zip the bundle directory.
  - `verifier.py` — check watertight meshes, positive mass, positive-definite inertia, and CoM inside convex hull.
  - `models.py` — Pydantic models for `BundleManifest`, `BundlePart`, `InertialData`, `BundleVerification`, `BundlePaths`.
- Fixed `ai_cad/assembly.py` duplicate-child error by switching `.move()` to `.moved()` in `transpile_assembly()`.
- Backend endpoints in `web/backend/main.py`: `POST /designs/{id}/simulate`, `GET /designs/{id}/bundle`, `GET /designs/{id}/simulation`.
- Frontend `SimulatePanel.jsx` in Kinetic Precision style + `api.js` helpers.
- `ai_cad/models.py` `ExportPaths.bundle` field.
- `requirements-dev.txt` with optional `mujoco>=3.0.0`.

**Test coverage:**
- `tests/test_geda_bridge.py` — 9 tests (cube, cylinder, L-bracket, 2-part assembly, gripper jaw, URDF/MJCF structure checks).
- `tests/test_web_backend.py` — 4 new endpoint tests.
- `tests/test_assembly.py` — duplicate-instance regression test + assertion update.
- `tests/test_geda_bridge_runtime.py` — 4 MuJoCo runtime validation tests:
  - `test_runtime_shape_cube` — cube shape loads in MJCF/URDF and simulates.
  - `test_runtime_shape_cylinder` — cylinder shape loads in MJCF/URDF and simulates.
  - `test_runtime_tree_l_bracket` — L-bracket feature-tree bundle loads and simulates.
  - `test_runtime_tree_two_part_assembly` — two-part assembly bundle loads and simulates.
- Full pytest suite: **152 passed** (was 148).

**Known gaps / next work:**
- Runtime validation with a standalone URDF loader (e.g., `yourdfpy`).
- Collision mesh simplification / convex decomposition for complex parts.
- Shared mesh reuse when multiple instances reference the same part (currently exports one STL per instance).

**Related:** [[robocad-end-to-end-roadmap]] | [[robocad-path-analysis]] | [[phase13-model-specialization]]
