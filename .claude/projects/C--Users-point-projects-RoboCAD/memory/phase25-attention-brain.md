---
name: phase25-attention-brain
description: Phase 25 — applied AI chip co-design ideas to RoboCAD world model and robot brain training layer.
metadata: 
  node_type: memory
  type: project
  originSessionId: 7435fc68-ca4e-4484-976a-3e6e62f81195
  modified: 2026-09-03T08:39:39.775Z
---

# Phase 25 — Attention-based robot brain training layer

**Date:** 2026-09-01  
**Status:** complete  
**Tests:** 170 default + 222 heavy/slow + 22 mujoco = 414 tests passing (Phase 24 baseline 376 + new brain tests).

## What was done

Applied concepts from Cao et al. *Advanced Design for High-Performance and AI Chips* (especially Figure 5: attention-based dynamic processing, event-driven sensing, compute budgets, dynamic pruning) to RoboCAD's world builder and a new lightweight robot-brain training package.

### World-model extensions (Phase 24 → 25 bridge)

- Added `ComputeBudget` dataclass to `ai_cad/geda_bridge/world_builder.py` with `tops`, `power_w`, `latency_ms`, `memory_mb`. Every built-in world template now carries a default compute budget.
- Added `attention_regions: list[SceneGoalRegion]` to `WorldTask` so a world can declare regions the agent should prioritise.
- Added `actuator_noise_std` and `sensor_dropout_prob` to `DomainRandomization` to model unreliable actuators / sparse sensors.
- Added `event_camera` support in `WorldSensor` with a numeric type flag and a mount family.
- Extended `run_world_replay` in `ai_cad/geda_bridge/world_loaders.py` to return per-body `saliency` (`max_vel`, `max_acc`, `max_force`) for downstream attention training.
- Serialised compute budget, attention regions, actuator noise and sensor dropout into both MJCF metadata and the Isaac JSON schema / exporter.
- Added `metadata: dict[str, Any]` to `Part` (`ai_cad/feature_tree.py`) and `PartFamily` (`ai_cad/part_families.py`) so families can carry compute-budget / power-budget annotations.
- Added `compute_module` and `event_camera_mount` electronics part families, registered in the family registry, and updated the electronics-stack composer to place them above the PCB / front of the enclosure.
- Bumped GEDA Bridge API version to `0.5.0` and documented the new `brain_train`, `brain_report`, and `brain_replay_attention` capability endpoints.

### Robot-brain package (`ai_cad/geda_bridge/brain/`)

New deterministic, NumPy-only brain training layer:

- `world_model.py` — `SaliencySnapshot`, `compute_saliency`, `AttentionBudget` (converts TOPS/latency/memory into a maximum active-observation dimension), and a tiny `LinearWorldModel` trained by ridge regression.
- `policies.py` — `AttentionMLPPolicy`, a fixed-architecture ReLU MLP with a hard attention mask on its inputs.
- `envs.py` — `AbstractAttentionEnv`, a pure-NumPy 2-D navigation task built from a `WorldDescription`'s attention regions and compute budget; plus a stub `WorldReplayEnv` for future MuJoCo-backed closed-loop rollouts.
- `trainer.py` — CEM trainer (`train_attention_policy`) and evaluation harness (`evaluate_attention_policy`, `train_and_evaluate`).
- `__init__.py` — clean public exports.

### Backend & frontend

- Added FastAPI endpoints:
  - `POST /designs/{id}/train-brain`
  - `GET /designs/{id}/brain`
  - `POST /designs/{id}/brain-replay-attention`
- Extended world builder endpoints to persist and return `compute_budget` and `attention_regions`.
- Added `BrainTrainingPanel.jsx` to the frontend grid with train controls, live report, and attention smoke-test.
- Extended `WorldBuilderPanel.jsx` to display compute budget and attention regions.
- Added `trainBrain`, `getBrainReport`, `replayBrainAttention` to `web/frontend/src/api.js`.

## Tests

- `tests/test_geda_bridge_brain.py` — 16 new tests covering saliency scoring, attention budgets, linear world model fitting, abstract environment rollouts, CEM training, and the high-level `train_and_evaluate` report.
- Updated `tests/test_part_families.py` to include the two new electronics families.
- Full suite run:
  - `python -m pytest -q` (default tier): 170 passed
  - `python -m pytest -q -m "heavy or slow"`: 222 passed, 1 xfailed
  - `python -m pytest -q -m mujoco`: 22 passed
  - Frontend `npm run build`: passes.

## Why

The paper's co-design loop (materials → devices → circuits → architecture → software) is too deep for a CAD-for-robotics pipeline to fabricate chips, but its architectural ideas — attention, event-driven sensing, compute budgets, dynamic pruning — map directly onto how a robot brain should prioritise sensing and control in a generated world. Adding them makes RoboCAD's simulation output training-ready for efficient, embedded policies instead of generic black-box RL.

## How to apply

- When building a world, inspect `compute_budget` and `attention_regions` returned by the world builder; use them to size onboard compute modules and sensor mounts.
- Run `/train-brain` on any design to produce a tiny attention-aware policy that can be exported as a flat weight vector for embedded inference.
- Use `/brain-replay-attention` as a quick smoke test to validate that compute-budget limits actually restrict observation dimensions.
- Extend `AbstractAttentionEnv` with richer dynamics, or implement `WorldReplayEnv.rollout` for real MuJoCo closed-loop training once the world description exposes stable closed-loop actuation.

## Links

- [[Phase 24 — world-model simulation builder]] — baseline world builder and replay system.
- [[Phase 15B RoboCompiler pipeline]] — existing NumPy-only CEM smoke test that the brain layer builds on.
- `ai_cad/geda_bridge/brain/` — new package.
