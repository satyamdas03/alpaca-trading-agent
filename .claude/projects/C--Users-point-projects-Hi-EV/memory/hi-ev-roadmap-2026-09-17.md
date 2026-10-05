---
name: hi-ev-roadmap-2026-09-17
description: Honest state assessment and phased roadmap toward the full Hi-EV vision.
metadata: 
  node_type: memory
  type: project
  originSessionId: 5b288aae-6b6f-48b4-8c74-35ee15384a5b
  modified: 2026-10-03T07:06:36.554Z
---

**Context:** The Web/Voice/HUD MVP is complete ([[web-voice-hud-mvp]]). The Phase A prep sprint is complete ([[hi-ev-phase-a-prep-sprint]]). This memory captures the honest gap between the current state and the full Hi-EV vision, plus the roadmap to close it.

**Current maturity (updated 2026-10-03):** ~7.5/10 toward the full operating-system vision. Phases A–E and the Phase F block are shipped. EV is now ambient (scheduler + semantic memory), measurable (router + eval harness), proactive (WebSocket alerts + morning brief + Telegram skeleton), persistent (chat threads), safely autonomous (T2 confirmation + T3 hard blocks), pluggable (OpenJarvis-style registry + skills), and has the foundations for self-expansion (safe code sandbox + eval runner). Local voice backends, an encrypted secrets vault, and a read-only auto-updater are wired. The daily-driver loop is usable on Windows via `scripts/desktop_presence.py`; it is not yet a cross-platform packaged app.

**Latest sync commits (2026-10-03):** `02781e2` (auto-updater + desktop presence rewrite + proactive test isolation), `d80837a` (encrypted secrets vault), `a425978` (eval runner + sandbox tool move), `f304bb5` (safe code sandbox), `517a8dd` (Phase F plugin architecture + skills + voice).

**What works today:**
- FastAPI daemon with CORS and WebSocket (`/ws`), plus `POST /focus` for desktop hotkey focus and `POST /voice/chat` for synchronous voice turns.
- SQLAlchemy structured memory (projects, ingest, deadlines, people, obligations, decisions, events) + sqlite-vec document memory with hybrid search.
- GitHub, notes, Gmail, Calendar ingestion with personal-only boundary and source-trust tiers.
- Tools: status, brief, research, deadlines, alerts, people, obligations, prep, calendar prep, drafting, Claude Code spawn; all tier-enforced (T0 read-only, T1 reversible, T2 confirmed, T3 blocked).
- Reasoning router with fast/agent/deliberate paths and eval harness (`ev.eval`).
- Streaming fast-chat path over WebSocket with stop control.
- Persistent chat threads with REST CRUD and resume across reconnects.
- Proactive WebSocket alerts, morning brief scheduler, optional Telegram relay skeleton.
- T2 confirmation flow in WebSocket/voice/CLI; T3 hard blocks in web/voice.
- Desktop presence entry point: global hotkey (`Ctrl+Alt+E`), system-tray widget, browser wake word ("hey ev"), and a voice loop that records/transcribes/chats/speaks.
- Plugin architecture: `ev.core.registry`, ABCs in `ev.core.component`, auto-discovery via `ev.core.discovery`, and a backward-compatible `ToolRegistry`.
- Skills runtime: `SKILL.md` discovery, `SkillManager`, `SkillTool`, built-in `hello_ev` / `summarize_notes`, and `GET /skills` / `ev skills list`.
- Safe code sandbox: AST policy, subprocess isolation, tier-2 `SandboxTool`.
- Encrypted secrets vault: Fernet-backed store, OS keyring or `EV_MASTER_PASSWORD` fallback, loaded before pydantic settings.
- Read-only auto-updater: compares `pyproject.toml` version to latest GitHub release; CLI `ev update` and tray "Check for updates".
- Browser voice/HUD frontend with Three.js reactor.

