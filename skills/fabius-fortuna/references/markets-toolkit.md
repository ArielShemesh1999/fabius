# Fabius Fortuna — the markets & quant toolkit

Loaded on demand by `fabius-fortuna`. The sourced, license-honest stack (2026) for market/econ **data**, **backtesting**, **TA/quant/stats**, and HF **finance/time-series models**. Two standing rules: everything here **informs analysis and bounds risk — fortuna never gives personalized financial advice and never touches market-manipulation or auto-execution**; and forecasts are **probabilistic + backtested, never oracle**. Licenses are flagged honestly (`Apache/MIT/BSD` ship freely; **`AGPL`/`Commons-Clause`/`NC` = flagged**), and one supply-chain hazard is called out below. For a data feed the License column covers the **client library only** — the feed's own data terms and rate limits are a separate contract, stated in the row.

## Data

| Source | License | Note |
|---|---|---|
| **yfinance** | Apache-2.0 | Key-free Yahoo prices/fundamentals — the default prototype feed. *Unofficial scrape — breaks without warning, not for production/redistribution.* |
| **fredapi** | Apache-2.0 *(client)* | St. Louis Fed FRED/ALFRED macro series (GDP/CPI/rates, ~800k). The econ spine; **ALFRED vintages avoid look-ahead bias** in backtests. The key is free; the *data* is not uniformly open. Two terms bind anything you ship: (1) the notice *"This product uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis"* must appear prominently in your application; (2) **a subset of series is third-party copyrighted** — those carry the word `Copyright` in their FRED notes and are enumerable via `fred/series/search`. Anything past your own personal use of one needs permission from the series *owner*, which the St. Louis Fed cannot grant. Filter for the copyright flag before an extract or a chart leaves the building — same exposure class as an AGPL/NC dependency in a paid deliverable. |
| **ccxt** | MIT | Unified API over 100+ crypto exchanges. *Live endpoints move money — analysis/risk only, never auto-execute.* |
| **OpenBB Platform** | ⚠️ **AGPL-3.0** | "Connect-once" normalizer over 100+ providers + agent-callable MCP server. *Network copyleft — review before embedding in a closed product.* |
| **Alpha Vantage** | MIT *(client)* | A contracted feed for when yfinance's fragility won't do — but **price it before you plan around it**: the free tier is **25 API requests per _day_**, not per minute (verified open-source and educational projects get unlimited daily requests). Paid is monthly at $49.99 = 75 req/min, $99.99 = 150, $149.99 = 300, $199.99 = 600, $249.99 = 1200. Read the pricing page carefully: it shows a second, near-identical set of cards labelled "/month" that are actually the *annual* plan billed yearly (~10×), so $2,499 is not a monthly tier. Free is enough to smoke-test one endpoint; a universe backfill is a paid-tier decision, made before you write the loop, not after it 429s. |
| **Massive** (formerly Polygon.io) | MIT *(client)* | The rebrand is done, not pending: `polygon.io` 301s to `massive.com`, the client is the PyPI package **`massive`** (v2.8+, MIT) and it defaults to the API base **`api.massive.com`** — `api.polygon.io` still answers and is supported "for an extended period", but `polygon-api-client` has been frozen at 1.16.3 since the rebrand day, so it is the wrong package to start on. Free "Stocks Basic" is **5 API calls/minute, 2 years of history, end-of-day only**; $29/mo buys unlimited calls with 5 years at a 15-minute delay, $79/mo 10 years, $199/mo 20+ years and real time. Size the tier to the backfill *before* writing the loop. |

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
| **TA-Lib** (ta-lib-python) | BSD-2 | 150+ industry-standard indicators + candlestick patterns. Since 0.6.5 `pip install TA-Lib` pulls a **prebuilt wheel with the native C library bundled inside it** — Linux/macOS/Windows × x86_64/arm64, Python 3.9–3.14, current line 0.7.x. The "build the C lib first" tax now only bites platforms with no published wheel. Don't downgrade to a pure-Python fallback on toolchain grounds; that reason expired. |
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
| **Chronos-2** (amazon/chronos-2) | Apache-2.0 | 120M-param encoder-only zero-shot forecaster covering **univariate, multivariate and covariate-informed** tasks in one architecture — past-only and known-future covariates, real and categorical, all in-context with no fine-tuning. First among public pretrained models on GIFT-Eval and fev-bench, with its widest margins exactly on the covariate tasks, and a **>90% win rate head-to-head against Chronos-Bolt**. This is the default forecaster now; `chronos-bolt-*` (Apache-2.0, univariate, no exogenous, ~250× faster than original Chronos) survives only as a cheap ensemble member. |
| **TimesFM 2.5** (google/timesfm-2.5-200m-pytorch) | Apache-2.0 | Architecturally-different second forecaster (longer context, quantile head, restored covariates) to cross-check Chronos-2. *(2.0-500m superseded.)* |
| **Granite TTM** (ibm-granite/granite-timeseries-ttm-r2) | Apache-2.0 | Compact (~1M params) **multivariate** foundation model with exogenous/static-categorical infusion. It is no longer the only commercially-clean multivariate option — Chronos-2 is Apache-2.0 and covariate-aware too — so pick it for what it uniquely is: two orders of magnitude smaller and CPU-cheap, viable where a 120M-param forecaster is not. The size-constrained deployment and an architecturally-independent cross-check, never the accuracy leader. |
| **Moirai 2.0** (Salesforce/moirai-2.0-R-small) | ⚠️ **CC-BY-NC-4.0** | Strong GIFT-Eval accuracy, any-variate — no longer the leaderboard top now that Chronos-2 is out, and **non-commercial** regardless; research/analysis only, use Chronos-2/TimesFM/Granite for shippable work. |
| **FinBERT** (ProsusAI/finbert) | ⚠️ **unspecified** | The de-facto financial-sentiment baseline — but **no license on the model card** (weights terms ambiguous; training corpus `financial_phrasebank` is NC). Verify before commercial use. |

**Pick on evidence, not hype:** **GIFT-Eval** (Salesforce, Apache-2.0 benchmark + live leaderboard, MASE/CRPS) is the referee for breadth — use its **no-leakage filter**. Pair it with **fev-bench** (AutoGluon, Apache-2.0: 100 tasks across seven domains, 46 of them *with covariates*), because a model that wins one and not the other has not earned your series. Then always re-validate the chosen model on *your* series — a leaderboard rank is not an edge on your data.

## Pairs with

`fabius-fortuna` (the analysis method + risk-first sizing), `fabius-doctrina` (serve/eval a forecasting model), `fabius-praesidium` (an AGPL/NC dependency shipping in a paid deliverable is a licensing risk), and `fabius-parcus` (a sourced classical baseline often beats a foundation model — don't add one the task doesn't need).
