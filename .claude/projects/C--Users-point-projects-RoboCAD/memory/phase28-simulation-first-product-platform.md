---
name: phase28-simulation-first-product-platform
description: "Phase 28 re-scoped as a simulation-first product platform — 28A/B/C complete, 28D/E/F in progress."
metadata: 
  node_type: memory
  type: project
  originSessionId: 7435fc68-ca4e-4484-976a-3e6e62f81195
  modified: 2026-09-10T02:57:30.663Z
---

# Phase 28 — Simulation-first product platform

**Date:** 2026-09-08
**Status:** 28A/B/C/D/E/F complete

## Overview

Phase 28 was re-scoped from pure packaging/distribution into a **simulation-first product platform**. The goal is to let a new user go from launcher to generated part or verified simulation asset in under 10 minutes, and to run real physics checks on generated designs.

## Sub-phases

- ✅ **28A — Launcher + health CLI + installer skeleton**
  - Files: `robocad/launcher.py`, `robocad/health.py`, `robocad/__main__.py`, `start.py`, `start.bat`, `start.sh`, `scripts/build_installer.py`.
  - Tests: `tests/test_launcher.py`, `tests/test_build_installer.py` — **13/13 passing**.
  - Entry point: `python start.py` or `python -m robocad.health`.

- ✅ **28B — Asset marketplace**
  - Files: `ai_cad/marketplace.py`, `marketplace/index.json`, `marketplace/starter_packs/`, `web/frontend/src/components/MarketplacePanel.jsx`.
  - Tests: `tests/test_marketplace.py` — **5/5 passing**.
  - Starter packs: bracket part, `gripper_cube_grasp` scene, `manipulator_on_base` robot template.
  - Direct archive upload added in 28F.

- ✅ **28C — Deep multi-physics engine**
  - Files: `ai_cad/solvers/*`, backend deep-verify endpoints, frontend "Deep Analysis" tab.
  - Tests: `tests/test_solver_*.py`, `tests/test_deep_verify_api.py` — **64/64 passing**.
  - Solvers: CalculiX (FEA), ElmerFEM (thermal), OpenFOAM (CFD), NVIDIA surrogate (fast analysis).
  - Real-solver dispatch + field extraction added in 28E.

- ✅ **28D — Morphology co-design lab**
  - Files: `ai_cad/morphology.py`, backend `/morphology/*` endpoints, frontend `MorphologyPanel.jsx`.
  - Deterministic, seedable parametric search over limb counts, link lengths, joint ranges, and end-effector choices for `humanoid`, `quadruped`, `manipulator_on_base`.
  - Composite scoring from stability, workspace reach, gait feasibility, actuator sizing, and span/height compactness.
  - World-model simulation + attention-based brain training smoke-test integration.
  - Tests: `tests/test_morphology.py` (10) + `tests/test_morphology_api.py` (5).
  - FK transform caching fix in `ai_cad/kinematic_tree.py`.

- ✅ **28E — Simulation certification**
  - Files: `ai_cad/sim_certification.py`, `ai_cad/solvers/field_export.py`, `ai_cad/solvers/report_export.py`, backend `/sim-cert` and `/deep-verify/{job_id}/field|report.md` endpoints, viewer heatmap overlay.
  - Real-vs-surrogate A/B comparison, weighted readiness score, certificate persistence.

- ✅ **28F — Product hardening + final docs**
  - Files: `scripts/setup_solvers.py`, `docs/SOLVER_INSTALL.md`, `tests/test_onboarding.py`, `tests/test_health.py`, `tests/test_setup_solvers.py`.
  - Solver install bootstrap, health install hints, onboarding smoke tests, marketplace upload wiring.

## Test counts

- Full default pytest suite: **380 passing, 224 deselected** (1 expected failure, 5 benchmark/network tests deselected).
- Heavy/slow pytest suite: **223 passing, 1 xfailed**.
- Marketplace + solver tests: **64 passing**.
- Morphology tests: **15 passing**.
- Frontend `npm run build`: passes (chunk-size warning only).

## End-to-end verification (2026-09-01)

- ✅ `python -m robocad.health` runs and reports environment, API keys, dependencies, and solver availability with install hints.
- ✅ `python start.py --help` works.
- ✅ Backend `/health` returns `{"status":"ok"}`.
- ✅ Marketplace create/list/get/verify/import and archive-upload endpoints work.
- ✅ Deep verify submit/status endpoints work; solver availability correctly reports external solvers absent and surrogate available.
- ✅ Real solver dispatch exercised with monkeypatched subprocesses; falls back to estimates when binaries are absent.
- ✅ Simulation certification scoring and Markdown report generation verified.
- ✅ Viewer heatmap overlay wired through `STLViewer.jsx` scalar field prop.

## Related memories

- [[phase28a-launcher-health-installer]]
- [[phase28b-asset-marketplace]]
- [[phase28c-deep-solver-integration]]
- [[phase28d-morphology-co-design-lab]]
- [[phase28e-28f-certification-hardening]]
- [[phase27-voice-nvidia-rendering]]
- [[phase23-humanoid-robot-synthesis]]
- [[phase22-multi-physics-verification]]
