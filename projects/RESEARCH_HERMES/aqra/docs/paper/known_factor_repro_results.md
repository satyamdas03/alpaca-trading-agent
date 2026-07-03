# Known-Factor Reproduction (real data)

Window 2012-01-01 to 2024-12-31, holding period 21d, costs 10.0bps on turnover, cross-sectional dollar-neutral long-short, survivorship-bias-free S&P 500 universe.

Universe membership (survivorship-bias-free constituency intervals) is
enforced; without it, post-delisting ticker-reuse garbage flips momentum
to Sharpe -0.83 (documented in the paper's data-integrity section).

| Factor | Sharpe | IC | MaxDD | Ann.Turnover | Expected Sharpe range | Consistent | Reference |
|---|---|---|---|---|---|---|---|
| 12-1 Momentum | -0.093 | 0.0087 | -0.27 | 4.97 | [-0.5, 0.5] | YES | Jegadeesh & Titman (1993); McLean & Pontiff (2016) decay |
| Value Composite | 0.017 | -0.0027 | -0.168 | 2.91 | [-0.3, 0.5] | YES | Fama & French (1992); value winter 2012-2020 |
| Quality | 0.744 | 0.0533 | -0.23 | 1.1 | [0.0, 1.5] | YES | Novy-Marx (2013) |
| Low Volatility | -0.405 | -0.0138 | -0.374 | 4.33 | [-1.0, 0.2] | YES | Ang et al. (2006); Frazzini & Pedersen (2014) — raw carries beta drag |
