---
name: robocad-end-to-end-roadmap
description: Full phased roadmap from current RoboCAD (Phases 0–15B) to the multi-domain voice/text/sketch → CAD → multi-physics → assembly → world model → HERMES → robot brain vision (Phases 16–28).
metadata: 
  node_type: memory
  type: project
  originSessionId: cb75c83a-be7b-4a7b-bc49-b8099018beb3
  modified: 2026-09-10T02:58:07.125Z
---

Date: 2026-08-27 (updated 2026-09-08).

Total horizon: ~5–7 years. North Star: **voice/text/sketch → multi-domain parametric CAD → per-part multi-physics testing → assembly → world-model simulation → HERMES oversight → robot brain trained on synthetic data with sim-to-real feedback loops**. First commercial milestone: **PATH1 / GEDA Bridge (Phases 14A–15B)** complete at **187/187 tests passing**. Current milestone: **Phase 28 — simulation-first product platform**, complete at **380/380 default + 223/223 heavy/slow tests passing**. All software phases through 28A/B/C/D/E/F are shipped; only Phase 27D (hardware-in-the-loop sim-to-real) remains blocked on physical robot hardware access.

## Domain tracks

The roadmap now explicitly covers four domain tracks on a shared feature-tree / bundle core:

1. **Mechanical assemblies** — parts, constraints, mates, mechanisms (existing core + Phase 19).
2. **Aerodynamics / thermal / propulsion** — airfoils, wings, ducts, heat sinks, propellers (Phase 20).
3. **Electronics / mechatronics** — PCB form factors, enclosures, connectors, cable/thermal hardware (Phase 21).
4. **Humanoid / full-robot systems** — biped, quadruped, manipulator-on-base templates (Phase 23).

Explicit boundary: full silicon EDA (transistor layout, SPICE, lithography/PnR) and autonomous high-fidelity CFD remain external tools; RoboCAD exports packages, boards, mounts, and CFD-ready surface meshes.

## Phase map

- **PATH1 (complete):** 13 → 14A → 14B → 15A → 15B.
- **PATH2 / multi-domain North Star:** 16 (cross-domain input) → 17 (domain representation) → 18 (decomposition + families) → 19 (mechanical assembly) → 20 (aero/thermal/propulsion) → 21 (electronics) → 22 (multi-physics verification) → 23 (humanoid/robot synthesis) → 24 (world-model simulation) → 25 (robot brain training) → 26 (HERMES supervisor) → 27A/B/C (voice + NVIDIA + rendering) → 28 (simulation-first product platform: launcher, marketplace, deep multi-physics, morphology lab, certification, hardening).
- **Remaining:** Phase 27D (hardware-in-the-loop sim-to-real) blocked on hardware access.

## Critical dependencies

- 15B done unlocks PATH1 monetization.
- 16/17 depend on Phase 13 generation quality.
- 18 depends on 17.
- 19 depends on 14A + 17 + 18.
- 20/21 depend on 17 + 18.
- 22 depends on 19 + 20 + 21.
- 23 depends on 19 + 22.
- 24 depends on 15A + 19 + 23.
- 25 depends on 24; 26 depends on 16/19/22/24; 27A/B/C complete; 27D depends on hardware access; 28 depends on PATH1 proven + 27 software layers.

## Why this is realistic

- PATH1 is already shipped and marketable, funding the longer layers.
- Domain tracks share the same feature-tree, bundle, and verification infrastructure.
- High-risk layers (decomposition, humanoid, multi-physics) are sequenced after the mechanical core is proven and use conservative templates first.
- HERMES remains supervisor/observer with human approval gates.

## Next action

All software phases through **28A/B/C/D/E/F** are complete. Current baseline: **380 default + 223 heavy/slow tests passing**, frontend build passes. Next optional work: Phase 27D hardware-in-the-loop sim-to-real when hardware is available, or follow-on features (voice-to-morphology, batch morphology certification, SaaS packaging).

**Related:** [[robocad-path-analysis]] | [[phase28-simulation-first-product-platform]] | [[phase28d-morphology-co-design-lab]] | [[phase27-voice-nvidia-rendering]] | [[phase26-hermes-plan]] | [[phase25-attention-brain]] | [[phase24-world-simulation]] | [[phase23-humanoid-robot-synthesis]] | [[phase22-multi-physics-verification]] | [[engineer-grade-roadmap]]
