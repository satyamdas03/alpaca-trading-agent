---
name: phase23-hotfix-memory-cpu-hardening
description: Phase 23 hotfix eliminating RAM/CPU hotspots before continuing humanoid/robot synthesis.
metadata: 
  node_type: memory
  type: project
  originSessionId: 7435fc68-ca4e-4484-976a-3e6e62f81195
  modified: 2026-09-01T02:10:33.906Z
---

# Phase 23 Hotfix — Memory / CPU Hardening (2026-09-01)

Before continuing Phase 23 humanoid/full-robot feature work, we fixed the RAM/CPU hotspots that were suspected of crashing the system.

## Hotspots fixed

| Hotspot | File(s) | Fix |
|---|---|---|
| Unbounded verification cache | `ai_cad/verification.py` | Replaced `_REPORTS: dict` with `_TimedLRUCache(maxsize=128, ttl=600)`. |
| Repeated mesh loads per request | `ai_cad/verification.py`, `ai_cad/mesh_quality.py` | Added `_MeshCache` so the STL is loaded once per `run_verification` call and shared across backends. `check_mesh_quality()` now accepts a pre-loaded mesh. |
| Executor temp-file growth | `ai_cad/executor.py` | Delete `generated_*.py` and `error_*.txt` on success; remove stale artifacts older than 24h in `output/executions`. |
| Per-part subprocess rebuild | `ai_cad/geda_bridge/exporter.py` | Added part-level mesh cache keyed by `(part.id, param_hash, tolerance)` inside `export_bundle_from_tree()`. |
| Double mesh copies | `ai_cad/geda_bridge/exporter.py` | Refactored to one copy per part: scale to meters, compute inertial, then export. |
| O(N²) assembly collision | `ai_cad/assembly_collision.py` | Lowered default `samples` to 500, added `max_instances=50` guard, added AABB culling, kept shared part meshes. |
| Kinematic recursion hazard | `ai_cad/kinematic_tree.py` | Added `recursion_seen` set guard in `forward_kinematics()` to break cyclic joint graphs safely. |
| Three.js viewer leaks | `web/frontend/src/components/STLViewer.jsx` | Dispose `BufferGeometry`/material on unmount/URL change and invalidate `THREE.Cache` for prior designs. |

## Tests added

- `tests/test_executor.py` — temp cleanup on success, artifact retention on failure.
- `tests/test_verification_api.py` — verification cache stays bounded.
- `tests/test_assembly_collision.py` — AABB culling and `max_instances` guard.
- `tests/test_geda_bridge.py` — duplicate part instances reuse one built mesh.
- `tests/test_kinematic_tree.py` — cyclic joint graph does not hang.

## Validation

- Backend default suite (excluding the pre-existing Phase 23 WIP failure): **125 passing**.
- Backend heavy/slow suite: **212 passing**.
- Frontend: `npm run build` passes.
- Phase 23 WIP failures were resolved in `phase23-humanoid-robot-synthesis.md`; full suite now **357/357 passing**.
- Commit: `6f9e61a`.
- Subsequent Phase 23 robot-template bugs fixed in commit `b5ef502`; full suite now 357/357.

## Pre-existing issue discovered

`tests/test_phase23_humanoid.py::test_forward_kinematics_zero_pose` and `test_get_joint_chain` originally failed with the Phase 23 WIP code. This was **not caused by the hotfix**; reverting only `ai_cad/kinematic_tree.py` still left those tests failing. They were fixed when resuming Phase 23 robot-template work — see [[phase23-humanoid-robot-synthesis]].

**Why this matters:** Eliminating the hotspots makes the backend stable enough to continue Phase 23 work without crashes from runaway caches, duplicate mesh builds, or unbounded collision checks.

**How to apply:** Keep the new guardrails (cache bounds, AABB cull, max_instances, cycle guard) when extending Phase 23. Do not reintroduce module-level unbounded dicts or per-instance mesh rebuilds.

## Related memories

- [[phase22-multi-physics-verification]] — previous phase baseline (330/330 tests).
- [[phase23-humanoid-robot-synthesis]] — Phase 23 robot synthesis completed after this hotfix.
