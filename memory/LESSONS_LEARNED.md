# Lessons Learned

## Session: 2026-11-04 (Pre-Market — Resumption After 6-Month Gap)

19. **GTC stop-loss orders have expiration dates — must verify at every session.** The April 2026 stop-losses (XLV $136.46, XLE $52.47, GLD $405.17) were set GTC "expire 7/22." They expired July 22. Positions ran unprotected for 3+ months. For 6-month gains, this was lucky (not disciplined). ALWAYS set stop-losses at market open of each session and verify they're active.

20. **A 6-month silence is catastrophic for risk management.** 80% cash + no monitoring = no CRON reconnection = no stop-loss maintenance = pure luck that positions survived. Need truly persistent scheduling (not session-only CRONs) or accept that monitoring is manual. Cloud-based triggers or webhook-based approach needed.

21. **Defensive positions can become winners given enough time.** XLV entered as "defensive" in Stress regime at $146.73. 6 months later ~$185 = +26.4% gain. Healthcare is both defensive AND growth in a sustained geopolitical risk environment (hospital demand, drug demand). Don't dismiss defensive positions as "wrong for regime" — they can compound nicely.

22. **XLE is a double-edged sword when Hormuz peace approaches.** Hormuz deal progress = oil crash = XLE destruction. Bought XLE for Hormuz disruption thesis; that thesis is now potentially reversing (Iran says "ready to reopen"). Tight stop essential. If deal announced → exit immediately regardless of price.

23. **Midterm elections: uncertainty removal beats party identity.** Dow +2.1% on Democrat sweep is not about policy — it's about removing the uncertainty premium. Market priced in potential crisis scenarios; gridlock is better than policy uncertainty. Historical: S&P +13.7% avg in year after midterms, positive 91% of cases.

24. **AI government spending is the new mega-trend.** Palantir +96% revenue to $2.31B is extraordinary. Government AI contracts (DoD, intelligence) are growing exponentially. PLTR is the pure play. Missed this by sitting in defensive positioning since April.

25. **Narrow market breadth + record index = warning sign.** Goldman Sachs: 60% of S&P 500 stocks in bear market while index near records. This "mega-cap masking" phenomenon precedes corrections. Maintain higher cash in Late Cycle, don't chase the index.

26. **Never let positions run 6 months without review.** The gap between 4/23 and 11/4 is unacceptable. If the agent wakes up after a long gap, the FIRST actions are: (1) verify positions still open, (2) verify stop-losses active, (3) assess regime from scratch. Don't assume anything from memory.

---

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

## Rules
- Document what worked and what didn't
- Note any patterns observed across sessions
- Track strategy adjustments and their outcomes
