# AQRA Full Pipeline Run

Run 2026-07-04 | train 2012-01-01..2018-12-31 | validation 2019-01-01..2024-12-31 | generation: mock | BY-FDR alpha 0.20 over the FULL trials ledger (14 trials).

**Certified: 0 / 14 evaluated candidates.**

| ID | Lane | Source | Formula | Train Sharpe | Val Sharpe | p | FDR | Cert | BEAR | Rejection |
|---|---|---|---|---|---|---|---|---|---|---|
| S_MOM_12_1 | S | library | `rank(mom_12_1)` | 0.025 | -0.209 | 0.6958 | False | REJECTED | True | Failed FDR selection; Sharpe below 0.6; Drawdown exceeds 20%; Turnover exceeds Lane S cap; Coverage below target |
| S_VALUE | S | library | `rank(add(pe_rank, pb_rank))` | 0.059 | -0.074 | 0.57168 | False | REJECTED | True | Failed FDR selection; Sharpe below 0.6; Turnover exceeds Lane S cap; Coverage below target |
| S_QUALITY | S | library | `rank(quality_score)` | 1.199 | 0.336 | 0.20569 | False | REJECTED | True | Failed FDR selection; Sharpe below 0.6; Drawdown exceeds 20%; Turnover exceeds Lane S cap |
| S_LOW_VOL | S | library | `rank(low_vol_score)` | -0.251 | -0.574 | 0.91965 | False | REJECTED | True | Failed FDR selection; Sharpe below 0.6; Drawdown exceeds 20%; Turnover exceeds Lane S cap; Coverage below target |
| I_GAP | I | library | `rank(overnight_gap)` | -1.045 | -0.96 | 0.99052 | False | REJECTED | False | Failed FDR selection; Coverage below target |
| I_VOLUME | I | library | `rank(volume_zscore)` | -2.342 | -1.688 | 0.99998 | False | REJECTED | False | Failed FDR selection; Half-life below 2 days; Turnover exceeds Lane I cap; Coverage below target |
| GEN_S_6ae4b1e5 | S | mock | `rank(insider_score)` | 0.046 | 0.089 | 0.41407 | False | REJECTED | True | Failed FDR selection; Sharpe below 0.6; Drawdown exceeds 20%; Turnover exceeds Lane S cap; Coverage below target |
| GEN_S_2fdbcf51 | S | mock | `sub(rank(insider_score), rank(quality_score))` | -1.227 | -0.37 | 0.8176 | False | REJECTED | True | Failed FDR selection; Sharpe below 0.6; Drawdown exceeds 20%; Turnover exceeds Lane S cap |
| GEN_S_5c181b91 | S | mock | `zscore(ts_mean(low_vol_score, 21))` | -0.178 | -0.546 | 0.90783 | False | REJECTED | True | Failed FDR selection; Sharpe below 0.6; Drawdown exceeds 20%; Turnover exceeds Lane S cap; Coverage below target |
| GEN_S_0ddeded2 | S | mock | `neg(delta(insider_score, 5))` | - | - | - | - | EVAL_EMPTY | - |  |
| GEN_I_c7f0e00b | I | mock | `rank(earnings_surprise)` | -0.432 | -0.009 | 0.50878 | False | REJECTED | False | Failed FDR selection; Coverage below target |
| GEN_I_c953460e | I | mock | `sub(rank(earnings_surprise), rank(volume_zscore))` | -2.934 | -2.412 | 1.0 | False | REJECTED | False | Failed FDR selection; Half-life below 2 days; Turnover exceeds Lane I cap |
| GEN_I_ef5a26fa | I | mock | `zscore(ts_mean(insider_event_score, 21))` | - | - | - | - | EVAL_EMPTY | - |  |
| GEN_I_801fb79f | I | mock | `neg(delta(earnings_surprise, 5))` | - | - | - | - | EVAL_EMPTY | - |  |
