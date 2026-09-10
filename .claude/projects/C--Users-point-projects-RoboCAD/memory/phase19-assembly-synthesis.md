---
name: phase19-assembly-synthesis
description: "Phase 19 shipped mechanical assembly synthesis with mate inference, kinematic solver, collision checks, joint-aware MJCF/URDF export, browser replay, and a default parallel-jaw prismatic gripper — 251/251 tests passing."
metadata: 
  node_type: memory
  type: project
  originSessionId: 49cf34d8-b8ab-4bdb-a372-7913c215a0bb
  modified: 2026-08-29T04:34:16.172Z
---

# Phase 19 — Mechanical Assembly Synthesis

**Shipped:** 2026-08-29.

## What changed

- `ai_cad/part_families.py` now exposes an `Interface` library on every part family, with type (`mount`, `pin`, `bore`, `slot`, `flange`, `face`) and `mate_hint` (`fixed`, `revolute`, `prismatic`, `concentric`, `coincident`). Legacy `interface_csys` is auto-converted for backward compatibility.
- `ai_cad/mate_inference.py` is a deterministic, rule-first engine that matches interfaces between instances and emits both `Mate` and `KinematicJoint` objects. It has a thin LLM fallback hook that is disabled by default for tests.
- `ai_cad/assembly.py` solver was extended to handle `revolute` and `prismatic` mates, detect overconstrained assemblies, and sample range-of-motion poses via `sample_assembly_poses()`.
- `ai_cad/assembly_collision.py` builds per-instance trimesh meshes from the solved pose graph and runs pairwise proximity + boolean-intersection checks, returning clearance/interference classification.
- `ai_cad/geda_bridge/exporter.py` now reads `Assembly.joints` and writes hierarchy-aware URDF/MJCF with real joints, actuators, and sensors.
- `ai_cad/composer.py` automatically calls mate inference for mechanical assemblies, so `/generate?decompose=True` now produces articulated mechanisms when the intent implies motion. The default `robot arm with gripper` layout now synthesizes a true parallel-jaw **prismatic gripper** attached to the forearm, verified by `tests/test_composer.py::test_compose_robot_arm_has_prismatic_gripper`.
- Backend endpoints added:
  - `POST /designs/{id}/synthesize-assembly`
  - `POST /designs/{id}/assembly-collision`
  - `GET /designs/{id}/assembly-poses`
- Frontend panels added:
  - `AssemblyReplayPanel.jsx` — lightweight range-of-motion player.
  - `AssemblyCollisionPanel.jsx` — pairwise clearance/interference status.
- New tests:
  - `tests/test_mate_inference.py`
  - `tests/test_kinematic_solver.py`
  - `tests/test_assembly_collision.py`
  - `tests/test_geda_bridge_mechanism.py`
  - endpoint coverage in `tests/test_web_backend.py`

## Test count

Full pytest suite: **251/251 passing**.

## Honest scope / caveats

- The kinematic solver is iterative relaxation, not a full analytical closed-loop solver; it is sufficient for the robot-arm/gripper/diff-drive demos and flags overconstrained assemblies.
- Browser replay is a geometry-only pose table, not a live MuJoCo WASM simulation.
- Closed-loop four-bar linkages and gear trains are not explicitly synthesized; they will be addressed in later phases.

## Why it matters

Phase 19 turns RoboCAD from a parts-and-fixed-assemblies tool into a mechanism-synthesis tool. A single prompt like “robot arm with gripper” now produces parts, mates, joints, a MuJoCo-loadable URDF, and a browser replay of the range of motion.

## How to apply

- Run the full suite with `pytest -q`.
- Test a mechanical system prompt with `python -m uvicorn web.backend.main:app` and hit `POST /generate?decompose=True` or the new assembly endpoints.
- Extend `ai_cad/part_families.py` interfaces when adding new mechanical families.

## Related

- [[phase18-decomposition-part-families]] — the Phase 18 foundation this builds on.
- [[phase20-aero-thermal-propulsion]] — Phase 20 (aero/thermal/propulsion geometry) complete.
- [[phase21-electronics-mechatronics]] — Phase 21 (electronics/mechatronics integration) complete.
- [[phase22-multi-physics-verification]] — Phase 22 (multi-physics verification engine) complete; Phase 23 — humanoid/full-robot synthesis — is next.
