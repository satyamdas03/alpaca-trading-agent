---
name: phase14b-scene-templates
description: Phase 14B standard manipulation scene templates — drop-in MuJoCo task scenes for RoboCAD exported assets.
metadata:
  node_type: memory
  type: project
  originSessionId: cb75c83a-be7b-4a7b-bc49-b8099018beb3
  modified: 2026-08-27T10:36:06.932Z
---

Date: 2026-08-27.

**Status:** ✅ Complete.

**Goal:** Give `LearningRobotics` reusable, drop-in MuJoCo/Isaac Sim scenes that place a RoboCAD-designed asset into a standard manipulation task.

**What was built:**
- `ai_cad/geda_bridge/scene_templates.py` — `ManipulationScene` composition API plus dataclasses `SceneDescription`, `SceneObject`, `SceneGoalRegion`, `ScenePose`.
- Built-in templates:
  - `gripper_cube_grasp` — parallel-jaw gripper asset above a table + target cube + lift goal site.
  - `bracket_hook_hang` — wall + peg + hang goal site.
  - `wedge_push_block` — table + block to push + target-zone goal site.
  - `peg_insertion` — board with four-wall hole + insertion goal site.
- `export_scene_to_mjcf()` generates a standalone MJCF world referencing the bundle `meshes/` directory.
- Backend endpoints in `web/backend/main.py`: `POST /designs/{id}/scene` and `GET /designs/{id}/scene`.
- Frontend `SceneTemplatePanel.jsx` integrated into `App.jsx`.
- Tests: `tests/test_geda_bridge_scenes.py` (8 tests) + 2 new backend endpoint tests in `tests/test_web_backend.py`.
- Full pytest suite: **160 passed**.

**Known gaps / next work:**
- Isaac Sim loader examples (deferred to Phase 15A/20).
- Collision mesh convex decomposition for complex asset geometries.
- RL-ready actuator definitions for grippers/end-effectors.

**Related:** [[phase14a-geda-bridge]] | [[robocad-end-to-end-roadmap]] | [[robocad-path-analysis]]
