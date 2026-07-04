# AQRA: An Autonomous Conformal Agent that Proposes, Certifies, and Deploys Trading Strategies

**Target:** ICAIF '26, 8 pages ACM sigconf, double-blind.
**Status:** full draft v1, 2026-07-04. Live-trading section pending deployment.

---

## Abstract

Large language models are increasingly used to mine trading signals, yet the
resulting agents are statistically unaccountable: they propose hundreds of
hypotheses and report the survivors as if they were pre-specified. We present
AQRA, an autonomous research agent in which *the agent proposes and the
statistics dispose*. An LLM generates candidate signals in a constrained
domain-specific language whose grammar makes look-ahead impossible by
construction; every proposal — including malformed and failed ones — is
registered in an immutable trials ledger *before* evaluation; and
certification requires surviving a Benjamini–Yekutieli false-discovery-rate
correction applied over the full ledger, conformal coverage checks,
hard risk gates, and an adversarial LLM review chamber. On a
survivorship-bias-free S&P 500 universe (2010–2026), AQRA reproduces the
post-publication behavior of four canonical factors, and then certifies
**zero of fourteen** candidate strategies whose in-sample Sharpe ratios
reached 1.2 — because they failed to generalize out-of-sample. In placebo
runs with cross-sectionally permuted signals, the gate certifies **zero of
eighteen** impostors. We argue that a research agent's willingness to reject
its own candidates is the correct headline metric for trustworthy AI in
finance, and we release the full pipeline, ledger, and live paper-trading
audit trail for reproduction.

---

## 1. Introduction

Three failure modes dominate quantitative strategy research: confirmation
bias, multiple-testing abuse, and look-ahead leakage. LLM-based factor-mining
agents amplify all three: they generate hypotheses at unprecedented rate,
they are trained to please their operators, and nothing in their sampling
process respects point-in-time data availability. Recent systems
(FactorMAD, QuantaAlpha, AlphaCrafter, QRAFTI) demonstrate impressive
generation capability but report survivors without charging the search
process for its failures. Harvey, Liu and Zhu's admonition — that a newly
claimed factor should clear a t-statistic of 3.0 precisely because of the
unreported multiplicity behind it — applies with more force, not less, when
the researcher is a language model that can emit a thousand candidates per
hour.

AQRA (Autonomous Quantitative Research Agent) inverts the design. The
generative freedom of the LLM is preserved, but every route from idea to
capital passes through statistical machinery the model cannot negotiate
with:

1. **A constrained signal DSL.** Candidates are JSON abstract-syntax trees
   over whitelisted point-in-time features and operators. Time-series
   operators reach strictly backward; cross-sectional operators act within a
   single date. Look-ahead is a type error, not a reviewer finding.
2. **A trials ledger.** Every proposal is registered *before* evaluation.
   Malformed proposals and failed backtests stay on the books with p = 1.
   The Benjamini–Yekutieli correction runs over the entire ledger, so each
   additional attempt raises the bar for all of them. You cannot un-try a
   hypothesis.
3. **A train/validation wall.** The generator's feedback loop sees
   train-window statistics only. Validation-window results never reach the
   model, closing the leakage channel through which an LLM could overfit the
   held-out data across generations.
4. **Independent certification.** Survivors of FDR selection must clear
   conformal coverage checks, hard Sharpe/drawdown/turnover gates, and an
   adversarial LLM review chamber (BEAR) that hunts for look-ahead bias,
   data mining, and missing economic rationale.
5. **A live deployment gate.** Certified strategies deploy to paper trading
   with lane budgets, kill switches, and a git-tracked audit trail.

Our contribution is the closed trustworthy loop, not the alpha. Indeed, our
headline empirical results are refusals: on real data the full pipeline
certifies 0/14 candidates (the best of which reached in-sample Sharpe 1.20),
and 0/18 placebo impostors. We contend this is what an honest autonomous
researcher looks like on a decade of large-cap US equities with free data,
and that the ledger discipline — not the generation cleverness — is the
transferable idea.

## 2. Related Work

