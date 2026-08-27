---
name: phase10-sketch-constraint-solver
description: Phase 10 sketch + 2D constraint solver complete — internal least-squares solver for sketch control points and driving dimensions.
metadata: 
  node_type: memory
  type: project
  originSessionId: cb75c83a-be7b-4a7b-bc49-b8099018beb3
  modified: 2026-08-25T00:56:08.322Z
---

**When:** 2026-08-25

**What:** Completed Phase 10 of the RoboCAD engineer-grade roadmap. Added a small internal 2D geometric constraint solver that resolves sketch control points before the feature tree is transpiled to `build123d`.

**Deliverables:**
- `ai_cad/sketch_solver.py` — internal solver using `scipy.optimize.least_squares` with Tikhonov regularization.
  - Supported constraints: `distance`, `horizontal`, `vertical`, `coincident`, `concentric`, `equal`, `fix`.
  - Supported driving dimensions: `distance`, `radius`, `diameter`, `angle`.
  - Control-point handles accept entity IDs (`"circle1"`) or point references (`"line1.start"`, `"circle1.center"`).
  - Parameter names in dimension values are resolved against the feature-tree parameter dictionary.
- `ai_cad/transpiler.py` updated to call `solve_sketch(sketch, parameters)` before emitting `BuildSketch` blocks.
- `tests/test_sketch_solver.py` — 8 tests covering distance dimensions, coincident, horizontal/vertical alignment, equal radii, fixed points, parameter substitution, and no-constraint passthrough.
- Full pytest suite: **105 passed**.

**Known design choices:**
- Solver uses Trust Region Reflective (`trf`) with a `1e-6` regularization vector so under-determined sketches still converge near their initial geometry.
- `equal` constraint equalizes radii for circles and distance-from-origin for other entities (length proxy).
- Non-linear constraints like `tangent` are parsed but not yet solved; they are reserved for a future PlaneGCS/SolveSpace integration if needed.

**Why it matters:** Moves sketches from raw coordinates guessed by the LLM to true parametric drawings where dimensions and constraints drive geometry. This keeps holes centered, lines aligned, and circles concentric when users edit parameters.

**How to apply:**
- Define constraints and dimensions in `Sketch` objects inside a `FeatureTree`.
- The transpiler automatically solves sketches before generating `build123d` code.
- Access solved coordinates programmatically via `solve_sketch(sketch, parameters)` for custom tooling or verification.

**Links:** [[phase9-feature-tree-backend]] | [[engineer-grade-roadmap]] | [[google-stitch-ui-redesign]]
