---
name: phase5-phase6-completion
description: Phase 5 (Onshape export + manufacturing reports) and Phase 6 (robotics component templates) are complete and committed.
metadata: 
  node_type: memory
  type: project
  originSessionId: a496167a-b1cf-4304-85e9-8d260f40418c
  modified: 2026-08-24T10:43:25.696Z
---

RoboCAD Phases 5 and 6 are complete as of 2026-08-22.

**Phase 5 deliverables:**
- `ai_cad/onshape.py` — HMAC-SHA256 authenticated Onshape API client (`create_document`, `list_documents`, `upload_step`, `upload_step_to_new_document`).
- `ai_cad/manufacturing.py` — manufacturability report (bounds, volume, surface area, overhang detection, hole diameter via cross-sections, print-time heuristic).
- Backend endpoints: `GET /onshape/documents`, `POST /designs/{id}/onshape`, `GET /designs/{id}/manufacturing-report`.
- Frontend components: `ManufacturingReport.jsx`, `OnshapeUpload.jsx`.
- Tests: `tests/test_onshape.py`, `tests/test_manufacturing.py`.

**Phase 6 deliverables:**
- `web/frontend/src/components/standard_components.json` — 12 curated robotics seed parts.
- `ComponentLibrary.jsx` — collapsible catalog that seeds prompts.
- `TagEditor.jsx` and `RemixPanel.jsx` for tags and child-design generation.
- Existing backend support: `PUT /designs/{id}` tags/prompt, `POST /designs/{id}/remix`, search/filter by tag.

**Test count:** 57 passing pytest tests (run in the hermes-agent venv after installing pip + requirements).

**End-to-end validation (2026-08-22 / 2026-08-23):**
- Frontend production build succeeds (`npm run build`).
- Backend starts and serves `/health`, `/designs`, `/exports`, `/designs/{id}/manufacturing-report`.
- Live generation with local Ollama `qwen3-coder:latest` succeeded for a 40×20×5 mm block with a 6 mm hole; result was manifold/watertight, manufacturing report detected the 6 mm hole.
- **Onshape upload succeeded end-to-end:** generated STEP uploaded to a new Onshape document, translation completed with `requestState: DONE`, and the Part Studio opened in the browser.
- Frontend dev server (`npm run dev`) proxies API calls to the backend correctly.

**Credential storage:**
- Onshape API credentials are stored in the gitignored `.env` file at the repo root.
- The backend loads `.env` automatically via `python-dotenv` (`override=True` so shell variables don't clobber the file).
- `.env.example` documents all required variables without containing secrets.

**How to run for user testing:**
```powershell
cd C:\Users\point\projects\RoboCAD
# Backend (already configured via .env)
.\web-start.ps1
# or manually:
"/c/Users/point/AppData/Local/hermes/hermes-agent/venv/Scripts/python" -m uvicorn web.backend.main:app --host 127.0.0.1 --port 8000

# Frontend (second terminal)
cd web/frontend
npm run dev
```
Then open http://localhost:5173.

**Next major work (as of 2026-08-22):** packaging/distribution after user end-to-end testing.

**Updated next major work (2026-08-23):** Engineer-grade roadmap Phases 8–14, starting with Phase 8 complexity benchmark + feature-tree specification. See [[engineer-grade-roadmap]].

**Related memories:** [[phase3-phase4-completion]] [[engineer-grade-roadmap]]