**Major gaps remaining:**
1. No cross-platform packaged desktop app — still a Python script on Windows; no Tauri wrapper or macOS/Linux installers.
2. No file-system watcher for notes vault — scheduler polls but does not watch.
3. No true cross-document synthesis / dedicated reranker.
4. No preference learning from ignored/acted-on alerts and answers.
5. No model-authored HTML blades / holographic information panels.
6. No closed-loop tool self-authoring — the sandbox exists, but EV cannot yet generate, test, and register a new tool end-to-end.
7. No structured observability / cost-latency tracing.
8. No cloud relay or webhook ingress.
9. No skill eval harness or example golden datasets.
10. Local STT/TTS is wired but defaults to mock unless heavy `[voice]` extras are installed.

**Phased roadmap:**
- **Phase A — Ambient Ingestion + Semantic Memory ✅ COMPLETE (commit `40aaa2b`):** scheduler, embeddings, hybrid search, `ev remember`.
- **Phase B — Reasoning Router + Eval Harness ✅ COMPLETE (commit `beb47fe`):** fast/agent/deliberate router, streaming, golden questions, guard model.
- **Phase C — Proactive Alerts + Persistent Context ✅ COMPLETE (commit `dff10c3`):** WebSocket push alerts, chat threads, morning brief scheduler, optional Telegram relay.
- **Phase D — Safe Autonomy + Desktop Presence ✅ COMPLETE (commit `92ff90d`, live smoke test passed):** T2 confirmation, T3 hard blocks, tray widget, global hotkey, local wake word.
- **Phase E — Launch MVP ✅ COMPLETE (commit `517a8dd`):** local Windows installer, first-run setup wizard, packaged desktop entry point, graceful missing-LLM-key fallback.
- **Phase F — Plugin Architecture + Skills + Voice + Eval + Secrets + Auto-Updater ✅ COMPLETE (commit `02781e2`):** OpenJarvis-style registry, skills, local voice pipeline, safe sandbox, eval harness, encrypted secrets vault, read-only auto-updater.
- **Phase G — Cross-Platform Shell + OS Presence + Cloud Relay (next):** Tauri wrapper, cross-platform installers, file-system watcher, desktop capture, global wake word, intent bridging, cloud relay/webhook ingress, observability, skill golden datasets.

**Recommended next sprint — Phase G kickoff (1–2 weeks):**
- Tauri desktop wrapper + cross-platform installer pipeline.
- File-system watcher for the notes vault and real-time ingestion.
- Richer OS presence: global wake word, desktop capture/screen context, intent bridging from tray/hotkey.
- Skill eval harness + small golden datasets for built-in skills.

**Prep sprint (completed 2026-09-17):**
Before Phase A, the following blockers were cleared:
- **SQLite + sqlite-vec** is now the default local database; no Postgres install is required to start Phase A.
- Postgres + pgvector remains an optional upgrade via `scripts/setup_postgres.py` and `EV_DATABASE_URL`.
- Test DB isolation via lazy engine/session factories (`src/ev/db/base.py`) and `tests/conftest.py` overrides.
- Config-driven work blocklist (`EV_BLOCKED_HANDLES`, `EV_BLOCKED_DOMAINS`) in `src/ev/config.py`.
- Local embedding model wiring (`src/ev/embeddings.py`, `sentence-transformers>=3.0.0`, `scripts/check_embeddings.py`).
- `DocumentChunk` model + `src/ev/db/vector.py` sqlite-vec helpers + `scripts/setup_sqlite_vec.py` + `scripts/smoke_vector_search.py`.
- Alembic migration discipline documented in `docs/development/migrations.md`.
- README setup instructions refreshed for the SQLite default with Postgres optional.
- 89 tests passing, 1 skipped; ruff clean.

**Full document:** `docs/superpowers/assessments/2026-09-17-hi-ev-honest-state-and-roadmap.md`.

**Why it matters:** Without ambient ingestion and semantic memory, EV stays a voice-controlled query engine. These two capabilities turn it into the persistent operating system for attention described in the README.
