# Trade Execution Skill

## Purpose
Execute trades via Alpaca MCP tools with proper documentation.

## Before Trading
1. Check `get_clock` — market must be open (or use extended hours if needed)
2. Check `get_account_info` — verify sufficient buying power
3. Check `get_all_positions` — avoid overconcentration
4. Review STRATEGY.md for current factor weights and regime

## Placing Orders

### Stock/ETF Orders
```
Use: place_stock_order
Parameters:
  - symbol: e.g., "AAPL"
  - qty: number of shares
  - side: "buy" or "sell"
  - type: "market", "limit", "stop", "stop_limit", "trailing_stop"
  - time_in_force: "day" or "gtc"
  - (for limit): limit_price
  - (for stop): stop_price
  - (for trailing_stop): trail_price or trail_percent
```

### Crypto Orders
```
Use: place_crypto_order
Parameters: similar to stock but with crypto symbol format
```

### Option Orders
```
Use: place_option_order
For multi-leg: provide legs array
```

## Order Management
- `get_orders` — check open orders
- `cancel_order_by_id` — cancel specific order
- `cancel_all_orders` — cancel all open orders
- `replace_order_by_id` — modify an existing order

## Position Management
- `get_all_positions` — list all positions
- `get_open_position` — details for one position
- `close_position` — close a specific position
- `close_all_positions` — liquidate everything

## Stop-Loss Rules
- Default: -7% stop-loss from entry price
- Volatile stocks: -10% stop-loss
- Use trailing_stop orders for automatic adjustment
- Midday routine: review all positions, tighten stops on winners

## Trade Logging
After EVERY trade execution, update `memory/TRADE_LOG.md`:
```
| 2026-04-21 09:35 | AAPL | BUY | 50 | $182.45 | Momentum signal: 12-1 +14.2% vs SPX +8.1% | Filled |
```

## Risk Checks Before Every Trade
1. Position size ≤ 20% of portfolio value
2. Not duplicating existing position without reason
3. Sufficient buying power available
4. Market is open (or pre-market is acceptable)