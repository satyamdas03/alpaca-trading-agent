---
name: web-voice-hud-mvp
description: Hi-EV web voice/HUD MVP completed and pushed to main.
metadata: 
  node_type: memory
  type: project
  originSessionId: 5b288aae-6b6f-48b4-8c74-35ee15384a5b
  modified: 2026-09-17T02:43:07.721Z
---

Hi-EV has a browser-native voice/HUD face in `web/`.

**What was delivered:**
- Vite + React + TypeScript + Three.js frontend (`web/`).
- Simplified JARVIS reactor/HUD shell: Boot, Ignition, Scene, Core, Particles, Hud, Diagnostics, Suggestions.
- Browser voice loop: `SpeechRecognition` STT, `speechSynthesis` TTS, push-to-talk via Space, click-to-talk, barge-in.
- WebSocket bridge (`web/src/lib/bridge.ts`) to `ws://127.0.0.1:7345/ws` with auto-reconnect.
- Backend `/ws` endpoint and `ChatSession` intent classifier in `src/ev/server/chat.py`.
- LLM-based intent classification routes to Hi-EV `ToolRegistry`; T2/T3 actions refused/confirmed in web UI.
- CORS configured for `http://localhost:5173` and `http://127.0.0.1:5173`.
- Tests: `tests/test_server.py` WebSocket ping, `tests/test_chat_handler.py` intent dispatch/tier refusal.
- End-to-end smoke script: `scripts/smoke_web.py`.
- Progress reporter: `scripts/progress_report.py`.
- Schema utility: `scripts/create_tables.py`.
- Fixed `alembic/versions/aacdc9089a90_add_deadlines.py` to include `status` and `snooze_until` columns.

**Verification:**
- `python -m pytest` → 89 passed, 1 skipped.
- `ruff check src tests scripts` → clean.
- `cd web && npm run build` → succeeds.
- `python -m evd` + `python scripts/smoke_web.py "status of Hi-EV"` → correct tool dispatch and response.
- `cd web && npm run dev` starts on `http://127.0.0.1:5173` and CORS is accepted by the daemon.

**Commits:**
- MVP shipped: `ac630a3` on `main`.
- Phase A prep sprint (SQLite + sqlite-vec default, config blocklist, embeddings, migration discipline): `3244a0f` on `main` (includes all later updates).

**Why it matters:** This closes the interface gap described in the README and gives Hi-EV a local-first, voice-first face without relying on external Claude Code bridges.

**How to apply:**
- To run locally:
  1. `pip install -e ".[dev]"`
  2. `python scripts/setup_sqlite_vec.py`
  3. `python -m evd` in one terminal
  4. `cd web && npm run dev` in another terminal
  5. Open `http://localhost:5173`, click INITIALISE, press Space, speak.
- To check progress: `python scripts/progress_report.py`.
- To recreate tables: `python scripts/setup_sqlite_vec.py` (or `alembic upgrade head` after removing the DB file).
