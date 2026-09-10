---
name: phase18-decomposition-part-families
description: Phase 18 — automatic system decomposition into domain part families with composed FeatureTree assembly; post-ship hardening fixed transpiler part-variable and duct-family bugs; 228/228 tests passing.
metadata: 
  node_type: memory
  type: project
  originSessionId: 586428af-d9d7-47a8-9106-92fdb2a15f35
  modified: 2026-08-30T01:11:06.922Z
---

# Phase 18 — Automatic decomposition and domain part families

Shipped 2026-08-29. RoboCAD can now take a single system-level prompt (e.g. “450 mm quadcopter with four motor arms”) and automatically split it into domain-specific parts, instantiate reusable part-family templates, compose a `FeatureTree` with assembly/instances/mates, transpile it to build123d, execute it, and export STL/STEP.

## What shipped

- **ai_cad/part_families.py** — `PartFamily` dataclass and registry of 12 families across mechanical, aero/thermal, electronics, and humanoid/robot domains. `instantiate_family()` returns a ready-to-transpile `Part` with domain-appropriate sketches, features, interfaces, and parameters.
- **ai_cad/decomposition.py** — `DecomposedPart` / `DecompositionResult` dataclasses. `should_decompose()` detects system prompts. `decompose()` uses rule-based templates for quadcopter, robot arm, humanoid, and fixed-wing, with a single-part fallback for non-system prompts. Includes helpers to extract counts and dimensions from natural language.
- **ai_cad/composer.py** — `compose_feature_tree()` turns a decomposition plan into a complete `FeatureTree`: global parameters, per-domain parts, assembly with instances, and mates. Domain-specific placement helpers lay out quadcopter hubs/arms/mounts and robot-arm links/joints.
- **Backend** (`web/backend/main.py`):
  - `POST /decompose` endpoint and `DecomposeRequest/DecomposeResponse` models.
  - `GenerateRequest` gains `decompose: bool = True`.
  - System prompts route through `_run_decomposed_generation()` when decomposition is enabled.
  - Fixed persistence so `feature_tree.json` is saved in the same `DESIGNS_DIR` as other artifacts.
  - Relaxed decomposed-generation success criterion: compounds of touching parts are allowed; success requires code execution + STL export rather than watertight validation.
- **Frontend**:
  - `DecomposePanel.jsx` displays the decomposition plan table (part, domain, family, quantity, parameters).
  - `PromptInput.jsx` adds an “Auto-decompose systems” checkbox (default checked).
  - `api.js` adds `decomposePrompt()` and passes the `decompose` flag to `generateDesign()`.
  - `App.jsx` renders `DecomposePanel` when a decomposition result is present.
- **Tests**:
  - `tests/test_part_families.py` (6)
  - `tests/test_decomposition.py` (8)
  - `tests/test_composer.py` (5)
  - Backend endpoint tests in `tests/test_web_backend.py` (3)

## Test count

Full pytest suite: **228/228 passing**.

## Key design decisions

- Part families are intentionally symbolic/parametric: each family exposes parameters (length, width, mount_diameter, etc.) and a `Part` interface, so the composer can override them per decomposition plan.
- Rule-based decomposition is used by default (`use_llm=False`) to keep tests deterministic and fast. The structure is ready for an LLM planner later.
- Multi-part assemblies are compounds of separate solids. Requiring a single watertight manifold would incorrectly reject every valid assembly, so the decomposed generation path marks success on execution + STL production and still reports validation metrics for diagnostics.

## Bugs fixed along the way

- `PlaneReference` names must be uppercase (`XY`, `XZ`, `YZ`) for the transpiler.
- `CoordinateSystem` origins must be numeric, not string expressions, in part-family interfaces.
- Heat-sink family avoids `linear_pattern` transpiler incompatibility by using a single centered fin.
- `_find_number_near` regex had an invalid `.*??`; corrected to `.*?`.
- `intent_parser.py` now coerces malformed LLM string outputs for `features`/`constraints`/`notes` into the expected dict/list shapes.
- Backend `save_feature_tree()` now receives `designs_dir=DESIGNS_DIR` so it writes to the same directory as `metadata.json`, `code.py`, etc.

## Post-ship hardening (2026-08-29)

Before entering Phase 19, a live end-to-end test of `/generate?decompose=True` with the quadcopter + aero shell prompt exposed two latent bugs that would have blocked mechanical assembly synthesis:

- **Transpiler part-variable bug:** `shell`, `fillet`, and `chamfer` hardcoded the variable `part`, but assemblies use `part_0`, `part_1`, etc. Fixed by threading `var_name` through `_transpile_feature` and `_render_edge_selector`.
- **Shell operation bug:** The transpiler emitted lowercase `shell(...)` and then `Shell(...)`; the correct build123d call is `{var_name}.part.hollow([faces], thickness=...)`.
- **Duct family bug:** The `duct` family used `shell()` to hollow a cylinder, which is geometrically fragile. Replaced with a robust outer cylinder + inner cylinder subtract.
- **Regression tests added:** `test_transpiler.py` for shell/fillet/chamfer with custom variables; `test_composer.py` for quadcopter-with-shell execution.
- **Full suite after hardening:** **228/228 tests passing**.
- **Live verification:** `/generate?decompose=True` for *“450 mm quadcopter with four motor arms and an aerodynamic shell”* now succeeds and exports STL/STEP.
- **Docs sync:** README banner, `memory.md`, `dossiers/robocad-end-to-end-roadmap.md`, `.superpowers/sdd/progress.md`, `docs/session_recovery_guide.md`, and `C:\Users\point\CLAUDE.md` all updated to reflect Phase 18 complete; subsequent phases through Phase 22 are also complete; Phase 23 is next.

## Scope and next phases

Phase 18 closes the loop from natural-language system description → structured decomposition → parametric part families → assembly → exported geometry. It enables the upcoming phases:

- [[phase19-assembly-synthesis]] — mate inference, kinematic loops, full subsystem MJCF/URDF export (complete).
- [[phase20-aero-thermal-propulsion]] — airfoil/wing/duct/heat-sink/propeller surface generation and CFD mesh stubs (complete).
- [[phase21-electronics-mechatronics]] — PCB outlines, enclosures, connector mounts, cable guides, fan mounts, heat spreaders, IDF/STEP export (complete).
- [[phase22-multi-physics-verification]] — structural, thermal, CFD, and dynamic checks from a single verification layer (complete).
- [[robocad-end-to-end-roadmap]] — Phase 23: humanoid and full-robot system synthesis (next).

## Why it matters

Before Phase 18, RoboCAD generated individual parts. Now it can synthesize multi-part robotic systems from a single sentence, using domain-aware reusable templates. This is the prerequisite for real mechanisms, aircraft, and humanoids rather than isolated brackets.

## How to apply

When a user gives a system prompt, set `decompose=True` in `/generate` and render the returned `decomposition` plan. Use the decomposition table to let users inspect and (eventually) edit which part families were chosen before committing to a full build.
