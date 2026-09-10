---
name: phase23-humanoid-robot-synthesis
description: "Phase 23 completed — humanoid/quadruped/manipulator-on-base templates, actuator sizing, stability/workspace/gait checks, whole-system MJCF/URDF export, backend endpoints, frontend panel; post-ship robot-arm solver fix; 357/357 tests passing."
metadata: 
  node_type: memory
  type: project
  originSessionId: 7435fc68-ca4e-4484-976a-3e6e62f81195
  modified: 2026-09-10T02:58:54.430Z
---

# Phase 23 — Humanoid and full-robot system synthesis

**Status:** COMPLETE as of 2026-09-01. Live-session verification and additional notes added 2026-09-02.

**Test count:** 357/357 tests passing (137 default + 220 heavy/slow/mujoco). Frontend production build passes. Backend endpoints verified with `TestClient` for all three templates plus analysis and simulation export. Dev servers (`uvicorn` on 8000 + Vite on 5173) verified end-to-end, including frontend proxy to `/robot-templates`. Commits: `b5ef502` (Phase 23 code), `ad15b1f` (dossier sync), `11f335d` (vite proxy fix), `174df8c` (assembly solver csys fix).

## What shipped

1. **Kinematic skeleton templates** (`ai_cad/robot_templates.py`)
   - `humanoid_template()` — biped with legs, arms, and fixed hand attachments.
   - `quadruped_template()` — four 3-DOF legs.
   - `manipulator_on_base_template()` — mobile base + serial arm.
2. **Correct forward kinematics** (`ai_cad/kinematic_tree.py`)
   - Fixed double-counting of absolute transforms; zero pose now returns nominal placements.
   - Added fixed hand joints so `get_joint_chain()` reaches `hand_l`/`hand_r`.
   - Clamped Euler asin input to avoid floating-point domain errors during workspace sampling.
   - Lazy reservoir sampling in `sample_reachable_workspace()` to avoid materializing 3^14 ≈ 4.8M joint combinations.
3. **Actuator sizing** (`ai_cad/actuator_sizing.py`) — unchanged; specs produced from payload × safety factor.
4. **Stability & gait** (`ai_cad/stability.py`, `ai_cad/verification_load_cases.py`)
   - Convex-hull support polygon from foot contact corners.
   - `warning_count` float metric instead of list so `VerificationResult` validates.
   - Workspace/gait load cases produce numeric-only metrics.
5. **Whole-system MJCF/URDF export** (`ai_cad/geda_bridge/exporter.py`)
   - Placeholder links with no geometry now emit a 10mm cube so skeleton templates still produce valid bundles.
   - Verified humanoid, quadruped, and manipulator templates export valid URDF + MJCF.
6. **Backend endpoints** (`web/backend/main.py`)
   - `GET /robot-templates`
   - `POST /robot-templates`
   - `POST /designs/{id}/robot-analysis`
   - `POST /designs/{id}/simulate` already exported the bundle from the tree.
7. **Frontend panel** (`web/frontend/src/components/HumanoidPanel.jsx`)
   - Template selector, parameter editor, create/analyze buttons, stability/workspace/gait readout.
   - Updated to consume `warning_count` from the backend stability summary.
8. **End-to-end API tests** (`tests/test_phase23_robot_api.py`) — covers all three templates, analysis, and simulation export.

## Critical fixes included

