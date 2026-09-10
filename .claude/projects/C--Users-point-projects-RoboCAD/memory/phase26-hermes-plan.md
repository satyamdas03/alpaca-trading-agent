---
name: phase26-hermes-plan
description: Phase 26 — HERMES cross-domain conversational supervisor (end-to-end complete).
metadata:
  node_type: memory
  type: project
  originSessionId: 7435fc68-ca4e-4484-976a-3e6e62f81195
  modified: 2026-09-06T03:18:37.496Z
---

# Phase 26 — HERMES conversational supervisor

**Date:** 2026-09-06  
**Status:** **end-to-end complete**  
**Tests:** **450/451 passing** across default, heavy/slow, and mujoco tiers (1 expected failure in `test_geda_bridge_brain.py`, 5 benchmark/network tests deselected).  
**Frontend build:** passes.

## What was done

Added an LLM-driven conversational supervisor that can talk to the user across design, simulation, and training APIs. HERMES proposes actions, explains results, shows live status, and requires human approval for expensive or destructive operations. Phase 26 shipped as a foundation; this hardening pass closed every caveat end-to-end.

### Backend: `ai_cad/hermes/`

| File | Responsibility |
|---|---|
| `ai_cad/hermes/__init__.py` | Public exports: `HermesSession`, `HermesAgent`, `HermesToolRegistry`, `ApprovalGate`, `explain_report`, `execute_plan_step`, `execute_tool`, `validate_tool_parameters`, `build_design_context`, `build_llm_caller`, `ValidationErrorMessage` |
| `ai_cad/hermes/models.py` | Pydantic models: `Session`, `Plan`, `PlanStep`, `Message`, `ToolCall`, `ToolResult` |
| `ai_cad/hermes/tools.py` | `HermesToolRegistry` with read-only and design-modifying tools; `execute()` dispatches to real executors |
| `ai_cad/hermes/gate.py` | `ApprovalGate` — which tool calls need human confirmation |
| `ai_cad/hermes/planner.py` | Dependency-aware plan execution, approval workflow, rejection cascading |
| `ai_cad/hermes/session.py` | JSON-persisted `HermesSession` under `designs/_hermes/{session_id}.json` |
| `ai_cad/hermes/agent.py` | Deterministic JSON-in-text parser + Anthropic/Ollama LLM caller integration |
| `ai_cad/hermes/explain.py` | Plain-language summaries of DFM/verification/brain/world-replay reports; LLM-driven + heuristic redesign proposals |
| `ai_cad/hermes/validation.py` | Pydantic parameter validation for every tool; raises `ValidationErrorMessage` on schema failure |
| `ai_cad/hermes/executor.py` | Real executors bound to backend callables for ~14 tools (`generate_design`, `regenerate_parameters`, `run_dfm_report`, `run_verification`, `build_world`, `replay_world`, `train_brain`, `synthesize_assembly`, etc.) |
| `ai_cad/hermes/context.py` | Compact design-context builder (`build_design_context`) and global context merge (`build_global_context`) |
| `ai_cad/hermes/llm.py` | `build_llm_caller(model=None, api_key=None)` supports Anthropic Claude and Ollama; `deterministic_mock_caller` for tests |

### Tool registry (Phase 26 end-to-end)

All tools execute against real backend APIs through injected callables. No stubs remain.

| Tool | Requires approval | Real executor |
|---|---|---|
| `classify_domain` | No | `_classify_domain_safe` |
| `decompose_prompt` | No | `decompose(..., use_llm=False)` |
| `generate_design` | Yes | `generate_design` (design creation) |
| `regenerate_parameters` | Yes | `regenerate_parameters` |
| `run_dfm_report` | No | `dfm_report` |
| `run_verification` | No | `verify_design` |
| `build_world` | No (fast stub) | `build_world` |
| `randomize_world` | No | `randomize_world` |
| `replay_world` | No | `replay_world` |
| `train_brain` | Yes | `train_brain` |
| `recommend_skill` | No | `recommend_skill` |
| `train_skill` | Yes | `train_skill` |
| `synthesize_assembly` | Yes | `synthesize_assembly` |
| `update_tags` | No | `update_design_tags` |
| `explain_last_failure` | No | `explain_report` |
| `propose_redesign` | No (proposes only) | LLM + heuristic redesign; backend auto-queues `regenerate_parameters` |

### FastAPI endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/hermes/session` | POST | Create a new HERMES session attached to a design (or global) |
| `/hermes/session/{session_id}` | GET | Load session state + current plan + design summary |
| `/hermes/session/{session_id}/message` | POST | Send a user message; returns assistant reply + any pending approvals |
| `/hermes/session/{session_id}/approve` | POST | Approve/reject a gated tool call and continue execution |
| `/hermes/session/{session_id}/explain` | POST | Ask HERMES to explain a persisted report |
| `/hermes/session/{session_id}/status` | GET | Current status: idle/running/awaiting_approval/error/done |

### Frontend

- `HermesPanel.jsx` — chat thread, plan viewer, approval cards, quick-explain buttons, live status badge, design-context summary, "Propose redesign" quick action, tool-result status cards, redesign proposal cards, inline step errors.
- API helpers in `web/frontend/src/api.js`.
- Integrated into `App.jsx` panels grid.

## Tests

- `tests/test_hermes.py` — unit tests covering gate, registry, planner, session, agent, explanation engine; now uses mock context callables and `latest_reports`.
- `tests/test_hermes_backend.py` — FastAPI endpoint tests covering session CRUD, messaging, approval/rejection, explain, status; patched with deterministic mock LLM caller.
- `tests/test_hermes_executor.py` — real executor dispatch and parameter validation.
- `tests/test_hermes_validation.py` — Pydantic parameter validation for every tool.
- `tests/test_hermes_context.py` — design-context builder and global-context merge.
- `tests/test_hermes_integration.py` — end-to-end design → HERMES → propose_redesign → auto-queued `regenerate_parameters` workflow.
- Full pytest suite: **450/451 passing** across default, heavy/slow, and mujoco tiers (1 expected failure, 5 benchmark/network tests deselected).
- Frontend `npm run build` passes.

## Why

As RoboCAD adds simulation and training APIs, the UI surface becomes too large for a panel-per-feature approach. HERMES gives users a single conversational interface to orchestrate the whole pipeline while keeping humans in the loop for expensive or design-changing actions. Closing the loop with real executors and parameter validation makes the supervisor production-trustworthy, not just a demo.

## How to apply

- Open the HERMES panel on any selected design and ask it to explain a DFM report, propose a redesign, or start a training run.
- Approve expensive steps explicitly; reject steps you don't want executed.
- Extend `HermesToolRegistry` with new actions by registering `HermesTool` entries and adding a real executor in `executor.py`; validation will automatically enforce the schema.
- For automated redesign: ask HERMES to "propose a redesign" after a verification/DFM failure. If the proposal includes `parameter_updates`, the backend appends a pending `regenerate_parameters` step for approval.

## Remaining work / caveats

- Native Anthropic tool-use integration (currently JSON-in-text for model-agnostic testing).  
- Optional: deeper LLM-driven redesign for simulation/world failures (currently mechanical/verification focused).  
- Phase 27 — sim-to-real feedback loop — will build on HERMES as the orchestration layer.

## Links

- [[Phase 25 — attention-based robot brain training layer]] — brain training APIs HERMES orchestrates.
- [[Phase 24 — world-model simulation builder]] — world builder APIs HERMES orchestrates.
- [[Phase 22 — multi-physics verification]] — verification reports HERMES explains.
