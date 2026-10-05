---
name: hi-ev_restart_2026-09-15
description: "EV / Hi-EV full session recovery dossier — read this first when restarting a fresh session."
metadata:
  node_type: memory
  type: reference
  originSessionId: c391edcd-a13c-4b1e-a13a-14088c80d1a3
  created: 2026-09-15
  modified: 2026-09-19T01:21:15.566Z
---

# EV / Hi-EV — Full Session Recovery Dossier

**Read this first** when a new Claude session starts with no context of this project.

> **Mirror location:** this file is kept in sync with `C:/Users/point/projects/Hi-EV/docs/superpowers/hi-ev_restart_2026-09-15.md`. Update both copies when editing.

---

## 1. What EV / Hi-EV is

**EV** is a personal, local-first AI operating system that runs on Satyam's RTX 5060 laptop. It is not a chatbot. It is meant to be a persistent cognitive layer above all personal projects.

When the laptop opens, EV is supposed to:
- Have already read overnight changes in personal repos.
- Know deadlines and upcoming meetings.
- Speak first (eventually via voice).
- Execute reversible work automatically (draft PRs, run tests, summarize emails, schedule focus time).
- Keep consequential actions behind explicit confirmation.

EV operates under a **strict personal-only boundary** — no work email, work Slack, work repos, or employer IP/patent data. This is enforced in code via `assert_personal_only()` and a `Blocklist` configured in `.env` (`EV_BLOCKED_HANDLES`, `EV_BLOCKED_DOMAINS`).

---

## 2. Repository location and key files

**Repo path:** `C:/Users/point/projects/Hi-EV`
**Remote:** `https://github.com/satyamdas03/Hi-EV`
**Branch:** `main`

Key directories and files:
- `src/ev/` — all source code.
- `src/ev/cli/main.py` — CLI entry point (`ev` commands).
- `src/ev/daemon/daemon.py` — FastAPI daemon runner.
- `src/ev/server/api.py` — FastAPI routes.
- `src/ev/server/chat.py` — WebSocket `/ws` endpoint and LLM intent classifier.
- `src/ev/server/scheduler.py` — background ingestion scheduler, wired into FastAPI lifespan.
- `src/ev/config.py` — Pydantic settings; includes blocklist, embedding model, Google OAuth, alert-loop flags, repo paths, `ingest_interval_sec`, `github_repos`.
- `src/ev/db/base.py` — lazy async engine/session factories; SQLite + sqlite-vec default, Postgres optional.
- `src/ev/db/models.py` — SQLAlchemy models: `DocumentChunk`, `Ingest`, `Project`, `Event`, `Deadline`, `Person`, `Obligation`, `Decision`.
- `src/ev/db/vector.py` — sqlite-vec virtual table helpers for semantic memory.
- `src/ev/embeddings.py` — local `sentence-transformers` embedding model wrapper.
- `src/ev/memory/chunks.py` — deterministic document chunker.
- `src/ev/memory/store.py` — `MemoryStore` with idempotent upsert for structured tables + document chunk upsert/search/delete.
- `src/ev/memory/status.py` — `build_status_summary()` for status/brief.
- `src/ev/llm/client.py` — async OpenAI-compatible LLM client (NVIDIA NIM default).
- `src/ev/ingestion/` — GitHub, notes, Gmail, Calendar connectors.
- `src/ev/security/boundary.py` — `Blocklist` and `assert_personal_only`.
- `src/ev/tools/` — tools: status, brief, research, work, draft tools, deadline watcher, alerts, prep, calendar prep, people, obligations, **memory, remember**.
- `web/` — Vite + React + TypeScript + Three.js voice/HUD frontend.
- `tests/` — pytest suite.
- `scripts/`:
  - `setup_sqlite_vec.py` — create local SQLite DB, run migrations, create vector table.
  - `setup_postgres.py` — create Postgres DB and enable pgvector (optional).
  - `smoke_vector_search.py` — end-to-end vector search smoke test.
  - `smoke_semantic_memory.py` — end-to-end memory store/search smoke test.
  - `check_embeddings.py` — verify local embedding model offline.
  - `smoke_web.py` — web client smoke test.
  - `progress_report.py` — MVP progress reporter.
  - `seed_demo.py` — seeds GitHub + notes data.
  - `sync_google.py` — ingests live Gmail + Calendar.
  - `google_auth.py` — standalone browser OAuth flow.
- `docs/development/migrations.md` — migration discipline policy.
- `docs/superpowers/assessments/2026-09-17-hi-ev-honest-state-and-roadmap.md` — honest maturity assessment and roadmap.
- `docs/superpowers/plans/2026-09-17-phase-a-prep-sprint.md` — Phase A prep sprint plan.
- `memory/hi-ev-phase-a-semantic-memory.md` — Phase A completion memory.
- `pyproject.toml` — hatchling packaging, pytest config.

---

## 3. Secrets and environment

All secrets live in `C:/Users/point/projects/Hi-EV/.env` (gitignored). Do not hardcode secrets in source files or memory.

