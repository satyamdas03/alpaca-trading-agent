---
name: google-stitch-ui-redesign
description: Integrated the Google Stitch Kinetic Precision dark scientific-workstation UI into the live RoboCAD React app.
metadata:
  type: project
  originSessionId: a496167a-b1cf-4304-85e9-8d260f40418c
  modified: 2026-08-24T10:43:31.414Z
---

Prepared `STITCH_BRIEF.md` and then integrated the resulting Google Stitch *Kinetic Precision* dark scientific-workstation UI into the live RoboCAD React app. The earlier Impeccable *Precision Lab Instrument* light theme was superseded by this darker, denser, engineering-control-room aesthetic.

**Design direction:** *Kinetic Precision* — dark-first scientific instrument control software. Near-black foundation (`#121315`), obsidian panels (`#1b1c1e` / `#1f2022`), surgical cyan accent (`#00e5ff`), tactical amber for warnings (`#feb300`), `Inter` + `JetBrains Mono` typography, machined 4px corners, inset fields, LED glow indicators.

**Implementation:**
- Mined the generated `stitch_precision_engineering_interface/` HTML mockups and `DESIGN.md` for tokens, layout, and component patterns.
- Replaced the `rc-*` CSS token system with the new `kp-*` system in `web/frontend/src/styles/index.css`.
- Rebuilt `App.jsx` into a fixed-pane workstation: instrument header, left sidebar, central 3D viewport, right inspector panel, bottom grid.
- Restyled every component: `PromptInput`, `StatusPanel`, `STLViewer`, `ParameterList`, `DownloadLinks`, `HistorySidebar`, `ComponentLibrary`, `ManufacturingReport`, `OnshapeUpload`, `TagEditor`, `RemixPanel`.
- Enhanced `STLViewer` with `@react-three/drei` `Grid` floor and cyan face-selection highlight + outline.
- Updated `index.html` fonts and direction contract.
- Preserved all integration contracts: `api.js` exports, backend endpoints, STLViewer face-click raycaster, component props, `standard_components.json`.

**Validation:**
- `npm run build` passes.
- `pytest tests -q` reports 56/57 passing tests (same known `test_generate_missing_api_key` env interaction).
- Live end-to-end generation verified: base plate and NEMA-17 mount both succeeded, manifold/watertight, with full parameter panels and manufacturing reports.
- Frontend preview running on `http://127.0.0.1:5173`; backend on `http://127.0.0.1:8000`.
- Commit `cbf8ca4` pushed to `origin/master`.

**Why:** The first redesign was coherent but the user wanted a more mature, scientific, dense workstation feel. The Google Stitch brief gave a concrete aesthetic target, and integrating it by hand inside the existing component tree kept all backend/frontend contracts intact.

**How to apply:** Use the `kp-*` CSS classes and custom properties in `index.css` for any new components. Keep the fixed-pane workstation layout. Test any visual changes with `npm run build` and the pytest suite.

## Demo video and README walkthrough

- Added `scripts/record_demo.py` (Playwright) that records a full end-to-end session against the running frontend/backend.
- Generated `assets/robocad_kinetic_precision_demo.webm` (2.20 MB) showing:
  1. App launch and the cyan **Backend online** indicator.
  2. Expanding the component library, choosing **Structural ▸ Base Plate**, and seeding the prompt composer.
  3. Generating the design and waiting for manifold validation.
  4. Clicking a face in the 3D viewport; the raycaster calls `/designs/{id}/guess-parameter`, which returns `thickness` and highlights the matching parameter row.
  5. Editing `thickness` from 5 mm to 6 mm and clicking **Regenerate from parameters**; the viewer refreshes with the thicker plate.
  6. Scrolling to the **Manufacturing Report** panel and reading bounding-box, volume, surface-area, print-time, and feature-size metrics.
- Embedded the video in `README.md` under the UI section with a step-by-step written description and under-the-hood flow while preserving the README's existing structure.
- Pushed commit `8f65118 docs(demo): add Kinetic Precision UI video demo + README walkthrough`.

## README demo visibility fix

- GitHub does not reliably render inline `<video>` tags with relative `src`, so the demo was not visible to users browsing the README.
- Generated `assets/robocad_kinetic_precision_demo.gif` (720×450, 10 fps, 4.2 MB) from the webm for autoplay inline display.
- Generated `assets/robocad_kinetic_precision_demo_poster.jpg` poster frame from the 3D face-click moment.
- Updated `README.md` to embed the GIF via standard Markdown image syntax and keep the webm as a direct-download link.
- Whitelisted the poster JPG in `.gitignore`.
- Pushed commit `2f26670 docs(demo): replace webm-only README embed with GIF for GitHub compatibility`.

## Strategic context after UI work

- The Kinetic Precision UI is the surface for the engineer-grade work that follows (Phases 8–14). All future feature-tree, sketch, assembly, and verification panels will be built inside this workstation layout using the `kp-*` token system.
- Pushed commit `f2723f3 docs(roadmap): add engineer-grade Phases 8-14 to README and PLAN`.

**Related:** [[impeccable-ui-redesign]] [[phase5-phase6-completion]] [[engineer-grade-roadmap]]
