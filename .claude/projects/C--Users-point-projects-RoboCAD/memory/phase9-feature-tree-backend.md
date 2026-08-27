---
name: phase9-feature-tree-backend
description: "Phase 9 feature-tree backend complete — structured feature trees, transpiler, store, API endpoints, and frontend panel."
metadata: 
  node_type: memory
  type: project
  originSessionId: cb75c83a-be7b-4a7b-bc49-b8099018beb3
  modified: 2026-08-25T00:44:04.221Z
---

**When:** 2026-08-25

**What:** Completed Phase 9 of the RoboCAD engineer-grade roadmap. The system now stores designs as a structured Feature-Tree JSON sidecar in addition to the legacy `code.py` path, and can regenerate parts by editing feature-tree parameters.

**Deliverables:**
- `ai_cad/feature_tree.py` — Pydantic models for the Feature-Tree JSON Schema v1.0.0 (parameters, coordinate systems, planes, sketches, entities, constraints, dimensions, features, parts, assemblies, mates).
- `ai_cad/transpiler.py` — transpiles a `FeatureTree` into executable `build123d` Python. Phase 9 coverage: base-plane sketches, rectangle/circle/line/arc/polygon entities, and extrude/revolve/fillet/chamfer/shell/mirror/linear_pattern/circular_pattern features.
- `ai_cad/feature_store.py` — persists `feature_tree.json` under `designs/{id}/` with versioning support; reads `ROBOCAD_DESIGNS_DIR` from environment.
- `ai_cad/generator.py` — added `generate_feature_tree()` and `self_correct_feature_tree()` helpers that ask the LLM to emit a Feature-Tree JSON block.
- `ai_cad/models.py` — `GenerationResult` now carries an optional `feature_tree: FeatureTree | None`.
- `ai_cad/api.py` — refactored `RoboCADBackend.generate()` into `_generate_from_code()` and `_generate_from_feature_tree()` helpers; `use_feature_tree: bool = False` flag with transparent fallback to legacy code path on failure.
- `web/backend/main.py` — added `GET /designs/{id}/feature-tree` and `POST /designs/{id}/regenerate-from-feature-tree`; `/generate` persists the feature tree when present.
- Frontend: `FeatureTreePanel.jsx`, `FeatureParameterEdit.jsx`; `api.js` helpers; `App.jsx` routes regeneration through the feature-tree endpoint when a tree is present.
- Tests: `tests/test_feature_tree.py`, `tests/test_transpiler.py`, `tests/test_feature_store.py` (25 new tests). Full suite: **97 passed**.

**Known issues resolved:**
- `test_generate_missing_api_key` was flaky because `.env` routes to local Ollama; now mocked deterministically.
- Initial `ai_cad/api.py` refactor had invalid syntax at the dispatch point; fixed by extracting two clean helper methods.

**Why it matters:** Replaces the monolithic `code.py` representation with a versioned, editable design history that can be partially regenerated, inspected, and later used for sketch constraints and assemblies in Phases 10–11.

**How to apply:**
- Use `backend.generate(prompt, use_feature_tree=True)` to request a feature-tree-based generation.
- Edit parameters through the new **Feature Tree** panel in the UI; it calls `POST /designs/{id}/regenerate-from-feature-tree`.
- Access raw feature trees via `GET /designs/{id}/feature-tree` for downstream tooling.

**Links:** [[engineer-grade-roadmap]] | [[phase5-phase6-completion]] | [[google-stitch-ui-redesign]]
