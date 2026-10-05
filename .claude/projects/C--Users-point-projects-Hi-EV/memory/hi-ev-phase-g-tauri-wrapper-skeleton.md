---
name: hi-ev-phase-g-tauri-wrapper-skeleton
description: "Phase G Tauri desktop wrapper skeleton built, compiles, and produces a Windows MSI installer."
metadata:
  node_type: memory
  type: project
  originSessionId: 66c534dc-e916-4ba3-9380-cfb72567fb6b
  modified: 2026-10-04T10:25:49.240Z
---

**Date:** 2026-10-04
**Repo:** `C:/Users/point/projects/Hi-EV`, branch `main`
**Tests:** `python -m pytest` → 253 passed, 1 skipped
**Lint:** `ruff check .` clean
**Frontend:** `cd web && npm run build` clean
**Tauri:** `cd desktop/src-tauri && cargo check` and `cargo clippy -- -D warnings` clean
**Installer:** `desktop/src-tauri/target/release/bundle/msi/Hi-EV_0.1.0_x64_en-US.msi` (4.64 MiB)

## What was done

Built the first Phase G stream: a native Tauri v2 desktop shell around the existing Hi-EV web face and Python daemon.

- New `desktop/` directory with a Tauri v2 Rust project.
- Tauri window loads the existing `web/dist` React/Three.js HUD.
- Rust daemon manager spawns `python -m evd`, polls `/health`, and stops the child process on quit.
- System tray menu: Show EV, Hide EV, Start daemon, Stop daemon, Settings, Quit.
- Global shortcut `Ctrl+Alt+E` (Windows/Linux) / `Cmd+Shift+E` (macOS) focuses the window and notifies the frontend to start a voice turn.
- Frontend bridge `web/src/lib/tauri.ts` detects native mode without breaking browser dev.
- Build orchestration script `scripts/build_tauri.py` builds web then Tauri release installers.
- Placeholder Hi-EV icons generated in `desktop/src-tauri/icons/`.
- README updated with Phase G status.

## Files added/modified

- `desktop/package.json`
- `desktop/src-tauri/Cargo.toml`
- `desktop/src-tauri/tauri.conf.json`
- `desktop/src-tauri/build.rs`
- `desktop/src-tauri/capabilities/default.json`
- `desktop/src-tauri/src/main.rs`
- `desktop/src-tauri/src/lib.rs`
- `desktop/src-tauri/src/daemon.rs`
- `desktop/src-tauri/src/tray.rs`
- `desktop/src-tauri/src/shortcut.rs`
- `desktop/src-tauri/icons/*`
- `scripts/build_tauri.py`
- `web/src/lib/tauri.ts`
- `web/src/App.tsx` (listens for native shortcut event)
- `docs/superpowers/plans/2026-10-04-phase-g-tauri-wrapper.md`
- `README.md` (status update)

## Verification

- `python -m pytest` → 253 passed, 1 skipped
- `ruff check .` → clean
- `cd web && npm run build` → clean
- `cd desktop/src-tauri && cargo check` → clean
- `cd desktop/src-tauri && cargo clippy -- -D warnings` → clean
- `cd desktop && npm run tauri:build` → succeeded, produced MSI

## Decisions

- **System Python + setup wizard** for daemon launch (no bundled Python runtime). This keeps the installer small (~5 MiB Tauri shell) and avoids antivirus false-positives that PyInstaller bundles trigger. The existing setup wizard will be extended to check Python ≥3.12.
- **PyInstaller fallback kept** during Phase G. `scripts/build_installer.py` still works; Tauri becomes the recommended primary install path once fully validated.
- **Cross-platform targets configured:** MSI (Windows), DMG (macOS), AppImage/deb (Linux). Only Windows MSI was verified in this session.

## Open items / next steps

1. Replace placeholder icons with real Hi-EV logo.
2. Extend setup wizard to detect/offer Python installation before first daemon spawn.
3. Add configurable global shortcut via `.env`.
4. macOS/Linux installer CI verification and code signing/notarization notes.
5. File-system watcher for notes vault (next Phase G stream).
6. Global wake word outside browser.
7. Cloud relay / webhook ingress for Telegram/GitHub.
8. Observability: cost/latency/audit traces and `ev why`.

**Why it matters:** EV now has a native desktop entry point that can be installed like a normal app, not just a browser tab + PyInstaller bundle. This is the launch-path shell.

**How to apply:** Use `scripts/build_tauri.py` for production builds; keep PyInstaller as fallback until cross-platform signing and smoke tests are complete. Pick the next Phase G stream based on launch urgency: file-system watcher adds immediate daily value; cloud relay enables phone/webhook ingress.
