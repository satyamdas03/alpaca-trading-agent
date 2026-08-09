# SynapseDB Dossier — Living Project Memory

**Project name:** SynapseDB  
**Codename origin:** `experimenting/database` session, 2026-08-09  
**Classification:** Agent-Native Data Kernel (new category, not a traditional database)  
**Status:** Planning complete; ready to start Phase 0 implementation  
**Dossier rule:** Append-only updates. When user says `POINTBREAK`, append the next block of progress to the end of this file.

---

## 1. Why SynapseDB Exists

The 2026 database landscape is a mature but fragmented ecosystem. Every category is a specialized answer to a specific workload, and every specialization carries permanent trade-offs:

- Consistency costs latency.
- Freshness costs metadata and compaction.
- Scale costs operational complexity.
- Flexibility costs query power.
- Speed costs durability guarantees.

The unsolved frontier is not making any one engine faster; it is **unifying models, automating operations, and exposing explicit consistency/latency/freshness contracts** so applications can stop being database integration projects.

---

## 2. The Vision

> **SynapseDB is an Agent-Native Data Kernel.**

It is not a database. It is a temporal inference substrate for autonomous software.

Every data model is a derived view. Every consistency level is a policy. Every deployment topology is a replica configuration. All of it is derived from one temporal, differential, disaggregated log.

---

## 3. Core Architectural Commitments

| Commitment | Meaning |
|------------|---------|
| **One Temporal Differential Log (TDL)** | Single append-only, time-versioned, Merkle-hashed log on object storage |
| **Models are derived views** | Relational, document, graph, vector, time-series, search are incrementally maintained views over the TDL |
| **Model-agnostic query language** | MAQL unifies SQL, graph pattern matching, vector KNN, time-series functions |
| **CALM-aware execution** | Coordination injected only where invariants require it; monotonic ops run coordination-free |
| **Disaggregated + learned storage** | Durable state on object storage; local NVMe as cache; learned indexes and ANN |
| **Foundation-model autopilot governor** | Simulates changes in sandbox; applies low-risk; escalates risky; auto-rollback |
| **Edge-native CRDT fabric** | WASM/unikernel replicas for local-first collaboration on drafts |
| **Optional verifiable proofs** | Merkle log + optional SNARKs for compliance-critical queries |

---

## 4. What Makes It Revolutionary

The world has seen unified databases, HTAP engines, streaming DBs, vector DBs, CRDT sync, and advisors. It has not seen a system that combines all of the following:

1. Temporal differential log as the single substrate (not just one storage engine).
2. Data models as derived views, not co-located engines.
3. Programmable consistency/freshness/latency contracts as a first-class API.
4. Foundation-model autopilot with sandbox simulation and policy gates.
5. Edge-first CRDT fabric as a native derived view over the same log.
6. Optional verifiable proofs on a temporal log.
7. **Retrieval as a write** (self-curating memory, from GEM/MemState).
8. **Edges as write-time programs** (executable schema/reconciliation, from WorldDB).
9. **Agentic speculation / branched transactions** (what-if inference, from CIDR 2026).
10. **Recursive content-addressed worlds** (Merkle identity + ontology scope).
11. **WASM/unikernel edge execution** (<50 ms cold start).
12. **Active metadata as the control plane**.

---

## 5. Honest Scope and Limits

SynapseDB does not claim to:
- Replace CRDTs with transactions for hard invariants.
- Violate CAP/PACELC cross-region latency costs.
- Beat specialists (kdb+, Redis, ClickHouse) at their extreme workloads.
- SNARK-prove every query at OLTP latency.

It is honest about limits and revolutionary within them.

---

## 6. Build Plan — 12 Phases

| Phase | Months | Goal |
|-------|--------|------|
| 0 | 1–3 | Durable temporal differential log |
| 1 | 4–8 | Incremental relational/document/time-series views |
| 2 | 9–14 | SQL + document + time-series query surface |
| 3 | 15–22 | Vector + graph as first-class views |
| 4 | 23–28 | Full-text search + hybrid ranking |
| 5 | 29–34 | Programmable consistency/freshness/latency contracts |
| 6 | 35–44 | Distributed consensus + sharding |
| 7 | 45–54 | Agentic speculation / branched transactions |
| 8 | 55–64 | Self-curating memory (retrieval as write) |
| 9 | 65–78 | Foundation-model autopilot with sandbox governance |
| 10 | 79–90 | WASM/unikernel edge fabric |
| 11 | 91–102 | Optional verifiable proofs |
| 12 | 103–120 | Managed cloud + ecosystem + PostgreSQL wire compat |

Current status: **Planning complete. Ready to begin Phase 0.**

---

## 7. Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Rust |
| Log storage | S3 Express One Zone / local NVMe / standard object store |
| Serialization | Apache Arrow / Parquet for bulk; msgpack for deltas |
| View storage | Custom LSM-tree or RocksDB + learned indexes |
| Query engine | Custom dataflow + DataFusion for SQL |
| Network | gRPC + HTTP/2 + QUIC |
| Edge | WASM (wasmtime) / unikernel (Unikraft/Firecracker) |
| Consensus | Raft (openraft/tikv) |
| Autopilot | External LLM API + deterministic simulators |
| Proofs | Merkle mountain range + optional SNARK (Plonky3 / FRI) |

---

## 8. Risk Register

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Building too much at once | High | Strict phase gates; hard cuts; ship kernel first |
| Cross-model optimizer complexity | High | Defer unified optimizer; start per-model |
| CALM automation too hard | Medium | Manual annotations first; automate incrementally |
| Distributed consensus delays | Medium | Phase 6 after MVP; single-node product can ship earlier |
| Autopilot hallucinates changes | Medium | Policy gates + sandbox + rollback |
| CRDT scope creep | Medium | Limit to drafts/collaboration only |
| SNARKs too slow | Low | Keep optional |
| Funding/team gap | High | Open-source core + managed cloud; VC pitch after Phase 2 |

---

## 9. First 90 Days

- **Weeks 1–4:** Rust workspace, TDL data model, local disk write path, unit tests.
- **Weeks 5–8:** S3 Express durability, Merkle hashing, snapshot read, crash recovery.
- **Weeks 9–12:** CLI, compaction, 1M-write acceptance test, design doc, Phase 1 gate review.

---

## 10. Session Artifacts

| File | Purpose |
|------|---------|
| `database_landscape_deep_research_2026.md` | Full taxonomy of database categories, shortcomings, and unsolved gaps |
| `synapsedb_design_2026.md` | Original full SynapseDB architectural blueprint |
| `synapsedb_feasibility_analysis_2026.md` | Honest feasibility verdict (NO for the all-conquering version; YES for the narrower vision) |
| `synapsedb_revolutionary_position_2026.md` | Why the narrower vision is revolutionary and what to add to make it category-defining |
| `synapsedb_build_plan_2026.md` | End-to-end 12-phase build plan with stack, risks, and 90-day start |
| `SYNAPSEDB_DOSSIER.md` | This file — living project memory |

All files live in `.claude/scratchpad/` except this dossier, which lives at project root.

---

## 11. Open Decisions Pending

1. Confirm Rust as primary language.
2. Choose first external API: gRPC, HTTP, or PostgreSQL wire protocol.
3. Choose license: Apache 2.0 open core vs. source-available.
4. Choose first design partner vertical: AI-agent startups, fintech compliance, or general SaaS.
5. Confirm team size assumption (skunkworks vs. funded effort).

---

## 12. POINTBREAK Update Log

*No POINTBREAK updates yet. This section will be appended when the user triggers the keyword.*

---

**Last updated:** 2026-08-09 — dossier created, planning complete.
