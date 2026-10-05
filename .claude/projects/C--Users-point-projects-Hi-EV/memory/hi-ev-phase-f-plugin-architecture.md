---
name: hi-ev-phase-f-plugin-architecture
description: "Phase F shipped — OpenJarvis-style plugin registry, skills, local voice pipeline, desktop voice wiring, auto-updater, and desktop presence rewrite."
metadata:
  node_type: memory
  type: project
  originSessionId: 9d09069a-5ac5-4f04-9451-61a9c7c80f8b
  modified: 2026-10-03T07:11:41.547Z
---

# Hi-EV Phase F — Plugin Architecture, Skills, Voice, and Auto-Updater

**Shipped:** 2026-09-18 (commit `517a8dd`); auto-updater/desktop presence update 2026-10-03 (commit `02781e2`).
**Tests:** 253 passed, 1 skipped.

## What changed

Ported and adapted the OpenJarvis-style plugin architecture into Hi-EV so the
system can grow as a hot-swappable ecosystem rather than a hardcoded tool list.

### Core registry + ABCs

- `ev.core.registry.RegistryBase[T]` with a global `@register(kind, name)`
  decorator.
- Registries live in `ev.core.registry.registry` for `tool`, `agent`, `memory`,
  `engine`, `skill`, `stt`, and `tts`.
- `ev.core.component` defines `BaseTool`, `BaseAgent`, `BaseMemory`,
  `BaseEngine`, `BaseSkill`, plus `AgentContext`/`AgentResult`.
- `ev.core.discovery.discover_package` / `discover_all` use `pkgutil` to import
  modules and trigger decorators on startup.
- `ev.tools.registry.ToolRegistry` was preserved as a thin layer over the global
  registry, so existing callers and tests keep working.

### Tool conversion

Every existing tool now registers via the decorator:
`status_tool`, `brief_tool`, `memory_tool`, `remember_tool`, `research_tool`,
`work_tool`, `draft_tools`, `calendar_prep_tool`, `alerts_tool`,
`deadline_watcher`, `prep_tool`, `obligations_tool`, `people_tool`.
`ev.server.api` dropped manual imports and now uses `_tool_registry(store)`
with auto-discovery.

### Agents and skills

- `ev.agents.simple` and `ev.agents.orchestrator` are `@register("agent", ...)`
  agents.
- `ev.skills` loads `SKILL.md` files (YAML frontmatter + body prompt template),
  parses manifests, discovers skills at runtime, and exposes each as a tool
  through `SkillTool` / `SkillToolAdapter`.
- Built-in skills: `hello_ev` and `summarize_notes` under `skills/`.
- Server startup calls `load_skills_into_registry()` when `enable_skills` is true.
- New REST endpoint `GET /skills` and CLI command `ev skills list`.

### Local voice pipeline

- `ev.voice.component` defines `BaseSTTBackend` and `BaseTTSBackend`.
- Backends are registered via decorators:
  - STT: `faster_whisper`, `mock`
  - TTS: `kokoro`, `pyttsx3`, `mock`
- `ev.voice.io` records/playback; it now falls back to stdlib `wave` when
  `soundfile` is unavailable so tests and degraded installs still work.
- `ev.voice.manager.VoiceManager` selects the best available backend from
  config (`voice_stt_backend`, `voice_tts_backend`) and provides
  `listen_and_transcribe()` and `say()`.

### Desktop presence wiring

- `scripts/desktop_presence.py` now lazily creates a `VoiceManager` when
  `voice_enabled` is true.
- Pressing the global hotkey (`ctrl+alt+e` by default) still focuses the HUD
  via `POST /focus`, and now also starts a voice turn in a background thread:
  record → transcribe → `POST /voice/chat` → synthesize and speak the reply.
- A `_voice_busy` flag prevents overlapping turns.

### REST additions

- `POST /voice/chat` — synchronous text-in/text-out chat path used by the
  desktop voice client. It runs the same guard/router/tool path as the
  WebSocket chat by driving `ChatSession` with a capturing fake WebSocket.
- `GET /skills` — discovered skill catalog.

### Configuration

`ev.config` gained:
- `skills_dir`, `skills_auto_discover`, `enable_skills`
- `voice_enabled`, `voice_stt_backend`, `voice_tts_backend`, `voice_model_dir`

