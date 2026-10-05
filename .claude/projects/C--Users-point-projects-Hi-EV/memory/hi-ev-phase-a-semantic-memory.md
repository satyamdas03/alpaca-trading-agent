---
name: hi-ev-phase-a-semantic-memory
description: "Phase A shipped — semantic memory engine, memory/remember tools, grounded-search, and daemon ingestion scheduler; committed and pushed."
metadata:
  node_type: memory
  type: project
  modified: 2026-10-03T07:11:06.382Z
  originSessionId: ccb82d8d-e0b2-40ca-b0f5-6e78b5783f48
---

**Status:** Phase A — Ambient Ingestion + Semantic Memory — is complete, committed, and pushed to `origin/main`. [[hi-ev-phase-a-prep-sprint]] cleared the SQLite + sqlite-vec blockers; this memory records the final shipped state.

**Latest relevant commits:**
- `40aaa2b` — hi-ev: Phase A — smoke test, env docs, memory update
- `2358a97` — hi-ev: Phase A — daemon ingestion scheduler loop
- `fa7a600` — hi-ev: Phase A — ground status, prep, and research tools in semantic memory
- `c989e27` — hi-ev: Phase A — semantic memory engine, memory/remember tools, grounded-search scaffold
- `db5e6ac` — docs: sync dossier, roadmap, and prep-sprint plan with current state

**What was delivered:**

- **Document chunking pipeline:** `src/ev/memory/chunks.py` — `Chunker` with paragraph/sentence/word fallback and configurable overlap.
- **Semantic memory store:** `src/ev/memory/store.py` adds `upsert_document_chunks`, `search_document_chunks`, and `delete_document_chunks` backed by `DocumentChunk` + sqlite-vec `vec_document_chunks`.
- **Idempotent upsert:** query-and-merge by `(source, source_id, chunk_index)`; re-indexes changed chunks by deleting stale vectors before inserting new ones.
- **Hybrid search:** sqlite-vec KNN + SQL keyword overlap + recency/source-type rerank.
- **Embedding model:** `sentence-transformers` `all-MiniLM-L6-v2` (384-dim), lazy-loaded in `src/ev/embeddings.py`.
- **Memory tools:** `src/ev/tools/memory_tool.py` with `MemoryTool` (search) and `RememberTool` (store).
- **`ev remember` CLI command:** `src/ev/cli/main.py` stores explicit user facts.
- **API endpoints:** `POST /memory` and `POST /remember` in `src/ev/server/api.py`.
- **WebSocket intents:** `memory`, `search_memory`, `find_memory`, `recall`, `remember`, `save_memory` routed through `src/ev/server/chat.py`.
- **Grounded tools:**
  - `StatusTool` appends "From memory:" snippets.
  - `PrepTool` injects "Related memory:" snippets using event title + project.
  - `ResearchTool` prepends memory snippets to web-search prompt and returns `memory_snippets`.
- **Daemon ingestion scheduler:** `src/ev/server/scheduler.py` with `_ingest_loop` and `_run_ingestion_pass`, wired into FastAPI lifespan. Runs `NotesIngestion`, `GitHubIngestion` (when `EV_GITHUB_REPOS` configured), `CalendarIngestion` + `GmailIngestion` (when `EV_GOOGLE_ENABLED=true`). Long-form records are chunked and indexed automatically. Respects `kill_switch` and quiet hours.
- **Smoke test:** `scripts/smoke_semantic_memory.py` verifies end-to-end store/search.
- **Tests:** `tests/memory/test_document_chunks.py`, `tests/tools/test_memory_tool.py`, grounded-memory tests for status/prep/research, and `tests/test_scheduler.py`.

**Verification at completion:**
- `python -m pytest` → **115 passed, 1 skipped**.
- `ruff check .` → clean.
- `python scripts/smoke_semantic_memory.py` → end-to-end memory store + search passes.
- `python scripts/progress_report.py` → **6/6 acceptance criteria met** for the Web/Voice/HUD MVP.

**How to use:**
- Store a memory: `ev remember "RoboCAD is in Phase 23" --project RoboCAD`
- Search via API: `POST /memory { "query": "what phase is RoboCAD in?" }`
- Configure background ingestion: set `EV_GITHUB_REPOS=owner/repo` and `EV_INGEST_INTERVAL_SEC=300` in `.env`.

**Next phase:** Phase B — Reasoning Router + Eval Harness (see [[hi-ev-roadmap-2026-09-17]]). As of 2026-10-03, Phases B, C, D, E, and F are also complete; the latest shipped commit is `02781e2` with 253 tests passing.
