# Fabius Fortuna — the markets & quant playbook

The on-demand depth for `fabius-fortuna`: the analysis frameworks, the valuation models, the backtest-honesty checklist, the data-source map, and the risk contract. The SKILL.md is the stance; this is how you run a market analysis without fooling yourself. These are capabilities fabius **applies** by reaching for named ecosystem tools — fabius bundles no runtime; the optional live tier (data feeds, broker APIs) routes to ARCHITECTURE.md external connections. Tool names and versions are a point-in-time snapshot (early 2026); re-verify before you depend on one.

Scout the market wide, strike the one bounded position you can defend, prove the edge out-of-sample.

## 1. Risk first — the contract that never trims (SKILL §2 in depth)

Run this *before* any return analysis:

- **Position sizing** — size to survivable loss, not imagined gain. Fixed-fractional / volatility-targeted / risk-parity beat conviction-weighting. Set a hard per-trade stop and a portfolio max-drawdown.
- **Tail and ruin** — model the drawdown, not the average; a strategy with a great mean and a fat left tail is a time bomb. Asymmetry of recovery (−50% needs +100%) governs sizing.
- **Diversification** — low-correlation exposures are the one free lunch; concentration is a thesis you'd better be able to defend.
- **Costs and liquidity** — every number is **net of** spread, slippage, fees, and the size you can actually fill. Strategy capacity (the AUM it survives) is part of the result, not a footnote.

## 2. The three analysis lenses — each a falsifiable read

**Fundamental — value from the business.**
- Read the financials: revenue/margin/cash-flow trajectory, balance-sheet health, unit economics. Pull primaries — filings (10-K/10-Q) and reported fundamentals, not a headline. *(ecosystem: SEC EDGAR access for filings; yfinance / AKShare / OpenBB for fundamentals.)*
- Value with a model whose **assumptions are stated and stress-tested**: DCF (project FCF, discount at WACC, terminal value — and show the sensitivity to the growth/discount inputs), or relative multiples (P/E, EV/EBITDA vs a defensible peer set). A target price without its assumption table is a guess.

**Technical — structure from price/volume.**
- Trend, support/resistance, momentum, volatility regime; indicators via the industry standard *(ecosystem: TA-Lib)*. Useful as **discipline** (defined levels, stops, regime filters); dangerous as prophecy — most patterns are noise. Never present a technical read as a certainty.

**Quantitative — a tested signal with a number.**
- A factor/strategy reduced to metrics (Sharpe/Sortino, hit-rate, max-drawdown, exposure) and held to §4's honesty bar. *(ecosystem: research/backtest stacks below.)*

## 3. The data-source map — source it, don't assert it

A financial fact has a source; produce it with its as-of date (the `fabius-scientia` lookup discipline for markets):

- **Prices / fundamentals** — yfinance (the data backbone), AKShare, or a unified research layer (**OpenBB** — open-source investment-research desk, Python + MCP). Financial-data MCP servers expose these to an agent.
- **Filings / fundamentals (primary)** — SEC EDGAR for the actual reports.
- **Macro / economic series** — an authoritative source (FRED-class, central-bank, statistics-office). Macro **revises**: distinguish the first print from the final, and *nowcast* (true now) from *forecast* (a bounded, falsifiable claim + the regime it assumes).
- **Crypto market data** — a unified exchange layer (**CCXT** — one API across exchanges).

Return auditable provenance: the source, the symbol, the as-of date, any revision/adjustment (splits, dividends, restatements).

## 4. Backtest honestly — guilty until proven innocent

A green equity curve is the easiest lie in finance. The bias catalog to clear *every time* (the same statistical rigor `fabius-scientia` applies to an experiment):

- **Lookahead / data-snooping** — the test must only see what was knowable at decision time (point-in-time fundamentals, no trading on a close you used to decide).
- **Survivorship bias** — test on the universe *as it was*, delisted/bankrupt names included.
- **In-sample → out-of-sample** — tune on one window, validate on a held-out window, then **walk-forward**. An in-sample Sharpe is a hypothesis.
- **Multiple-testing / overfitting** — penalize for the search (deflated Sharpe, a parameter-stability check); 200 tries guarantee one lucky winner.
- **Costs & capacity** — net of realistic transaction costs and slippage, at executable size.

Pick the engine to the job, not the hype: **vectorbt** (vectorized, fast research sweeps), **Qlib** (AI/ML quant pipelines), **Lean/QuantConnect** or **NautilusTrader** (event-driven, production-grade, closer to live fills), **Freqtrade** (crypto bot with built-in backtest). The engine that models fills and costs honestly beats the one with the prettier curve.

> A backtest predicts the past. Out-of-sample, cost-aware, search-penalized — or it's marketing.

## 5. Portfolio construction

Combine signals into a portfolio, not a pile of bets: define the objective (return target / vol target / drawdown cap), the constraints (position limits, sector/liquidity caps), and the method (mean-variance with shrinkage, risk-parity, or a simpler equal-risk weighting when the covariance estimate is noisy). Rebalance on a rule, not a feeling; account for turnover cost. Out-of-sample, a robust simple allocation usually beats a fragile optimized one — the same YAGNI discipline (`fabius-parcus`) applies to optimizers.

## 6. Agents over markets (route the pieces)

LLM-agent finance frameworks (a virtual trading desk, an AI "hedge fund", an autonomous quant researcher — TradingAgents / ai-hedge-fund / RD-Agent class) are real and instructive, but **own each piece at its layer**: the *agent* (roles, tools, orchestration, output contract, least-privilege on any broker key) is `fabius-cohors`; any *predictive model* it serves/evaluates is `fabius-doctrina`; the *financial reasoning and risk* is fortuna's; the *chart* is `fabius-decor`. Don't collapse them into one "trading bot" — that's how the risk control gets skipped.

## Boundaries & the bright line

- **No personalized financial advice** — analysis, scenarios, and risk framing, with assumptions surfaced; the decision is the user's. Default a plain *"analysis, not financial advice"* note on anything actionable.
- **No market manipulation, ever** — no pump-and-dump copy, no fabricated signals to move a price, no insider-trading facilitation. Refuse and say why (the `fabius-praesidium` defensive-only line, the `fabius-mercatus` proof-over-hype line).
- Charts → `fabius-decor` (figura) renders what fortuna reads (a TradingView-Lightweight-Charts-class candlestick is decor's pixels, fortuna's interpretation). On-chain/DeFi execution and wallets → `fabius-catena`. Trade-automation wiring → `fabius-machina`.

---

Drawn from the strongest finance/quant tools catalogued in the ARGAZ directory (OpenBB, Qlib, Lean/QuantConnect, NautilusTrader, vectorbt, Freqtrade, CCXT, TA-Lib, yfinance, SEC EDGAR) — re-expressed in fabius's own voice as *how to analyze a market with method and bound the risk*, crediting each tool by name. fabius bundles no runtime; the optional live tier is in [ARCHITECTURE.md](../../../ARCHITECTURE.md) (*External connections*).
