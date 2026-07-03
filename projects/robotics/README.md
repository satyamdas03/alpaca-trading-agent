# Robotics: Uncertainty-Aware Physics-Coupled LLM Multi-Robot Construction

A local-LLM-driven multi-robot block-construction demo in PyBullet. The
planner runs on your machine via Ollama, and high-uncertainty plan steps are
validated with fast physics rollouts before real execution.

## What this is

This project turns a PyBullet simulator into an active reasoning module. An
8B-class local LLM (Ollama) emits a JSON plan for each robot. The planner then:

1. Samples multiple plans at non-zero temperature.
2. Fuses them into a consensus plan with **per-step ensemble uncertainty**.
3. For every step whose uncertainty exceeds a threshold, runs a reversible
   **physics rollout** via `pybullet.saveState` / `restoreState`.
4. Executes the step for real only if the rollout succeeds and contact forces
   stay within bounds.
5. On real failure, reports the failed step back to the LLM for closed-loop
   replanning.

## Quick start

Requirements:
- Python 3.10+
- `pip install -r requirements.txt` (or manually: `pybullet`, `numpy`, `opencv-python`)
- [Ollama](https://ollama.com) running with a model installed (default is
  `qwen3.5:latest`; edit `OLLAMA_MODEL` in
  `next_level/world_building_construction_uncertainty.py` to switch)

Run the red-blue alternating wall demo:

```bash
ollama serve                      # if not already running
python next_level/world_building_construction_uncertainty.py
```

For a fully automated / headless run:

```bash
BULL_AUTO_START=1 BULL_DIRECT=1 python next_level/world_building_construction_uncertainty.py
```

## Key files

| File | Purpose |
|------|---------|
| `next_level/world_building_construction_uncertainty.py` | Main demo: uncertainty-aware planner + multi-robot PyBullet skills |
| `next_level/world_building_construction_COMPLETE.py` | Stable baseline multi-robot stacking controller (no uncertainty) |
| `llm_robot_controller_vision.py` | Single-robot LLM controller with OpenCV vision |
| `tests/test_uncertainty_snapshot.py` | Unit tests for save/load state and physics rollouts |

## Architecture

```
User command
    │
    ▼
┌─────────────────┐
│  Ensemble LLM   │  ← 3 samples at T=0.8, fused by step-level voting
│    planner      │
└────────┬────────┘
         │ JSON plan + per-step uncertainty
         ▼
┌─────────────────┐
│  parse_and_     │  ← threshold check; rollout if uncertainty ≥ 0.6
│   execute()     │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
 Rollout    Real
(DIRECT)   (GUI)
    │         │
    └────┬────┘
         ▼
   PyBullet skills
   (move_to, pickup, place_at, return_object)
```

### Uncertainty fusion

`_ensemble_uncertainty()` compares the N sampled plans step-by-step. A step
receives `uncertainty = 1.0 - (votes / N)`. If the LLM also reports its own
self-confidence, that field is preserved but **not used** for the threshold;
the ensemble vote is the primary signal because self-reported confidence is
notoriously unreliable in small LLMs.

### Reversible physics rollout

`save_world_state()` captures:
- PyBullet full physics state via `p.saveState()`
- Base positions/orientations/velocities of every object
- Python-side robot mental state (`held_object_name`, `current_constraint`)

`simulate_branch()` runs the candidate plan at maximum speed, checks for
excessive contact forces, and restores the snapshot before returning. The
real execution therefore never sees the side effects of a failed candidate.

## Tests

```bash
python tests/test_uncertainty_snapshot.py
```

Tests cover:
- Physics-state snapshot/restore
- Robot mental-state restore
- Branch simulator rejecting an unreachable placement

## Tuning

- `UNCERTAINTY_ROLLOUT_THRESHOLD` in the main file controls when a rollout is
  triggered (default `0.6`).
- `USE_ENSEMBLE` in `main()` toggles single-plan vs. ensemble planning.
- `OLLAMA_MODEL` selects the Ollama model.

## Current demo behavior

The default demo instructs three R2-D2 robots to build a horizontal red-blue-red
alternating wall:

- robot_0 → `block_red` at `(-2.25, 0, 0.1)`
- robot_1 → `block_blue` at `(-2.0, 0, 0.1)`
- robot_2 → `block_red_2` at `(-1.75, 0, 0.1)`

In the latest run the planner produced identical samples (uncertainty 0.0),
so no physics rollouts fired, but the ensemble planner, failure reporting, and
closed-loop replanning all executed correctly.

