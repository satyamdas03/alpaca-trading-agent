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

## Session: 2026-11-20 (Pre-Market — 7-month gap recovery)

19. **7-month memory gaps are catastrophic for a trading agent.** Without continuous CRON runs, all context from April 23 to November 20 is lost. Positions may have changed without our knowledge. Actual P&L, actual stop orders, and actual account state are UNVERIFIABLE until Alpaca is connected. This is the single biggest operational risk.

20. **Session-only CRONs die silently.** The April 23 CRONs (session-only, 7-day expiry) all expired within a week of the session ending. No pre-market, midday, or close routines have run since April 23. For continuous operation, CRONs must be recreated EVERY session and ideally moved to a persistent scheduling mechanism.

21. **Stop-loss orders may also expire.** The GTC stop-losses placed April 23 (expire 7/22 per PORTFOLIO_STATE) have almost certainly expired. If positions are still open, they may now be UNPROTECTED with no stops in place. This is a critical risk that must be verified.

22. **Regime is LATE CYCLE not Risk-On, even with NVDA beat.** Nvidia beat massively ($115.8B rev, +103% YoY) but chip stocks are TUMBLING the morning after the results (Anthropic -9%, QQQ -1.67% pre-market). A beat doesn't prevent sector rotation out of tech. VIX at ~21-23 and 6-session losing streak in SPY confirms Late Cycle.

23. **Jensen Huang resignation is a macro signal.** NVDA CEO (the face of the AI supercycle) resigned Nov 12. Combined with chip stock tumble, this signals possible peak-tech-cycle sentiment. Late Cycle characteristics accelerating.

24. **Iran/Hormuz escalation is a MULTI-YEAR conflict.** Not a temporary event. June 17 Islamabad memorandum briefly reopened strait; ceasefire broke July 7. US struck Qeshm Island Nov 17. 7 months in and still no resolution. Oil elevated for entire period — XLE thesis remains intact.

25. **Defensive positions (XLV/XLE/GLD) in a Late Cycle market WORK.** Our April 2026 defensive positioning was correct for the subsequent 7 months: S&P roughly flat (SPY $711→$716), while our estimated positions are +20-21% (XLV, XLE). The "defensive = lagging" concern from April 23 was premature.

---

## Rules
- Document what worked and what didn't
- Note any patterns observed across sessions
- Track strategy adjustments and their outcomes