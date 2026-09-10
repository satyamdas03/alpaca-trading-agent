---
name: phase16-17-multi-domain-foundation
description: "Batch A (Phases 16–17) multi-domain foundation complete — domain classifier, intent parser, feature-tree v2.0.0, airfoil sketch support, frontend badges."
metadata: 
  node_type: memory
  type: project
  originSessionId: e6e5fb08-55cf-4c48-9b91-b44e90e81150
  modified: 2026-08-29T02:29:30.247Z
---

# Batch A — Phases 16–17 Multi-Domain Foundation

**Date:** 2026-08-29
**Status:** ✅ Complete
**Full pytest suite:** 201/201 passing

## What shipped

### Phase 16 — Cross-domain input layer

- `ai_cad/domain.py` — keyword + optional `sentence-transformers` embedding domain classifier for six domains: `mechanical`, `aero`, `thermal`, `electronics`, `humanoid`, `multi`.
- `ai_cad/intent_parser.py` — per-domain LLM intent parser returning `DomainIntent` (domain, confidence, parameters, constraints, feature operations, surface/PCB/kinematic hints).
- Backend endpoints in `web/backend/main.py`:
  - `POST /classify-domain`
  - `GET /designs/{id}/domain-intent`
  - `detect_domain` flag on `POST /generate` persists `domain_intent.json`
- Frontend:
  - `DomainBadge.jsx` component with domain-specific colors.
  - Domain badges in `HistorySidebar.jsx`.
  - Domain-intent inspector card in `App.jsx`.
  - "Detect domain" checkbox in `PromptInput.jsx`.

### Phase 17 — Domain-aware parametric representation

- `ai_cad/feature_tree.py` schema bumped to **v2.0.0**:
  - `domain` tags on `Feature`, `Part`, `Assembly`, `FeatureTree`.
  - Top-level `features` list with discriminated union (`Feature | SurfaceFeature | PCBOutline`).
  - New models: `SurfaceFeature`, `KinematicJoint`, `PCBOutline`.
  - `SketchEntity` `airfoil` type with `naca` 4-digit code and `chord`.
  - `Sketch.points` field for computed profiles.
  - `created_at` optional with UTC default.
- `ai_cad/sketch_solver.py` airfoil support:
  - `_naca_4digit_points(code, chord, n=40)` computes camber + thickness profiles.
  - `_solve_airfoils(sketch)` populates entity points.

## Tests added

- `tests/test_domain_classifier.py`
- `tests/test_intent_parser.py`
- `tests/test_feature_tree_v2.py`
- `tests/test_sketch_airfoil.py`
- Additional backend coverage in `tests/test_web_backend.py`

## Honest boundaries

- Voice / STT integration was **not** implemented; it is deferred to later phases.
- Ambiguity-resolution clarifying-questions UI was **not** implemented.
- Aero/thermal surface transpiler and kinematic-tree backend are scaffolded in schema only; full transpilers come in Phases 20 and 23.

## Related memories

- [[multi-domain-scope-expansion]] — decision to expand scope to full robotics world.
- [[robocad-end-to-end-roadmap]] — long-horizon phase plan.
- [[phase15b-robocomplier-pipeline]] — prior phase that Batch A builds on.
- [[phase18-decomposition-part-families]] — next phase completed; post-ship hardening raised suite to 228/228.

**Why:** A shared domain-aware representation is the load-bearing prerequisite for aero, electronics, and humanoid tracks. Without it, later phases would duplicate data models.

**How to apply:** When continuing to Phase 19 (mechanical assembly synthesis), use `FeatureTree.domain`, `SurfaceFeature`, `KinematicJoint`, and `PCBOutline` as the canonical containers. The classifier and intent parser from Phase 16 feed decomposition; the schema from Phase 17 carries domain tags and surface/kinematic/PCB shapes.
