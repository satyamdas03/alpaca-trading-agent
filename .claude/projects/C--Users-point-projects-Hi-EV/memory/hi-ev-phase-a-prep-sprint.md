---
name: hi-ev-phase-a-prep-sprint
description: Phase A prep sprint completion — SQLite + sqlite-vec default, config blocklist, embeddings, migration discipline.
metadata:
  node_type: memory
  type: project
  originSessionId: 5b288aae-6b6f-48b4-8c74-35ee15384a5b
  modified: 2026-09-17T02:42:45.809Z
---

**Context:** The [[web-voice-hud-mvp]] is complete. Before starting Phase A (Ambient Ingestion + Semantic Memory), several blockers had to be cleared. This memory records the prep sprint and the pivot from Postgres+pgvector to SQLite+sqlite-vec as the default local database.

**Why the prep sprint happened:**
- Phase A needs vector search, a maintainable blocklist, and disciplined migrations.
- Postgres 16 + pgvector was not installed in the environment and required user action, so the default was switched to SQLite + sqlite-vec to keep progress unblocked.

**What was delivered:**
- **SQLite + sqlite-vec default:** `src/ev/config.py` now defaults `EV_DATABASE_URL` to `~/.hiev/hiev.db`.
- **Lazy async engine with sqlite-vec loaded:** `src/ev/db/base.py` uses a custom `aiosqlite` creator that loads the `sqlite-vec` extension on every connection.
- **`DocumentChunk` model:** Added to `src/ev/db/models.py` with Alembic migration `e65cfe42f3a6_add_document_chunks.py`.
- **Vector helpers:** `src/ev/db/vector.py` wraps sqlite-vec virtual table creation, indexing, search, and deletion.
- **Setup + smoke scripts:** `scripts/setup_sqlite_vec.py` and `scripts/smoke_vector_search.py`.
- **Config-driven blocklist:** `EV_BLOCKED_HANDLES` / `EV_BLOCKED_DOMAINS` in `src/ev/config.py`; ingestion connectors use `Blocklist.from_settings(config)`.
- **Local embedding model:** `src/ev/embeddings.py` wraps `sentence-transformers` `all-MiniLM-L6-v2` (384-dim); `scripts/check_embeddings.py` smoke test.
- **Test DB isolation:** `tests/conftest.py` forces in-memory SQLite for tests and disposes the engine at session finish.
- **Migration discipline:** `docs/development/migrations.md` documents frozen base revision `aacdc9089a90` and rules for new migrations.
- **Docs refreshed:** `README.md` and `.env.example` describe the SQLite default with Postgres as an optional upgrade.

**Verification:**
- `python -m pytest` → 89 passed, 1 skipped.
- `ruff check src tests scripts` → clean.
- `python scripts/setup_sqlite_vec.py` → database ready.
- `python scripts/smoke_vector_search.py` → top-K similarity search returns correct chunks.
- `python scripts/check_embeddings.py` → 384-dim vectors.

**Commits:**
- Prep sprint base: `7118e70` on `main`.
- SQLite + sqlite-vec unblock: `f5db9e5` on `main`.
- Prep sprint plan update: `3244a0f` on `main`.

**Why it matters:** Phase A can now proceed without waiting for a system Postgres install. When Postgres is available later, the same embedding model, dimensions, and schema can migrate to pgvector with a single Alembic revision.

**How to apply:**
- Fresh clone: `pip install -e ".[dev]"`, then `python scripts/setup_sqlite_vec.py`.
- To use Postgres instead: install Postgres 16 + pgvector, set `EV_DATABASE_URL=postgresql://localhost:5432/hiev`, run `python scripts/setup_postgres.py`, then `alembic upgrade head`.
- Always follow migration discipline from `docs/development/migrations.md`.
