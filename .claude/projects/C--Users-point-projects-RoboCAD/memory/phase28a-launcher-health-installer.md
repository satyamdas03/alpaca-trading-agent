---
name: phase28a-launcher-health-installer
description: "Phase 28A — one-command launcher, health CLI, and PyInstaller installer skeleton."
metadata: 
  node_type: memory
  type: project
  originSessionId: 7435fc68-ca4e-4484-976a-3e6e62f81195
  modified: 2026-09-10T02:59:06.401Z
---

# Phase 28A — Launcher + health CLI + installer skeleton

**Date:** 2026-09-08
**Status:** complete
**Commit:** `b5b04de` — `robocad: Phase 28A — launcher, health CLI, and installer skeleton`

## What shipped

1. **`robocad/launcher.py`** — cross-platform one-command launcher.
   - `check_python_version()`, `environment_report()`, `install_python_deps()`.
   - `start_backend()` and `start_frontend()` spawn `python -m web.backend.main` and `npm run dev` via subprocess.
   - `main()` entry point for `python -m robocad start`.

2. **`robocad/health.py`** — environment health reporter.
   - `health_report()` checks Python version, key dependency versions, API keys from `.env`, and external solver availability.
   - Outputs ASCII-only `[OK]` / `[FAIL]` markers to avoid Windows console encoding issues.

3. **`robocad/__main__.py`** — `python -m robocad [start|health]` CLI dispatch.

4. **User-facing entry points:**
   - `start.py` — Python wrapper (Windows/Linux/macOS).
   - `start.bat` — Windows batch entry point.
   - `start.sh` — Linux/macOS shell entry point.

5. **`scripts/build_installer.py`** — PyInstaller desktop installer skeleton.
   - Builds a one-folder executable bundle from `start.py`.
   - `main(argv)` accepts an argv parameter so tests can call it with `[]` without argparse consuming pytest args.

6. **Tests:**
   - `tests/test_launcher.py` — 8 tests covering Python-version check, environment report, backend/frontend start helpers (mocked), and CLI dispatch.
   - `tests/test_build_installer.py` — 5 tests covering PyInstaller spec generation and CLI invocation.
   - **13/13 passing.**

## Residual caveats / next steps

- PyInstaller build requires `pyinstaller` installed and produces a local bundle; code-signing and NSIS/Tauri installers remain Phase 28F.
- `start.py` assumes the repo-root `.venv` is already present or falls back to the ambient Python; automatic venv creation is not implemented.
- Health CLI now reports solver install hints (added in Phase 28F).
