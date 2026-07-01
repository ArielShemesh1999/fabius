<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->
# Fabius — system architecture

Fabius is **one agent**, not a bundle of plugins. A router (`fabius` itself) coordinates fourteen capability layers over a thin supporting spine — fifteen layers in all, counting the router — composing the agent's end-to-end engineering capability. The router dispatches on three axes together: **which layer(s)**, **how much machinery**, and **which model tier**. This document is the system's own architecture and its capability matrix.

The organizing idea is the Fabian one: **scout wide, strike narrow.** Investigate broadly (process and memory make you wide); deliver the single smallest correct thing (lean makes you narrow). The layers below split exactly along that line.

---

## Layer model

```
                    ┌───────────────────────────────────────────────┐
   ROUTER     ───►  │  fabius — the praetorium: reads the job, sets  │
                    │  the stance, picks layer + machinery + tier    │
                    └───────────────────────────────────────────────┘
                                        │
   CORE       ───►  fabius-parcus — always-on lean core (runs under every layer)
                                        │
      ┌─────────┬─────────┬─────────┬───┴─────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐
      ▼         ▼         ▼         ▼         ▼         ▼         ▼         ▼         ▼         ▼         ▼         ▼         ▼
 disciplina   decor    cohors   archivum  mercatus praesidium   ludus    catena    machina  scientia  doctrina   fortuna  concilium
    eng.    design +    agent  persistent  go-to-   defensive   game    on-chain   automa-   science   ML eng.   markets cross-model
   process  data-viz    eng.     memory    market   security    craft    + seal     tion      + bio    + eval   + finance  council
      └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
                                        │
                    ┌───────────────────────────────────────────────┐
   SPINE      ───►  │  references/ · CORPUS.md · evals/ · AGENTS.md  │
                    │  (deep-dives) (the index) (benchmark)(any tool)│
                    └───────────────────────────────────────────────┘
                                        │
                                        ▼
   end to end: code · prose · UI + data-viz · agents · debug · memory · marketing
               · defensive-security · games · on-chain + provenance · automation · science
               · ML engineering · markets & finance · the cross-model council
```

