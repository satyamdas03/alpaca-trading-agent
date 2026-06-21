# Trading Strategy

## Goal
Beat the S&P 500 using fundamentals-driven swing trading. Paper trading mode — experiment aggressively.

## Factor Framework

| Factor | Weight (Risk-On) | What We Look For | Data Source |
|--------|-----------------|------------------|------------|
| Quality | 25% | Gross margins > sector avg, Piotroski F-Score > 6, low accruals | Alpaca fundamentals + WebSearch |
| Momentum | 30% | 12-1 month return > S&P, relative strength | Alpaca get_stock_bars |
| Value | 10% | P/E and P/B below sector average | Alpaca get_stock_snapshot |
| Low Volatility | 15% | Beta < 1.0, realized vol below median | Alpaca get_stock_bars |
| Sentiment | 20% | Low short interest, positive news flow, insider buying | Alpaca get_news + WebSearch |

## Regime Detection

| Regime | Signal | Factor Shift |
|--------|--------|--------------|
| Risk-On | VIX < 20, SPX above 200MA, PMI > 50 | Momentum ↑, Value ↓ |
| Late Cycle | VIX 20-25, PMI declining, yield curve flattening | Value ↑, Momentum ↓ |
| Stress | VIX > 25, SPX below 200MA, HY spreads widening | Low Vol ↑, Momentum ↓ |
| Recovery | VIX declining from peak, PMI bottoming, yield curve steepening | Quality ↑, Momentum ↑ |

## Position Sizing
- Aggressive mode: Up to 20% of portfolio per position
- Default: 10% per position
- Minimum: $500 per trade

## Exit Rules
- Stop-loss: -7% default (wider for volatile names)
- Trailing stop: 10% on winning positions
- Time-based: Close swing trades after 30 days if no catalyst

## What We Trade
- US stocks and ETFs (primary)
- Options for hedging or leveraged bets
- Crypto for diversification
- No restrictions in paper trading mode