`pyproject.toml` gained `[voice]` extras (`faster-whisper`, `kokoro`,
`pyttsx3`, `sounddevice`, `soundfile`) and `greenlet>=3.0.0` in core deps.

## Why

The original tool system was a manually-curated list. That does not scale to a
personal AI OS where users, skills, agents, and voice backends should be
addable without editing core code. The OpenJarvis registry/ABC pattern gives us
that extensibility while keeping the existing surface backward-compatible.
Voice support had to be optional and mock-backed so CI and minimal installs
pass without multi-gigabyte model downloads.

## How to apply

- Use `@register("tool", "my_tool")` for any new tool; import the module at
  startup (or rely on `discover_all`) and `ToolRegistry` will find it.
- Add a `skills/<skill>/SKILL.md` with frontmatter to expose a prompt-based
  capability as a tool; no Python required for simple skills.
- Enable voice by setting `EV_VOICE_ENABLED=true` and optional
  `EV_VOICE_STT_BACKEND=faster_whisper` / `EV_VOICE_TTS_BACKEND=kokoro`.
- For the desktop hotkey voice loop, install the `[voice]` extras.

## Safe code sandbox (commit `f304bb5`)

Shipped immediately after Phase F:

- `ev.sandbox` package with `SandboxPolicy`, `CodeRunner`, `isolated` subprocess
  runner, and `SandboxTool`.
- Static AST checks allow a small whitelist of stdlib imports (`math`, `json`,
  `datetime`, etc.) and ban dangerous builtins (`open`, `exec`, `eval`,
  `__import__`, etc.).
- Snippets run in a subprocess with a configurable timeout; `input_data` is
  provided and the final value of `result` is returned.
- `SandboxTool` is tier 2, so the HUD/voice UI requires user confirmation.
- Wired into `ChatSession` so the orchestrator can dispatch generated helper
  snippets.

## Eval runner abstraction (commit `a425978`)

Shipped after the sandbox:

- `ev.eval` package with `EvalCase`, `EvalSuite`, `EvalResult`, checks
  (`contains`, `exact`, `regex`, `json_path`), JSON/YAML loader, runner, and
  reporter.
- `EvalRunner` discovers suite files, executes tool calls through the live
  `ToolRegistry`, and produces pass/fail reports with per-case latency.
- CLI: `ev eval run [suite_dir]` with `--json` output.
- Moved `SandboxTool` into `ev.tools.sandbox_tool` so the auto-discovering
  registry finds it; the core sandbox stays in `ev.sandbox`.

## Encrypted secrets vault (commit `d80837a`)

Shipped after the eval runner:

- `ev.secrets` package with `EncryptedSecretStore` backed by `cryptography.fernet`.
- Vault JSON file stores encrypted key/value pairs. The encryption key is
  retrieved from the OS credential store via `keyring` when available,
  otherwise derived from `EV_MASTER_PASSWORD`.
- `get_settings()` loads the vault into `os.environ` before pydantic reads
  environment variables, so encrypted secrets override `.env` values.
- CLI commands: `ev secrets set/get/list/delete`.
- Added `[secrets]` extras and dev dependencies for `cryptography` and
  `keyring`; added a `.gitignore` exception for `src/ev/secrets/`.

## Auto-updater and desktop presence (commit `02781e2`)

Landed after the secrets vault:

- `src/ev/updater/checker.py` provides `UpdateChecker`, a read-only GitHub
  releases comparator. It reports whether a newer release exists and prints the
  installer URL; it never downloads or runs code without user confirmation.
- New CLI command: `ev update [--repo owner/repo] [--json]`.
- `scripts/desktop_presence.py` was repaired: restored `_focus_hiev`,
  `_run_hotkey`, `_run_tray`, and added `_check_updates(base_url)` so the
  system-tray "Check for updates" item works.
- Added `tests/test_updater.py` covering update-available, up-to-date,
  network-error, and version-normalization paths.
- Stabilized `tests/test_proactive_alerts.py` by cancelling leftover async
  tasks before teardown, eliminating the SQLite "database is locked" error
  that appeared in full-suite runs.

## Next work

Remaining OpenJarvis-inspired items to port/adapt:
- Tauri desktop wrapper and cross-platform installers.
- Richer OS-level presence (global wake word, desktop capture, intent bridging).
- Skill eval harness and example golden datasets.
