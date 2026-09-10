---
name: phase24-world-simulation
description: "Phase 24 completion — world-model simulation builder with domain templates, randomization, MuJoCo + Isaac Sim export, frontend replay, and tests."
metadata: 
  node_type: memory
  type: project
  originSessionId: 7435fc68-ca4e-4484-976a-3e6e62f81195
  modified: 2026-09-03T07:31:14.973Z
---

# Phase 24 — World-model simulation builder

**Completed:** 2026-09-03 (initial ship) + 2026-09-01 (post-ship hardening)

**Goal:** Drop the assembled RoboCAD system into a parameterized scene with objects, terrain, sensors, and domain randomization, ready for policy training across manipulation, locomotion, aerial, and humanoid tasks.

## What shipped

- `ai_cad/geda_bridge/world_builder.py`
  - `WorldDescription`, `WorldBuilder`, `WorldTerrain`, `WorldSensor`, `WorldTask`, `DomainRandomization`
  - Domain templates: `pick_place`, `push`, `walker`, `drone_hover`, `humanoid_stand`
  - `apply_domain_randomization(world, seed)` — deterministic mass/friction/actuator/sensor/wind/thermal perturbation
  - `export_world_to_mjcf(world, path)` — MuJoCo world with robot MJCF include, terrain, props, sensors, task sites
  - `export_world_to_isaac_json(world, path)` — Isaac Sim consumable JSON world description with built-in schema validation (`validate_isaac_world_json`)
  - Procedural terrain helpers: `plane_terrain`, `box_terrain`, `slope_terrain`, `stair_terrain`, `ramp_terrain`, `uneven_terrain`
  - Body-name alias resolver: `resolve_body_alias`, `resolve_world_body_aliases` so locomotion/humanoid sensor and task references map to actual MJCF body names
- `ai_cad/geda_bridge/world_loaders.py`
  - `load_world_into_mujoco(world, output_dir)` — resolves aliases before export
  - `load_world_into_isaac_sim(world, output_dir)` — resolves aliases before JSON export
  - `run_world_replay(...)` — rich replay capturing positions, orientations, linear velocities, contact forces, actuator controls/forces, and sensor readings
- `ai_cad/geda_bridge/__init__.py` — exported all new symbols
- `ai_cad/geda_bridge/capabilities.py` — added `isaac_sim` simulator and new world templates; bumped API version to 0.4.0
- `web/backend/main.py` — new endpoints:
  - `POST /designs/{id}/world`
  - `GET /designs/{id}/world`
  - `POST /designs/{id}/world/randomize`
  - `POST /designs/{id}/world/replay`
- `web/frontend/src/api.js` — `buildWorld`, `getWorldReport`, `randomizeWorld`, `replayWorld`
- `web/frontend/src/components/WorldBuilderPanel.jsx` — template selector, randomize toggle/seed, build/randomize/replay buttons, status + download links
- `web/frontend/src/App.jsx` — `WorldBuilderPanel` wired into the panel grid
- `tests/test_world_builder.py` — 19 tests covering all templates, terrain variants, MJCF load, Isaac JSON schema validation, body alias resolution, randomization determinism, sensor/terrain serialization, and rich replay

## Test results

- Default pytest suite: **154 passed**, 222 deselected
- Heavy/slow/MuJoCo pytest suite: **222 passed**, 154 deselected
- **Total: 376/376 tests passing**
- Frontend production build: passes

**Why:** Phase 24 is the bridge between editable parametric robot design and downstream policy-training environments. The same world description now feeds both MuJoCo (contact-rich RL) and Isaac Sim (GPU-parallel synthetic data).

**How to apply:** Use the `WorldBuilderPanel` in the frontend after generating a robot or mechanism, or call the backend endpoints directly from `LearningRobotics` / training scripts.

**Caveats resolved by hardening:** body-name fragility for locomotion/humanoid templates; replay limited to positions; simple block-only terrain; Isaac Sim JSON not structurally validated. **Remaining caveat:** full Isaac Sim runtime import/load/render cannot be validated on this machine because the NVIDIA Omniverse / Isaac Sim packages are not installed.

Related memories: [[phase23-humanoid-robot-synthesis]], [[phase22-multi-physics-verification]], [[phase14b-scene-templates]], [[phase15a-learning-robotics-handshake]]
