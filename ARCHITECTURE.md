<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · release evidence: PROVENANCE.md · github.com/shear559/fabius -->
# Fabius — system architecture

Fabius is **one agent**, not a bundle of plugins. A router (`fabius` itself) coordinates fourteen capability layers over a thin supporting spine — fifteen public layers in all, counting the router — composing the agent's end-to-end engineering capability. It first classifies three binary process loads—**Memory**, **Tools/Action**, and **Planning**—and separately selects any domain owner. Only then does it choose the machinery rung and model tier. This document is the system's own architecture and capability matrix.

The organizing idea is the Fabian one: **scout wide, strike narrow.** Investigate broadly (process and memory make you wide); deliver the single smallest correct thing (lean makes you narrow). The layers below split exactly along that line.

---

## Layer model

```
                    ┌───────────────────────────────────────────────┐
   ROUTER     ───►  │  fabius — the praetorium: reads the job, sets  │
                    │  process loads + domain, then machinery + tier │
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

- **`fabius`** — the router (the *praetorium*). Reads the task; classifies Memory, Tools/Action, and Planning; selects any domain owner; then chooses the smallest sufficient machinery rung and model tier. Owns the system-level kill-switch and the *scout-wide / strike-narrow* maxim.
- **`fabius-parcus`** — the always-on lean core. Runs *underneath* every other layer (never instead of one): terse prose, the YAGNI ladder, surgical changes, assumption-checking.
- **`fabius-disciplina`** — the engineering-process layer: impact map → failing reproduction → minimal fix → mapped regression set → proof, plus root-cause debugging. Owns planning, test discipline, and the clarifying-question procedure; it does not impose slogan-level TDD without a covering-test map.
- **`fabius-decor`** — the design layer: token vocabulary, the one-accent laws, mobile-first, the live-verify checklist — **and the data-visualization concern** (the *figura* library: data-ink charts, reproducible tokenized SVG, diagrams-as-code).
- **`fabius-cohors`** — the agent-engineering layer: the definition schema, least-privilege permissions, the five orchestration patterns (sequential / parallel / hierarchical / human-in-the-loop / swarm).
- **`fabius-archivum`** — the permissioned persistent-memory layer: interlinked notes, index + append-only log, gated recall, and when to add vector retrieval. Security, incident, outage, rollback, and error-recovery routes begin with fresh evidence rather than recalled precedent.
- **`fabius-mercatus`** — the go-to-market layer: positioning, message-to-awareness match, proof over adjectives, a one-action funnel, converting copy, the smallest-campaign launch loop.
- **`fabius-praesidium`** — the defensive-security layer: STRIDE threat-modeling per trust boundary, the OWASP pass, secrets + least-privilege hygiene, and a severity→fix→proof finding contract. Hardens, never weaponizes.
- **`fabius-ludus`** — the game-craft layer: the core loop first, deliberate game feel (juice), state as an explicit machine, the pixel-art lane, balance one knob at a time, jam-sized scope.
- **`fabius-catena`** — the on-chain layer: account-validation-first smart-contract / program development (EVM + Solana), money-safe transaction flow, and the verifiable cryptographic-provenance *sealing* primitive (content hash → signature → timestamp proof whose pending/confirmed state is reported → offline verification bundle, boring cryptography only). Defensive; references `fabius-praesidium`'s threat model and `fabius-parcus`'s never-trim floor.
- **`fabius-machina`** — the automation layer: deterministic service-to-service workflow glue (n8n-class) — discover-from-live-schema → build incrementally → validate AND verify → activate, plus the silent-failure gotcha discipline. Distinct from `fabius-cohors`: machina wires fixed steps, cohors orchestrates generative agents.
- **`fabius-scientia`** — the scientific-research layer: the empirical method made executable (competing falsifiable hypotheses → experiment design → reproducible result), a unified scientific-database lookup with cross-identifier mapping, pipeline-as-router over field-standard tools, and the domain reproducibility checklist.
- **`fabius-doctrina`** — the AI/ML-engineering layer: the model lifecycle as production software (dataset → train/fine-tune → evaluate → serve → monitor) — model serving and inference (vLLM-class), MLOps and experiment tracking (MLflow-class), and rigorous model/LLM evaluation (held-out sets, blind judges, regression gates). Distinct from `fabius-scientia` (the scientific method over natural-science data) and `fabius-cohors` (doctrina owns the model an agent calls, not the agent).
- **`fabius-fortuna`** — the markets-and-economics layer: method over money — equity/market analysis (fundamental + technical + quantitative), economic data and indicators, valuation, backtesting with honest statistics (lookahead/survivorship/overfitting controls), portfolio construction, and risk-first position sizing. Reads the market; `fabius-decor` (figura) draws the chart. Distinct from `fabius-scientia` (natural-science data), `fabius-doctrina` (a predictive model it may serve), and `fabius-mercatus` (go-to-market). Defensive and honest: analysis not advice, never market manipulation.
- **`fabius-concilium`** — the cross-model deliberation layer: first sample the strongest available seat under the same budget; convene a council only when that exposes material disagreement or a known diversity gap. The council runs independent first opinions → closed-schema anonymized peer-review → chairman synthesis. Provider diversity is a hypothesis under test, not guaranteed superiority, and malformed ballots are dropped rather than invented. Distinct from `fabius-cohors` (which splits *work* across task specialists) and `fabius-doctrina` (which owns model evaluation).

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
| Agent-system evaluation — ground-truth benchmarks, long-run durability (the *model* an agent calls is evaluated one row up) | `fabius-cohors` |
| Market & economic analysis, valuation, honest backtesting, risk/position sizing | `fabius-fortuna` |
| Cross-model council — first opinions, blind peer-review, chairman synthesis | `fabius-concilium` |
| Agent-shape catalog, wiki schema (the deep references) | `fabius-cohors` / `fabius-archivum` `references/` |

`fabius-parcus` keeps the *never-trim* security floor (don't cut validation/security); `fabius-praesidium` owns the *active* security work (model the threat, name the check, prove it closed) and references that floor instead of restating it — single owner on each side of the line.

`fabius-parcus` is the only always-on layer. It composes with whatever task layer the router selects, and it never competes for a task verb — there is no "build" or "design" it wants to own, so it can run underneath the layer that does.

## Skill-resolution flow

```
prompt → fabius (router)   ── classify Memory/Tools/Planning + Domain; choose machinery + tier
         ├─ any output / any code         → fabius-parcus      → references/lean/guidelines/
         ├─ build / fix / refactor / plan  → fabius-disciplina  → references/process-playbook.md · references/process/
         ├─ UI / design / brand            → fabius-decor      → references/design-tokens.md · references/design/ (69 brands)
         ├─ chart / graph / diagram        → fabius-decor      → references/visualization.md (figura entry)
         ├─ build / orchestrate agents     → fabius-cohors     → references/agent-patterns.md · references/agent-catalog.md
         ├─ remember / knowledge base      → fabius-archivum   → references/memory-schema.md · references/knowledge/ (design references)
         ├─ copy / launch / positioning    → fabius-mercatus   → references/marketing-playbook.md · corpus slot
         ├─ secure / threat-model / audit  → fabius-praesidium → references/security-playbook.md · references/ai-review.md · corpus slot
         ├─ game / loop / juice / playable → fabius-ludus      → references/game-playbook.md · corpus slot
         ├─ on-chain / smart contract / seal → fabius-catena   → references/onchain-playbook.md · references/sealing.md
         ├─ automation / workflow system / webhook workflow → fabius-machina → references/automation-playbook.md
         ├─ science / bio / hypothesis     → fabius-scientia   → references/science-playbook.md
         ├─ serve / eval / train a model   → fabius-doctrina   → references/ml-engineering-playbook.md
         ├─ stock / market / econ / backtest → fabius-fortuna   → references/markets-and-quant-playbook.md
         └─ council / ask several models     → fabius-concilium → references/council-protocol.md · references/council.mjs