- **`fabius`** — the router (the *praetorium*). Reads the task, sets the working stance, and dispatches on three axes: which layer(s), how much machinery (the capability ladder), and which model tier. Owns the system-level kill-switch and the *scout-wide / strike-narrow* maxim.
- **`fabius-parcus`** — the always-on lean core. Runs *underneath* every other layer (never instead of one): terse prose, the YAGNI ladder, surgical changes, assumption-checking.
- **`fabius-disciplina`** — the engineering-process layer: brainstorm → plan → test-first → prove, grilling ambiguity, root-cause debugging. Owns planning, test discipline, and the clarifying-question procedure.
- **`fabius-decor`** — the design layer: token vocabulary, the one-accent laws, mobile-first, the live-verify checklist — **and the data-visualization concern** (the *figura* library: data-ink charts, reproducible tokenized SVG, diagrams-as-code).
- **`fabius-cohors`** — the agent-engineering layer: the definition schema, least-privilege permissions, the five orchestration patterns (sequential / parallel / hierarchical / human-in-the-loop / swarm).
- **`fabius-archivum`** — the persistent-memory layer: interlinked notes, index + log, when to add vector retrieval.
- **`fabius-mercatus`** — the go-to-market layer: positioning, message-to-awareness match, proof over adjectives, a one-action funnel, converting copy, the smallest-campaign launch loop.
- **`fabius-praesidium`** — the defensive-security layer: STRIDE threat-modeling per trust boundary, the OWASP pass, secrets + least-privilege hygiene, and a severity→fix→proof finding contract. Hardens, never weaponizes.
- **`fabius-ludus`** — the game-craft layer: the core loop first, deliberate game feel (juice), state as an explicit machine, the pixel-art lane, balance one knob at a time, jam-sized scope.
- **`fabius-catena`** — the on-chain layer: account-validation-first smart-contract / program development (EVM + Solana), money-safe transaction flow, and the verifiable cryptographic-provenance *sealing* primitive (content hash → signature → Bitcoin-anchored timestamp → offline verification bundle, boring-cryptography only). Defensive; references `fabius-praesidium`'s threat model and `fabius-parcus`'s never-trim floor.
- **`fabius-machina`** — the automation layer: deterministic service-to-service workflow glue (n8n-class) — discover-from-live-schema → build incrementally → validate AND verify → activate, plus the silent-failure gotcha discipline. Distinct from `fabius-cohors`: machina wires fixed steps, cohors orchestrates generative agents.
- **`fabius-scientia`** — the scientific-research layer: the empirical method made executable (competing falsifiable hypotheses → experiment design → reproducible result), a unified scientific-database lookup with cross-identifier mapping, pipeline-as-router over field-standard tools, and the domain reproducibility checklist.
- **`fabius-doctrina`** — the AI/ML-engineering layer: the model lifecycle as production software (dataset → train/fine-tune → evaluate → serve → monitor) — model serving and inference (vLLM-class), MLOps and experiment tracking (MLflow-class), and rigorous model/LLM evaluation (held-out sets, blind judges, regression gates). Distinct from `fabius-scientia` (the scientific method over natural-science data) and `fabius-cohors` (doctrina owns the model an agent calls, not the agent).
- **`fabius-fortuna`** — the markets-and-economics layer: method over money — equity/market analysis (fundamental + technical + quantitative), economic data and indicators, valuation, backtesting with honest statistics (lookahead/survivorship/overfitting controls), portfolio construction, and risk-first position sizing. Reads the market; `fabius-decor` (figura) draws the chart. Distinct from `fabius-scientia` (natural-science data), `fabius-doctrina` (a predictive model it may serve), and `fabius-mercatus` (go-to-market). Defensive and honest: analysis not advice, never market manipulation.
- **`fabius-concilium`** — the cross-model deliberation layer: convene a **council** of heterogeneous models on one question and aggregate their answers into a better single one — first opinions (each model answers independently) → anonymized peer-review (each ranks the others blind) → chairman synthesis (one model fuses the ranked field). Ensemble epistemics that spends the *every-model* identity to cut single-model error and bias. Gated hard by `fabius-parcus` (a council is N+N+1 model calls — convene only when a wrong answer is costly). Distinct from `fabius-cohors` (which splits the *work* across task-specialist agents; concilium aggregates one *answer* across whole models) and `fabius-doctrina` (whose blind-judge discipline it borrows for the ranking, but does not own).

## Coordination contract — single owner, zero overlap

Each rule has exactly one owning layer; every other layer references it instead of restating it. This is what keeps fifteen skills from contradicting each other:

| Rule | Owner |
|---|---|
| Planning (`step → verify`), test discipline, the clarifying-question / grill procedure | `fabius-disciplina` |
| Lean prose, the YAGNI ladder, the never-trim list, auto-clarity carve-outs | `fabius-parcus` |
| System kill-switch, routing + dispatch (layer · machinery · model tier), the shared maxim | `fabius` |
| Token contract, the one-accent laws, the data-visualization (figura) rules | `fabius-decor` |
| Message + positioning + the funnel path + converting copy | `fabius-mercatus` |
| Threat model, the audit, the finding contract (active security work) | `fabius-praesidium` |
| The game loop, game feel, balance, the studio pipeline | `fabius-ludus` |
| On-chain account validation + transaction safety + the provenance-sealing primitive | `fabius-catena` |
| The automation build-and-verify discipline + the silent-failure catalog | `fabius-machina` |
| The scientific method, the database-lookup contract, the reproducibility checklist | `fabius-scientia` |
| The model lifecycle — serving, MLOps/experiment-tracking, model/LLM evaluation | `fabius-doctrina` |
| Market & economic analysis, valuation, honest backtesting, risk/position sizing | `fabius-fortuna` |
| Cross-model council — first opinions, blind peer-review, chairman synthesis | `fabius-concilium` |
| Agent-shape catalog, wiki schema (the deep references) | `fabius-cohors` / `fabius-archivum` `references/` |

