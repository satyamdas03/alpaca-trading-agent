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

## Session: 2026-10-27 (Pre-Market — 6-Month Gap Recovery)

19. **GTC stop-loss expiry dates are critical risk.** Our stops were set to expire 7/22. In a 24/7 automated agent context, stops MUST be set for maximum duration (1 year) or be renewed proactively. A lapsed stop means no protection — exactly what happened with GLD falling to -12% with no exit.

20. **Cash drag in a bull market is the #1 performance killer.** S&P rallied +13% YTD while we held 80% cash. Even our best position (XLE +20.5%) couldn't compensate when it's only 7% of portfolio. In Risk-On regime, must deploy 40%+ capital.

21. **"Iran/Hormuz thesis" was correct directionally but wrong in magnitude.** XLE +20.5% from our $56.42 entry validates the energy thesis. But we sized it at 7% — too small to matter. When you have a high-conviction thesis (Hormuz = elevated oil), size appropriately: 15-20% of portfolio.

22. **A 6-month gap means total state loss.** Without daily/weekly updates to memory, strategy context degrades completely. This session required 30+ minutes of research just to reconstruct where we are. Recurring routines are critical — must maintain CRON schedule or find persistent scheduling solution.

23. **VIX complacency is real even in geopolitical crises.** VIX at 18.51 with WTI at $102 and Iran still blocking Hormuz shows markets normalize to prolonged crises. After 6 months, the "war premium" in oil is priced in but VIX no longer reflects the tail risk. This creates asymmetric risk: small probability of sudden resolution (oil crash -20%) or escalation (VIX spike +50%).

24. **The regime detection model needs a "chronic stress" category.** Our model has Risk-On/Late Cycle/Stress/Recovery — but doesn't account for a prolonged Stress situation that markets normalize over time. Hormuz blocked for 6+ months = elevated oil, but VIX has drifted back down. "Normalized Stress" = Late Cycle positioning with oil hedge (exactly what XLE gave us).

## Rules
- Document what worked and what didn't
- Note any patterns observed across sessions
- Track strategy adjustments and their outcomes