---
name: hi-ev-phase-d-safe-autonomy
description: "Phase D core complete — safe autonomy + desktop presence: T2 confirmation, T3 hard blocks, tray widget, global hotkey, local wake word."
metadata:
  node_type: memory
  type: project
  modified: 2026-10-03T07:11:23.008Z
  originSessionId: ccb82d8d-e0b2-40ca-b0f5-6e78b5783f48
---

**Status:** Phase D — Safe Autonomy + Desktop Presence — **shipped and live-verified**. [[hi-ev-phase-c-proactive-context]] is complete. Next: Phase E per [[hi-ev-roadmap-2026-09-17]].

**Latest relevant commits:**
- `92ff90d` — hi-ev: Phase D — T2/T3 confirmation, desktop presence skeleton, and frontend source tracking
- `3cc7f4c` — docs: sync README, roadmap, architecture, and plans with Phases A–D completion
- `d546580` — test: dispose engine before dropping proactive alert fixtures (teardown hardening)

**Critical repo hygiene fix:**
- `.gitignore` had a bare `lib/` pattern that ignored `web/src/lib/`, meaning the voice/bridge/audio/TTS/VAD source files from Phases B and C were never tracked. Changed to `/lib/` (root-only) so the frontend core source is now in git.

**Goal from [[hi-ev-roadmap-2026-09-17]]:** Close the gap between reactive voice/chat and an ambient, autonomous assistant that still refuses dangerous actions. Phase D focuses on safe action confirmation and desktop presence, not open-ended automation.

**Delivered in this session:**

- **T2 confirmation flow:**
  - `src/ev/server/chat.py` `ChatSession` now pauses on T2 tools, sends `type: confirm` over WebSocket, and waits for `confirm_response`.
  - Confirmed actions run via `_run_confirmed_tool`; denied actions return a cancellation message.
  - A new user transcript cancels any pending confirmation.
  - Tool tiers promoted: `work_on`, `draft_commit`, `draft_pr`, `draft_reply` → T2; `remember` → T1; all read-only tools remain T0.

- **T3 hard blocks:**
  - T3 tools are refused immediately in the web/voice interface with a permanent-block message.
  - The guard already blocks tier-downgrade requests and work-boundary violations; untrusted content caps effective tier automatically.

- **Frontend confirmation UX:**
  - `web/src/ui/ConfirmModal.tsx` blocking modal with Confirm/Deny buttons and voice hint.
  - `web/src/store.ts` tracks `pendingConfirmation` and `focusRequested`.
  - `web/src/lib/voice.ts` supports voice confirm/deny while a confirmation is pending.
  - `web/src/lib/bridge.ts` adds `confirm`, `confirm_response`, and `focus` message types.

- **CLI confirmation:**
  - `src/ev/cli/main.py` T2 commands (`work on`, `draft commit`, `draft pr`, `draft reply`) require `--yes` / `-y` or an interactive `click.confirm`.

- **Desktop presence:**
  - `POST /focus` endpoint in `src/ev/server/api.py` pushes `type: focus` to all active WebSockets.
  - `scripts/global_hotkey.py` uses `pynput` to listen for `Ctrl+Alt+E` and hit `/focus`.
  - `scripts/tray_widget.py` uses `pystray` + `Pillow` to show a system-tray EV icon with Open HUD / Focus / Exit menu.
  - `web/src/lib/voice.ts` adds a continuous wake-word listener (`startWakeListening`) that triggers normal listening on "hey ev".
  - `web/src/App.tsx` subscribes to phase changes and starts/stops wake listening when dormant.

- **Configuration:**
  - `src/ev/config.py` adds `base_url`, `global_hotkey_enabled`, `global_hotkey_combo`, `tray_widget_enabled`, `wake_word_enabled`, `wake_word_phrase`.
  - `pyproject.toml` adds optional `[desktop]` dependencies: `pynput`, `pystray`, `Pillow`.

- **Tests:**
  - `tests/test_chat_handler.py` covers T1 auto-run, T2 confirmation request, confirm/deny response, and T3 hard block.
  - `tests/test_cli.py` updated for `--yes` requirement and interactive confirmation.
  - `tests/test_server.py` adds `/focus` endpoint test.
  - `tests/test_draft_tools.py` updated for tier 2.
  - Fixed pre-existing ruff issues in `tests/test_chat_threads.py` and `tests/test_proactive_alerts.py`.

**Verification at completion:**
- `python -m pytest tests/` → **197 passed, 1 skipped**.
- `ruff check .` → clean.
- `cd web && npm run build` → clean.
- Commit `92ff90d` pushed to `origin/main`.

**Verification after live smoke test:**
- Ran `python $CLAUDE_JOB_DIR/tmp/e2e_phase_d.py` against the daemon on `127.0.0.1:7345` — **all Phase D live smoke tests passed**:
  - Health endpoint OK.
  - T2 `work_on` request paused and emitted `type: confirm` with tool, tier, risk, prompt, and args.
  - Confirming the T2 request advanced through `phase: acting`, returned a delta, and emitted `done`.
  - Denying the T2 request returned a cancellation delta and `done`.
  - Destructive request was handled gracefully without crash.
  - `POST /focus` notified the connected WebSocket client with `type: focus`.

