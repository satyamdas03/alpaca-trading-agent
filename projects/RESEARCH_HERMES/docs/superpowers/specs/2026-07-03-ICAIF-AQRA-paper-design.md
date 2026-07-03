# Design: AQRA → ICAIF '26 submission (30-day sprint)

**Date:** 2026-07-03
**Deadline:** Aug 2, 2026 23:59 AoE (paper), ICAIF '26, Milan (Nov 14-17, in-person presentation required)
**Status:** Approved (user directed pivot; autonomous execution authorized)

## Target

Paper: **"AQRA: An Autonomous Conformal Agent for Quantitative Strategy Discovery"**
Venue fit: AI Agents & RL / Trading & Asset Management / Trustworthy & Responsible AI.
Format: 8 pages ACM sigconf, double-blind, no supplementary material, CMT submission.

## Thesis of the paper

An autonomous agent that discovers, certifies, adversarially reviews, and live-deploys
equity strategies — where every claim carries a statistical guarantee (per-lane conformal
p-values + Benjamini-Yekutieli FDR control) and every strategy survives an adversarial LLM
review chamber before touching (paper) capital. The contribution is the closed trustworthy
loop, not the alpha: the system's willingness to reject candidates (placebo tests) is a
headline result.

## What exists (Phase 1a, commit 01f7464, 29 tests green)

Dual-lane architecture (S structural / I informational), DuckDB store, feature builders with
PITGuard, walk-forward backtests with costs, conformal validator + BY FDR, lane certifiers,
BEAR chamber (mock + Anthropic modes), registry + regime allocator, Alpaca gate/monitor,
Typer CLI, synthetic end-to-end integration test, paper skeleton.

## Gaps to close for the paper (priority order)

1. **Historical S&P 500 constituents** (survivorship-bias-free universe). Source: Wikipedia
   current list + "Selected changes" table parsed back to ~2005; store constituency intervals
   in DuckDB; universe.at_date(date) becomes real.
2. **Real data at scale**: yfinance OHLCV for all historical constituents 2005-2026 (remove
   the 10-ticker cap; batch download; cache).
3. **Real fundamentals for Lane S value/quality**: EDGAR XBRL company facts (free, keyless
   except User-Agent) → P/E, P/B, gross margin, accruals. FMP fallback where keys exist.
4. **Known-factor reproduction** (momentum, value, quality sign + magnitude) — validation
   gate for the pipeline; fills the notebook with real numbers.
5. **Full pipeline run**: candidate library → backtests → conformal + BY within lane →
   certifiers → BEAR (LLM mode) → registry → allocation. Report certified set.
6. **Placebo + regime stress**: shuffled labels must certify zero strategies; report
   regime-conditional Sharpe (2008, 2020, 2022 windows).
7. **Live paper deployment** (start IMMEDIATELY for maximal live window before Aug 2):
   deploy top certified strategies on Alpaca paper with lane budgets + kill switches;
   daily monitor cron; git-tracked memory logs as audit trail. Requires ALPACA_API_KEY /
   ALPACA_SECRET_KEY in env — flag to user if missing.
8. **Paper writing**: ACM sigconf 8p from the existing skeleton; anonymized repo for
   double-blind; arXiv preprint after acceptance decision (allowed, uncited).

## Explicit non-goals (out of scope for this paper)

India market, options/crypto, genetic-programming symbolic discovery, real money, the C_42
work (separate math track), NeuralQuant integration.

## Schedule (deadline Aug 2)

- Jul 3-9: gaps 1-3 (data). Deploy live by Jul 9 at latest (gap 7 start) → 3.4 weeks live.
- Jul 10-16: gaps 4-6 (experiments).
- Jul 17-24: results freeze, gap 8 writing.
- Jul 25-31: adversarial internal review (BEAR the paper itself + codex review), polish.
- Aug 1: submit (buffer for CMT issues).

## Amendment A1 (2026-07-03, CEO review): LLM-generated candidates

Landscape review (FactorMAD ICAIF'25, QuantaAlpha, AlphaCrafter, QRAFTI) shows LLM
factor-mining is crowded but statistically unaccountable. AQRA's differentiator becomes
a generation layer feeding the existing gate — "agent proposes, statistics disposes":

- **Constrained signal DSL** (`aqra/signals/dsl.py`): JSON AST over whitelisted
  primitives (rank, zscore, ts_mean, delta, ratio, lag) and PIT features only;
  lookahead impossible by construction; schema validator rejects everything else.
- **LLM generator** (`aqra/generate/llm_generator.py`): Anthropic API proposes
  candidates from the feature catalog + train-window-only accept/reject stats.
  Never sees validation-window results. Mock mode for tests.
- **Trials ledger** (`aqra/generate/ledger.py`): every candidate registered in DuckDB
  BEFORE evaluation; BY-FDR corrects across the full ledger, not survivors. The
  ledger is the paper's honest-accounting headline artifact.
- Placebo protocol extends to generated candidates (shuffled labels must certify 0).

Paper title updated: "AQRA: An Autonomous Conformal Agent that Proposes, Certifies,
and Deploys Trading Strategies". Gaps renumbered: generation layer becomes gap 4.5,
after known-factor reproduction, before full pipeline run. Schedule absorbs it in the
Jul 10-16 experiments week. Full review record:
`~/.gstack/projects/satyamdas03-alpaca-trading-agent/ceo-plans/2026-07-03-icaif-aqra-llm-candidates.md`

## Risks

- Real-data certification may reject most/all candidates → reframed as trustworthiness
  result (placebo + honest FDR); paper stands on the method + live audit trail.
- Alpaca keys absent → live section shrinks to deployment-gate design + dry-run; ask user
  for keys early.
- 8-page limit → aggressive appendix-free writing; architecture diagram compressed.
- In-person Milan attendance + visa lead time — user action item, flag early.

## Success criteria

Submitted by Aug 2 with: real-data certified strategy table (or honest empty set + placebo),
known-factor reproduction, live paper-trading audit trail (≥3 weeks), and full
reproducibility (single make target).
