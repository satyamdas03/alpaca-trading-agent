---
name: synapsedb-agent-native-data-kernel
description: "New database category project — temporal differential log, derived views across models, CALM-aware execution, autopilot, edge fabric, and verifiable proofs."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5d8dc737-27db-49d8-acf4-b0065ed4605d
  modified: 2026-08-09T04:44:53.599Z
---

# SynapseDB — Agent-Native Data Kernel

**Date:** 2026-08-09  
**Project location:** `C:\Users\point\projects\experimenting\database`  
**Dossier:** `SYNAPSEDB_DOSSIER.md` (project root, append-only on keyword `POINTBREAK`)  
**Status:** Planning complete; ready to start Phase 0 implementation  
**Category:** New database / data-systems category

## One-line summary

SynapseDB is an **Agent-Native Data Kernel** — a temporal, differential, disaggregated log from which relational, document, graph, vector, time-series, and search views are incrementally derived, with programmable consistency contracts, a foundation-model autopilot, CRDT edge replicas, and optional verifiable proofs.

## Why it matters

The 2026 database landscape is fragmented into specialized engines (OLTP, OLAP, HTAP, vector, graph, time-series, search, edge). Each solves one workload well but forces applications to integrate many systems via brittle pipelines. SynapseDB proposes a new abstraction: one temporal differential log that is simultaneously the operational store, data lake, audit trail, and streaming source, with every data model as a derived view.

## What makes it revolutionary

1. **Temporal differential log as single substrate** — no separate WAL, CDC, or warehouse load.
2. **Models as derived views** — relational, document, graph, vector, time-series, search from one stream.
3. **Retrieval as a write** — queries update salience; the system self-curates memory.
4. **Edges as write-time programs** — schema is executable reconciliation policy.
5. **Agentic speculation / branched transactions** — AI agents run what-if branches over the log.
6. **Programmable consistency/freshness/latency contracts** — per-operation trade-offs, not per-engine.
7. **Foundation-model autopilot governor** — simulates changes in sandbox before applying.
8. **WASM/unikernel edge replicas** — instant cold-start local-first collaboration.
9. **Optional verifiable proofs** — Merkle log + SNARKs for compliance queries.

## Honest limits

- CRDTs are limited to drafts/collaboration, not hard-invariant transactions.
- CAP/PACELC cross-region strong consistency still costs latency.
- Specialists (kdb+, Redis, ClickHouse) still win at their extremes.
- SNARK proofs are too expensive for every query; they remain optional.

## Build plan overview

12 phases over ~10 years, with strict gates:

| Phase | Goal |
|-------|------|
| 0 | Durable temporal differential log |
| 1 | Incremental derived views |
| 2 | Query surface |
| 3 | Vector + graph views |
| 4 | Full-text search |
| 5 | Programmable consistency contracts |
| 6 | Distributed consensus + sharding |
| 7 | Agentic speculation / branched transactions |
| 8 | Self-curating memory |
| 9 | Foundation-model autopilot |
| 10 | Edge fabric |
| 11 | Verifiable proofs |
| 12 | Managed cloud + ecosystem |

## Technology stack

- **Rust** kernel
- **S3 Express One Zone / NVMe / object storage** durability
- **Apache Arrow / Parquet** bulk serialization
- **Custom LSM-tree or RocksDB + learned indexes** view storage
- **DataFusion + custom differential dataflow** query execution
- **gRPC + HTTP/2 + QUIC** network
- **WASM / unikernels** edge
- **Raft** consensus
- **External LLM API + deterministic simulators** autopilot
- **Merkle mountain range + optional SNARKs** proofs

## First 90 days

- Weeks 1–4: Rust workspace + TDL data model + local disk write path.
- Weeks 5–8: S3 Express durability + Merkle hashing + snapshot reads + crash recovery.
- Weeks 9–12: CLI + compaction + 1M-write acceptance test + Phase 1 gate review.

## Session artifacts

| File | Location |
|------|----------|
| Database landscape deep research | `.claude/scratchpad/database_landscape_deep_research_2026.md` |
| Original full design | `.claude/scratchpad/synapsedb_design_2026.md` |
| Feasibility analysis | `.claude/scratchpad/synapsedb_feasibility_analysis_2026.md` |
| Revolutionary positioning | `.claude/scratchpad/synapsedb_revolutionary_position_2026.md` |
| End-to-end build plan | `.claude/plans/synapsedb_build_plan_2026.md` |
| Living dossier | `projects/experimenting/database/SYNAPSEDB_DOSSIER.md` |

## Open decisions

1. Confirm Rust as primary language.
2. Choose first external API: gRPC, HTTP, or PostgreSQL wire protocol.
3. Choose license: Apache 2.0 open core vs. source-available.
4. Choose first design partner vertical.
5. Confirm team size assumption.

## Next step

Begin **Phase 0**: create Rust workspace, implement the temporal differential log, and pass the 1M-write durability acceptance test.

**Why:** This is the foundational layer. Everything else derives from it.

## Related

- [[project_aureum_financial_semantic_kernel]] — prior work on self-proving semantic kernels; may inform the verifiable-proofs layer.
- [[project_darkwatch]] — example of a project managed via a living `DOSSIER.md`.
