# Fabius Fortuna — the markets & quant toolkit

Loaded on demand by `fabius-fortuna`. The sourced, license-honest stack (2026) for market/econ **data**, **backtesting**, **TA/quant/stats**, and HF **finance/time-series models**. Two standing rules: everything here **informs analysis and bounds risk — fortuna never gives personalized financial advice and never touches market-manipulation or auto-execution**; and forecasts are **probabilistic + backtested, never oracle**. Licenses are flagged honestly (`Apache/MIT/BSD` ship freely; **`AGPL`/`Commons-Clause`/`NC` = flagged**), and one supply-chain hazard is called out below.

## Data

| Source | License | Note |
|---|---|---|
| **yfinance** | Apache-2.0 | Key-free Yahoo prices/fundamentals — the default prototype feed. *Unofficial scrape — breaks without warning, not for production/redistribution.* |
| **fredapi** | Apache-2.0 | St. Louis Fed FRED/ALFRED macro series (GDP/CPI/rates, ~800k). The econ spine; **ALFRED vintages avoid look-ahead bias** in backtests. Free key. |
| **ccxt** | MIT | Unified API over 100+ crypto exchanges. *Live endpoints move money — analysis/risk only, never auto-execute.* |
| **OpenBB Platform** | ⚠️ **AGPL-3.0** | "Connect-once" normalizer over 100+ providers + agent-callable MCP server. *Network copyleft — review before embedding in a closed product.* |
| **Alpha Vantage** (MIT) · **Polygon/"Massive"** (MIT) | MIT | Contracted feeds when yfinance's fragility won't do. |

## Backtesting — the "does it actually work" engine

| Engine | License | Note |
|---|---|---|
| **NautilusTrader** | LGPL-3.0 | Rust-native, event-driven, **backtest=live parity** with look-ahead-safe fills — kills the overfit-then-fails gap. Steeper curve; most actively maintained. |
| **QuantConnect LEAN** | Apache-2.0 | Institutional multi-asset (equities/options/futures/FX/crypto) + corporate actions + documented path to live. Heavier setup. |
| **vectorbt** | ⚠️ **Commons Clause** | NumPy/Numba-vectorized — thousands of param combos in seconds, the *honest-statistics* many-trials engine. **Not OSI-open** (can't sell it as a service; PRO is paid). |
| **Zipline-reloaded** | Apache-2.0 | Maintained Zipline fork. *(backtrader is GPL-3.0 and effectively unmaintained since ~2021 — quick studies only.)* |

## TA · quant · stats

| Tool | License | Note |
|---|---|---|
| **TA-Lib** (ta-lib-python) | BSD-2 | 150+ industry-standard indicators + candlestick patterns. *Needs the native C lib installed first.* |
| **pandas-ta-classic** | MIT | 250+ pure-Python indicators, no C toolchain. ⚠️ **Supply-chain flag:** the original `twopirllc/pandas-ta` was **deleted, its PyPI wiped, and relaunched behind a paid license** (community flagged it attack-shaped) — **pin this MIT fork**, not the new paid "pandas-ta". |
| **QuantLib** | BSD-3 | Reference derivatives/fixed-income pricing, curves, Greeks (use `QuantLib-Python`). |
| **PyPortfolioOpt** | MIT | Mean-variance/efficient-frontier, Black-Litterman, HRP, shrinkage — the portfolio-construction + risk-first sizing layer. *Outputs inform, never advise.* |
| **statsmodels** | BSD-3 | Econometrics + classical time series (OLS/ARIMA/VAR, unit-root, cointegration) — the falsifiable-statistics backbone (p-values, CIs). |
| **arch** (bashtage) | NCSA | **Volatility** modeling (ARCH/GARCH/EGARCH) + unit-root/cointegration/bootstrap — the VaR/risk input statsmodels doesn't cover. |
| **QuantStats** | Apache-2.0 | Sharpe/Sortino/max-DD/VaR tearsheets — the honest performance/risk **reporting** layer over a backtest's output distribution. |
| **statsforecast** (Nixtla) | Apache-2.0 | Fast classical baselines (AutoARIMA/ETS/Theta) with probabilistic + exogenous forecasts — **benchmark the FMs below against these to expose hype.** |

## HF time-series & finance models

Zero-shot forecasters output **uncertainty bands, not point oracles** — always backtest before acting, and cross-check two architecturally-different models.

| Model (HF id) | License | Note |
|---|---|---|
| **Chronos-Bolt** (amazon/chronos-bolt-base) | Apache-2.0 | Fast probabilistic zero-shot forecasting (~250× faster than original Chronos). Univariate, no exogenous — a baseline/ensemble member. |
| **TimesFM 2.5** (google/timesfm-2.5-200m-pytorch) | Apache-2.0 | Architecturally-different second forecaster (longer context, quantile head, restored covariates) to cross-check Chronos. *(2.0-500m superseded.)* |
| **Granite TTM** (ibm-granite/granite-timeseries-ttm-r2) | Apache-2.0 | Compact (~1M params) **multivariate** foundation model with exogenous/static-categorical infusion — the commercial-clean multivariate option the others lack. |
| **Moirai 2.0** (Salesforce/moirai-2.0-R-small) | ⚠️ **CC-BY-NC-4.0** | Top GIFT-Eval accuracy, any-variate — but **non-commercial**; research/analysis only, use Chronos/TimesFM/Granite for shippable work. |
| **FinBERT** (ProsusAI/finbert) | ⚠️ **unspecified** | The de-facto financial-sentiment baseline — but **no license on the model card** (weights terms ambiguous; training corpus `financial_phrasebank` is NC). Verify before commercial use. |

**Pick on evidence, not hype:** **GIFT-Eval** (Salesforce, Apache-2.0 benchmark + live leaderboard, MASE/CRPS) is the referee — use its **no-leakage filter** and always re-validate the chosen model on *your* series.

## Pairs with

`fabius-fortuna` (the analysis method + risk-first sizing), `fabius-doctrina` (serve/eval a forecasting model), `fabius-praesidium` (an AGPL/NC dependency shipping in a paid deliverable is a licensing risk), and `fabius-parcus` (a sourced classical baseline often beats a foundation model — don't add one the task doesn't need).
