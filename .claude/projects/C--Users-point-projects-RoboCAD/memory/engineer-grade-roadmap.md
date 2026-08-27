---
name: engineer-grade-roadmap
description: Strategic decision and phased roadmap to evolve RoboCAD from single-part prompt-to-code into an engineer-grade CAD system with feature trees, constraints, assemblies, and verification.
metadata:
  type: project
  originSessionId: a496167a-b1cf-4304-85e9-8d260f40418c
  modified: 2026-08-24T10:43:51.680Z
---

RoboCAD completed Phases 0–7: AI → build123d code loop, editable parameters, face-click guessing, design library, Onshape export, robotics component templates, and the Google Stitch *Kinetic Precision* UI redesign. The app works end-to-end for single-part prismatic robotics hardware.

**Strategic decision (2026-08-23):** To make RoboCAD usable by real mechanical engineers for complex, high-precision, multi-part designs, the next leap is **not** a bigger model or longer prompt. It is a change in representation:

> From `prompt → one Python script → one STL`  
> To `prompt → structured feature tree + 2D constraints + assembly mates → verified CAD → manufacturing/FEA report`

This aligns with where the CAD industry and research are moving. PTC's Onshape FeatureScript MCP Server (Aug 2026) and the CADFS research project both treat executable parametric feature histories — not static meshes — as the correct AI target. RoboCAD already generates parametric code; the new phases add symbolic CAD infrastructure around it.

## Phase summary

| Phase | Goal |
|---|---|
| **8** | Complexity benchmark + feature-tree JSON schema |
| **9** | Feature-tree backend (replace monolithic `code.py`) |
| **10** | Sketch + 2D constraint solver |
| **11** | Assembly system with LCS-based mates |
| **12** | Verification + physics layer (DFM, FEA, tolerances) |
| **13** | Model specialization / LoRA fine-tuning |
| **14** | Distribution + packaging |

## Why this is the right path

- **Feature trees** give rollback, partial regeneration, and human-readable design history.
- **2D sketch constraints** keep holes centered and aligned when dimensions change; this is where real precision lives.
- **Assemblies** are required because robotics is motors, bearings, brackets, and wheels working together — not isolated parts.
- **Verification** gives engineers confidence that parts can be manufactured and will survive loads.
- **Fine-tuning** improves success rates on complex parts without depending solely on prompt engineering.
- **Packaging** is required because real users cannot manually set up Python/Node.

## Key trade-offs

- Start with a minimal internal 2D constraint subset; migrate to PlaneGCS/SolveSpace only after validation.
- Use LCS/expression-based assembly mating (Assembly4-style) rather than a full physics solver to avoid instability.
- Make FEA optional with graceful degradation if CalculiX/ElmerFEM is not installed.
- Keep `code.py` as a fallback while `feature_tree.json` becomes the preferred source of truth.

## First step

Phase 8: build and run a complexity benchmark against the current local Ollama model, define the feature-tree schema, and publish the baseline report. This provides data to validate every later phase.

## Documentation updated

- `README.md` — extended phase table and new **🎯 Engineer-grade roadmap** section.
- `PLAN.md` — new sections 9–11 with detailed phase definitions, trade-offs, and risks.
- Memory files updated to reference the roadmap.
- Pushed commit `f2723f3 docs(roadmap): add engineer-grade Phases 8-14 to README and PLAN`.

**Related:** [[phase5-phase6-completion]] [[google-stitch-ui-redesign]]