## Project history / this iteration

This codebase was dormant and was revived with a focused build toward a
novel, demo-able advancement: an **Uncertainty-Aware Physics-Coupled Local-LLM
Planner for Multi-Robot Block Construction**.

What was done in this iteration:

1. **Project archaeology** — read every historical controller variant
   (`llm_robot_controller.py`, `llm_robot_controller_ad.py`,
   `llm_robot_controller_dynamic_replanning.py`, `llm_robot_controller_vision.py`,
   and all `next_level/world_building_construction_*.py` files) to understand the
   lineage, strengths, and weaknesses.

2. **Direction selected** — from a brainstorming workflow, chose Direction #1:
   make PyBullet an active reasoning module where the LLM emits plans with
   per-step uncertainty, and high-uncertainty steps are validated by fast physics
   rollouts before real execution.

3. **Implementation base** — copied the most stable multi-robot stacking file
   (`world_building_construction_COMPLETE.py`) into
   `world_building_construction_uncertainty.py` and extended it.

4. **Planner extensions**
   - Added optional per-step `uncertainty` field to the system prompt.
   - Added `temperature` control to `get_llm_plan()`.
   - Added ensemble planning functions (`_step_key`, `_ensemble_uncertainty`,
     `get_ensemble_plan`) that fuse N temperature-perturbed samples into one plan
     with uncertainty scores.

5. **Physics-coupled rollout infrastructure**
   - `save_world_state()` / `load_world_state()` capture PyBullet physics state,
     object positions/velocities, and Python-side robot mental state.
   - `simulate_branch()` runs candidate plans at full speed in a reversible
     snapshot, checks contact forces, and restores the world before returning.

6. **Executor wiring** — `parse_and_execute()` triggers a physics rollout for
   any step with `uncertainty >= UNCERTAINTY_ROLLOUT_THRESHOLD` (default 0.6) and
   rejects the step if the rollout fails. Failed steps are reported back for
   closed-loop LLM replanning.

7. **Demo scenario** — changed the task from a vertical stack to a horizontal
   **red-blue-red alternating wall** by adding `block_red_2` and target positions
   `-2.25/-2.0/-1.75, 0, 0.1`.

8. **Runtime metrics** — added counters for ensemble plans, replans, rollouts,
   rollout rejections, executed steps, and failed steps, printed at demo end.

9. **Automation flags** — added `BULL_AUTO_START=1` to skip the interactive
   prompt and `BULL_DIRECT=1` to force PyBullet DIRECT mode for headless runs.

10. **Unit tests** — created `tests/test_uncertainty_snapshot.py` with passing
    tests for:
    - Physics-state snapshot/restore
    - Robot mental-state restore
    - Branch simulator rejecting an unreachable placement

11. **Model portability** — made the Ollama model a top-level constant
    (`OLLAMA_MODEL = "qwen3.5:latest"`) so the demo adapts to whatever model is
    installed locally.

12. **Documentation & packaging** — wrote `README.md`, created
    `requirements.txt`, and committed the work.

13. **Live demo run** — executed the full demo in DIRECT mode. robot_0 and
    robot_2 placed their blocks on the first try; robot_1 timed out moving to
    `block_blue` and successfully replanned. Final metrics:
    - ensemble_plans_generated: 4
    - replan_attempts: 1
    - failed_steps: 1
    - steps_executed: 10
    - rollouts_run: 0 (the current LLM produced identical samples at T=0.8)

## Git status note

There is no dedicated GitHub remote for this robotics subdirectory yet. The
only configured `origin` is `alpaca-trading-agent`, which is a different project.
If you want this on GitHub, create a new repository (e.g.,
`satyamdas03/robotics-llm-construction`) and run:

```bash
cd C:/Users/point/projects/robotics
git init
git add .
git commit -m "Initial commit: uncertainty-aware physics-coupled LLM planner"
git remote add origin https://github.com/satyamdas03/YOUR_NEW_REPO.git
git push -u origin main
```

## Next steps / experiments

- Raise ensemble temperature or add command ambiguity to trigger live physics
  rollouts in the demo.
- Add vision-based world-state confidence (e.g., object detection score) into
  the uncertainty budget.
- Compare wall-building success with vs. without physics rollouts across many
  randomized initial poses.
- Export a trajectory video / metrics log for a paper or portfolio entry.
- Move to a dedicated GitHub repository for the robotics project.
