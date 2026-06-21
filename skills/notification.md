# Notification Skill

## Purpose
Send email notifications via Gmail MCP to satyamdas03@gmail.com.

## When to Send

### Trade Executed
Send immediately after order fill. Use `mcp__claude_ai_Gmail__create_draft` or send directly.

Subject: `[Bull] Trade: {SIDE} {QTY} {SYMBOL} @ {PRICE}`
Body:
```
Trade Executed:
- {SIDE} {QTY} {SYMBOL} @ ${PRICE}
- Signal: {which factor triggered}
- Data: {key data points with values}
- Source: {Alpaca / WebSearch}
- Risk: {counter-arguments}

Current Portfolio:
- Total Value: ${TOTAL}
- Cash: ${CASH}
- Positions: {count}
```

### Daily Summary (Market Close)
Subject: `[Bull] Daily Summary — {DATE}`
Body:
```
Daily Performance:
- Portfolio Value: ${VALUE}
- Day P&L: ${PL} ({PCT}%)
- Open Positions: {count}

Position Details:
| Symbol | Qty | Entry | Current | P/L |
|--------|-----|-------|---------|-----|
| ... | ... | ... | ... | ... |

Top Movers Today:
- Gainers: {list}
- Losers: {list}

Tomorrow's Watch:
- {any pre-planned actions}
```

### Weekly Review (Friday)
Subject: `[Bull] Weekly Review — Week of {DATE}`
Body:
```
Weekly Performance:
- Portfolio Return: {pct}%
- S&P 500 Return: {sp_pct}%
- Alpha: {alpha}%

Top Trades This Week:
1. {best trade}
2. {second best}

Worst Trades This Week:
1. {worst trade}

Strategy Adjustments:
- {any changes}

Next Week Focus:
- {plans}
```

### Urgent Alerts
Subject: `[Bull] URGENT: {issue}`
Body: Brief description of anomaly, drawdown, or circuit breaker.

## Gmail MCP Usage
- Use `mcp__claude_ai_Gmail__create_draft` to draft the email
- Send to: satyamdas03@gmail.com
- Always include [Bull] prefix in subject for filtering