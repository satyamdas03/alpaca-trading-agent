# Getting Started

## Installation

Aureum requires Python 3.11+ and Rust 1.80+.

```bash
pip install aureum
```

For development:

```bash
git clone https://github.com/point/aureum.git
cd aureum
cargo build --workspace
pip install -e bindings/python
```

## Run your first backtest

```bash
aureum backtest examples/strategies/momentum.yaml --data data/prices.parquet
```

## Next steps

- Read the [DSL reference](./dsl.md)
- Explore the [architecture](../ARCHITECTURE.md)
- Join the community on GitHub
