---
name: phase11-assembly-system
description: "Phase 11 assembly system complete — multi-part instances, LCS-based mates, and multi-body assembly export."
metadata: 
  node_type: memory
  type: project
  originSessionId: cb75c83a-be7b-4a7b-bc49-b8099018beb3
  modified: 2026-08-25T01:09:08.358Z
---

**When:** 2026-08-25

**What:** Completed Phase 11 of the RoboCAD engineer-grade roadmap. The system now supports multi-part designs with local coordinate system mates and can export them as a multi-body `build123d` `Compound`.

**Deliverables:**
- `ai_cad/assembly.py`:
  - `compute_instance_transforms(tree, assembly)` — solves instance placement from explicit `translation`/`rotation` transforms and LCS-based mate constraints using iterative Gauss-Seidel-like relaxation.
  - `transpile_assembly(tree)` — emits a build123d script that creates one `BuildPart` per unique part and places instances in a `Compound` named `result`.
  - Supported mate types: `coincident`, `concentric`, `distance`, `parallel`, `perpendicular`, `fixed`, `angle` (stored for future use).
  - Helper functions for homogeneous transform matrices, Z-axis alignment, and coordinate-system lookup.
- `ai_cad/api.py` extended with `use_assembly: bool = False`; when true, feature-tree generation transpiles with `transpile_assembly` if an assembly is present.
- `web/backend/main.py`:
  - `GenerateRequest.use_assembly` flag.
  - `GET /designs/{id}/assembly` endpoint returning the first assembly from the feature tree.
  - `GET /designs/{id}` now also returns `assembly` in the response.
  - `POST /designs/{id}/regenerate-from-feature-tree` uses `transpile_assembly` when `tree.assemblies` is non-empty.
- Frontend:
  - `AssemblyPanel.jsx` displays instances and mates.
  - `api.js` adds `loadAssembly(id)`.
  - `App.jsx` renders `AssemblyPanel` in the bottom panels grid.
- `tests/test_assembly.py` — 7 tests including explicit transform, coincident, distance, parallel mates, transpilation output, single-part fallback, and end-to-end execution of an assembly script.
- Full pytest suite: **112 passed**.

**Known limitations / future work:**
- The mate solver is a simple relaxation and does not enforce all degrees of freedom simultaneously like a full constraint solver. Complex over-constrained assemblies may need PlaneGCS/SolveSpace in a future phase.
- Only the first assembly in a feature tree is exported.
- Multi-body STL export merges bodies into a single mesh; per-part STL export is a future enhancement.

**Why it matters:** Robotics parts are rarely isolated — motors, brackets, bearings, and wheels form assemblies. Phase 11 lets RoboCAD represent and export those assemblies with explicit mates, so changes to one part's dimensions propagate through the assembly layout.

**How to apply:**
- Create a `FeatureTree` with multiple `Part`s and an `Assembly` containing `Instance`s and `Mate`s.
- Call `transpile_assembly(tree)` to generate the build123d script, or use `backend.generate(prompt, use_feature_tree=True, use_assembly=True)`.
- Use the frontend **Assembly** panel to inspect instances and mates for designs that include them.

**Links:** [[phase10-sketch-constraint-solver]] | [[phase9-feature-tree-backend]] | [[engineer-grade-roadmap]]