```

Skills self-surface by their `description`; the router composes them. "Build a landing page" resolves to `fabius-disciplina` (brainstorm the spec) → `fabius-decor` (execute at quality), all under `fabius-parcus`. A vertical (a game, a launch, a security review) runs a studio: the domain skill leads, process plans, execution follows (routing-policy R13).

## The spine

- **`references/`** — bundled, on-demand depth under one owning public skill. Nested source contracts are deliberately named `REFERENCE.md`, not `SKILL.md`, so plugin discovery exposes exactly the fifteen reviewed entry contracts rather than vendored sub-skills. The current bundle includes design teardowns, agent shapes, process references, playbooks, and tool catalogs. Some imported prototypes—including Archivum's RAG scripts—are design references until their dependencies and package names are made executable; they are not advertised as runnable plugin features. Figura currently ships its entry contract and chart guidance, not a complete generated component library.
- **`runtime/`** — the optional local runner for use without a harness. It is a zero-dependency Node CLI that loads the same public contracts, verifies them against the seal, routes tasks, gates tools behind canonical-path and capability checks, reserves model spend before calls, audits selected external surfaces, and supports an encrypted keypair channel. Its model call is injectable, so the aggregate runtime suite exercises the loop without provider spend; specification-vector checks skip loudly until their upstream vectors are fetched. Current commands and security boundaries are documented in [`runtime/README.md`](runtime/README.md).
- **`CORPUS.md`** — the one fabius-branded index over every capability library; the brain holds the index and pages in only the matching slice (routing-policy M9 · R9 · M7).
- **`evals/`** — the benchmark and deterministic repository gates; [`evals/README.md`](evals/README.md) is the index. Structural checks validate the exact public-skill inventory, frontmatter budgets, references, version matrix, and seal. The Fabius Benchmark Suite remains count-locked at 100 tasks in three tiers and three modes. Panel receipts distinguish executed checks from model-graded checklists and print replay limits rather than calling both objective. Run the aggregate verifier for the current check totals; do not copy a stale `N/N` count into architecture prose. Method and measured numbers → [BENCHMARKS.md](BENCHMARKS.md).
- **`AGENTS.md`** — the cross-tool bridge. The stance, compiled to plain markdown, so Codex / Cursor / Windsurf / Cline / Copilot / OpenCode / Gemini all run fabius.
- **Decision policy** — the `fabius` router carries `references/routing-policy.md` (our own research: the proven core R1–R13 / M1–M9 — all twenty-two rules derived and adversarially verified, coherence established over the full set — plus the researched frontier layer R14–R16 · M10–M13, held honestly at the working edge), `references/agent-research.md` (the knowledge base behind the policy, kept current), and `references/failures.md` (the lesson log that grows from real incidents — the learning lives in the file, no fine-tuning). The reasoning, the math, and the measured-vs-derived honesty ledger are in [RESEARCH.md](RESEARCH.md).

## External connections — the optional live tier

The core is plain-markdown skills and requires no hosted service, MCP server, or model roster. The repository's local Node runner is optional and has no dependency tree. A few capabilities also have an **optional live tier**: to run them against a real external system, the user configures the named API or MCP service. Fabius encodes the pattern, never silently provisions the dependency, and `fabius-parcus` governs whether it should exist at all.

| Capability | Optional live tier — *you* configure it | Works without it |
|---|---|---|
| `fabius-machina` | n8n's **first-party MCP** + `N8N_API_URL` / `N8N_API_KEY`; a community bridge only when the first-party surface cannot hold | design, discovery, and validation need no API |
| `fabius-catena` (on-chain) | an **RPC endpoint** (EVM: Infura / Alchemy / public; Solana: a cluster) + an optional **Solana MCP** | writing/reviewing contracts offline; one-shot reads via `curl` to any RPC; static analysis (Slither) + fuzzing (Echidna / Foundry) run local |
| `fabius-catena` (sealing) | **OpenTimestamps → Bitcoin** for the anchor | hashing, signing, and verification run fully offline/local |
| `fabius-archivum` | explicitly enabled lifecycle hooks and an external-corpus connector (**NotebookLM** / a vector store), all under the same write/recall authority gates | the markdown index + append-only log + symbolic search need nothing |
| `fabius-scientia` | external scientific-DB **REST APIs** (NCBI / Ensembl / PubChem …), structure/literature services (**AlphaFold**, **Zotero**, **Jupyter-AI**) + keys / rate-limits | the method, scoring, and pipeline structure are pure |
| `fabius-disciplina` | **web-search / deep-research** APIs or MCP (Perplexity / Exa / Brave / Firecrawl) for scouting reality, and **browser automation** (Playwright MCP) for proving a UI | scouting by hand, code-graph build, and most proving need nothing |
| `fabius-cohors` | **MCP tool servers** the agents call (reference servers / Composio / a bridge) and a **code-execution sandbox** (E2B / Modal / Docker) | defining agents, least-privilege, output contracts, and the orchestration patterns are pure |
| `fabius-doctrina` | the user's own **compute** (a GPU for serving/training), an **MLflow**-class tracking server + model registry, and any hosted **inference API** | the rung ladder, the eval design, and the lifecycle decisions are pure knowledge |
| `fabius-fortuna` | a **market-data API** (prices/fundamentals — yfinance / OpenBB / a data MCP), a **macro source** (FRED-class), and any **broker/exchange API** for live data or execution (CCXT / Alpaca) | the frameworks, valuation, backtest discipline, and risk rules are pure knowledge |
| `fabius-concilium` | **LLM API access for several models** — one **OpenRouter** key (every provider through one gateway) or per-provider keys; to *run* a council you must reach the seats | the protocol, the stage prompts, the anonymization, and the Borda aggregation are pure — `references/council.mjs --selftest` proves them with no key |

The other six skills — the router `fabius` itself, plus `parcus`, `decor`, `mercatus`, `praesidium`, and `ludus` — need no external connection. No third-party live service is bundled or silently activated; each live tier is the user's to authorize and wire.

## Capability matrix

What an engineer (or an agent) can do end-to-end under fabius:

| Capability | Layer(s) | What it produces |
|---|---|---|
| Write / refactor code lean | parcus (+ disciplina) | minimal, surgical, no speculative scope |
| Plan a multi-step change | disciplina | a `step → verify` plan you can loop on |
| Build or fix with mapped tests | disciplina | impact map → failing reproduction → minimum pass → mapped regressions |
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
| Prove provenance (seal) | catena | content-bound hash + signature + timestamp proof, with pending/confirmed state verified rather than assumed |
| Wire an automation | machina | discover-from-live-schema → build incrementally → validate AND verify → activate, silent-failures caught |
| Research scientifically | scientia | competing falsifiable hypotheses, source-grounded lookups, reproducible field-standard pipelines |
| Serve / fine-tune / evaluate a model | doctrina | an inference endpoint, a tracked training run, a regression-gated eval harness |
| Analyze a market or a company | fortuna | a sourced, risk-bounded, falsifiable read — valuation, honest backtest, position size |
| Convene a model council | concilium | strongest-seat baseline → first opinions → schema-checked blind review → chairman synthesis; compare against the baseline |
| Talk lean | parcus | shorter output, full substance |
| Never cut what matters | parcus (guardrail) | validation, security, a11y, data-loss handling preserved |

## Extension points

- **Add a capability layer** — a new `skills/fabius-<name>/SKILL.md` plus its path in [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) `skills[]`. Give it a precise `description` and a single owned concern; link to siblings, don't duplicate them. Nested reference material must not be named `SKILL.md`.
- **Deepen a layer** — add a `references/<file>.md` and point the skill at it (progressive disclosure).
- **Externalize the corpus** — bulk reference material (agent catalogs, design teardowns, swipe files, hardening guides, vector stores) belongs **outside** the agent's core as the indexed **fabius corpus** ([CORPUS.md](CORPUS.md) — one fabius-branded index over every capability library); the skill ships a lean entry doc + an index and pages in only the matching slice on demand (routing-policy R9 · M7 · M9). Adding a capability = adding a row to the corpus index, not a megabyte. The agent's core stays lean; the library scales without it.
- **Add a benchmark task or model** — the suite is versioned and count-locked (`evals/suite/validate.mjs` asserts exactly 20/50/30 and the per-category balance), so a task is *swapped* inside its tier in `evals/suite/tier1.smoke.jsonl` / `tier2.core.jsonl` / `tier3.stress.jsonl`; growing the suite means a suite-version change. A model goes in the relevant panel harness or in `evals/eval.mjs` for the no-system-prompt baseline. Add structural invariants to `evals/structural.mjs`; the aggregate verifier owns the live count.
- **Target a new tool** — copy `AGENTS.md` into that tool's rules path.

## Design principles

1. **One system, one stance** — one agent, work end-to-end.
2. **Single owner, zero overlap** — one rule, one home; everyone else links.
3. **Lean by default, never flimsy** — minimal artifact, guardrails non-negotiable.
4. **Scout wide, strike narrow** — fan out to understand; deliver the smallest correct thing.
5. **Model- and tool-agnostic** — prompt-level scaffolding, portable to any agent that reads standing instructions.
