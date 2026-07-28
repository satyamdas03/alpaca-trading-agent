# Aureum — Self-Proving Semantic Kernel for Finance

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Rust](https://img.shields.io/badge/rust-1.80%2B-orange)](https://www.rust-lang.org/)

> A self-proving semantic kernel that lets financial institutions write, run, and audit any contract, model, report, or strategy in one meaning-layer — so an AI agent can propose a trade, and a theorem prover can prove it is safe.

## What Aureum is

Aureum is **not** a new programming language. It is a **formal financial operating substrate**:

```
Layer 4: Applications — risk models, contracts, regulatory reports, DeFi, quant strategies
Layer 3: AI agents operating THROUGH the kernel; actions are conjectures, kernel proves/rejects
Layer 2: Polyglot surfaces — Excel formulas, Python/Polars, SQL, FIX, Bloomberg, Solidity, ACTUS, CDM, XBRL
Layer 1: Formal execution engine — deterministic DAG, dimensional types, Lean/SMT verifier, full lineage
Layer 0: Semantic substrate — FIBO + CDM + ACTUS + custom ontologies, one canonical identity per object
```

## Current status

**Aureum is in early development.** The first public milestone is the **Aureum Quant Kernel** — a quant strategy workbench with:

- Natural-language strategy authoring
- Structured, schema-valid strategy DSL
- Deterministic, lineage-complete backtesting
- Dimensional type checking
- Formal risk-constraint verification
- AI reflection and attribution loop

## Quick start

```bash
pip install aureum
aureum backtest examples/strategies/momentum.yaml --data data/prices.parquet
```

## Repository structure

```
.
├── crates/aureum-core      # Rust execution engine
├── crates/aureum-py        # PyO3 bindings
├── bindings/python         # Python package (`aureum` on PyPI)
├── frontend/web            # React/TypeScript web IDE
├── docs                    # Documentation site
├── examples/strategies     # Sample strategy DSLs
└── tests                   # Integration tests
```

## Roadmap

| Phase | Goal | Status |
|---|---|---|
| 0 | Repo, docs, and buildable skeleton | In progress |
| 1 | Quant Kernel MVP: DSL + backtest + lineage | Planned |
| 2 | Dimensional types + formal risk guardrails | Planned |
| 3 | AI authoring + reflection loop | Planned |
| 4 | Multi-user surfaces (indie, fund, fintech, DeFi) | Planned |
| 5 | Public launch and community | Planned |

## Why open source?

The semantic substrate of finance should be a public good. Aureum is released under Apache-2.0 so that banks, funds, fintechs, researchers, and regulators can build on a shared, auditable foundation.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). We are looking for contributors in:
- Rust core development
- Python quant tooling
- Lean 4 / formal methods
- Financial domain modeling (ACTUS, CDM, FIBO)
- Frontend / developer experience

## License

Apache-2.0. See [LICENSE](./LICENSE).
