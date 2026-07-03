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

## Next steps / experiments

- Raise ensemble temperature or add command ambiguity to trigger rollouts live.
- Add vision-based world-state confidence (e.g., object detection score) into
  the uncertainty budget.
- Compare wall-building success with vs. without physics rollouts across many
  randomized initial poses.
- Export a trajectory video / metrics log for a paper or portfolio entry.
