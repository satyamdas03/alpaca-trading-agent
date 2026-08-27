---
name: robocad-end-to-end-roadmap
description: Full phased roadmap from current RoboCAD (Phases 0–13) to the voice-to-CAD-to-world-model vision (Phases 13–24).
metadata: 
  node_type: memory
  type: project
  originSessionId: cb75c83a-be7b-4a7b-bc49-b8099018beb3
  modified: 2026-08-27T07:52:39.329Z
---

Date: 2026-08-25.

Total horizon: ~5–7 years. North Star: PATH2 (voice/text → parametric CAD → per-part physical testing → assembly → world-model simulation → HERMES oversight → robot brain trained on synthetic data with retraining loops). First commercial milestone: PATH1 (GEDA Bridge).

## Cross-cutting foundation

Runs entire roadmap:
- Benchmark discipline: keep 30-prompt complexity suite green; publish scores per model/prompt change.
- Test pyramid: unit → integration → simulation-load → end-to-end skill.
- Model zoo: maintain both local (Ollama) and cloud (Claude) paths; specialize local models for speed/cost.
- Schema governance: version feature-tree, assembly, bundle, and world-model schemas; provide migrations.
- CI/CD + git hygiene: every change committed, every demo recorded.
- Documentation: keep README/PLAN/API docs in sync.

## Phase 13 — Robust generation + local model specialization

**Goal:** Get benchmark to ≥80% on T1–T4 and close extractor/self-correction edge cases.

**Status:** ✅ Complete on the T1–T4 quality gate.

**Current state:**
- 134/134 unit tests pass.
- Full 30-prompt benchmark with `claude-sonnet-5-20250501`: **21/30 (70.0%)**.
- T1–T4 aggregate: **21/24 (87.5%)**, above the ≥80% gate.
- T5 aggregate: **0/6** on targeted re-run; T5 remains genuinely hard and is not gating Phase 14A.
- Ollama fine-tuning scaffolding is in place (`robocad-ft:latest` Modelfile created).
- Anthropic SDK compatibility fixes and nested-fence extraction are committed and pushed.

**Deliverables:**
- ✅ Claude Sonnet 5 T1–T4 run at ≥80% (achieved 87.5%).
- ✅ Root-cause report for remaining failures: token limits, nested markdown fences in self-correction, and genuine geometry complexity (assemblies/fillets).
- ✅ Aggressive nested-fence extraction in `_extract_code_block()`.
- ⏳ Clean self-correction prompt to prevent nested fences (can be improved incrementally).
- ⏳ Local model dataset completion and first fine-tuned checkpoint (background work; not blocking).
- ✅ Updated PLAN.md / README.md / memory files with Phases 13–24 roadmap.

**Timeline:** 1–2 months (core gate achieved; remaining work in parallel).

## Phase 14A — GEDA Bridge: MuJoCo / URDF exporter

**Goal:** Convert any RoboCAD part or assembly into a simulation-ready bundle.

**Deliverables:**
- `ai_cad/geda_bridge/exporter.py` with `export_to_mujoco()` and `export_to_urdf()`.
- Bundle schema v2.0.0: manifest, meshes, inertial JSON, MJCF, URDF, DFM report.
- Backend endpoints: `POST /designs/{id}/simulate`, `GET /designs/{id}/bundle`, `GET /designs/{id}/simulation`.
- Frontend Simulate button + download bundle panel.
- Verification: mass > 0, positive-definite inertia, CoM inside convex hull.
- Tests: cube, cylinder, L-bracket, 2-part assembly, gripper jaw.

**Timeline:** 2–3 months.

## Phase 14B — Standard manipulation scenes

**Goal:** Provide reusable scene templates so LearningRobotics can drop a RoboCAD asset into a task.

**Deliverables:**
- Scene templates: `gripper_cube_grasp`, `bracket_hook_hang`, `wedge_push_block`, `peg_insertion`.
- Template composition API: add object, add end-effector, define goal region.
- Example notebooks for MuJoCo and Isaac Sim loaders.

**Timeline:** 1 month.

## Phase 15A — LearningRobotics handshake

**Goal:** LearningRobotics consumes a RoboCAD bundle, loads it into a standard scene, and runs a physics stability check.

**Deliverables:**
- Shared OpenAPI / JSON-Schema contract for bundle ingestion.
- Reference loader in Python for MuJoCo + Isaac Sim.
- End-to-end test: RoboCAD exports wedge → LearningRobotics loads scene → runs 10 s stability rollout.
- Capability registry: `/capabilities` endpoint listing supported part families and scene templates.

**Timeline:** 1–2 months.

## Phase 15B — RoboCompiler asset pipeline

**Goal:** When a human demonstrates a skill on video, RoboCAD suggests/generates a custom end-effector and LearningRobotics trains on it.

**Deliverables:**
- Skill-to-part recommendation.
- Auto-generated part variants (gripper finger lengths, wedge angles, etc.).
- Batch bundle export for variant sweeps.
- Integration test: human video → generated wedge → trained push policy.

