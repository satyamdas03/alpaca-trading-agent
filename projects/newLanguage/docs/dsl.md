# Aureum DSL Reference

The Aureum Quant Kernel uses a declarative YAML-based DSL for strategies.

## Top-level structure

```yaml
apiVersion: aureum.io/v1alpha1
kind: Strategy
metadata:
  name: my-strategy
  description: A short human-readable description
spec:
  universe: ...
  schedule: ...
  signals: ...
  ranking: ...
  weights: ...
  risk: ...
  execution: ...
  audit: ...
```

## Metadata

| Field | Type | Description |
|---|---|---|
| `name` | string | Unique identifier |
| `description` | string | Human-readable intent |
| `tags` | list | Search/discovery tags |

## Universe

Defines the investment universe and filters.

```yaml
universe:
  source: sp500
  filter:
    sector: Technology
    min_price: 5.00
    min_adv20: 1_000_000
```

## Schedule

```yaml
schedule:
  rebalance: 1M
  lookback: 252d
```

## Signals

Each signal is a typed expression over market data.

```yaml
signals:
  - name: momentum_12_1
    expr: returns(close, 252).sum() - returns(close, 21).sum()
    type: return
```

## Risk

Risk constraints can be hard (must be provable) or soft (monitored).

```yaml
risk:
  max_drawdown:
    value: 0.10
    hard: true
  max_leverage:
    value: 1.00
    hard: true
```

## Audit

```yaml
audit:
  lineage: full
  deterministic: true
  deterministic_seed: 42
```
