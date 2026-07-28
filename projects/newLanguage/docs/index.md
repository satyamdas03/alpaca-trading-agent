# Aureum

Aureum is a **self-proving semantic kernel for finance**.

It lets you write, run, and audit financial models, contracts, reports, and trading strategies in one meaning-layer — so an AI agent can propose a trade, and a theorem prover can prove it is safe.

## What makes Aureum different

- **Semantic substrate:** Every object has a canonical identity and meaning (FIBO, CDM, ACTUS).
- **Dimensional types:** `float<USD>` and `float<shares>` cannot be added by mistake.
- **Deterministic execution:** The same inputs produce the same outputs, bit-for-bit.
- **Proof as a service:** Risk constraints are checked by Lean 4 / SMT, not just unit tests.
- **Polyglot:** Use Python, Excel, SQL, or Solidity. Aureum provides the meaning-layer underneath.

## Get started

```bash
pip install aureum
```

```python
from aureum import Strategy

strategy = Strategy.from_yaml("examples/strategies/momentum.yaml")
report = strategy.backtest(data="data/prices.parquet")
report.summary()
```

## Learn more

- [Architecture](../ARCHITECTURE.md)
- [Contributing](../CONTRIBUTING.md)
- [GitHub](https://github.com/point/aureum)