**Timeline:** 2–3 months.

## Phase 16 — Voice/text + sketch input

**Goal:** Add voice and multimodal input as first-class modalities; keep text as the debuggable source of truth.

**Deliverables:**
- Whisper/local STT integration.
- Intent parser mapping speech/text to feature-tree operations and constraints.
- Ambiguity resolution UI.
- Sketch-to-constraint: rough 2D sketch → dimension inference → feature tree.
- Voice prompt templates for common operations.

**Timeline:** 2–3 months.

## Phase 17 — Automatic part decomposition

**Goal:** For complex prompts, generate a feature tree for each part plus an assembly plan with mates, fasteners, and manufacturing method.

**Deliverables:**
- Decomposition planner (LLM + heuristic rules).
- Standard joint interfaces (revolute, prismatic, rigid).
- Fastener/surface-join suggestions.
- Manufacturing method hint per part.
- Validation: statically determined assembly, no part intersections.

**Timeline:** 3–4 months. **High risk** — start with parameterized part families.

## Phase 18 — Per-part physical testing

**Goal:** Automatically test each part under realistic load cases before assembly.

**Deliverables:**
- Load-case templates: static load, drop test, thermal expansion, fatigue, fastener pull-out.
- Integration with CalculiX/FEBio for linear/static FEA.
- Material library with density, Young's modulus, yield strength.
- Failure report with suggested redesign.
- Mesh-quality pre-checker.

**Timeline:** 2–3 months. **High risk** — start with closed load-case templates.

## Phase 19 — Assembly synthesis and verification

**Goal:** Combine decomposed parts into a coherent assembly, verify kinematics and clearances, export full robot bundle.

**Deliverables:**
- Mate inference from part interfaces.
- Kinematic loop solver for closed chains.
- Assembly-level collision and clearance checks.
- Full-robot MJCF export with joints, actuators, sensors.
- Assembly replay in the browser.

**Timeline:** 3–4 months.

## Phase 20 — World-model simulation

**Goal:** Drop assembled robot into a parameterized scene with objects, sensors, and domain randomization, ready for policy training.

**Deliverables:**
- World builder API: robot + objects + terrain + sensors + task.
- Domain randomization for mass, friction, actuator gains, sensor noise.
- Scene templates for pick-place, push, locomotion, insertion.
- Export to MuJoCo and Isaac Sim from same world description.
- Replay and inspection tools in frontend.

**Timeline:** 3–4 months.

## Phase 21 — Robot brain training loop

**Goal:** Generate training data, train a policy, evaluate in sim, feed performance back into design.

**Deliverables:**
- Synthetic dataset generator (RGB, depth, segmentation, state, action).
- RL training harness (Isaac Lab / rl-zoo / custom).
- Evaluation metrics: success rate, energy, cycle time, robustness.
- Design feedback loop: flag parts that cause policy failure.
- First closed-loop demo: design → train → evaluate → redesign → retrain.

**Timeline:** 4–6 months. **High risk** — start with imitation learning before full RL.

## Phase 22 — HERMES conversational supervisor

**Goal:** User can talk to RoboCAD like a colleague: ask status, request changes, approve simulations, get explanations.

**Deliverables:**
- HERMES agent with tool use across design, simulation, training APIs.
- Status dashboard: current phase, failures, suggested next actions.
- Approval gates for expensive/dangerous operations.
- Explanation engine for test failures and policy results.
- Memory of project context across sessions.

**Timeline:** 3–4 months. **High risk** — use deterministic execution paths, not black-box control.

## Phase 23 — Sim-to-real feedback loop

**Goal:** Deploy trained policy on real robot, collect failure data, close loop back into simulation and design.

**Deliverables:**
- ROS 2 / micro-ROS / hardware bridge.
- Real-world failure data logger.
- Automatic sim parameter calibration from real trajectories.
- Retraining pipeline: real data → fine-tune policy → re-deploy.
- Safety monitoring: detect OOD states and halt.

**Timeline:** 6–12 months.

## Phase 24 — Distribution and commercialization

**Goal:** Product packaging, licensing, and community.

**Deliverables:**
- Open-source core with paid cloud simulation/training tier.
- Asset marketplace: verified parts, scene templates, trained policies.
- Enterprise features: private model training, PLM integrations, audit logs.
- Community benchmarks and competitions.
- Documentation, tutorials, certification tracks.

**Timeline:** Ongoing.

## Why this plan is realistic

- **Ship-first milestones:** every phase produces something runnable.
- **PATH1 funds PATH2:** bridge is marketable in 6–9 months, funds harder vision layers.
- **Explicit dependencies:** decomposition needs single-part generation; brain training needs world simulation.
- **Risks front-loaded:** high-risk layers get conservative timelines and mitigations.
- **Human in the loop:** HERMES proposes/explains; humans approve safety-critical actions.

**Related:** [[robocad-path-analysis]] | [[engineer-grade-roadmap]] | [[phase13-model-specialization]] | [[claude5-integration-fixes]]