`fabius-parcus` keeps the *never-trim* security floor (don't cut validation/security); `fabius-praesidium` owns the *active* security work (model the threat, name the check, prove it closed) and references that floor instead of restating it — single owner on each side of the line.

`fabius-parcus` is the only always-on layer. It composes with whatever task layer the router selects, and it never competes for a task verb — there is no "build" or "design" it wants to own, so it can run underneath the layer that does.

## Skill-resolution flow

```
prompt → fabius (router)   ── dispatch: which layer(s) · how much machinery · which model tier
         ├─ any output / any code         → fabius-parcus      → references/lean/guidelines/
         ├─ build / fix / refactor / plan  → fabius-disciplina  → references/process-playbook.md · references/process/
         ├─ UI / design / brand            → fabius-decor      → references/design-tokens.md · references/design/ (69 brands)
         ├─ chart / graph / diagram        → fabius-decor      → references/visualization.md · assets/charts/ (figura)
         ├─ build / orchestrate agents     → fabius-cohors     → references/agent-patterns.md · references/agents/ (catalog + fabius-vec.db)
         ├─ remember / knowledge base      → fabius-archivum   → references/memory-schema.md · references/knowledge/ (vector · wiki · rag)
         ├─ copy / launch / positioning    → fabius-mercatus   → references/marketing-playbook.md · corpus slot
         ├─ secure / threat-model / audit  → fabius-praesidium → references/security-playbook.md · references/ai-review.md · corpus slot
         ├─ game / loop / juice / playable → fabius-ludus      → references/game-playbook.md · corpus slot
         ├─ on-chain / contract / seal     → fabius-catena     → references/onchain-playbook.md · references/sealing.md
         ├─ automate / workflow / webhook  → fabius-machina    → references/automation-playbook.md
         ├─ science / bio / hypothesis     → fabius-scientia   → references/science-playbook.md
         ├─ serve / eval / train a model   → fabius-doctrina   → references/ml-engineering-playbook.md
         ├─ stock / market / econ / backtest → fabius-fortuna   → references/markets-and-quant-playbook.md
         └─ council / ask several models     → fabius-concilium → references/council-protocol.md · references/council.mjs
```

Skills self-surface by their `description`; the router composes them. "Build a landing page" resolves to `fabius-disciplina` (brainstorm the spec) → `fabius-decor` (execute at quality), all under `fabius-parcus`. A vertical (a game, a launch, a security review) runs a studio: the domain skill leads, process plans, execution follows (routing-policy R13).

## The spine

- **`references/`** — on-demand depth bundled per layer, loaded only when a layer needs it so the skills stay lean. Each specialist ships a lean entry doc **plus a full library**: `fabius-decor` → a 69-brand design teardown library (`references/design/`) + the figura visualization entry (`references/visualization.md`); `fabius-cohors` → a 200+-agent production catalog with a `fabius-vec.db` memory index (`references/agents/`); `fabius-archivum` → a knowledge engine, wiki pattern, and RAG pipeline (`references/knowledge/`); `fabius-disciplina` → the craft + discipline process library (`references/process/`); `fabius-mercatus` → a channel + swipe library (`references/channel-swipe-library.md`); `fabius-praesidium` → a hardening + audit library (`references/hardening-guides.md`); `fabius-ludus` → an engine + feel library (`references/engine-recipes.md`); `fabius-catena` → the on-chain dev + sealing playbooks (`references/onchain-playbook.md` + `references/sealing.md`); `fabius-machina` → the automation build-and-verify playbook (`references/automation-playbook.md`); `fabius-scientia` → the scientific-method + database-lookup playbook (`references/science-playbook.md`); `fabius-doctrina` → the ML-engineering playbook — serving, MLOps, evaluation (`references/ml-engineering-playbook.md`); `fabius-fortuna` → the markets & quant playbook — analysis, valuation, honest backtesting, risk (`references/markets-and-quant-playbook.md`); `fabius-concilium` → the council protocol + a zero-dependency runnable reference (`references/council-protocol.md` + `references/council.mjs`); `fabius-parcus` → the lean guidelines (`references/lean/`).
- **`CORPUS.md`** — the one fabius-branded index over every capability library; the brain holds the index and pages in only the matching slice (routing-policy M9 · R9 · M7).
- **`evals/`** — a runnable, vendor-agnostic benchmark harness that scores a model with and without the fabius stance: `eval.mjs` (Anthropic/OpenAI), `portable_eval.py` (cross-vendor), a `harness.workflow.js` multi-agent variant, and the `results.json` they write on a run (gitignored — the measured numbers are recorded in [BENCHMARKS.md](BENCHMARKS.md)).
- **`AGENTS.md`** — the cross-tool bridge. The stance, compiled to plain markdown, so Codex / Cursor / Windsurf / Cline / Copilot / OpenCode / Gemini all run fabius.
- **Decision policy** — the `fabius` router carries `references/routing-policy.md` (the proven core R1–R10 / M1–M8, plus the operational extensions R11–R13 / M9, each sourced honestly to the agent-research canon — ReAct, Toolformer, Tree of Thoughts, RAP, Reflexion, MemGPT, DSPy, Voyager, the efficiency and memory surveys…), `references/agent-research.md` (the knowledge base + the source-mapped canon table), and `references/failures.md` (a Reflexion-style lesson log that grows from real incidents). The reasoning, the math, and the direct-vs-analogy honesty ledger are in [RESEARCH.md](RESEARCH.md).

## External connections — the optional live tier

fabius is plain-markdown skills: it bundles **no runtime and no MCP server**, and requires **no external service to install**. Most capabilities are pure knowledge contracts that produce code, prose, or a plan. A few have an **optional live tier** — to *run* the capability against a real system you configure an MCP server or an API the skill names. fabius encodes the *pattern*, never the dependency, and the never-build-it-until-you-need-it gate (`fabius-parcus`) governs whether you stand it up at all.

| Capability | Optional live tier — *you* configure it | Works without it |
|---|---|---|
| `fabius-machina` | the **`n8n-mcp`** MCP server + `N8N_API_URL` / `N8N_API_KEY` (or the per-platform equivalent — **Composio**, **Activepieces**) | design, discovery, and validation need no API |
| `fabius-catena` (on-chain) | an **RPC endpoint** (EVM: Infura / Alchemy / public; Solana: a cluster) + an optional **Solana MCP** | writing/reviewing contracts offline; one-shot reads via `curl` to any RPC; static analysis (Slither) + fuzzing (Echidna / Foundry) run local |
| `fabius-catena` (sealing) | **OpenTimestamps → Bitcoin** for the anchor | hashing, signing, and verification run fully offline/local |
| `fabius-archivum` | Claude Code lifecycle **hooks** (auto-recall) and an external-corpus connector (**NotebookLM** / `notebooklm-mcp` / a vector store) | the markdown index + log + grep needs nothing |
| `fabius-scientia` | external scientific-DB **REST APIs** (NCBI / Ensembl / PubChem …), structure/literature services (**AlphaFold**, **Zotero**, **Jupyter-AI**) + keys / rate-limits | the method, scoring, and pipeline structure are pure |
| `fabius-disciplina` | **web-search / deep-research** APIs or MCP (Perplexity / Exa / Brave / Firecrawl) for scouting reality, and **browser automation** (Playwright MCP) for proving a UI | scouting by hand, code-graph build, and most proving need nothing |
| `fabius-cohors` | **MCP tool servers** the agents call (reference servers / Composio / a bridge) and a **code-execution sandbox** (E2B / Modal / Docker) | defining agents, least-privilege, output contracts, and the orchestration patterns are pure |
| `fabius-doctrina` | the user's own **compute** (a GPU for serving/training), an **MLflow**-class tracking server + model registry, and any hosted **inference API** | the rung ladder, the eval design, and the lifecycle decisions are pure knowledge |
| `fabius-fortuna` | a **market-data API** (prices/fundamentals — yfinance / OpenBB / a data MCP), a **macro source** (FRED-class), and any **broker/exchange API** for live data or execution (CCXT / Alpaca) | the frameworks, valuation, backtest discipline, and risk rules are pure knowledge |
| `fabius-concilium` | **LLM API access for several models** — one **OpenRouter** key (every provider through one gateway) or the synapse console's own 5-provider runtime + `X-LLM-Key` vault; to *run* a council you must reach the seats | the protocol, the stage prompts, the anonymization, and the Borda aggregation are pure — `references/council.mjs --selftest` proves them with no key |

The other five skills (`parcus`, `decor`, `mercatus`, `praesidium`, `ludus`) need no external connection at all. Nothing here is bundled; each live tier is the user's to wire — the same lean rule everywhere: **hold the pattern, add the runtime only when the task demands it.**

## Capability matrix

What an engineer (or an agent) can do end-to-end under fabius:

| Capability | Layer(s) | What it produces |
|---|---|---|
| Write / refactor code lean | parcus (+ disciplina) | minimal, surgical, no speculative scope |
| Plan a multi-step change | disciplina | a `step → verify` plan you can loop on |
| Build test-first | disciplina | failing test → minimum pass → refactor |
| Debug by root cause | disciplina | reproduce → minimize → hypothesize → fix the cause → regression-test |
| Prove before "done" | disciplina | evidence — a run, a passing check — never "should work" |
| Ship-grade UI | decor | tokenized, one-accent, mobile-first, a11y-checked, live-verified |
| Visualize data | decor (figura) | data-ink charts, reproducible tokenized SVG, the right chart for the question |
| Build / orchestrate agents | cohors | precise description + least-privilege tools + output contract |
| Persist + retrieve knowledge | archivum | interlinked notes, index + log, cheap retrieval |
| Market a thing | mercatus | positioning, converting copy, a one-action funnel, a tested launch |
| Harden / audit (defensive) | praesidium | a STRIDE model, the OWASP pass, severity→fix→proof findings |
| Build a small game | ludus | a fun core loop, deliberate juice, an explicit state machine, jam-sized scope |
| Develop on-chain | catena | account-validation-first contracts/programs (EVM + Solana), money-safe transactions, the right toolchain |
| Prove provenance (seal) | catena | a content-bound hash + signature + Bitcoin-anchored timestamp, verifiable offline by anyone, forever |
| Wire an automation | machina | discover-from-live-schema → build incrementally → validate AND verify → activate, silent-failures caught |
| Research scientifically | scientia | competing falsifiable hypotheses, source-grounded lookups, reproducible field-standard pipelines |
| Convene a model council | concilium | first opinions → blind peer-review → chairman synthesis — one answer better than any single seat |
| Talk lean | parcus | shorter output, full substance |
| Never cut what matters | parcus (guardrail) | validation, security, a11y, data-loss handling preserved |

## Extension points

- **Add a capability layer** — a new `skills/fabius-<name>/SKILL.md` plus its path in `plugin.json` `skills[]`. Give it a precise `description` and a single owned concern; link to siblings, don't duplicate them.
- **Deepen a layer** — add a `references/<file>.md` and point the skill at it (progressive disclosure).
- **Externalize the corpus** — bulk reference material (agent catalogs, design teardowns, swipe files, hardening guides, vector stores) belongs **outside** the agent's core as the indexed **fabius corpus** ([CORPUS.md](CORPUS.md) — one fabius-branded index over every capability library); the skill ships a lean entry doc + an index and pages in only the matching slice on demand (routing-policy R9 · M7 · M9). Adding a capability = adding a row to the corpus index, not a megabyte. The agent's core stays lean; the library scales without it.
- **Add a benchmark model or task** — edit `evals/eval.mjs`.
- **Target a new tool** — copy `AGENTS.md` into that tool's rules path.

## Design principles

1. **One system, one stance** — one agent, work end-to-end.
2. **Single owner, zero overlap** — one rule, one home; everyone else links.
3. **Lean by default, never flimsy** — minimal artifact, guardrails non-negotiable.
4. **Scout wide, strike narrow** — fan out to understand; deliver the smallest correct thing.
5. **Model- and tool-agnostic** — prompt-level scaffolding, portable to any agent that reads standing instructions.
