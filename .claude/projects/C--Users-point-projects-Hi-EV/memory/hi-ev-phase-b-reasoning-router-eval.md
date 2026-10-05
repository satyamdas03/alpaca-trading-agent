---
name: hi-ev-phase-b-reasoning-router-eval
description: "Phase B complete — reasoning router, source trust, guard, streaming fast path, and eval harness all wired and passing."
metadata:
  node_type: memory
  type: project
  modified: 2026-10-03T07:11:10.870Z
  originSessionId: ccb82d8d-e0b2-40ca-b0f5-6e78b5783f48
---

**Status:** Phase B — Reasoning Router + Eval Harness — all 17 items implemented, verified end-to-end, and passing. [[hi-ev-phase-a-semantic-memory]] is complete.

**Why this phase:** Every later capability depends on choosing the right reasoning depth and measuring whether changes make EV better. Phase B installs the routing and measurement layer.

**Completed in this session:**
- Fixed `tests/test_chat_handler.py::test_chat_guard_blocks_injection` assertion.
- Implemented `src/ev/reasoning/router.py` with fast/agent/deliberate heuristic classifier + optional LLM fallback (`route_request`, `Router`, `RouteDecision`).
- Added `tests/reasoning/test_router.py` with 20+ representative queries; router hits ≥90% accuracy on the heuristic suite.
- Integrated router into `src/ev/server/chat.py` behind `EV_ENABLE_REASONING_ROUTER`; emits `phase: route:<path>`.
- Added `ToolTierError` and guard-aware `ToolRegistry.get(..., guard_decision=...)` tier enforcement.
- Marked ingestion content with source trust: `trusted=True` for notes/user_memory, `trusted=False` for gmail, calendar, and GitHub.
- Added `trusted` boolean columns to `Ingest` and `DocumentChunk` models and generated Alembic migration `3fdf19081353`.
- Propagated trust through chunker (`TextChunk`) and semantic retrieval scoring.
- **End-to-end verification found and fixed two gaps:**
  - `trusted` was not returned in `search_document_chunks` results; fixed.
  - `trusted` columns were nullable, so existing rows would be treated as untrusted; made non-nullable with `server_default=true` and re-applied migration.
  - Added chunker fallback that marks external sources untrusted if the ingestion source omits the flag.
- Added scheduler tests verifying source trust end-to-end.
- Server API tests (status, brief, work, research, draft, calendar-prep, WebSocket ping) all pass.
- Wired `LLMClient.complete_stream()` into the fast chat path in `src/ev/server/chat.py`; WebSocket emits `phase: streaming`, multiple `delta` messages, and `done`.
- Added backend `stop` message handling in `ChatSession` so the frontend can cancel an in-progress stream; added `test_chat_stop_cancels_stream`.
- Built an extraordinary frontend streaming UI:
  - New `web/src/ui/Chat.tsx` transcript panel with auto-scroll, per-role bubbles, and a glowing animated caret on the live EV response.
  - Streaming phase badge (`STREAMING`, `ROUTE FAST`) and a red **STOP** button that sends `type: stop` over the WebSocket.
  - `web/src/store.ts` tracks `isStreaming` / `streamPhase`; `voice.ts` coordinates streaming state and speaks the full response when streaming completes.
  - `Scene.tsx` maps the `streaming` phase to a brighter core color and faster reactor spin.
  - All CSS lives in `index.css` with reduced-motion support.
- Built eval harness under `tests/eval/`: seeded fixtures (`conftest.py`), scorers (`judge.py`), and per-category evals for status, memory, research, prep, and guard refusal.
- Added standalone report runner `scripts/run_eval.py`; produces `eval_report.json` with per-category averages and latency.
- Full test suite: **181 passed, 1 skipped**. `ruff check .` clean; `cd web && npm run build` clean.
- Commits `afaf249`, `276660a`, `e8e7156`, and `beb47fe` pushed to `origin/main`.

**Plan summary (17 ranked steps):**
1. ✅ Centralize Phase B feature flags in `src/ev/config.py`.
2. ✅ Add streaming completion to `src/ev/llm/client.py`.
3. ✅ Implement guard engine in `src/ev/security/guard.py`.
4. ✅ Extend boundary helpers in `src/ev/security/boundary.py`.
5. ✅ Wire guard into `src/ev/server/chat.py`.
6. ✅ Add source trust and tier enforcement to `src/ev/tools/registry.py`.
7. ✅ Mark ingestion content with source/trusted metadata.
8. ✅ Implement reasoning router in `src/ev/reasoning/router.py`.
9. ✅ Integrate router into `src/ev/server/chat.py` behind `ENABLE_REASONING_ROUTER`.
10. ✅ Integrate streaming into the fast chat path.
11–15. ✅ Build eval harness: fixtures, golden cases, scorers, per-category tests, end-to-end eval.
16. ✅ Create standalone eval runner `scripts/run_eval.py`.
17. ✅ Update frontend streaming UI.

**Key architectural decisions:**
- Guard runs before router; blocked transcripts never reach routing.
- Deliberate path is non-streaming; fast chat streams; agent path returns bounded summary.
- Eval uses seeded fixtures and runs with feature flags on.
- All chat.py changes are feature-flagged and tested incrementally.
- Guard and router share `LLMClient.complete()` for classification; streaming is user-facing only.

**Acceptance criteria:**
- `pytest tests/eval/` produces a score report.
- A prompt change that lowers eval score is caught before merge.
- WebSocket responses stream word-by-word with visible streaming UI. ✅
- Router correctly classifies 20 sample queries with ≥90% accuracy. ✅
- Guard blocks known prompt-injection patterns and work-boundary violations. ✅
- `python -m pytest` passes; `ruff check .` clean. ✅

**Next immediate actions:**
- Phase B is fully closed. Move to Phase C per `hi-ev-roadmap-2026-09-17.md`: proactive WebSocket alerts, persistent chat threads, morning brief scheduler, optional Telegram relay.
- As of 2026-10-03, Phases C, D, E, and F are also complete; latest shipped commit is `02781e2` with 253 tests passing. See [[hi-ev-phase-f-plugin-architecture]].
