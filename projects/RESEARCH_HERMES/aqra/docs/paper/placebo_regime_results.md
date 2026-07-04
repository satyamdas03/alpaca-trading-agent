# Placebo + Regime Stress

## Placebo (18 trials, 3 seeds x 6 candidates, validation window)

**Certified placebo strategies: 0 (must be 0).**

| Candidate | Seed | Sharpe | p | FDR | Cert |
|---|---|---|---|---|---|
| S_MOM_12_1 | 11 | -0.226 | 0.70988 | False | REJECTED |
| S_VALUE | 11 | -1.349 | 0.99951 | False | REJECTED |
| S_QUALITY | 11 | -0.728 | 0.96244 | False | REJECTED |
| S_LOW_VOL | 11 | -1.185 | 0.99811 | False | REJECTED |
| I_GAP | 11 | -3.148 | 1.0 | False | REJECTED |
| I_VOLUME | 11 | -3.859 | 1.0 | False | REJECTED |
| S_MOM_12_1 | 23 | 0.254 | 0.26736 | False | REJECTED |
| S_VALUE | 23 | -0.233 | 0.71608 | False | REJECTED |
| S_QUALITY | 23 | -0.61 | 0.9322 | False | REJECTED |
| S_LOW_VOL | 23 | -0.777 | 0.97128 | False | REJECTED |
| I_GAP | 23 | -3.199 | 1.0 | False | REJECTED |
| I_VOLUME | 23 | -3.254 | 1.0 | False | REJECTED |
| S_MOM_12_1 | 47 | -1.207 | 0.99841 | False | REJECTED |
| S_VALUE | 47 | -0.869 | 0.9832 | False | REJECTED |
| S_QUALITY | 47 | -0.29 | 0.76101 | False | REJECTED |
| S_LOW_VOL | 47 | -1.158 | 0.99767 | False | REJECTED |
| I_GAP | 47 | -3.552 | 1.0 | False | REJECTED |
| I_VOLUME | 47 | -3.587 | 1.0 | False | REJECTED |

## Regime-conditional Sharpe (library candidates)

Data horizon starts 2010 — 2008 GFC not coverable; windows: 2011 downgrade H2, 2020 COVID, 2022 bear.

| Candidate | Lane | 2011 H2 | 2020 | 2022 |
|---|---|---|---|---|
| S_MOM_12_1 | S | -0.975 | -0.372 | 0.206 |
| S_VALUE | S | 0.814 | -0.19 | 0.337 |
| S_QUALITY | S | -1.707 | 0.038 | -0.88 |
| S_LOW_VOL | S | 0.903 | -0.77 | 0.406 |
| I_GAP | I | 1.073 | -1.834 | 0.775 |
| I_VOLUME | I | -2.491 | -3.341 | -1.635 |
