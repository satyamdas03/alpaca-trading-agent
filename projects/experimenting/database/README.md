# SynapseDB

An **agent-native data kernel** built around one idea: a single append-only, time-versioned, differential log is enough to derive relational, document, graph, vector, time-series, and search views.

This repository is the Phase 0 skeleton: a durable temporal differential log with a content-addressed Merkle Mountain Range, crash recovery, and a small CLI.

## Phase 0 status

- [x] Rust workspace: `synapse-types`, `synapse-log`, `synapse-cli`
- [x] `(entity_id, attribute, value, timestamp, diff)` record model
- [x] Segment-based append-only log with length-prefixed frames and CRC32
- [x] Merkle Mountain Range over every record for verifiable history
- [x] `snapshot_as_of(t)` time-travel read
- [x] Crash recovery with torn-write truncation
- [x] CLI: `init`, `write`, `read`, `snapshot`, `verify`, `recover`
- [x] Acceptance test: 1M writes → crash → recover → snapshot

## Build

```bash
cargo build --workspace --release
```

## Test

Fast unit + integration tests:

```bash
cargo test --workspace --all-targets
cargo clippy --workspace --all-targets
```

1M-write acceptance test (release mode recommended):

```bash
cargo test --test acceptance --release -- --ignored --nocapture
```

Latest acceptance run on this machine:

- **1,000,000 records written in ~0.68 s**
- **~1.47M records/s** (single-threaded, debuggable release build, NVMe-ish laptop SSD)
- Crash → recover → snapshot validated end-to-end

## CLI usage

```bash
# create a data directory
./target/release/synapse init --dir /tmp/synapse --segments 100000

# append a fact
./target/release/synapse write --dir /tmp/synapse \
  --entity 1 --attr name --value '"hello"' --ts 1

# read by global offset
./target/release/synapse read --dir /tmp/synapse --offset 0

# time-travel snapshot
./target/release/synapse snapshot --dir /tmp/synapse --as-of 1

# verify MMR root
./target/release/synapse verify --dir /tmp/synapse

# recover after a crash
./target/release/synapse recover --dir /tmp/synapse
```

## Repository layout

```
.
├── Cargo.toml
├── README.md
├── SYNAPSEDB_DOSSIER.md          # living project dossier; updated via "POINTBREAK"
├── synapse-types/src             # EntityId, Attribute, Value, Timestamp, Record, Diff
├── synapse-log/src               # LocalLog, segment format, MMR, recovery, compaction
├── synapse-log/tests/acceptance.rs
└── synapse-cli/src/main.rs       # `synapse` command-line binary
```

## Next: Phase 1

Phase 1 adds the derived view engine (`synapse-views`): incremental relational, document, and time-series views maintained from the log using differential dataflow operators.

See `SYNAPSEDB_DOSSIER.md` for the full vision, build plan, and session history.
