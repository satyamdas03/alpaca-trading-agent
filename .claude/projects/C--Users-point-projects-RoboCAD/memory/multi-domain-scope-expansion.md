---
name: multi-domain-scope-expansion
description: Scope expansion decision to move RoboCAD from mechanical-CAD tool to multi-domain generative engineering platform covering aero/thermal, electronics, and humanoid/robot systems.
metadata: 
  node_type: memory
  type: project
  originSessionId: cb75c83a-be7b-4a7b-bc49-b8099018beb3
  modified: 2026-08-30T01:11:01.602Z
---

Date: 2026-08-27 (updated 2026-08-29).

## Decision

The user's intended scope for RoboCAD is the **entire robotics world**: from simple mechanical parts to complex multi-domain systems including **robot mechanisms, aerodynamics / thermal / propulsion surfaces, electronics integration, and full humanoid / robot subsystems**. The official plan, README, dossiers, and memory files have been updated to reflect this.

## Why the original plan was too narrow

The previous roadmap stopped at mechanical assemblies + world-model simulation + robot brain training. It did not explicitly include:
- Aerodynamic / thermal geometry (wings, ducts, heat sinks, propellers).
- Electronics / mechatronics form-factor co-design (PCB outlines, enclosures, connectors, thermal hardware).
- Humanoid / full-robot system synthesis.
- Multi-physics verification spanning structural, thermal, CFD, and dynamic checks.

These domains are now first-class tracks, layered on the existing feature-tree + bundle + verification core.

## How the plan changed

- **Phases renumbered/expanded from 16–24 → 16–28.**
- **New phase map:**
  - 16 — Cross-domain input (voice/text/sketch + domain detection)
  - 17 — Domain-aware parametric representation
  - 18 — Automatic decomposition + domain part families
  - 19 — Mechanical assembly synthesis
  - 20 — Aerodynamics, thermal, and propulsion geometry
  - 21 — Electronics and mechatronics integration
  - 22 — Multi-physics verification engine
  - 23 — Humanoid and full-robot system synthesis
  - 24 — World-model simulation
  - 25 — Robot brain training loop
  - 26 — HERMES cross-domain conversational supervisor
  - 27 — Sim-to-real feedback loop
  - 28 — Distribution / ecosystem / advanced co-design

- **Dependencies updated** so aero/thermal (20) and electronics (21) depend on domain representation (17) + decomposition (18); multi-physics (22) depends on all three; humanoid (23) depends on mechanical assembly (19) + multi-physics (22); world model (24) depends on PATH1 (15A) + assembly (19) + humanoid (23).

- **Explicit out-of-scope boundary added:** full silicon EDA (transistor layout, SPICE, lithography/PnR) and autonomous high-fidelity CFD are not part of RoboCAD. RoboCAD handles packages, boards, mounts, and CFD-ready surface meshes; external tools handle the rest.

- **Benchmark sentence added** for Phases 16–28: a 450 mm quadcopter frame with motor arms, aerodynamic body shell, battery/PCB tray, and heat-sink base plate.

## What was updated

- `PLAN.md` — product definition, risk table, benchmark sentences, Sections 12–14.
- `README.md` — roadmap table, vision section, example user sentence, HERMES phase reference, changelog.
- `dossiers/robocad-end-to-end-roadmap.md` — full phased plan now 16–28.
- `dossiers/PATH1_PATH2_analysis.md` — PATH2 reframed as multi-domain North Star with domain tracks and new phase sequence.
- Memory files: `robocad-end-to-end-roadmap.md`, `robocad-path-analysis.md`, `phase16-17-multi-domain-foundation.md`, `phase18-decomposition-part-families.md`, and this file.

## Completed since expansion

- ✅ Phase 16 — Cross-domain input: `ai_cad/domain.py` classifier, `ai_cad/intent_parser.py`, `/classify-domain`, domain badges, **201/201 tests passing**.
- ✅ Phase 17 — Domain-aware representation: feature-tree schema v2.0.0, `SurfaceFeature`, `KinematicJoint`, `PCBOutline`, NACA airfoil sketch, **201/201 tests passing**.
- ✅ Phase 18 — Automatic decomposition + domain part families: `ai_cad/decomposition.py`, `part_families.py`, `composer.py`, `/decompose`, `/generate?decompose`, `DecomposePanel.jsx`; post-ship hardening fixed transpiler part-variable and duct-family bugs; **228/228 tests passing**.
- ✅ Phase 19 — Mechanical assembly synthesis: mate inference, kinematic solver, collision checks, joint-aware MJCF/URDF export, browser replay; **251/251 tests passing**.
- ✅ Phase 20 — Aerodynamics, thermal, and propulsion geometry: NACA airfoils, wings, propeller blades, heat sinks, CFD mesh stubs, `AeroPanel.jsx`, `ThermalPanel.jsx`; **276/276 tests passing**.
- ✅ Phase 21 — Electronics and mechatronics integration: `PCBOutline` transpilation, electronics part families, stack decomposition + composer layout, electronics analysis, IDF/STEP export, `ElectronicsPanel.jsx`; **299/299 tests passing**.
- ✅ Phase 22 — Multi-physics verification engine: `ai_cad/materials.py`, `ai_cad/verification*.py`, `ai_cad/mesh_quality.py`, closed load-case templates, mesh-quality gate, backend `/verify` endpoints, frontend `VerificationPanel`; **330/330 tests passing**.

## Next action

Open **Phase 23 — Humanoid and full-robot system synthesis**: biped/quadruped/manipulator-on-base templates, dynamic stability, whole-system MJCF/URDF export. Keep Phases 14A–22 maintained and the 330-test suite green.

**Related:** [[robocad-end-to-end-roadmap]] | [[robocad-path-analysis]] | [[phase22-multi-physics-verification]] | [[phase21-electronics-mechatronics]] | [[phase20-aero-thermal-propulsion]] | [[engineer-grade-roadmap]]
