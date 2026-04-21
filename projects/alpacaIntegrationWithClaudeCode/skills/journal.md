# Journal Skill

## Purpose
Update memory files before each session ends. This is how the stateless agent persists knowledge.

## Update Protocol

### Every Routine Run
1. **PORTFOLIO_STATE.md** — Update with current:
   - Cash balance (from `get_account_info`)
   - Position list (from `get_all_positions`)
   - Portfolio value and P/L
   - Last-updated timestamp

2. **Git commit and push:**
   ```bash
   git add memory/
   git commit -m "bull: {routine_name} {date}"
   git push origin main
   ```

### On Trade Execution
1. **TRADE_LOG.md** — Add new row:
   ```
   | 2026-04-21 09:35 | AAPL | BUY | 50 | $182.45 | Momentum +14.2% vs SPX | Filled |
   ```

### After Research Session
1. **RESEARCH_LOG.md** — Add session entry:
   ```
   ## Pre-Market 2026-04-21
   - Regime: Risk-On (VIX 16.2, SPX above 200MA)
   - Candidates: AAPL, MSFT, NVDA, GOOGL, AMZN
   - Top Pick: AAPL (composite 8.4/10)
   - Key Data: {cited data points}
   ```

### Weekly Review
1. **LESSONS_LEARNED.md** — Add observations
2. **WEEKLY_REVIEW.md** — Fill in weekly template
3. **STRATEGY.md** — Update if strategy changes are warranted

## File Format Rules
- Always append to logs, never overwrite
- Use consistent date format: YYYY-MM-DD HH:MM
- Keep files under 200 lines (prune old entries when needed)
- Include timestamps on every update