- Kinematic transform double-counting → feet now at correct z ≈ 0 mm.
- Empty hand joint chains → `hand_r` reachable.
- `sample_reachable_workspace` RAM spike → capped lazy sampling.
- `VerificationResult` validation errors for string/list metrics → cleaned metrics dicts.
- Skeleton template export failure → fallback cube meshes for placeholder parts.
- Frontend dev proxy missing Phase 16–23 endpoints → added `/decompose`, `/classify-domain`, `/capabilities`, `/robot-templates` and switched target to `127.0.0.1:8000`.
- **Post-ship rule-based "robot arm with gripper" quality fix (commits `87c8f7b`, `980482b`, `174df8c`, `4de18d8`, `1b83561`):**
  - Decomposition now maps upper/forearm links to `limb_segment` and the gripper to `end_effector` instead of raw mechanical `link`/`mount` boxes.
  - Composer places instances by aligning limb pin interfaces, producing a real revolute upper/forearm chain and a parallel-jaw gripper with prismatic Y-axis motion.
  - Mate inference now respects the explicit `Part.family` field, so parts like `upper_link` use their registered family interfaces rather than substring guessing.
  - Commit `980482b` corrected the elbow spacing and gripper jaw mirroring so the upper and forearm connect and the two jaws sit on opposite sides of the Y axis.
  - Commit `174df8c` fixed the assembly solver so it resolves mate coordinate systems through the instance → part → part-family interface chain (`limb_pin_a`, `limb_pin_b`, `gripper_pivot_csys`). Previously the solver only searched `tree.coordinate_systems`, fell back to default origins, and drifted the whole arm chain; explicit composer transforms now survive solver relaxation unchanged.
  - Commit `4de18d8` fixed the transpiler: sketch entities inside `BuildSketch` were emitted as `Rectangle(...).move(Location(...))`, but build123d ignores `.move()` there, so the limb-segment body stayed centered at the origin while its pin holes were offset. The transpiler now wraps centered entities in `with Locations(Location(center)):` so they actually move.
  - Commit `1b83561` added separate subtractive circle sketches to the `limb_segment` and `end_effector` families so the joint bores and pivot hole are real holes, not solid disks. Combined STL now has 1556 vertices / 3092 faces and exports a valid URDF with a revolute elbow and two opposing prismatic gripper jaws.
  - Commit `69367a1` fixed a sketch-ID / parameter-name collision in the humanoid hub families: `_humanoid_hip_hub()` and `_humanoid_shoulder_hub()` used subtractive sketch IDs `hip_bore` and `shoulder_bore`, which shadowed the global parameters of the same name. The generated Python then failed with `TypeError: unsupported operand type(s) for /: 'BuildSketch' and 'int'` because `Circle(radius=hip_bore / 2)` tried to divide a `BuildSketch` object by `2`. Renaming the subtractive sketches to `hip_bore_cut_profile` and `shoulder_bore_cut_profile` removed the shadowing, and the rule-based "biped humanoid robot" prompt now succeeds end-to-end.
  - Commit `6a9faf4` fixed misleading validation reporting for rule-based assemblies. The merged STL preview of touching parts was always non-watertight/non-manifold, causing the frontend to show "Manifold: FAIL / Watertight: FAIL" even though each individual body was watertight. `_build_assembly_validation_report()` now splits the merged preview into bodies, verifies each body, and marks the design `valid=True` while honestly keeping `manifold=False/watertight=False` and surfacing an explanatory warning. The frontend `Assembly collision` button also had a method mismatch (GET vs POST); the API call now uses POST.
  - Live backend verification:
    - "robot arm with gripper" produces a 154 KB STL and an 81 KB MJCF/URDF bundle with per-part watertight meshes; URDF contains joints `j_i_upper_link_i_forearm_link` (revolute), `j_i_forearm_link_i_gripper_0/1` (prismatic, opposing Y axes). After `6a9faf4` the frontend status shows Success with a warning that the merged STL is an assembly preview.
    - "biped humanoid robot" produces a 382 KB STL with 3840 vertices and bounds `[-70.22, -40, 192.08]` to `[203.09, 65, 472.0]`.
  - 357/357 tests passing (137 default + 220 heavy/slow/mujoco); frontend dev server on port 5173 still responding; backend restarted with the new code.

## Stress-test routing summary

A three-prompt stress test clarified which code path `/generate` uses and where failure modes remain:

| Prompt | Path | Anthropic API? | Result | Notes |
|---|---|---|---|---|
| "wheel hub for go-kart" | LLM direct | Yes | ✅ Success | Single rotational part; revolve + bolt-pattern operations are easy for the LLM. |
| "worm gear reducer housing" | LLM direct | Yes | ✅ Success | Extruded box with bores/ribs/flange; no articulated mates. |
| "biped humanoid robot" | Rule-based decomposition | No | ✅ Success after `69367a1` | Part-family composition, assembly solver, transpiler chain. |

