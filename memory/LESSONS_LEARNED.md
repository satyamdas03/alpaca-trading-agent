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

## Session: 2026-10-29 (Pre-Market — 6-Month Gap Recovery)

19. **Stop-loss GTC orders expire — always check their duration.** Stop-losses set on 4/23 with GTC and "expire 7/22" literally expired July 22, 2026. Positions went unprotected for 3 months. LESSON: When setting stop orders, note the expiration date and create a calendar reminder or cron to reset them before expiry.

20. **Hormuz crisis is a multi-month trade, not a day trade.** The XLE position entered at $56.42 in April with oil at $90-93. Oil climbed to $126 before pulling back to $101-108 in October. That's a 6-month sustained thesis. Don't take profits too early on geopolitical commodity plays.

21. **6-month data gap = flying blind.** Waking up after 6 months with no updates means uncertainty about: (a) exact portfolio values, (b) whether stop-losses fired, (c) actual P&L. Always verify positions via Alpaca portal when Alpaca MCP is unavailable. Never assume state from 6 months ago is still current.

22. **80% cash in a 6-month bull run = catastrophic underperformance.** S&P went from 7,137 to 7,844 (+9.9% peak) during April-August 2026. Our 80% cash position meant we captured only ~20% of the rally in our positions. This was the right call in April (Stress regime), but we failed to redeploy as regime shifted to Risk-On in May-August.

23. **Regime transitions require proactive monitoring.** Stress → Risk-On transition happened in late April/May 2026, but we never redeployed capital during the bull run. The pre-market routine fires are the mechanism for this — they failed to fire consistently, or we failed to adapt when they did.

24. **Trump renewed strike threats = binary oil event.** October 24 news: Trump hinting at renewed strikes on Iran. This is a new escalation. If strikes happen: (a) oil spike to $120-130+, XLE rockets, (b) market sells off (VIX spike), (c) GLD could go either way. Prepare contingency orders.

25. **Stagflation is the hardest regime.** Q3 2026 GDP at 1.4% + Core PCE 3.1% + 10Y >5% = stagflation. This is the worst regime for equities: bonds hurt from inflation, equities hurt from slow growth. Only winners: commodities (oil, gold), short-duration assets. Our XLE + GLD is the right positioning.

---

## Rules
- Document what worked and what didn't
- Note any patterns observed across sessions
- Track strategy adjustments and their outcomes