Known keys in `.env` (see the actual `.env` file; never commit real tokens):
- `EV_GITHUB_TOKEN` — classic personal token.
- `EV_NVIDIA_API_KEY` and `EV_NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1`
- `EV_DATABASE_URL` — defaults to `sqlite+aiosqlite:///%USERPROFILE%/.hiev/hiev.db`; set to Postgres URL to use Postgres.
- `EV_BLOCKED_HANDLES`, `EV_BLOCKED_DOMAINS` — JSON arrays of work handles/domains to block.
- `EV_EMBEDDING_MODEL` — defaults to `all-MiniLM-L6-v2`.
- `EV_NOTES_PATH` — path to markdown notes vault.
- `EV_GOOGLE_ENABLED=true/false` and `EV_GOOGLE_CREDENTIALS_PATH` — Gmail/Calendar OAuth.
- `EV_ALERT_INTERVAL_SEC`, `EV_ALERT_WINDOW_HOURS`, `EV_QUIET_START`, `EV_QUIET_END`, `EV_KILL_SWITCH`.
- `EV_ROBOCAD_PATH`, `EV_LEARNINGROBOTICS_PATH`, `EV_HIEV_PATH` — local repo paths.
- `EV_GITHUB_REPOS` — comma-separated list of `owner/repo` for scheduled ingestion.
- `EV_INGEST_INTERVAL_SEC` — seconds between background ingestion passes (default 300).

OAuth files (also gitignored):
- `C:/Users/point/projects/Hi-EV/secrets/credentials.json` — Google Desktop app client secret.
- `C:/Users/point/projects/Hi-EV/secrets/token.json` — user access token from completed OAuth flow.

---

## 4. Current phase and status

**Web/Voice/HUD MVP is complete and pushed.**
**Phase A prep sprint is complete and pushed.**
**Phase A — Ambient Ingestion + Semantic Memory is complete and pushed.**

Latest commit: `40aaa2b`.
Key prior commits:
- `ac630a3` — Web/Voice/HUD MVP.
- `7118e70` — Phase A prep sprint (Postgres path, test isolation, config blocklist, embeddings, migration discipline).
- `f5db9e5` — SQLite + sqlite-vec default, `DocumentChunk` model, vector helpers, setup/smoke scripts.
- `3244a0f` — Dossier and plan updates.
- `c989e27` — Semantic memory engine, memory/remember tools, grounded-search scaffold.
- `fa7a600` — Ground status, prep, and research tools in semantic memory.
- `2358a97` — Daemon ingestion scheduler loop.
- `40aaa2b` — Smoke test, env docs, memory update.

Test result:
- `python -m pytest` → **115 passed, 1 skipped**.
- `ruff check src tests scripts` → clean.

Database:
- Default: SQLite + sqlite-vec at `~/.hiev/hiev.db`.
- Optional: Postgres 16 + pgvector via `EV_DATABASE_URL` and `scripts/setup_postgres.py`.
- Migration base revision `aacdc9089a90` is frozen.

Daemon state:
- EV daemon runs on `http://127.0.0.1:7345`.
- Health: `GET /health` returns `{"status":"ok"}`.
- WebSocket: `ws://127.0.0.1:7345/ws` for the browser HUD.
- Routes available: `/status`, `/brief`, `/research`, `/work`, `/draft`, `/calendar-prep`, `/deadlines`, `/people`, `/obligations`, `/alerts`, `/prep`, `/memory`, `/remember`, `/health`, `/ws`.

---

## 5. What has been delivered

### Web/Voice/HUD MVP (complete)

- `web/` frontend with Three.js reactor/HUD shell.
- Browser voice loop: `SpeechRecognition` STT, `speechSynthesis` TTS, push-to-talk via Space.
- WebSocket bridge to `ws://127.0.0.1:7345/ws` with auto-reconnect.
- Backend `/ws` endpoint and `ChatSession` intent classifier.
- CORS for `http://localhost:5173` and `http://127.0.0.1:5173`.

### Phase A prep sprint (complete)

- SQLite + sqlite-vec default database.
- Lazy async engine with sqlite-vec extension loaded.
- `DocumentChunk` model + Alembic migration.
- `src/ev/db/vector.py` helpers for vector table CRUD and search.
- `scripts/setup_sqlite_vec.py` and `scripts/smoke_vector_search.py`.
- Config-driven blocklist via `.env`.
- Local embedding model (`all-MiniLM-L6-v2`, 384-dim).
- Test DB isolation via in-memory SQLite.
- Migration discipline documented.

### Phase A — Ambient Ingestion + Semantic Memory (complete)

- Document chunking pipeline in `src/ev/memory/chunks.py`.
- Idempotent document chunk upsert/search/delete in `src/ev/memory/store.py`.
- sqlite-vec hybrid search (vector KNN + keyword overlap + recency/source-type rerank).
- `MemoryTool` + `RememberTool` in `src/ev/tools/memory_tool.py`.
- `ev remember "..."` CLI command and `POST /remember` endpoint.
- WebSocket intents: `memory`, `search_memory`, `find_memory`, `recall`, `remember`, `save_memory`.
- Grounded `StatusTool`, `PrepTool`, `ResearchTool` inject document-memory snippets.
- Background ingestion scheduler in `src/ev/server/scheduler.py`, wired into FastAPI lifespan.
- Tests: chunking, memory tool, grounded tools, scheduler.
- Smoke test: `scripts/smoke_semantic_memory.py`.