**LLM agents for factor mining.** FactorMAD (ICAIF '25) uses multi-agent
debate for interpretable alpha mining; QuantaAlpha evolves factor
populations; AlphaCrafter builds full-stack multi-agent trading pipelines;
QRAFTI orchestrates empirical research workflows. These systems evaluate
generated factors on held-out data but do not account for the number of
draws taken, and none maintain a pre-registration ledger. AQRA is
complementary: any of their generators could sit upstream of our gate.

**Multiple testing in finance.** Bailey and López de Prado formalized
backtest overfitting and the deflated Sharpe ratio; Harvey, Liu and Zhu
documented the multiplicity crisis in factor research; McLean and Pontiff
measured post-publication decay. Benjamini and Yekutieli's FDR procedure is
valid under arbitrary dependence, which matters because trading-strategy
p-values are strongly dependent. Our contribution is operational: the
correction is enforced over a ledger the agent cannot bypass, rather than
applied post hoc by a well-intentioned author.

**Conformal prediction** (Vovk et al.; Angelopoulos and Bates) provides
finite-sample, distribution-free coverage guarantees. We use split-conformal
intervals calibrated on the training window and report validation coverage
per candidate; coverage degradation itself becomes a certification signal
(Section 6.3).

**Pre-registration.** Our ledger is the algorithmic analogue of clinical
trial registries — the same instrument that reduced reported effect sizes in
medicine when outcome switching became visible.

## 3. The AQRA Architecture

### 3.1 Dual-lane design

| Lane | Sources | Horizon | Examples |
|---|---|---|---|
| S — structural | prices, fundamentals | 21 d | momentum, value, quality, low-vol |
| I — informational | prices, volume, events | 1–5 d | overnight gap, volume shock |

Lanes have independent feature tables, calibration, backtests, certifiers,
and turnover caps (Lane S: 1.0x annualized; Lane I: higher cap, half-life
floor of 2 days).

### 3.2 The signal DSL

Grammar (JSON AST):

```
leaf     := {"feature": f}                    f in whitelisted PIT features
unary    := {"op": u, "arg": AST}             u in {rank, zscore, neg, abs, sign}
ts       := {"op": t, "arg": AST, "window": w} t in {ts_mean, ts_std, delta, lag},
                                               1 <= w <= 252
binary   := {"op": b, "left": AST, "right": AST} b in {add, sub, mul, div, min, max}
```

Limits: depth ≤ 6, nodes ≤ 25. `rank`/`zscore` act cross-sectionally within
a date; `ts_*` operators act per ticker and reach strictly backward. Because
leaves are point-in-time features and no operator can reference the future,
**look-ahead is unrepresentable**. A property test mutates all feature
values after a cutoff date and asserts the signal before the cutoff is
bit-identical.

The hand-written factor library is itself expressed in the DSL, so library
and generated candidates share one evaluation path and one ledger.

### 3.3 The trials ledger

Lifecycle: `REGISTERED → {REJECTED_INVALID, REJECTED_EVAL, EVALUATED}`.
Registration precedes evaluation; the ledger API raises on any attempt to
record results for an unregistered trial. FDR selection queries the full
ledger; non-evaluated trials enter at p = 1.0. In our tests, a marginal
p = 0.03 candidate that survives BY correction alone is correctly killed
once 200 failed attempts join the ledger.

### 3.4 Generation with a train/validation wall

The generator (Anthropic Claude) receives the grammar, the feature
catalogue, and per-trial feedback consisting of *formula, status, train
Sharpe, train IC* — never validation numbers. The prompt states the FDR
consequence explicitly: "each weak idea you emit makes the statistical bar
higher for all of them." Malformed output is parsed defensively; unparseable
proposals are ledgered as `REJECTED_INVALID`. A deterministic mock mode
makes the entire pipeline reproducible without API access.

### 3.5 Certification stack

For each evaluated candidate: (i) one-sided t-test p-value on validation
daily returns (proxy for the conformal p-value; both reported);
(ii) BY-FDR at alpha = 0.20 over the full ledger; (iii) conformal coverage of
90% train-calibrated intervals on validation days; (iv) lane gates — Lane S:
Sharpe ≥ 0.6, max drawdown ≥ −20%, turnover ≤ 1.0x; Lane I: half-life ≥ 2 d,
turnover cap; (v) BEAR adversarial review (look-ahead, mining, lane
misclassification, economic rationale, robustness). Only candidates passing
all five stages receive a `CERTIFIED` dossier and reach the registry.

### 3.6 Backtest engine

Cross-sectional dollar-neutral long-short: signals are rank-demeaned into
weights with gross exposure 1 on each rebalance date and applied from the
next trading day; transaction costs (10 bps) are charged on turnover;
information coefficients are non-overlapping Spearman correlations at
rebalance dates. Universe membership is enforced point-in-time (Section 4).

## 4. Data and the Ticker-Reuse Hazard

Universe: historical S&P 500 constituency reconstructed from the index
change log (897 membership intervals across 874 tickers, 2010–2026);
prices via bulk OHLCV download; fundamentals from SEC EDGAR XBRL frames
(keyless, point-in-time `available_at` stamps).

**A data-integrity finding worth reporting.** Free price feeds resolve
tickers, not securities. After a constituent is delisted, its symbol is
frequently reassigned or its series degrades: in our feed, post-2013 "BMC"
prices belong to a different instrument trading near 22,700, and "PTV"
exhibits ±4,900% daily moves in 2016 — five years after Pactiv was acquired.
With naive backtests over all listed history, this garbage concentrates in
the short leg of momentum (delisted losers) and flips its Sharpe from
−0.09 to **−0.83**: a purely artifactual result that would survive casual
inspection because it *underestimates* performance rather than inflating it.
Enforcing constituency intervals as a point-in-time join removes every such
episode without any outlier winsorization. We suspect a nontrivial share of
published negative (and positive) results on free data carry this defect.

## 5. Known-Factor Reproduction

Validation gate for the pipeline: canonical factors must behave as the
*post-publication* literature says they behaved in a large-cap universe over
2012–2024 — not as their discovery papers say they behaved decades earlier.

| Factor | Sharpe | IC | MaxDD | Turnover | Expected range | Consistent |
|---|---|---|---|---|---|---|
| Momentum 12-1 | −0.09 | +0.009 | −0.27 | 5.0x | [−0.5, 0.5] | yes |
| Value (E/P+B/P) | +0.02 | −0.003 | −0.17 | 2.9x | [−0.3, 0.5] | yes |
| Quality (gross margin) | +0.74 | +0.053 | −0.23 | 1.1x | [0.0, 1.5] | yes |
| Low volatility (raw) | −0.41 | −0.014 | −0.37 | 4.3x | [−1.0, 0.2] | yes |

Momentum's flat performance reflects the documented post-2010 large-cap
decay and the 2016/2020–21 momentum crashes (visible in our regime table);
value's flatness is the "value winter"; raw dollar-neutral low-vol carries
negative beta drag in a bull decade (the anomaly is a beta-adjusted claim —
Frazzini–Pedersen). Quality is the era's robust survivor. 4/4 consistent.

## 6. The Gate at Work

### 6.1 Full pipeline run: an honest empty set

Six library candidates plus eight generated candidates (mock mode for the
headline run; LLM mode reported in the appendix) were registered, trained on
2012–2018, and validated on 2019–2024. Three generated candidates failed
evaluation (constant signals on placeholder features) and entered the ledger
at p = 1.

**Result: 0/14 certified.** The strongest candidate — quality — earned
train Sharpe 1.20 but validation Sharpe 0.34 (p = 0.21) and failed FDR
selection, the Sharpe floor, and the turnover cap. Every rejection reason is
recorded in the run artifact. A system tuned to please its operator would
have certified quality; the gate declined, and the train→validation collapse
in the very next column is why it was right to.

### 6.2 Placebo: the gate rejects impostors

Within-date cross-sectional permutation destroys the signal–return link
while preserving both marginals. Three seeds x six candidates on the
validation window: **0/18 certified**, mean placebo p = 0.92, no placebo
trial passes FDR. The pipeline does not manufacture significance from noise.

### 6.3 Conformal coverage as a regime instrument

Intervals calibrated on 2012–2018 achieve less than the nominal 90% coverage
on 2019–2024 for most candidates — the validation window contains the COVID
volatility regime. Rather than a failure, per-candidate coverage becomes a
certification input (coverage floor) and a deployed-strategy retirement
signal (rolling 30-day coverage).

### 6.4 Regime stress

| Candidate | 2011 H2 | 2020 | 2022 |
|---|---|---|---|
| Momentum | −0.98 | −0.37 | +0.21 |
| Value | +0.81 | −0.19 | +0.34 |
| Quality | −1.71 | +0.04 | −0.88 |
| Low-vol | +0.90 | −0.77 | +0.41 |
| Overnight gap | +1.07 | −1.83 | +0.78 |
| Volume shock | −2.49 | −3.34 | −1.64 |

Defensive factors bid in 2011/2022 drawdowns; momentum crashes in 2020 —
patterns matching the literature, from a pipeline that was never shown these
windows during construction. (2008 is outside the data horizon and reported
as such.)

## 7. Live Deployment

Certified strategies (currently: none — the registry honestly holds the
empty set) deploy through a gate enforcing paper-only trading, lane budgets,
daily loss limits, and drawdown kill switches; a monitor writes daily
git-committed logs (portfolio value, per-strategy P&L, rolling conformal
coverage, retirement events). *[Section to be completed with the N-week live
audit trail before submission; the gate design itself is part of the
artifact.]*

## 8. Limitations

(1) The t-test p-value is a proxy; full conformal p-values per candidate are
computed but the two are reported side-by-side rather than unified.
(2) Free fundamentals cover ~44% of ticker-days for valuation and ~11% for
quality — coverage bias toward larger, longer-listed firms. (3) BEAR runs in
mock mode for the headline results; LLM-mode reviews are reported in the
appendix. (4) Flat 10 bps costs; no market impact. (5) One decade, one
universe, long-only-short-only construction; the ledger discipline, not the
specific gates, is the claimed contribution. (6) Generated candidates in the
headline run use the deterministic mock generator for exact reproducibility;
the LLM-mode run (appendix) is stochastic by nature.

## 9. Reproducibility

Single-command pipeline: `make ingest && make repro && make pipeline &&
make placebo`. All artifacts (ledger, run reports, placebo tables) are
emitted as versioned JSON/markdown. Anonymized repository accompanies
submission; mock mode reproduces every headline number without API keys.

## 10. Conclusion

AQRA demonstrates that an LLM research agent can be made statistically
accountable without curtailing its generative freedom: constrain the
hypothesis language so look-ahead cannot be expressed, register every
attempt before evaluation, charge the whole ledger to every survivor, wall
off the validation data from the feedback loop, and let independent gates
dispose. On a decade of large-cap US equities with free data, the honest
answer was the empty set — delivered with the placebo evidence to prove the
gate can tell signal from noise, and a live audit trail to prove the loop
closes. We offer the trials ledger as the missing organ of LLM-driven
quantitative research.

---

## References (to be BibTeX'd)

- Angelopoulos & Bates (2021). Gentle introduction to conformal prediction.
- Bailey & López de Prado (2014). The deflated Sharpe ratio.
- Bailey, Borwein, López de Prado, Zhu (2016). The probability of backtest overfitting.
- Benjamini & Yekutieli (2001). FDR under dependency. Ann. Statist.
- Fama & French (1992). Cross-section of expected returns.
- Frazzini & Pedersen (2014). Betting against beta.
- Harvey, Liu & Zhu (2016). ...and the cross-section of expected returns.
- Jegadeesh & Titman (1993). Returns to buying winners.
- López de Prado (2018). Advances in Financial Machine Learning.
- McLean & Pontiff (2016). Does academic research destroy predictability?
- Novy-Marx (2013). The other side of value.
- FactorMAD (ICAIF '25); QuantaAlpha (2026); AlphaCrafter (2026); QRAFTI (2026).
  [full citations to be added]

## Appendix A: LLM-mode generation run
*[pending key rotation — will report: N proposals, invalid rate, ledger
growth, FDR threshold movement, any certified survivors]*

## Appendix B: BEAR prompts and review transcripts
*[LLM mode pending; mock rubric included in artifact]*
