---
name: plan-g3-to-g6
description: Execution plan for completing Hi-EV launch phases G3 through G6.
metadata:
  node_type: memory
  type: project
  originSessionId: 66c534dc-e916-4ba3-9380-cfb72567fb6b
  modified: 2026-10-05T02:58:42.120Z
---

# Hi-EV G3→G6 Execution Plan

**Goal:** Complete voice end-to-end, skill eval golden datasets, security/kill-switch, and final launch sweep in one continuous push. Verify with tests after every phase.

**Checkpoint 2026-10-05:** Phase G3 complete. Backend voice endpoints hardened and tested, setup wizard Voice section visible, `scripts/smoke_voice.py` added, Tauri/HUD mic fallback wired, and 12 endpoint tests added (272 passed, 1 skipped, 1 unrelated flaky teardown error; ruff clean; web build clean; Tauri cargo check/clippy clean). See [[hi-ev-phase-g3-voice-checkpoint]].

---

## G3 — Voice End-to-End

1. **Backend voice endpoints** ✅
   - Add `GET /voice/settings` → current STT/TTS backend names, voice enabled, available backends.
   - Add `POST /voice/transcribe` → accept multipart WAV upload, return transcript using selected STT backend.
   - Add `POST /voice/speak` → accept text, return audio file path using selected TTS backend.
   - Wire guard check into existing `POST /voice/chat`.

2. **Model cache paths** ✅
   - Ensure `voice_model_dir` (`%LOCALAPPDATA%\Hi-EV\models`) is created and passed to `FasterWhisperSTT`, `KokoroTTS`, and `Pyttsx3TTS`.

3. **Setup wizard voice settings** ✅
   - Extend `SetupRequest` / `SetupResponse` / `.env` template with `voice_enabled`, `voice_stt_backend`, `voice_tts_backend`. ✅
   - Add voice section to `SetupWizard.tsx`. ✅

4. **Smoke script** ✅
   - Create `scripts/smoke_voice.py` that exercises `/voice/settings`, `/voice/speak`, and `/voice/transcribe` against a running daemon.

5. **HUD mic fallback** ✅
   - Browser `startListening` already uses Web SpeechRecognition as primary path. ✅
   - When running in Tauri and browser SpeechRecognition is unavailable, the shortcut/HUD falls back to recording with `MediaRecorder` and posting to `/voice/transcribe`. ✅

6. **Voice endpoint tests** ✅
   - Add tests for `/voice/settings`, `/voice/transcribe`, `/voice/speak`, and `/voice/chat` guard block.

**Acceptance:** `scripts/smoke_voice.py` passes against a running daemon; setup wizard saves voice settings; `/voice/settings` reflects them; all builds green.

---

## G4 — Skill Eval Golden Datasets

1. **Golden skill eval suites**
   - `evals/skills/hello_ev.json` — greet a named user, expect name + time mention.
   - `evals/skills/summarize_notes.json` — seed a note for `robocad`, expect 3-bullet summary.

2. **Seeding support**
   - Extend `EvalRunner` to support optional `setup` cases that seed memory before assertions.

3. **CLI**
   - Add `ev eval skills` command that runs `evals/skills/` and prints report.

4. **Tests**
   - `tests/test_skill_eval.py` runs golden suites deterministically with mock LLM where possible.

**Acceptance:** `ev eval skills` reports all built-in skills passing; test suite stays green.

---

## G5 — Security / Kill Switch / Audit

1. **Audit log model**
   - Add `AuditLog` ORM table (`id`, `timestamp`, `action`, `actor`, `details`, `outcome`).
   - Migration via `Base.metadata.create_all` / Alembic base already frozen; new table created by model sync in tests.

2. **Kill switch enforcement**
   - Add `/security/kill-switch` GET/POST endpoint.
   - Block T1+ tool execution in `ChatSession` when kill switch enabled.
   - Proactive loops already respect `kill_switch`; extend to ingestion loop and any new actions.

3. **Guard integration**
   - Guard check `/voice/chat` before processing.
   - Audit log every guard block and T2 confirmation.

4. **CLI**
   - `ev security kill-switch [--enable/--disable]`.
   - `ev security audit [--limit N]`.

**Acceptance:** Kill switch toggles via API/CLI and blocks tool runs; audit entries appear in DB; tests pass.

---

## G6 — Final Integration & Launch Sweep

1. **Version bump**
   - `pyproject.toml` version `0.1.0` → `0.2.0`.
   - Add `CHANGELOG.md` with G1-G6 summary.

2. **Build verification**
   - `python -m pytest` full suite.
   - `ruff check src tests`.
   - `cd web && npm run build`.
   - `cd desktop/src-tauri && cargo check && cargo clippy -- -D warnings`.
   - `cd desktop && npm run tauri:build` produces MSI.

3. **Documentation**
   - Update `README.md` with final launch status and voice setup instructions.
   - Update `docs/superpowers/plans/2026-10-04-hi-ev-launch-roadmap.md` to mark G3-G6 complete.

4. **Memory & commit**
   - Write `hi-ev-phase-g3-voice.md`, `hi-ev-phase-g4-skill-eval.md`, `hi-ev-phase-g5-security.md`, `hi-ev-phase-g6-launch-sweep.md`.
   - Update `MEMORY.md` and `hi-ev-restart-handoff-2026-10-03.md`.
   - Commit and push after each verified phase.

**Acceptance:** All tests/builds green, MSI produced, memory synced, `origin/main` up to date.

---

## Order of operations

Run G3 → tests → commit → G4 → tests → commit → G5 → tests → commit → G6 → tests/build → final commit/push.
