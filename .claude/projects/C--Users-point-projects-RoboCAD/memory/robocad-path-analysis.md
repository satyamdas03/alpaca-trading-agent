---
name: robocad-path-analysis
description: Strategic comparison of PATH1 (GEDA Bridge) and PATH2 (voice-to-CAD-to-world-model) for RoboCAD.
metadata: 
  node_type: memory
  type: project
  originSessionId: cb75c83a-be7b-4a7b-bc49-b8099018beb3
  modified: 2026-08-27T07:52:53.060Z
---

Date: 2026-08-25.

We analyzed two strategic directions for RoboCAD against market data, technical feasibility, and competitive landscape.

## PATH1: GEDA Bridge / Phase 15

**What it is:** A delivery-infrastructure play that takes RoboCAD's parametric CAD output and exports it into MuJoCo / URDF / MJCF with correct inertial properties, DFM reports, and a bundle schema that LearningRobotics can consume.

**Market context:**
- Robot skill-learning platforms: ~$4.2–5.4 B (2026), 18–29% CAGR
- Robot learning from demonstration: ~$3.2–4.1 B (2026), 28% CAGR
- Imitation learning for robotics: ~$2.1–2.8 B (2026), 34% CAGR
- AI copilots for robot programming: ~$2.75 B (2026), 28–32% CAGR
- Physical AI simulation / digital twin for robotics: ~$3.8 B+ (2026), 28% CAGR
- Synthetic data generation for robotics: ~$2.5 B (2026), 33% CAGR

**Technical feasibility:** High. The current codebase already has parametric generation, feature trees, assemblies, DFM checks, and exports. A MuJoCo exporter is mostly plumbing and unit conversion.

**Competitive angle:** MuJoCo has no turnkey CAD importer. RoboCAD fills that gap with parametric, editable, manufacturable parts.

**Verdict:** Do this first. It is reachable in 4–6 weeks, creates the exact asset format PATH2 needs, and validates that AI-generated CAD can be physically useful.

## PATH2: Voice/text → CAD → physical test → assembly → world model → HERMES → robot brain

**What it is:** A full-stack robotics design operating system. It bundles six serious sub-products:
1. Voice/text engineering-intent parser
2. Automatic part decomposition
3. Per-part physical simulation (FEA)
4. Automated assembly synthesis
5. World-model simulation + robot brain training
6. HERMES conversational supervisor

**Market context:** Large downstream markets (generative AI in design ~$7 B, digital twin ~$35–47 B, physical AI training ~$3.2 B → $101 B by 2035), but crowded and capital-intensive.

**Technical feasibility:** Mixed. Voice-to-text and LLM intent parsing are mature; part decomposition, arbitrary FEA, and policy training remain hard research problems.

**Verdict:** The right North Star, but the wrong next milestone. It should guide architecture, not be the immediate build target.

## Recommendation

**Ship PATH1 first, then use it as the foundation for PATH2.**

Sequence:
1. ✅ Complete Phase 13 benchmark tuning (target ≥80% on T1–T4). Achieved **87.5% (21/24)** with `claude-sonnet-5-20250501`; T5 remains hard and is not gating.
2. Build the MuJoCo exporter as Phase 14A/15A.
3. Complete the LearningRobotics handshake.
4. Then add voice input, decomposition, physical testing, assembly synthesis, world models, and HERMES.

**Why this order works:**
- PATH1 is independently valuable and marketable.
- It produces the bundle schema + API surface that PATH2 needs.
- It avoids betting everything on multiple unsolved problems at once.
- Each phase ships something a user or partner can actually run.

**Related:** [[engineer-grade-roadmap]] | [[robocad-end-to-end-roadmap]] | [[claude5-integration-fixes]] | [[phase13-model-specialization]]
