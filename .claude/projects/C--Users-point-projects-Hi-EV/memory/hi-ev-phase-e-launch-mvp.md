---
name: hi-ev-phase-e-launch-mvp
description: "Phase E Launch MVP shipped — local Windows installer, first-run setup wizard, unified desktop entry point, and graceful missing-LLM-key fallback."
metadata:
  node_type: memory
  type: project
  originSessionId: 9d09069a-5ac5-4f04-9451-61a9c7c80f8b
  modified: 2026-10-03T07:11:33.137Z
---

# Hi-EV Phase E Launch MVP — 2026-10-03

Shipped a launch-ready, local-only Windows MVP for Hi-EV so a non-technical client can download, install, and run it without editing `.env` files or opening a terminal.

## What changed

- **Unified desktop entry point:** `scripts/desktop_presence.py` starts the FastAPI daemon, global hotkey listener, system-tray widget, and opens the HUD in one command.
- **First-run setup wizard:**
  - Backend: `src/ev/server/setup.py` with `check_setup_status`, `apply_setup`, `get_setup_defaults`.
  - API: `GET /setup` and `POST /setup` in `src/ev/server/api.py`.
  - Frontend: `web/src/ui/SetupWizard.tsx` integrated into `App.tsx`; styles in `web/src/index.css`.
  - Writes `%LOCALAPPDATA%\Hi-EV\.env` and supports notes path, LLM provider/keys, GitHub token, blocked handles/domains, quiet hours, repo paths.
- **Static HUD serving:** the daemon serves `web/dist` at `/` when the build output exists, so the installer bundle has a single URL to open.
- **Graceful LLM fallback:**
  - `Settings.llm_ready()` checks the configured provider's API key.
  - `/health` returns `llm_ready`.
  - `ChatSession` returns a friendly setup-wizard message when no key is configured instead of crashing.
  - `Diagnostics` displays LLM key status.
- **Installer build script:** `scripts/build_installer.py` uses PyInstaller to produce `dist/Hi-EV/` (one-folder) and `dist/Hi-EV-Portable/` (one-file). Added `pyinstaller>=6.0` to the `desktop` extra in `pyproject.toml`.
- **PowerShell installer (recommended):** `scripts/install_windows.ps1` checks Python 3.12+, creates `%LOCALAPPDATA%\Hi-EV\venv`, installs Hi-EV + desktop extras, builds the web HUD, creates Start Menu/Desktop shortcuts, and launches the desktop entry point. This avoids the antivirus false-positives that block unsigned PyInstaller executables.
- **Configuration:** `src/ev/config.py` uses `%LOCALAPPDATA%\Hi-EV` as the app data dir, searches that `.env` first, and adds `desktop_auto_open_hud` / `setup_wizard_enabled` flags.
- **Dependencies:** added `greenlet>=3.0.0` to `pyproject.toml` because SQLAlchemy asyncio requires it.
- **Tests:** added `tests/test_setup.py` (5 tests) and `tests/test_config.py::test_llm_ready_per_provider`. Full suite: **203 passed, 1 skipped**.

## Verification

- `python -m pytest` — 203 passed, 1 skipped (one flaky teardown lock in proactive alerts, passes on rerun).
- `cd web && npm run build` — clean TypeScript + Vite build.
- README updated with Windows installer path, developer setup, and troubleshooting table.
- `python scripts/build_installer.py --smoke` — PyInstaller one-folder build completes and produces `dist/Hi-EV/Hi-EV.exe`.
- Source runtime smoke test passes: `python scripts/desktop_presence.py` starts daemon, `/health`, and WebSocket respond.
- PowerShell installer smoke test passes: `scripts/install_windows.ps1 -NoShortcuts -SkipFrontendBuild` creates venv, installs deps, and the resulting venv runs `desktop_presence.py` successfully.

## Distribution

- **Recommended client path:** `scripts/install_windows.ps1`. It creates a per-user venv and shortcuts; it does not trip antivirus because it runs plain Python from source.
- **PyInstaller bundle:** builds successfully, but unsigned executables are frequently flagged by Windows Defender / McAfee (`WinError 225`). `scripts/build_installer.py` now catches this error and prints a remediation message instead of crashing.
- To ship the PyInstaller build, **sign the executable with a code-signing certificate** or guide users to add an antivirus exclusion.

## Out of scope for v1.0 (some shipped in Phase F)

- ✅ Local STT/TTS scaffold — shipped in Phase F via `ev.voice` with mock/faster-whisper/kokoro/pyttsx3 backends and `POST /voice/chat`; defaults to mock without heavy extras.
- ✅ OS keyring / encrypted secrets — shipped in Phase F via `ev.secrets` (Fernet-backed vault, keyring or `EV_MASTER_PASSWORD` fallback).
- ✅ Auto-updater — shipped in Phase F via `ev.updater` (read-only GitHub releases comparator) and `ev update` CLI / tray item.
- ❌ Tool self-authoring closed loop — not yet built (sandbox exists, but EV cannot generate/test/register a tool end-to-end).
- ❌ Cloud relay / webhook ingress beyond existing Telegram skeleton.
- ❌ macOS / Linux installers.
- ❌ `ev why` audit query tool.

## Next phase

**Phase F — Plugin Architecture + Skills + Voice + Eval + Secrets + Auto-Updater** is complete (commit `02781e2`, 253 tests passing). See [[hi-ev-phase-f-plugin-architecture]].

**Phase G (next):** Tauri desktop wrapper, cross-platform installers, file-system watcher, richer OS presence (global wake word, desktop capture, intent bridging), skill eval harness / golden datasets, cloud relay / webhook ingress, observability / cost-latency tracing.

**Why:** The launch MVP intentionally traded the full Phase E vision for a narrow, shippable, local-first installer. Phase F then ported OpenJarvis-style extensibility and shipped the deferred v1.1 scaffolding. Phase G is the polish sprint to make Hi-EV a cross-platform daily-driver product.

[[hi-ev-phase-d-safe-autonomy]]
[[hi-ev-phase-f-plugin-architecture]]
[[hi-ev-roadmap-2026-09-17]]
