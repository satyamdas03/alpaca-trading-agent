# Contributing to Aureum

Thank you for helping build the self-proving semantic kernel for finance.

## Getting started

1. Install [Rust](https://rustup.rs/) 1.80+ and [Python](https://www.python.org/) 3.11+.
2. Install [uv](https://docs.astral.sh/uv/) for fast Python environment management.
3. Clone the repo and run `cargo build` and `uv sync`.

```bash
git clone https://github.com/point/aureum.git
cd aureum
cargo build --workspace
uv sync
```

## Areas where help is most needed

- **Rust core:** expression DAG, dimensional type system, deterministic evaluator.
- **Python bindings:** PyO3, CLI, Polars integration.
- **Formal methods:** Lean 4 bridge, SMT constraint encoding, financial semantics.
- **Domain modeling:** ACTUS contract terms, CDM mappings, FIBO ontologies.
- **Frontend:** React/TypeScript web IDE and visual DAG.
- **Docs:** user guides, DSL reference, examples.

## Development workflow

1. Open an issue or comment on an existing one before large changes.
2. Branch from `main`.
3. Add tests for new functionality.
4. Run `cargo test` and `pytest` before pushing.
5. Submit a PR with a clear description and linked issue.

## Code of conduct

Be respectful, precise, and collaborative. Finance is a high-stakes domain; our code and conversations should reflect that responsibility.
