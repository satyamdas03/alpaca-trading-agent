# Lessons Learned

## Session: 2026-04-22 (Pre-Open Assessment)

1. **Ceasefire extensions can flip regime overnight.** Trump went from "bombing" to "indefinite extension" in hours. Oil jumped $4 on the news. Always check regime BEFORE trading, not from yesterday's notes.

2. **VIX >25 = Stress, not Late Cycle.** Previous sessions called this "Late Cycle leaning Stress." With Hormuz closed and VIX confirmed >25, this is full Stress. Call it what it is.

3. **Two days, zero trades = unacceptable.** Backtesting engine and MCP verification are done. No more excuses. Tomorrow we trade.

4. **Iran/Hormuz is the dominant macro driver.** Everything else (earnings, Fed) is secondary. Oil and VIX move in lockstep. Trade the regime, not individual stocks.

5. **TSLA earnings = binary event.** Don't pre-position. Wait for results, then decide.

5. **IRGC ship seizures change the Hormuz calculus.** Commercial vessels being actively attacked and seized is escalation beyond just "blockade." Oil risk is higher than VIX implies — VIX dropped on ceasefire headline but fundamentals unchanged.

6. **TSLA earnings = pure binary risk.** P/E of 235 means miss = big drop, beat = big pop. Don't size large either direction. If trading, keep to $3-5K max.

7. **Day orders + paper trading = no partial fill risk.** But always verify fills at open before planning next moves.

7. **Day orders + paper trading = no partial fill risk.** But always verify fills at open before planning next moves.

8. **TSLA EPS beat ≠ clean buy signal.** EPS beat $0.41 vs $0.37 but revenue miss + spending shock erased after-hours gains. Mixed signals = no trade. Wait for clean directional catalyst.

9. **Stop-losses can block trailing stops.** Alpaca holds shares for stop orders, so you can't place a trailing stop on the same shares. Solution: cancel stop-loss, place trailing stop when position appreciates enough to justify it.

10. **Defensive positions lag in relief rallies.** SPY +1.03% on 4/22, our portfolio -0.04%. That's the cost of Stress-regime positioning. Don't chase — regime hadn't shifted to Risk-On yet.

11. **VIX regime shifts can be deceptive.** VIX crashed to ~17.48 (Risk-On) but Hormuz still closed, oil >$100, IRGC seizing ships. VIX reflects ceasefire headline, not Hormuz reality. Don't blindly shift to momentum just because VIX < 20. Use HYBRID approach when macro and VIX disagree.

12. **Alpaca MCP can disconnect.** REST API with direct keys works as fallback. Always have API keys accessible for curl-based recovery.

## Session: 2026-04-23 (Market Close)

13. **Regime timing is everything.** Opened positions in Stress regime, but market shifted to Risk-On within 24 hours. Defensive positions now significantly lagging S&P (+1.05% day vs our -0.01%). Entry regime ≠ current regime — must adapt positions to current regime.

14. **80% cash in Risk-On = massive opportunity cost.** S&P up +1.05%, Nasdaq +1.64% while we have $80K sitting idle. In Risk-On, at minimum deploy 40-50% capital. 20% is too conservative.

15. **XLE is the one position working.** Oil tailwind from Hormuz is real and persistent. XLE +0.54% while XLV flat and GLD underwater. When regime and position thesis align, that's the winner.

16. **GLD entry was too high.** Bought at $435.66 (near peak). Gold pulled back to $433.43. Entry timing matters — even for safe havens, buy on dips not on spikes.

17. **Hormuz escalation is accelerating, not resolving.** IRGC seized 2 more ships. Oil jumped 4% in a day. The "ceasefire" is purely symbolic — actual military actions are escalating. Market ignoring this at its peril. Our XLE position benefits, but we need contingency plans for sudden resolution (oil crash scenario).

18. **Boeing beat earnings significantly** — loss of ($0.20) vs ($0.83) expected, record backlog. BA +5.53%. Missed opportunity — we should have had BA on watchlist given Hormuz/oil impact on airlines (contrarian: BA benefits from resolution, not escalation).

---

## Session: 2026-11-13 (Pre-Market)

19. **GTC stop-loss orders have expiration dates — always check.** The April 2026 stops were set GTC "expire 7/22." They expired July 22, 2026, leaving positions unprotected for 4+ months. For every new position, explicitly track stop expiration dates in TRADE_LOG.md and set a calendar reminder to renew.

20. **A 7-month data gap is catastrophic for an autonomous agent.** CRON jobs are session-only (expire 7 days). Without persistent scheduling infrastructure, the agent goes dark for months. Must implement persistent scheduling outside of Claude sessions — Windows Task Scheduler, cloud triggers, or GitHub Actions.

21. **Alpaca REST can be blocked by session proxy.** Even with valid API keys, paper-api.alpaca.markets is blocked in this cloud session's proxy config. Need to test API access at the start of each new session and have a fallback (web dashboard manual check).

22. **Gmail MCP failure = silent notification blackout.** No email = owner doesn't know the agent ran. Need secondary notification channel (PushNotification tool, GitHub commit as indicator).

23. **When you can't verify positions, estimate from public ETF data.** XLV NAV from SSGA, XLE/GLD from ETFdb, provide directional sense even without broker access. The estimates here (XLV ~$189, XLE ~$88) suggest strong unrealized gains — urgency to protect them.

24. **Inflation surprise (CPI +0.3% vs +0.2%) + high yields (5.103%) = Late Cycle, not Risk-On.** Even with VIX below 20, the macro fundamentals point to Late Cycle regime. Don't blindly follow VIX — weight macro fundamentals equally.

25. **CEO scandal at a key holding is a major systemic risk.** Nvidia CEO probe affects the entire AI/tech sector. Even if we're not holding NVDA, it suppresses XLK and growth ETFs. In Late Cycle, avoid concentration in scandal-affected names.

26. **Post-earnings is safer than pre-earnings for binary plays.** NVDA reporting Nov 17 with CEO probe ongoing = maximum uncertainty. Wait for the print, then trade the direction.

## Rules
- Document what worked and what didn't
- Note any patterns observed across sessions
- Track strategy adjustments and their outcomes