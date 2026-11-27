# Lessons Learned

## Session: 2026-11-27 (Pre-Market — 7-Month Gap Recovery)

19. **7-month session gaps leave the portfolio in an unknown state.** Stop-loss GTC orders expire after ~90 days on Alpaca. Positions could have stopped out, been closed by expiring orders, or grown significantly. ALWAYS check Alpaca live before any trade after a long gap. No assumptions.

20. **Nvidia governance events create non-linear index risk.** When a single stock (NVDA) causes the S&P 500 to swing ±4.7% in a day, sector diversification means less than it did. Watch credit watch events, CEO changes, and governance flags as early warning signals for index-level moves.

21. **Late Cycle rotation is a tradable signal.** When equal-weight S&P outperforms cap-weight for multiple sessions (best 3-day stretch since April 2025, Nov 23-25), it's a systematic signal that money is rotating from mega-cap momentum to value/cyclicals. XLF, XLI, and XLE are primary beneficiaries.

22. **Fed rate hike cycles are tradable with XLF.** A 97.8% probability Dec hike is effectively certain. Banks earn more on higher rates (NIM expansion). XLF is a direct, low-idiosyncratic-risk bet on rate hike certainty. This is a Late Cycle signal consistent with strategy.

23. **OPEC+ decisions are binary events for energy.** The Nov 29 OPEC ministerial meeting on 2027 framework is the same type of binary event as the Iran ceasefire deadlines. Wait for the outcome before deciding on XLE. Don't pre-position on speculation.

24. **Hormuz has partially recovered but remains a persistent tail risk.** From near-0% throughput in April to 49% in November — a 7-month partial recovery with ongoing incidents (sea mines Nov 25). The situation is not resolved; it's oscillating. Keep GLD as a hedge while this continues.

25. **Holiday-shortened sessions are not for new entries.** Black Friday (Nov 27) closes at 1 PM ET. Volume is thin, spreads are wide, fills are unreliable. The right call is to hold existing positions and prepare the Monday plan.

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
