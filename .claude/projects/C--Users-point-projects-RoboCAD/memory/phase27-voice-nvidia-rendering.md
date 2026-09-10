---
name: phase27-voice-nvidia-rendering
description: "Phase 27 progress — LiveKit voice for HERMES, NVIDIA NIM integration, and rendering hardening."
metadata: 
  node_type: memory
  type: project
  originSessionId: 7435fc68-ca4e-4484-976a-3e6e62f81195
  modified: 2026-09-10T02:58:32.306Z
---

# Phase 27 — voice, NVIDIA intelligence, and rendering hardening

**Status:** ✅ Phase 27A/B/C complete; Phase 27D (hardware-in-the-loop sim-to-real) remains future work blocked on hardware access.
**Date:** 2026-09-01.
**Test count:** 263 default + 222 heavy/slow = 485 passing (1 xfail), frontend build passes.

## What landed

### Phase 27A — LiveKit + NVIDIA voice for HERMES
- `ai_cad/hermes/livekit_token.py` — user and agent token generation.
- `ai_cad/hermes/nvidia_voice.py` — NVIDIA NIM STT (`nemotron-asr-streaming`) and TTS (`chatterbox-multilingual-tts`) REST clients.
- `ai_cad/hermes/voice_plugins.py` — LiveKit `STT`/`TTS` plugin adapters wrapping the NVIDIA clients.
- `ai_cad/hermes/voice_agent.py` — room-based HERMES voice worker: VAD buffering, NVIDIA STT, HTTP call to `/hermes/session/{id}/message`, NVIDIA TTS reply, data-channel transcript sync.
- `web/backend/main.py` — `POST /hermes/session/{id}/livekit-token` endpoint.
- `web/frontend/src/components/VoiceControls.jsx` — React LiveKit room connection, mic publish, data-channel transcript/status handling.
- `web/frontend/src/components/HermesPanel.jsx` — integrated voice controls into chat UI.
- `tests/test_hermes_voice.py` — 15 unit tests for tokens, endpoint, NVIDIA STT/TTS, and plugin construction.

### Phase 27B — rendering hardening
- `web/frontend/src/components/STLViewer.jsx` rebuilt with:
  - `@react-three/drei` `Bounds` for auto-fit camera on any model size.
  - Hemisphere + directional key/fill lighting with shadow maps.
  - `ContactShadows` for a professional grounded look.
  - Working toolbar: Reset view, Grid toggle, Wireframe overlay, AI Critique.
  - `preserveDrawingBuffer: true` so the canvas can be screenshotted.

### Phase 27C — NVIDIA intelligence layer
- `ai_cad/nvidia_client.py` — generic NVIDIA NIM client with chat, vision, and Cosmos scenario generation.
- `ai_cad/render_critique.py` — vision-language critique of a render screenshot, returning score/issues/suggestions/safe_to_show_user.
- `ai_cad/hermes/llm.py` — HERMES can now route to NVIDIA Nemotron/Meta models via `build_nvidia_caller`.
- Backend endpoints:
  - `POST /designs/{design_id}/render-critique` (screenshot upload).
  - `POST /world/scenario` (Cosmos physics-aware scenario generation).
  - `GET /nvidia/models` (catalog of usable NIM IDs).
- `web/frontend/src/api.js` — added `critiqueRender`, `listNvidiaModels`, `generateScenario`.
- `tests/test_nvidia_client.py` — 15 tests covering client, HERMES caller integration, critique, and the new endpoints.

## Secrets
- NVIDIA API key, LiveKit URL/API key/secret stored in repo-root `.env` (gitignored).
- Keys were exposed in the previous chat; reminder to rotate them after this session.

## Open items / next steps
- [ ] Real end-to-end voice smoke test against LiveKit Cloud room (requires live room + mic).
- [x] Canvas screenshot capture wired into `STLViewer.jsx` AI Critique button.
- [x] NVIDIA model catalog and scenario generation surfaced via backend endpoints; frontend panel wiring remains optional polish.
- [ ] Tune the render-critique prompt and select the best vision model from the catalog after real image evals.
- [ ] Decide whether to expose NVIDIA as a selectable HERMES model in the UI (currently env-driven).
- [ ] Begin Phase 27D once real robot hardware and a safe test environment are available.

## Related
- [[Phase 26 — HERMES plan]]
- [[Phase 23 — humanoid/robot synthesis]]
- [[Phase 24 — world-model simulation builder]]
- [[phase28-simulation-first-product-platform]]
