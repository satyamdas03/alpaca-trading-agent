---
name: phase20-aero-thermal-propulsion
description: "Phase 20 completion — aero/thermal surface geometry, CFD stubs, backend endpoints, and frontend panels. 276/276 tests passing."
metadata: 
  node_type: memory
  type: project
  originSessionId: 49cf34d8-b8ab-4bdb-a372-7913c215a0bb
  modified: 2026-08-29T03:59:19.940Z
---

RoboCAD Phase 20 (aerodynamics, thermal, and propulsion geometry) is complete.

**What changed:**
- `ai_cad/transpiler.py` now transpiles `SurfaceFeature` objects for `airfoil`, `wing`, `propeller_blade`, and `heat_sink` (plus `duct` fallback). Airfoil/wing/propeller use `BuildLine` + `Polyline(..., close=True)` → `BuildSketch` + `make_face(...)` → `extrude`. Heat sinks use a base plate plus a `GridLocations` fin array.
- `ai_cad/part_families.py` registers `propeller_blade`; `heat_sink` uses a single `SurfaceFeature`; `airfoil`/`wing` keep their airfoil sketch + surface feature pairing.
- `ai_cad/sketch_solver.py` resolves parameter-name chords so NACA airfoils no longer crash with ZeroDivisionError.
- New analysis/export modules: `ai_cad/aero.py`, `ai_cad/thermal.py`, `ai_cad/cfd.py` with `AeroResult`, `ThermalResult`, and `CFDMeshResult` dataclasses and `model_dump()` methods.
- Backend endpoints in `web/backend/main.py`: `POST/GET /designs/{id}/aero-report`, `POST/GET /designs/{id}/thermal-report`, `POST /designs/{id}/cfd-mesh`.
- Frontend: `AeroPanel.jsx` (aero estimates + CFD mesh export) and `ThermalPanel.jsx` (heat-sink thermal resistance / max temp), both domain-gated in `App.jsx`. API helpers added to `web/frontend/src/api.js`.
- New tests: `tests/test_surface_geometry.py`, `tests/test_transpiler_surface.py`, `tests/test_part_families_aero_thermal.py`, `tests/test_cfd_export.py`.

**Verification:**
- Full pytest suite: **276/276 passing**.
- Frontend production build: `npm run build` succeeds.

**Why:** Phase 20 extends RoboCAD beyond mechanical parts into aero/thermal subsystems, a prerequisite for multi-domain robot design (drones, cooled electronics, propulsion).

**How to apply:** Use the new families/endpoints when prompts mention wings, airfoils, propellers, heat sinks, ducts, or CFD. Continue through [[phase21-electronics-mechatronics]] and [[phase22-multi-physics-verification]] for full multi-domain verification.

**Related:** [[phase19-assembly-synthesis]], [[phase21-electronics-mechatronics]], [[phase22-multi-physics-verification]], [[phase16-17-multi-domain-foundation]], [[multi-domain-scope-expansion]]