**Remaining Phase D polish (later shipped):**
- ✅ Package the tray widget / global hotkey as a single desktop entry point — shipped in Phase E via `scripts/desktop_presence.py`, later rewritten in Phase F with voice-loop integration.
- ✅ Local STT/TTS pipeline scaffold — shipped in Phase F via `ev.voice` with mock/faster-whisper/kokoro/pyttsx3 backends and `POST /voice/chat`; defaults to mock without heavy extras.
- As of 2026-10-03, Phases E and F are also complete; latest shipped commit is `02781e2` with 253 tests passing. See [[hi-ev-phase-e-launch-mvp]] and [[hi-ev-phase-f-plugin-architecture]].

**Scope (4–5 week roadmap):**
1. **T2 confirmation flow** — reversible/consequential actions (draft PR, send email, calendar write-back, spawn work session) require explicit user confirmation before running.
2. **T3 hard blocks** — destructive or high-risk actions (delete data, send to external accounts, raw shell, modify secrets, bypass personal-only boundary) are permanently blocked in every interface.
3. **Tray widget** — small desktop system-tray/status icon showing EV state and recent alerts.
4. **Global hotkey** — keyboard shortcut (e.g., Ctrl+Alt+E) to open/bring the HUD to foreground.
5. **Local wake word** — browser-native or lightweight local wake-word detection ("Hey EV") so the HUD can be invoked hands-free.

**Implementation plan for this session:**

1. **Backend confirmation protocol:**
   - Add `PendingConfirmation` state to `ChatSession`.
   - When a T2 tool is requested, pause execution, send a `type: confirm` WebSocket message with `tool`, `args`, `tier`, `risk`, and `prompt`.
   - Wait for a matching `type: confirm_response` message with `confirmed: true/false`.
   - On confirm, run the tool; on deny, send a polite refusal and clear pending state.
   - T3 tools are rejected immediately with `type: error` and a hard-block reason.

2. **Tool tier audit:**
   - Review every registered tool and assign the correct tier:
     - T0: `status`, `brief`, `memory`, `deadline_watcher`, `alerts`, `people`, `obligations` (read-only).
     - T1: `remember`, `prep`, `calendar_prep` (reversible local writes).
     - T2: `work_on` (spawns Claude Code), `draft_pr`, `draft_commit`, `draft_reply` (consequential external-facing drafts), and future calendar write-back / email send.
     - T3: destructive ops, shell execution, secret modification, work-account actions — none currently exposed, but the registry must enforce a T3 ceiling.

3. **Guard hardening:**
   - `Guard.check()` already blocks tier-downgrade requests and work-boundary violations.
   - Extend `check_tool_request()` so that T3 is blocked when `max_tool_tier < 3`.
   - Ensure untrusted content caps at T1/T2 automatically.

4. **Frontend confirmation UX:**
   - `web/src/ui/ConfirmModal.tsx` — blocking modal that shows tool name, summary of action, and Confirm/Deny buttons.
   - `web/src/lib/voice.ts` dispatches `confirm` events to the store.
   - `web/src/store.ts` tracks `pendingConfirmation` and helpers to approve/deny.
   - HUD renders the modal when a confirmation is pending.
   - Voice path: if the user says "confirm" or "yes" while a confirmation is pending, send `confirm_response` with `confirmed: true`; "cancel"/"no" denies.

5. **CLI confirmation:**
   - Add a `--yes` / `-y` flag to T2 CLI commands; without it, prompt interactively (`click.confirm`).
   - T3 CLI commands are not added — hard-blocked by design.

6. **Desktop presence basics:**
   - **Global hotkey:** small optional service using `pynput` (cross-platform) or `keyboard` on Windows to listen for `Ctrl+Alt+E` and send a `POST /focus` to the frontend/raise the HUD window. This is intentionally a separate lightweight process, not in the main daemon.
   - **Wake word:** use the browser `Web Speech API` continuous recognition with a custom grammar/filter for "Hey EV"; when matched, transition from dormant to listening. This avoids shipping a separate STT model in Phase D.
   - **Tray widget:** create a minimal Electron/Tauri/Win32-free system-tray skeleton. For this session, ship a `scripts/tray_widget.py` proof-of-concept using `pystray` plus a browser-launcher so the user can opt into it. A full native tray app is Phase E polish.

7. **Tests:**
   - `tests/test_confirmation.py` — WebSocket `confirm`/`confirm_response` round trip, deny path, T3 hard block, timeout/expiration, guard tier downgrade.
   - `tests/test_guard.py` — T3 refusal, untrusted content tier cap, boundary blocks.
   - `tests/cli/test_cli_confirmation.py` — `--yes` required for T2 CLI commands.
   - Update `test_chat_handler.py` if T2 defaults change behavior.

**Acceptance criteria:**
- A T2 request from the web UI triggers a confirmation modal; the action only runs after the user confirms. ✅ target
- A T3 request is refused in every interface without running. ✅ target
- CLI T2 commands require `--yes` or interactive confirmation. ✅ target
- Global hotkey can bring the HUD to the foreground. ✅ target
- Wake-word detection can trigger the HUD from dormant state. ✅ target
- Tray widget skeleton launches and shows EV status/alerts. ✅ target
- `python -m pytest` passes; `cd web && npm run build` passes. ✅ target

**Next phase after D:** Phase E — Local Voice + Advanced HUD + Self-Expansion (faster-whisper + Piper/Kokoro, HTML blades, tool self-authoring, preference learning).
