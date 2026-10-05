---
name: hi-ev-launch-roadmap-2026-10-04
description: End-to-end launch roadmap approved by user; phases G1-G6 to reach product launch.
metadata:
  node_type: memory
  type: project
  originSessionId: 66c534dc-e916-4ba3-9380-cfb72567fb6b
  modified: 2026-10-05T02:58:25.037Z
---

# Hi-EV — End-to-End Launch Roadmap (2026-10-04)

## Decisions made today

- **Voice strategy:** Local-first (`faster-whisper` + Kokoro/pyttsx3) with browser fallback; LiveKit optional post-launch.
- **Launch scope:** Polished local Windows app + file-system watcher + full test coverage. Cloud relay, observability, macOS/Linux, tool self-authoring, and OpenJarvis direct integration move to v1.1 / Phase H.
- **OpenJarvis:** Pattern already implemented in Phase F. Real OpenJarvis skill/codebase integration deferred until v1.1.

## Current baseline

- Phases A–F complete, pushed to `origin/main`.
- Phase G1 Tauri launch polish complete.
- Phase G2 file-system watcher complete.
- **Phase G3 voice end-to-end complete**:
  - Backend voice endpoints (`/voice/settings`, `/voice/transcribe`, `/voice/speak`) hardened and tested.
  - Guard check added to `/voice/chat`.
  - `voice_model_dir` is created and passed to `FasterWhisperSTT`, `KokoroTTS`, and `Pyttsx3TTS`.
  - Setup wizard now shows a visible Voice section with enable toggle and STT/TTS dropdowns.
  - `scripts/smoke_voice.py` exercises the voice endpoints headlessly.
  - Tauri shortcut/HUD mic fallback uses `/voice/transcribe` when browser `SpeechRecognition` is unavailable.
  - Security hardening pass: UUID-safe filenames, content-type validation, upload/TTS caps, generic errors, backend allowlist.
  - `tests/test_voice_api.py` added with 12 security + functional tests.
- Tests: 272 passed, 1 skipped, 1 flaky teardown error in `test_proactive_alerts.py` (passes in isolation); ruff clean; web build clean; Tauri `cargo check`/`cargo clippy` clean.

## Phases to launch

1. **G1 — Tauri Launch Polish** — complete.
2. **G2 — File-System Watcher** — complete.
3. **G3 — Voice End-to-End** — complete.
4. **G4 — Skill Eval Golden Datasets** — not started.
5. **G5 — Security / Kill Switch / Audit** — not started.
6. **G6 — Final Integration & Launch Test Sweep** — not started.

## Document

Full plan lives in the repo at [[hi-ev-launch-roadmap-2026-10-04|docs/superpowers/plans/2026-10-04-hi-ev-launch-roadmap.md]].

## Next step

Phase G4 — build skill eval golden datasets and `ev eval skills` CLI.

**Why:** Voice is now end-to-end verified; the next launch blocker is proving skills work correctly against representative real-world inputs.

**How to apply:** Create `evals/skills/` golden suites, extend the eval runner with setup cases, wire `ev eval skills`, add deterministic tests, and run pytest/ruff/web-build/Tauri checks before committing.
