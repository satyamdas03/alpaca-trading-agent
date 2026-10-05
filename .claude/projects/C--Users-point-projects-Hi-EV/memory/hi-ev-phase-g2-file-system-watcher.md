---
name: hi-ev-phase-g2-file-system-watcher
description: Phase G2 complete — incremental file-system watcher for the Hi-EV memory vault.
metadata:
  node_type: memory
  type: project
  originSessionId: 66c534dc-e916-4ba3-9380-cfb72567fb6b
  modified: 2026-10-04T12:43:47.939Z
---

# Hi-EV Phase G2 — File-System Watcher

## What was delivered

- New `ev.ingestion.watcher` package using `watchdog`:
  - `VaultWatcher` watches `settings.notes_path` and any configured project paths (`robocad_path`, `learningrobotics_path`, `hiev_path`) recursively.
  - `VaultEventHandler` filters for `.md` files and ignores directories/noisy events.
  - Events are enqueued thread-safely into the async event loop via `loop.call_soon_threadsafe` because `watchdog` fires from its own observer thread.
- Debounce + coalesce: a 2-second quiet period per path before running ingestion, so rapid create/modify bursts collapse into a single incremental pass.
- Incremental ingestion:
  - `_ingest_paths` reads changed `.md` files, upserts `Ingest` rows, and re-chunks/upserts `DocumentChunk` + vector entries.
  - `_delete_paths` removes both vector chunks and the `Ingest` row when a note is deleted.
  - Content-hash idempotency is preserved by reusing the existing `MemoryStore`/`chunk_ingest_records` pipeline.
- FastAPI lifespan hook: `VaultWatcher` starts when the daemon starts and stops cleanly on shutdown (`src/ev/server/api.py`).
- Tests in `tests/test_ingestion_watcher.py` cover:
  - new note ingestion,
  - modified note re-ingestion,
  - deleted note removal,
  - non-`.md` files ignored,
  - no valid paths is a no-op.
- Test fixture isolation: each test gets its own temp DB via `EV_DATABASE_URL` and clears the cached engine/session maker; project paths are disabled to avoid watching the real repo directories during tests.

## Verification

- `python -m pytest` → 260 passed, 1 skipped.
- `ruff check src tests` → clean.
- `ruff format` applied to changed files.

## Files changed

- `src/ev/ingestion/watcher.py`
- `src/ev/server/api.py`
- `tests/test_ingestion_watcher.py`
- `pyproject.toml` (added `watchdog>=4.0.0`)

## Decisions / notes

- Chose `watchdog` Observer over polling because it is the standard async-friendly file-system watcher for Python and integrates cleanly with an asyncio queue.
- Kept project-path watching opt-in via explicit settings so tests stay deterministic and users do not accidentally watch unrelated directories.
- `STARTUP_DELAY_SECONDS = 0.5` gives the Windows observer thread time to register before callers write files; the real reliability fix was isolating tests from the live project directories, which were flooding the queue and causing flaky ingestion timing.

## Next step

Start Phase G3 — Voice End-to-End. Wire local STT/TTS backends through the Tauri global shortcut and HUD mic fallback, and add `scripts/smoke_voice.py`.

**Why:** Voice is the front-door experience for the product; with the watcher in place, the launch path now focuses on making the hotkey / mic flow reliable offline.

**How to apply:** Audit `ev.voice` backends, expose voice settings in the setup wizard, connect the Tauri shortcut to a full record→transcribe→chat→synthesize→play turn, and add a browser HUD mic fallback.
