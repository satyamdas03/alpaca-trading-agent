# Aureum Architecture

## Design principles

1. **Semantics first.** Every object has a canonical identity and meaning before it is executed.
2. **Determinism by default.** The same inputs produce the same outputs, bit-for-bit.
3. **Dimensional types.** `float<USD>` and `float<shares>` cannot be added by mistake.
4. **Proof as a service.** Risk constraints and semantic equivalences are checked by a theorem prover, not just tested.
5. **Polyglot by design.** Users stay in Python/Excel/SQL/Solidity; Aureum provides the meaning-layer underneath.
6. **Open by default.** Core is Apache-2.0; platform services are built on top.

## Layer diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ Layer 4: Applications                                               │
│  Risk models · Contract lifecycle · Regulatory reports · DeFi ·     │
│  Quant strategies                                                   │
├─────────────────────────────────────────────────────────────────────┤
│ Layer 3: AI agents                                                  │
│  Natural-language authoring · Reflection · Attribution ·          │
│  Every proposed action = conjecture; kernel proves or rejects it    │
├─────────────────────────────────────────────────────────────────────┤
│ Layer 2: Polyglot surfaces                                          │
│  Excel formulas · Python/Polars · SQL · FIX · Bloomberg ·           │
│  Solidity · ACTUS · CDM · XBRL                                      │
├─────────────────────────────────────────────────────────────────────┤
│ Layer 1: Formal execution engine (Rust core)                        │
│  Deterministic DAG · Dimensional types · Versioned transforms     │
│  Lean/SMT verifier bridge · Lineage graph · Audit trail             │
├─────────────────────────────────────────────────────────────────────┤
│ Layer 0: Semantic substrate                                         │
│  FIBO · FINOS CDM · ACTUS · Custom ontologies                       │
│  One canonical identity per instrument, contract, metric, entity    │
└─────────────────────────────────────────────────────────────────────┘
```

## Core components

### `aureum-core` (Rust)

- **Expression DAG:** lazy, acyclic, hash-addressed computation graph.
- **Quantity:** numeric value + unit/dimension + provenance + version.
- **Transform:** pure function node; inputs and outputs are typed.
- **Workspace:** immutable snapshot of a model/strategy at a point in time.
- **Lineage store:** content-addressed map from transform hash to source, assumptions, and dependencies.
- **Verifier bridge:** serializes constraints to Lean 4 / SMT-LIB and parses proof results.

### `aureum-py` (PyO3 + Python package)

- Pythonic API over the Rust core.
- Polars/NumPy/Pandas interoperability.
- CLI entry point `aureum`.
- Jupyter notebook magics (future).

### `frontend/web` (React/TypeScript)

- Strategy editor with schema validation.
- Visual DAG explorer.
- Backtest result viewer.
- Lineage and audit inspector.

### `docs` (MkDocs)

- User guide, DSL reference, formal-methods primer, contributor docs.

## Data flow: a quant strategy

1. **Intent.** User describes a strategy in plain English or writes YAML.
2. **DSL.** LLM or human produces a schema-valid `Strategy` document.
3. **Type check.** Engine checks dimensional consistency of all signals and weights.
4. **Verify.** Risk constraints (drawdown, leverage, turnover) are encoded and sent to verifier.
5. **Execute.** DAG evaluator runs the backtest deterministically.
6. **Lineage.** Every output cell is traceable to source data, transforms, and assumptions.
7. **Reflect.** P&L attribution identifies which rule caused gains/losses; LLM proposes edits.
8. **Re-verify.** Only out-of-sample improvements are accepted.

## Versioning and identity

Every Aureum object is identified by a content hash. A change in data, formula, or assumption produces a new identity. This enables:

- Reproducible backtests
- Diff-aware code review
- Regulatory audit trails
- Semantic equivalence proofs across representations
