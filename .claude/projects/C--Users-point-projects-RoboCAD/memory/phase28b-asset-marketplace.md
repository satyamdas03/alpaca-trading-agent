---
name: phase28b-asset-marketplace
description: Phase 28B — verified asset marketplace backend + frontend + tests.
metadata: 
  node_type: memory
  type: project
  originSessionId: 7435fc68-ca4e-4484-976a-3e6e62f81195
  modified: 2026-09-08T01:22:33.041Z
---

# Phase 28B — Asset Marketplace

**Date:** 2026-09-08
**Status:** complete
**Commit:** `9a7bf5a` — `robocad: Phase 28B — asset marketplace backend with CRUD, verified-asset validation, starter packs, and import endpoints`

## What shipped

1. **`ai_cad/marketplace.py`** — file-system-backed asset catalog.
   - `AssetType` enum: `part`, `scene_template`, `robot_template`, `world_template`, `electronics_template`, `aero_template`.
   - `MarketplaceItem` and `MarketplaceImportResult` Pydantic models.
   - Local JSON index at `marketplace/index.json`.
   - CRUD helpers: `list_items`, `get_item`, `create_item`, `update_item`, `delete_item`, `record_download`.
   - `verify_asset()` — verification gate that must pass before an item can be marked `verified`:
     - **Parts:** DFM analysis + mesh-quality pre-check on `model.stl`.
     - **Scene / robot / world templates:** bundle verification (`verify_bundle`) + MuJoCo runtime validation (`validate_bundle_with_mujoco`).
   - `import_item_into_design()` — copies the asset source directory into `designs/{design_id}/imports/{item_id}/`, merges `feature_tree.json` if present, and records the import in `metadata.json`.

2. **`web/backend/main.py`** — FastAPI marketplace endpoints.
   - `GET /marketplace/items` (filter by `asset_type`, `tag`, `search`, `verified_only`).
   - `GET /marketplace/items/{id}`.
   - `POST /marketplace/items`.
   - `POST /marketplace/items/{id}` (update).
   - `POST /marketplace/items/{id}/verify`.
   - `POST /marketplace/items/{id}/download`.
   - `POST /marketplace/items/{id}/import/{design_id}`.
   - `DELETE /marketplace/items/{id}`.

3. **Starter asset packs** under `marketplace/starter_packs/`.
   - `parts/bracket/` — L-bracket with `model.stl` and `feature_tree.json`.
   - `scene_templates/gripper_cube_grasp/` — simulation bundle (MJCF/URDF/STL).
   - `robot_templates/manipulator_on_base/` — simulation bundle (MJCF/URDF/STL).
   - `.gitignore` updated to allow committed starter-pack STLs/STEPs/URDFs/MJCFs.

4. **Frontend marketplace UI.**
   - `web/frontend/src/components/MarketplacePanel.jsx` — grid view, upload form, import/download buttons, verified badges.
   - `web/frontend/src/api.js` — marketplace API helpers.
   - `web/frontend/src/App.jsx` — wired `MarketplacePanel` into the panels grid.

5. **`tests/test_marketplace.py`** — endpoint-level coverage.
   - CRUD create/list/get/update/delete.
   - Verification badge for a `part` (DFM + mesh-quality).
   - Verification badge for a `scene_template` (bundle + MuJoCo runtime).
   - Download counter.
   - Import into a persisted design.
   - **5/5 passing.**

## Caveats / next steps

- Marketplace upload is source-path based (repo-relative asset directory), not a direct file upload; direct file upload remains future UX work.
- Ratings, versioned asset packs, Onshape/part-library sync, and paid cloud marketplace tier remain Phase 28F.

## End-to-end verification

- ✅ Backend `/marketplace/items` create/list/get/update/delete endpoints work against a running server.
- ✅ `POST /marketplace/items/{id}/verify` passes for starter-pack `part`, `scene_template`, and `robot_template`.
- ✅ `POST /marketplace/items/{id}/import/{design_id}` copies asset files into `designs/{id}/imports/{item_id}/` and merges `feature_tree.json`.
- ✅ Verified badges surface correctly in API responses.
