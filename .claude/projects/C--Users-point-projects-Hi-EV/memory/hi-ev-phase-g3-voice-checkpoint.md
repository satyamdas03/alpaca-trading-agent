---
name: hi-ev-phase-g3-voice-checkpoint
description: Phase G3 voice end-to-end complete — backend endpoints hardened, setup wizard UI, smoke script, Tauri fallback, and endpoint tests verified.
metadata:
  node_type: memory
  type: project
  originSessionId: 66c534dc-e916-4ba3-9380-cfb72567fb6b
  modified: 2026-10-05T02:58:17.291Z
---

# Hi-EV Phase G3 — Voice End-to-End (complete)

## What was delivered

- Voice model cache path fix:
  - `Settings.voice_model_dir` defaults to `%LOCALAPPDATA%\Hi-EV\models` and is created on demand.
  - `FasterWhisperSTT`, `KokoroTTS`, and `Pyttsx3TTS` now accept and use `model_dir` for downloads/caches.
- Setup wizard backend + UI voice settings:
  - `SetupRequest` extended with `voice_enabled`, `voice_stt_backend`, `voice_tts_backend` and allowlist validator.
  - `.env` template writes `EV_VOICE_ENABLED`, `EV_VOICE_STT_BACKEND`, `EV_VOICE_TTS_BACKEND`.
  - `get_setup_defaults()` returns current voice config and available backend lists for the HUD form.
  - Visible Voice section added to `web/src/ui/SetupWizard.tsx` with enable checkbox and STT/TTS dropdowns.
- Backend voice endpoints (`src/ev/server/api.py`):
  - `GET /voice/settings` → voice enabled, STT/TTS backend names, available backends, model dir.
  - `POST /voice/transcribe` → multipart audio upload → transcript via configured STT backend.
  - `POST /voice/speak` → text → synthesized WAV path via configured TTS backend.
  - Guard check added to existing `POST /voice/chat`.
- Security hardening (Application Security Engineer pass):
  - `/voice/transcribe` uses UUID-safe filename, rejects non-`audio/*` content types, enforces 10 MB upload limit.
  - `/voice/transcribe` and `/voice/speak` return generic client-facing errors; full exceptions logged server-side.
  - `voice_stt_backend` / `voice_tts_backend` restricted to known backend allowlist in `SetupRequest`.
  - `/voice/speak` text capped at 5,000 characters via Pydantic.
  - Fixed `_available_voice_backends` to use `get_class()` and shared `VoiceBackendError` from `ev.voice.component`.
  - Added `tests/test_voice_api.py` with 12 security + functional tests.
- Shared `VoiceBackendError` moved to `ev.voice.component` so `setup.py`, `api.py`, `stt.py`, `tts.py`, and `manager.py` all use the same exception base.
- Smoke script (`scripts/smoke_voice.py`):
  - Queries `/voice/settings`, synthesizes via `/voice/speak`, and transcribes a tiny in-memory WAV via `/voice/transcribe`.
- HUD / Tauri mic fallback (`web/src/lib/voice.ts` + `web/src/App.tsx`):
  - Fixed `App.tsx` setup flag (`data.needs_setup`, was `data.setup_needed`).
  - When running inside the Tauri shell and browser `SpeechRecognition` is unavailable, the HUD falls back to recording with `MediaRecorder` and posting to `/voice/transcribe`.
- Dossiers updated:
  - `README.md` current status and Phase G roadmap.
  - `docs/superpowers/plans/2026-10-04-hi-ev-launch-roadmap.md` G3 status and deliverables.
  - Memory files refreshed (this file, launch roadmap, restart handoff, plan-g3-to-g6).

## Verification

- `python -m pytest` → **272 passed, 1 skipped, 1 teardown error** (error is a flaky `sqlite3.OperationalError: database is locked` in `tests/test_proactive_alerts.py::test_alert_loop_pushes_to_websockets` teardown; test passes in isolation and is unrelated to voice changes).
- `ruff check src tests` → clean.
- `cd web && npm run build` → clean.
- `cd desktop/src-tauri && cargo check && cargo clippy -- -D warnings` → clean.
- `/health` smoke test passed.

## Files changed

- `src/ev/voice/component.py`
- `src/ev/voice/stt.py`
- `src/ev/voice/tts.py`
- `src/ev/voice/manager.py`
- `src/ev/server/setup.py`
- `src/ev/server/api.py`
- `web/src/ui/SetupWizard.tsx`
- `web/src/App.tsx`
- `web/src/lib/voice.ts`
- `web/src/index.css`
- `scripts/smoke_voice.py` (new)
- `tests/test_voice_api.py` (new)
- `README.md`
- `docs/superpowers/plans/2026-10-04-hi-ev-launch-roadmap.md`
- Memory files in `C:/Users/point/.claude/projects/C--Users-point-projects-Hi-EV/memory/`

## Decisions / notes

- Kept `/voice/transcribe` and `/voice/speak` synchronous within the request rather than streaming, because the Tauri/desktop shortcut path can poll for the resulting file path.
- Default STT backend remains `faster_whisper` with automatic fallback to `mock`; default TTS remains `pyttsx3` with fallback to `mock`.
- Guard check on `/voice/chat` blocks inputs the same way WebSocket chat does.
- Voicebox deep dive concluded it is a full standalone product, not a library; keep Hi-EV's existing local voice stack for v1.0 and optionally support Voicebox as an external adapter in v1.1.

## Next step

Phase G4 — Skill Eval Golden Datasets.

1. Create `evals/skills/hello_ev.json` and `evals/skills/summarize_notes.json`.
2. Extend `EvalRunner` to support optional `setup` cases that seed memory before assertions.
3. Add `ev eval skills` CLI command.
4. Add `tests/test_skill_eval.py` with deterministic mock-LLM runs.
5. Verify and commit as "hi-ev: Phase G4 — skill eval golden datasets".

**Why:** Voice is now end-to-end verified; the next launch blocker is proving skills work correctly against representative real-world inputs.

**How to apply:** Start in `src/ev/eval/` (or create it), model golden suites after existing eval harnesses, wire `ev eval skills` in the CLI, and run pytest/ruff/web-build/Tauri checks before committing.
