# Adversarial Self-Review — draft v1 vs artifacts (2026-07-04)

## Number verification (draft + main.tex vs JSON artifacts)

| Claim | Artifact value | Draft | Verdict |
|---|---|---|---|
| Momentum Sharpe/IC/turnover/MaxDD | -0.093 / +0.0087 / 4.97 / -0.27 | -0.09 / +0.009 / 5.0x / -0.27 | OK (rounding) |
| Value | +0.017 / -0.0027 / 2.91 / -0.168 | +0.02 / -0.003 / 2.9x / -0.17 | OK |
| Quality | +0.744 / +0.0533 / 1.1 / -0.23 | +0.74 / +0.053 / 1.1x / -0.23 | OK |
| Low-vol | -0.405 / -0.0138 / 4.33 / -0.374 | -0.41 / -0.014 / 4.3x / -0.37 | OK |
| Pipeline certified | 0/14; 3 EVAL_EMPTY; 6 library + 8 generated | same | OK |
| Quality train→val | 1.199 → 0.336, p=0.20569 | 1.20 → 0.34, p=0.21 | OK |
| Placebo certified | 0/18 | 0/18 | OK |
| **Placebo mean p** | **0.906** | **0.92** | **FIXED → 0.91** |
| Regime table | matches placebo_regime_results.json | same | OK |
| Fundamentals coverage | 43.6% / 11.0% | ~44% / ~11% | OK |
| Membership intervals | 897 / 874 tickers | same | OK |
| Momentum garbage flip | -0.093 clean vs -0.83 corrupted | -0.09 → -0.83 | OK |
| **PTV timeline** | Pactiv acquired 2010, garbage 2016 | "five years after" | **FIXED → six** |

## Overclaim fixes applied

1. "**immutable** trials ledger" (abstract, intro): rows transition status via
   UPDATE (never deleted, registration row persists) — "immutable" is stronger
   than the implementation. → "persistent trials ledger" + intro sentence
   about append-style discipline unchanged (accurate).
2. Abstract "we release the full pipeline, ledger, **and live paper-trading
   audit trail**": live deployment is pending (blocked on credential
   rotation). → abstract now promises pipeline + ledger; audit trail promised
   in Section 7 conditional on deployment before submission.

## Double-blind / anonymization checklist (for artifact repo)

- [ ] `src/aqra/data/universe.py` `HEADERS` User-Agent contains the author's
      real email — MUST be replaced with a neutral string in the anonymized repo.
- [ ] `aqra_paper_skeleton.md` contains author name — exclude from artifact
      or scrub (draft.md and main.tex are clean).
- [ ] pyproject/git metadata: strip author fields, git history NOT included
      (export snapshot, not clone).
- [ ] memory/ logs may contain identifying paths — exclude from artifact.
- [ ] README badges/links to personal accounts — check before export.

## Deferred (acceptable for submission)

- t-test proxy vs conformal p-value unification — disclosed in Limitations.
- BEAR mock mode for headline — disclosed; LLM mode goes to Appendix A after
  key rotation.
- QuantaAlpha bib truncated to first 5 authors + "and others" (24 listed on
  arXiv) — ACM style accepts et al.