### Phase 2 + 3 features (complete)

- NVIDIA NIM LLM client.
- `ev status`, `ev brief`, `ev research`, `ev work on`, `ev draft` tools.
- Read-only Gmail/Calendar ingestion via OAuth.
- Structured memory tables: `Project`, `Ingest`, `Deadline`, `Person`, `Obligation`, `Decision`, `Event`.
- Deadline watcher, alert loop, `ev prep`, people/obligations lookup.

---

## 6. What is blocked / waiting

**Nothing is currently blocked.** Phase B (Reasoning Router + Eval Harness) is ready to start.

---

## 7. Permission tiers (current state)

| Tier | Policy | Examples |
|------|--------|----------|
| T0 | Always auto | memory/web/repo search, `ev status`, `ev brief`, `ev research`, `ev deadlines`, `ev people`, `ev obligations`, `ev alerts` |
| T1 | Auto, log, undoable | draft PR/commit/email, run tests, spawn Claude Code, `ev work on`, `ev calendar-prep`, `ev prep`, read-only Gmail/Calendar sync, `ev remember` |
| T2 | Confirm exact payload | send email, push non-main branch, merge PR, post publicly (not yet implemented) |
| T3 | Hard-blocked | push to main, publish anything, spend money, touch work accounts or patent/IP (not yet fully enforced) |

Tier enforcement is currently metadata-level; real T2 confirmation UI and T3 hard blocks are Phase D scope.

---

## 8. Default commands to verify health

```bash
cd C:/Users/point/projects/Hi-EV
python -m pytest
ruff check src tests scripts
python scripts/check_embeddings.py
python scripts/setup_sqlite_vec.py
python -m evd
```

Web HUD:
```bash
cd web
npm install
npm run dev
# open http://localhost:5173
```

---

## 9. Phase A plan summary (complete)

Phase A — Ambient Ingestion + Semantic Memory — is complete and pushed.

Main goals delivered:
1. Continuous ingestion scheduler.
2. Document chunking pipeline.
3. Semantic memory search with sqlite-vec.
4. `ev remember "..."` command.
5. Update `status`, `brief`, `research`, `prep` to retrieve document chunks.
6. Tests and smoke scripts for the memory layer.

## 10. Phase B plan summary (next)

Phase B — Reasoning Router + Eval Harness — is the next major milestone.

Main goals:
1. Reasoning router (fast / agent / deliberate paths).
2. Streaming completions in `LLMClient` and WebSocket `/ws`.
3. Eval harness with 100+ golden questions.
4. Guard model / prompt-injection classifier.
5. Begin designing T2/T3 confirmation flows.

---

## 11. Non-obvious context for a new session

- The default LLM **must** be `meta/llama-3.2-11b-vision-instruct`. Do not switch back to `meta/llama-3.3-70b-instruct`; it is EOL and returns 410 Gone.
- Use `scripts/test_nvidia_models.py` to probe which models work if the default ever breaks.
- The default database is SQLite + sqlite-vec. If you want Postgres, set `EV_DATABASE_URL` and run `scripts/setup_postgres.py`.
- If tests hang on exit, ensure `pytest` disposes the async engine; `tests/conftest.py` handles this.
- `ev status` takes a positional argument (`ev status Hi-EV`), not `--project`.
- `ev draft commit` and `ev draft pr` require `--project`.
- `ev remember` stores text as a `DocumentChunk`; use `--project` to tag it.
- Daemon port is `7345`. If it fails to bind, kill the existing `python` process on that port.
- The project is local-first; the NVIDIA API is the primary cloud dependency. DuckDuckGo search and Google APIs (read-only) are also used.
- Always preserve the personal-only boundary. If a connector or tool might touch work data, gate it behind `EV_PERSONAL_ONLY=true` (default) and the blocklist.
- User explicitly authorized use of `.env`, running tests, and running the daemon without asking each time.
- `token.json` from Google OAuth is saved in `secrets/`. If it expires, run `python scripts/google_auth.py` again to refresh.
- For local DB resets: delete the SQLite file and run `python scripts/setup_sqlite_vec.py`. For Postgres: `dropdb hiev && createdb hiev && psql -d hiev -c "CREATE EXTENSION IF NOT EXISTS vector;" && alembic upgrade head`.

---

## 12. Related memories

- [[web-voice-hud-mvp]] — browser-native voice/HUD face.
- [[hi-ev-phase-a-prep-sprint]] — Phase A prep sprint completion.
- [[hi-ev-phase-a-semantic-memory]] — Phase A — Ambient Ingestion + Semantic Memory completion.
- [[hi-ev-roadmap-2026-09-17]] — honest state assessment and phased roadmap.
