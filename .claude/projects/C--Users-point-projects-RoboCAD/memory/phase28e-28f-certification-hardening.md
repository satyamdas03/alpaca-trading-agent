---
name: phase28e-28f-certification-hardening
description: Phase 28E/F — simulation certification + real-solver dispatch + marketplace upload + solver install bootstrap.
metadata: 
  node_type: memory
  type: project
  originSessionId: 7435fc68-ca4e-4484-976a-3e6e62f81195
  modified: 2026-09-10T02:57:08.267Z
---

# Phase 28E/F — Simulation certification + product hardening

**Date:** 2026-09-01
**Status:** complete

## What shipped

- **Real-solver dispatch** in `ai_cad/solvers/verification_deep.py`:
  - `solver_mode` supports `"auto"`, `"real"`, `"surrogate"`.
  - `CalculiXAdapter`, `ElmerAdapter`, `OpenFOAMAdapter` now invoke actual binaries when installed, with deterministic lightweight fallbacks otherwise.
  - Coarse analysis mesh built from STL bounding box so adapters can run without Gmsh/Netgen.
  - `solver_availability()` reports path/version/install hints.

- **Field extraction + viewer heatmaps**:
  - `ai_cad/solvers/field_export.py` parses CalculiX `.dat`, Elmer `.ep`, and OpenFOAM coefficients.
  - `map_field_to_surface_vertices` attaches scalar values to STL vertices.
  - Backend `GET /designs/{id}/deep-verify/{job_id}/field` and frontend `VerificationPanel.jsx` "Show heatmap" / "Clear heatmap" controls.
  - `STLViewer.jsx` vertex-color heatmap overlay via `scalarField` prop.

- **Simulation certification**:
  - `ai_cad/sim_certification.py` runs a suite of closed load cases, computes a weighted readiness score, optionally A/B compares real vs surrogate, and persists certificates to `certificates/{cert_id}.json`.
  - Backend `POST /designs/{id}/sim-cert`, `GET /designs/{id}/sim-cert/{cert_id}`, `GET /designs/{id}/sim-certs`.

- **Professional reports**:
  - `ai_cad/solvers/report_export.py` generates Markdown reports from deep-verify results.
  - Backend `GET /designs/{id}/deep-verify/{job_id}/report.md`.

- **Marketplace direct file upload**:
  - `POST /marketplace/upload` accepts `.zip`/`.tar.gz`/`.tgz` archives, extracts them to `marketplace/uploads/{uuid}/`, and creates a catalog entry.
  - `MarketplacePanel.jsx` file input + `uploadMarketplaceArchive` API helper.
  - `ai_cad/marketplace.py` `create_item_from_upload`.

- **Solver install bootstrap + health hints**:
  - `scripts/setup_solvers.py` detects platform/package manager and installs CalculiX/ElmerFEM/OpenFOAM/Gmsh where supported.
  - `docs/SOLVER_INSTALL.md` licensing and install instructions.
  - `robocad/health.py` reports solver `install_hint` and version strings.

- **Onboarding smoke tests**:
  - `tests/test_onboarding.py`, `tests/test_health.py`, `tests/test_setup_solvers.py`.

## Test results

- Full default pytest suite after 28D: **380 passed, 224 deselected**, 3 warnings (JWT key length), 1 expected failure, 5 benchmark/network tests deselected.
- Heavy/slow/mujoco suite after 28D: **223 passed, 1 xfailed**.
- Frontend `npm run build`: passes (chunk-size warning only).
- `python -m robocad.health`: reports environment, deps, API keys, solvers, and install hints.

## End-to-end verification

- ✅ Real solver dispatch exercised with monkeypatched subprocess calls; falls back to estimates when binaries are absent.
- ✅ Certification result parsing and score computation verified.
- ✅ Markdown report generation verified.
- ✅ Marketplace archive upload backend + frontend wiring verified.
- ✅ Health CLI prints install hints for missing optional solvers.

## Residual caveats

- Real solver binaries remain optional; install bootstrap is a convenience helper, not a guaranteed installer on every platform.
- Phase 28D (morphology co-design lab) is now complete.