**Rule-based / no-API prompts:** robot arm with gripper, biped humanoid robot, quadruped walking robot, drone quadcopter frame, fixed-wing UAV, electronics stack motor controller.

**LLM / API-required prompts:** wheel hub, worm gear housing, custom servo bracket, heat sink, PCB mounting enclosure, NACA airfoil/wing, custom single parts not matching system templates.

**Edge cases still likely to degrade:** robotic hand (no hand/finger families), hexapod (no template), tracked rover (no track family), delta/SCARA arms (no templates). These will go to the LLM as single parts and may be structurally incomplete.

## Latest live-session verification (2026-09-02)

- User-generated `robot arm with gripper` (design #60bf6c9e) was analyzed end-to-end. The output was structurally correct: the upper and forearm connect at the elbow, and the two gripper jaws are on opposite sides of the Y axis. The merged STL preview was marked valid after commit `6a9faf4`, with `manifold=False`/`watertight=False` honestly reported because touching parts cannot form a single watertight manifold.
- The `Assembly collision` frontend button had a GET/POST method mismatch that caused `{"detail":"Method Not Allowed"}`; fixed in `6a9faf4` by changing `web/frontend/src/api.js` to POST.
- The project `.venv` was missing `python-dotenv`, so the backend was restarted using the Hermes venv (`C:\Users\point\AppData\Local\hermes\hermes-agent\venv\Scripts\python`). The frontend Vite server on port 5173 remained running.
- Prompt `robotic arm with five fingers` was tested and fell back to the standard 2-link robot arm because the rule-based decomposer has no hand/finger part family. It matched the `robot arm` keyword set and ignored the fingers.
- Full pytest suite: **357/357 passing**. Frontend production build: passes.

## Cosmetic/mechanical refinement queued

The user explicitly flagged the next priority: upgrade the rule-based robot arm from a valid first pass to an engineer-grade starting point by adding deterministic, testable options to `limb_segment` and `end_effector`:

1. Fillets and chamfers scaled by part size.
2. Joint bosses / flanges around pin interfaces.
3. Tapered links (`taper_ratio`) for structural I-beam/trapezoid profiles.

**Note:** These cosmetic refinements remain queued; Phase 28D instead shipped the morphology co-design lab on top of the existing templates. They can be picked up in a future hardening pass.
4. Gripper jaw shaping: contact pads, rounded fingertips, V-groove centering.
5. Transpiler name-mangling guard so sketch IDs can never shadow global parameters again.

These are intentionally rule-based improvements, not LLM prompt engineering.

## Resource/robustness notes

- No new unbounded recursion or Cartesian-product loops introduced.
- `forward_kinematics()` retains recursion cycle guard from the Phase 23 hotfix.
- Workspace sampling still caps at 4096 configurations.
- Placeholder cube keeps bundles valid without waiting for family-builder geometry.

## Why it matters

Phase 23 closes the loop from a one-line robot description to a parameterized kinematic tree, actuator sizing, stability gate, reachable workspace, gait feasibility, and a MuJoCo/URDF-ready bundle. This is the foundation for Phase 24 world-model simulation and Phase 25 training loops.

## How to apply / extend

- To add a new morphology, add a template function in `ai_cad/robot_templates.py` and register it in `/robot-templates`.
- To tune stability thresholds, adjust parameters passed to `check_stability()` or the verification load cases.
- To replace placeholder meshes, run decomposition + composer + family builders before exporting.

## Related memories

- [[phase23-hotfix-memory-cpu-hardening]] — RAM/CPU safeguards applied before this phase.
- [[phase22-multi-physics-verification]] — verification engine this phase builds on.
- [[phase19-assembly-synthesis]] — kinematic mates and assembly synthesis reused here.
- [[phase14a-geda-bridge]] — MJCF/URDF exporter used for whole-system export.
