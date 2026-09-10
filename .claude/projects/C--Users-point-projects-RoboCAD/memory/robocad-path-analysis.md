---
name: robocad-path-analysis
description: Strategic comparison of PATH1 (GEDA Bridge) and PATH2 (multi-domain voice/world-model-to-robot) for RoboCAD.
metadata: 
  node_type: memory
  type: project
  originSessionId: cb75c83a-be7b-4a7b-bc49-b8099018beb3
  modified: 2026-08-30T01:10:35.938Z
---

Date: 2026-08-25 (updated 2026-08-29).

We analyzed two strategic directions for RoboCAD against market data, technical feasibility, and competitive landscape.

## PATH1: GEDA Bridge / Phases 14A–15B

**What it is:** A delivery-infrastructure play that takes RoboCAD's parametric CAD output and exports it into MuJoCo / URDF / MJCF with correct inertial properties, DFM reports, and a bundle schema that LearningRobotics can consume.

**Market context:**
- Robot skill-learning platforms: ~$4.2–5.4 B (2026), 18–29% CAGR
- Robot learning from demonstration: ~$3.2–4.1 B (2026), 28% CAGR
- Imitation learning for robotics: ~$2.1–2.8 B (2026), 34% CAGR
- AI copilots for robot programming: ~$2.75 B (2026), 28–32% CAGR
- Physical AI simulation / digital twin for robotics: ~$3.8 B+ (2026), 28% CAGR
- Synthetic data generation for robotics: ~$2.5 B (2026), 33% CAGR

**Status:** ✅ Complete — PATH1 (Phases 14A–15B) shipped at **187/187 tests passing**; later phases through Phase 21 are also complete, with the full suite now **299/299 passing** as of 2026-08-29.

**Technical feasibility:** High. The current codebase already has parametric generation, feature trees, assemblies, DFM checks, and exports. A MuJoCo exporter is mostly plumbing and unit conversion.

**Competitive angle:** MuJoCo has no turnkey CAD importer. RoboCAD fills that gap with parametric, editable, manufacturable parts.

**Verdict:** Do this first. It is reachable, creates the exact asset format PATH2 needs, and validates that AI-generated CAD can be physically useful.

## PATH2: Multi-domain voice/text/sketch → CAD → multi-physics → world model → HERMES → robot brain

**What it is:** A full-stack, multi-domain robotics design operating system now spanning **Phases 16–28**:
1. Cross-domain input (16)
2. Domain-aware parametric representation (17)
3. Automatic decomposition + domain part families (18)
4. Mechanical assembly synthesis (19)
5. Aerodynamics, thermal, propulsion geometry (20)
6. Electronics / mechatronics co-design (21)
7. Multi-physics verification engine (22)
8. Humanoid / full-robot system synthesis (23)
9. World-model simulation builder (24)
10. Robot brain training loop (25)
11. HERMES cross-domain supervisor (26)
12. Sim-to-real feedback loop (27)
13. Distribution / ecosystem / advanced co-design (28)

**Market context:** Large downstream markets (generative AI in design ~$7 B, digital twin ~$35–47 B, physical AI training ~$3.2 B → $101 B by 2035, aero/thermal design, electronics co-design), but crowded and capital-intensive.

**Technical feasibility:** Mixed. Voice-to-text and LLM intent parsing are mature; part decomposition, arbitrary multi-physics, humanoid morphology, and sim-to-real remain hard. The plan mitigates this by building domain tracks on a shared core and starting with parameterized templates.

**Explicit boundaries:** Full silicon EDA (transistor layout, SPICE, lithography/PnR) and autonomous high-fidelity CFD stay external; RoboCAD owns form-factor co-design and export bridges.

**Verdict:** The right North Star, but the wrong next milestone. It should guide architecture, not be the immediate build target.

## Recommendation

**Ship PATH1 first, then use it as the foundation for PATH2.**

Sequence:
1. ✅ Complete Phase 13 benchmark tuning (target ≥80% on T1–T4). Achieved **87.5% (21/24)** with `claude-sonnet-5-20250501`; T5 remains hard and is not gating.
2. ✅ Build the MuJoCo exporter and LearningRobotics handshake as Phases 14A–15A.
3. ✅ Complete the RoboCompiler asset pipeline as Phase 15B — **187/187 tests passing**.
4. ✅ Add cross-domain input (16) → domain-aware representation (17) → decomposition + domain part families (18), all **201/201** then **228/228** tests passing after hardening.
5. ✅ Phase 19 (mechanical assembly synthesis) complete — **251/251 tests passing**.
6. ✅ Phase 20 (aerodynamics, thermal, and propulsion geometry) complete — **276/276 tests passing**.
7. ✅ Phase 21 (electronics / mechatronics co-design) complete — **299/299 tests passing**.
8. Next: 22 (multi-physics) → 23 (humanoid/robot) → 24 (world model) → 25 (brain training) → 26 (HERMES) → 27 (sim-to-real) → 28 (distribution).

**Why this order works:**
- PATH1 is independently valuable and marketable.
- It produces the bundle schema + API surface that PATH2 needs.
- Multi-domain features are added as tracks on a proven core, not as parallel unrelated products.
- Explicit boundaries prevent scope creep into full EDA/CFD.
- Each phase ships something a user or partner can actually run.

**Related:** [[engineer-grade-roadmap]] | [[robocad-end-to-end-roadmap]] | [[claude5-integration-fixes]] | [[phase13-model-specialization]] | [[multi-domain-scope-expansion]]
