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

## Session: 2026-11-16 (Pre-Market, 7-Month Gap)

19. **GTC orders expire — always check stop-loss expiry.** Stop-loss orders were set GTC expire 7/22 (July 22). They have now expired. Positions are unprotected until stops are re-entered. Never set GTC without reviewing expiry dates. Lesson: Set recurring reminder to verify/re-enter stops monthly.

20. **Stale memory = stale regime.** Last session was April 23. Regime flipped from Risk-On to Late Cycle in the interim (VIX from 17 to 20, Fed from cutting to hiking, 4 consecutive weekly declines). Always assume context is stale and research fresh on every wakeup.

21. **XLV outperformed over 7 months (+27%)** despite being labeled a "wrong sector" in the April Risk-On environment. Healthcare is resilient in corrections. The initial Stress-regime entry rationale proved out over time — entry thesis can be right for wrong-term reasons.

22. **Hormuz improved dramatically (1 → 30 vessels/day) but is not resolved.** XLE thesis partially intact but oil is now $7 lower than entry. Oil at $90 WTI still historically elevated but thesis no longer as strong. Consider reducing XLE exposure if oil drops below $85.

23. **Fed regime flip changes everything.** April 2026 had Fed cutting. By September 2026, first rate hike in 3+ years. December 2026 hike expected. This is a major regime shift — rising rates hurt growth stocks, support defensives and cash. VIX rising from 16 to 20 reflects this.

24. **NVIDIA earnings binary event (±10.6% implied) = no position building day before.** The rule holds for large-cap market movers: never add new positions the day before a major earnings binary event that the whole market is watching.

25. **Hedge funds cutting AI risk at fastest pace in decade** (Nov 16, 2026) = institutional de-risking signal. When large sophisticated investors are cutting fast, momentum is broken. Wait for stabilization before buying dips in AI names.

## Rules
- Document what worked and what didn't
- Note any patterns observed across sessions
- Track strategy adjustments and their outcomes