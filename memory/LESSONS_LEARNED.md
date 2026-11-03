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

## Session: 2026-11-03 (Pre-Market, after 6-month gap)

19. **Session continuity is a real operational risk.** A 6-month gap with no active trading sessions means: stops expired, positions unprotected, data stale. The CRON jobs were session-only and died with the original session. **LESSON: Implement persistent scheduling (not session-only CRONs) for a 24/7 trading agent.**

20. **GTC stop-loss orders expire.** Orders set with "GTC, expire 7/22" actually expired July 22, 2026. All three stops on XLV/XLE/GLD are gone. Without live monitoring, this creates unmanaged tail risk. **LESSON: Always re-check stop status at every routine. Reset stops to GTC with distant expiry (1 year) when possible.**

21. **Defensive positions in Late Cycle are still appropriate.** Even after a 5.7% S&P rally, our portfolio of XLV/XLE/GLD is likely up (GLD surged massively from gold's run past $4,000-5,000/oz). The XLE Hormuz thesis ran throughout 2026. Defensive positioning with the right catalysts can outperform.

22. **Oil inflation forces Fed reversal.** The Hormuz supply disruption sustained oil at $95-110+ throughout 2026, keeping inflation elevated, which caused the Fed to reverse from 2025 cuts and now signal rate hikes. This has cascading effects: BEARISH for growth stocks, BULLISH for value/energy/financials.

23. **US military escalation (Qeshm strikes) is qualitatively different from IRGC piracy.** When the US military directly strikes Iranian territory, the probability of Iran retaliation is high — but so is the probability of a negotiated settlement. This is actually a potential de-escalation catalyst (forcing Iran to the table) or a severe escalation risk. Watch closely.

24. **Midterm elections follow a reliable market pattern.** Historically (since 1950): average +15.4% in the 12 months AFTER midterm elections, 0% negative years. After results are known (regardless of outcome), market typically rallies. The uncertainty itself is the drag.

25. **AMD/chips is the momentum play for Late Cycle AI wave.** Even in Late Cycle/Stress, AI chip demand (AMD, NVDA, AVGO, MU) has been a secular growth story immune to macro headwinds. Monitor AMD tonight for potential momentum entry.

---

## Rules
- Document what worked and what didn't
- Note any patterns observed across sessions
- Track strategy adjustments and their outcomes