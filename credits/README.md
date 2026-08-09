# Credits & inspiration

The fabius **system** — the fifteen skills, the router/dispatch policy, `AGENTS.md`, `CORPUS.md`, the architecture, the provenance apparatus, and the evals — is original work, written from scratch under one stance (*scout wide, strike narrow*). Each skill is an original operating contract in fabius's own voice.

What we owe to the open community is the **learning**: the on-demand depth under each skill's `references/` was **informed by and adapted from** the open work below. We studied these projects and wrote our own version; credit where it's due. Two honest rules govern this file:

1. **Inspiration vs. bundling.** Most rows below are *informed-by* — concepts re-expressed in fabius's own words, no upstream files copied. Where actual upstream **files are bundled** under a `references/` tree, that project's original `LICENSE` travels with them, and for Apache-2.0 sources a `NOTICE` stating our changes travels with them too. Eleven trees are genuinely bundled rather than merely studied, and each is scoped by its own licence file:

   | bundled tree | upstream | terms |
   |---|---|---|
   | `fabius-cohors/references/agents/{android,go,java,kotlin,python,typescript}/` | Google ADK sample agents | **Apache-2.0** — `LICENSE` + `NOTICE` per tree |
   | `fabius-cohors/references/agents/fabius-agency/` | AgentLand Contributors | **MIT** — `LICENSE` |
   | `fabius-cohors/references/agents/orchestration/` | ruvnet | **MIT** — `LICENSE` |
   | `fabius-disciplina/references/process/discipline/` | superpowers (obra — Jesse Vincent) | **MIT** — `LICENSE` |
   | `fabius-disciplina/references/process/craft/` | skills (mattpocock — Matt Pocock) | **MIT** — `LICENSE` |
   | `fabius-decor/references/design/fabius-design/` | Open Design contributors | **Apache-2.0** — `LICENSE` + `NOTICE` |
   | `fabius-decor/references/design/fabius-frames/` | HyperFrames (HeyGen, Inc.) | **Apache-2.0** — `LICENSE` + `NOTICE` |
   | `fabius-decor/references/design/fabius-motion/` | GSAP animation skills (GreenSock) | **MIT** — `LICENSE` |
   | `fabius-decor/references/design/fabius-uiux/` | UI/UX Pro Max (Next Level Builder) | **MIT** — `LICENSE` |
   | `fabius-decor/references/design/uiverse/` | Uiverse.io | **MIT** — `LICENSE` |
   | `fabius-archivum/references/knowledge/fabius-engine/` | vector-engine (Ryan Codrai) | **MIT** — `LICENSE` |
2. **No silent relicensing.** fabius itself is **proprietary — all rights reserved** (see [LICENSE](../LICENSE)); that covers fabius's own code and prose. Bundled third-party work is **not** relicensed in either direction — each keeps its upstream terms.

## Inspired / adapted from — by layer

| fabius layer | Inspired / adapted from | Upstream license |
|---|---|---|
| `fabius` (router · dispatch · model-tier) | claude-code-router (musistudio), cc-switch (farion1231) — model/route switching | see repos |
| `fabius` (long-horizon loop · R12) | the "Ralph" autonomous-loop technique (Geoff Huntley) via ralph-claude-code (frankbria) | see repo |
| `fabius-parcus` (lean guidelines) | the caveman (prose-trim) and ponytail (code-trim) disciplines | — |
| `fabius-disciplina` (process · method) | compound-engineering-plugin (EveryInc), get-shit-done (gsd-build), learn-claude-code (shareAI-lab), claude-code-best-practice (shanraisshan), gstack (garrytan) | see repos |
| `fabius-disciplina` (discipline set — **files bundled, not just studied**) | **superpowers** (obra — Jesse Vincent) — the brainstorm/plan/TDD/debug/verification skill tree, carried under `references/process/discipline/` with fabius naming | **MIT** |
| `fabius-disciplina` (craft set — **files bundled, not just studied**) | **skills** (mattpocock — Matt Pocock) — the engineering/productivity/writing craft skill tree, carried under `references/process/craft/` with fabius naming | **MIT** |
| `fabius-disciplina` (on-simulator prove loop) | ios-simulator-skill (conorluddy) — accessibility-tree-first verification, progressive-disclosure build output, simctl recipes | MIT |
| `fabius-decor` (design library — **files bundled, not just studied**) | open design teardowns + skill bundles (Open Design, GSAP animation, UI/UX Pro Max, HyperFrames, Uiverse.io) — see the bundled-tree table above; each tree carries its upstream `LICENSE` (and `NOTICE` where Apache-2.0) | Apache-2.0 · MIT (per tree) |
| `fabius-decor` (figura / data-viz) | graphify (safishamsi) — chart/graph generation for agents | see repo |
| `fabius-decor` (generative imagery) | skill-prompt-generator (huangserva) — slot-based image-prompt schema, mandatory-lighting, era/culture cascades, conflict pass | MIT |
| `fabius-decor` (explanatory diagrams) | Understand-Anything (Yuxiang Lin / Infinite Universe, Egonex-AI) — deterministic-extract-then-LLM, typed-graph schema, topology-driven pedagogical tour | MIT |
| `fabius-decor` (Israeli / Hebrew localization — *Fabius Yisrael*) | Skills-IL (skills-il / YooTech · [agentskills.co.il](https://agentskills.co.il)) — the Israeli-market Agent Skills set (Hebrew RTL, IS 5568 accessibility, Chok HaSpam, PPA / Amendment-13 privacy, Israeli formats & i18n). Studied for *what an Israel-ready product must handle*, then re-authored original; no files bundled. | **MIT** |
| `fabius-cohors` (swarm orchestration) | claude-flow / ruflo by ruvnet — coordinator + specialized-worker swarms, anti-drift, worktree isolation ([repo](https://github.com/ruvnet/ruflo)) | see repo |
| `fabius-cohors` (agent catalog) | wshobson/agents, VoltAgent/awesome-claude-code-subagents — studied, re-expressed | MIT (wshobson) · see repos |
| `fabius-cohors` (agent corpus — **files bundled, not just studied**) | **Google ADK sample agents** (google/adk-samples and related Google ADK sample material) — 85 sample projects carried under `references/agents/`, with upstream copyright notices and licence headers retained and our changes stated in each tree's `NOTICE` | **Apache-2.0** |
| `fabius-archivum` (memory, LLM-wiki) | Andrej Karpathy's "the wiki pattern" — incrementally-built personal knowledge bases ([gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)) | — |
| `fabius-archivum` (vector engine) | the `fabius-vec` knowledge engine, after open vector-search work (turbovec / ruvector) | see repos |
| `fabius-archivum` (auto-recall · re-injection) | claude-mem (thedotmack) — the capture → compress → re-inject loop wired to session lifecycle; oh-my-claudecode (Yeachan-Heo) | **Apache-2.0** (claude-mem) · see repos |
| `fabius-archivum` (external-corpus connector) | notebooklm-skill (PleasePrompto) — source-grounded KB connector, source registry, ask-until-complete loop | MIT |
| `fabius-mercatus` (go-to-market) | marketingskills (coreyhaines31) | see repo |
| `fabius-praesidium` (defensive security) | Anthropic-Cybersecurity-Skills (mukul975) — defensive guidance only | **Apache-2.0** |
| `fabius-praesidium` (AI diff/PR review) | claude-code-security-review (Anthropic) — confidence-gate, do-not-report exclusion list, two-stage filter, exploit-path requirement | MIT |
| `fabius-ludus` (game craft) | Claude-Code-Game-Studios (Donchitos) | see repo |
| `fabius-catena` (on-chain dev) | solana-dev-skill (Solana Foundation) — account-validation-first checklist, Anchor/Pinocchio rules, the LiteSVM/Mollusk/Surfpool testing pyramid, toolchain corpus | MIT |
| `fabius-catena` (provenance sealing) | **SEAL** — Ariel Shemesh's own research (SEAL whitepaper v2.0, kept outside this repo): provenance-not-truth, content-bound hard binding, boring-cryptography-only, Bitcoin-anchored timestamps, self-contained verification bundles, crypto-agile renewal | original (author's own) |
| `fabius-machina` (automation) | n8n-skills (Romuald Członkowski, aiadvisors.pl) — the n8n-mcp tool-per-intent decision tree, silent-failure gotchas, validate-AND-verify-before-activate discipline | MIT · hooks layer **Apache-2.0** |
| `fabius-scientia` (science · bio) | scientific-agent-skills (K-Dense Inc.) — per-domain single-concern skills, pipeline-as-router, the unified database-lookup contract + cross-ID maps, the hypothesis-generation loop, reproducibility gotchas | MIT (per-skill varies) |
| `fabius-concilium` (cross-model council) | Andrej Karpathy's **llm-council** — the council pattern: dispatch one question to N models, anonymized cross-review/ranking, a chairman model that synthesizes the field ([repo](https://github.com/karpathy/llm-council)) | see repo |
| `fabius-archivum` (meeting capture → memory) | Meetily (Zackriya-Solutions) — local mic+system-audio → whisper.cpp/Parakeet transcription → pluggable-LLM summary, studied as a capture→compress→retrieve source | **MIT** |
| `fabius-archivum` (publish the KB) | docsify (docsifyjs) — no-build, client-side markdown→site with full-text search, as the lean vault viewer | **MIT** |
| `fabius-cohors` (visual agent authoring) | Flowise (FlowiseAI) — drag-and-drop node canvas for LLM flows/agents; flow-as-REST-endpoint | **Apache-2.0** (core) · ⚠️ enterprise partition **Commercial** |
| `fabius-cohors` (deep-research harness) | DeerFlow (bytedance/deer-flow) — lead-agent → parallel isolated sub-agents → synthesis; the coordinator→planner→researcher→reporter shape | **MIT** |
| `fabius-cohors` (agent voice I/O) | Voicebox (jamiepine) — local multi-engine TTS + a FastMCP voice-output server giving an agent a spoken voice | **MIT** (app code; wrapped model weights keep their own terms) |
| `fabius-decor` (agentic video production) | OpenMontage (calesthio) — plain-language brief → research→script→asset→compose across 12 pipelines; free-local vs paid-cloud provider ladder | ⚠️ **AGPL-3.0** |
| `fabius-doctrina` (local inference) | llama.cpp (ggml-org) — GGUF on-device inference + OpenAI-compatible `llama-server` (embeddings, multimodal, GBNF grammar) | **MIT** |
| `fabius-doctrina` (operator dashboard) | Open WebUI (open-webui) — self-hosted chat/RAG/RBAC front-end over a served endpoint | ⚠️ **Open WebUI License** (BSD-3 + branding-protection clause) |
| `fabius-mercatus` (de-AI-tell copy) | humanizer (blader / Siqi Chen) — a prompt-only skill that strips AI-writing tells + voice-matches, from Wikipedia's "Signs of AI writing" | **MIT** |
| `fabius-cohors` (agent durability · non-inheriting capabilities) · `fabius-disciplina` (instruction + machine check) | Flue (withastro) — repair-don't-re-execute when resuming an interrupted tool batch, force-deliver deadline, capped tool-call step; allow-listed child construction (capabilities never inherit, environment does); contract-tests consumed by every adapter + a validator that hard-fails a guide whose upgrade section lacks a real diff | **Apache-2.0** |
| `fabius-praesidium` (agent egress boundary) · `fabius-doctrina` (trajectory eval) | Onyx (onyx-dot-app) — the sandbox egress proxy: network-level lockdown as the boundary with the request classifier as heuristic-on-top, proxy-injected secrets, mid-flight approval rendezvous, the packaging deny-list; and tool-trajectory assertions + rolled-back-transaction evals against the real entrypoint | **MIT** *(sources studied outside `ee/`)* |
| `fabius-cohors` (local agent runtime) · `runtime/` | OpenWorker (andrewyng) — the desktop-agent shape: a local server the shell talks to, BYOK across providers, connectors plus MCP, and above all **approval before consequential action** as a first-class part of the loop rather than a setting. Studied for *what a download-and-run agent must get right*; re-authored in fabius's own architecture (capability-per-tool, symlink-resolved jail, the irreversibility hold), no code carried | **MIT** |
| `fabius-praesidium` (external recon) · `runtime/src/recon.mjs` | web-check (Alicia Sykes / lissy93) — the all-in-one "what does the internet already see about this domain" inventory: which checks are worth running (DNS·TLS·headers·cookies·mail-auth·DNSSEC·security.txt·robots) and how each maps to an operator decision. fabius's implementation is an **independent from-scratch build on `node:dns`/`node:tls`/`fetch`** — keyless by design, with per-directive CSP grading and delegated-zone demotion added; no upstream code used | **MIT** |
| `fabius-cohors` (serverless channel) · `runtime/src/nostr.mjs` | bitchat (permissionlesstech) — the thesis that a channel should have **no owner**: keypair-as-identity, no accounts or phone numbers, interchangeable relays, TTL-bounded relay, store-and-forward, and — the part fabius took most seriously — a project that *documents its own metadata leakage* instead of claiming none. The Bluetooth-mesh half is out of scope for a software agent and is not claimed; the transport-independent design lessons and the Nostr-side envelope model are what carried over. Implementation written against the BIP-340 / NIP-44 / NIP-17 specifications and their official test vectors, not against bitchat's Swift source | **Unlicense** (public domain) |
| `fabius-cohors` (adversarial review swarm) | GitNexus (abhigyanpatwari) — persona lanes with a self-critique **hard gate**, a lane dependency DAG, per-lane model tiers, a closed verdict set + the Risk / Evidence / Fix / Blocks-merge finding schema. **Structure paraphrased, re-authored end to end; no code and no persona text taken** — see the note below | ⚠️ **PolyForm Noncommercial 1.0.0** |

### Copyleft & fair-code note (integrated toolkits)

**Four** classes of not-plainly-permissive terms appear above, and fabius flags each where it appears: **OpenMontage** is **AGPL-3.0** (network copyleft), **Open WebUI** carries a **branding-protection clause** (no white-labeling above 50 users without an enterprise license), **Flowise** is **open-core** (Apache-2.0 community core + a proprietary Commercial enterprise partition), and **GitNexus** is **PolyForm Noncommercial 1.0.0** — a **fourth class**, and the strictest of the four for this repo. As with every other row here, fabius **re-expresses the pattern in its own words and bundles no upstream files** — so none of these terms are triggered by the fabius install today. If any such file is ever vendored into the corpus, its `LICENSE` travels with it and the constraint is honored in full: the AGPL's source-offer obligation, Open WebUI's branding lock, and Flowise's enterprise boundary each stand.

**PolyForm Noncommercial is different in kind, not just in strictness — state it plainly.** It is *fair-code, not open source*: the grant covers **noncommercial purposes only**. For a proprietary product fabius is sold as, that makes GitNexus's source **legally untouchable at any volume** — no vendoring, no copying, no adaptation, and no "vendor it and carry the LICENSE" escape hatch, because there is no volume of attribution that turns a noncommercial grant into a commercial one. The other three classes constrain *how* you may ship the code; this one removes shipping it as an option. What fabius took is the **structure of an idea expressed in markdown prompts** — thin ground where idea and expression nearly meet, which is exactly why the line was drawn hard: re-authored end to end in fabius's own words, no code, no persona text, no wording carried.

It also carries a **supply-chain trap** worth naming once, because it is the reason a careful team ships this license by accident: **GitHub reports PolyForm as `NOASSERTION`**. A dependency gate written the obvious way — block AGPL, allow the rest — passes a noncommercial license straight through and reports green. `fabius-praesidium` owns that as a default-deny finding (`hardening-guides.md` §9: an unidentifiable license is an unmeetable one), alongside treating any copyleft/branding/gated dependency in a shipped product as a licensing risk to surface.

### Apache-2.0 note (security corpus)

The cybersecurity skills corpus (mukul975/Anthropic-Cybersecurity-Skills) is **Apache-2.0**. `fabius-praesidium` currently re-expresses its **defensive** concepts (STRIDE, the OWASP pass, the finding contract) in fabius's own voice — inspiration, no files carried, and nothing offensive imported. If any Apache-2.0 file is later bundled into the corpus, its `LICENSE` and `NOTICE` ship alongside it, with changes stated, per the license.

Two more sources carry **Apache-2.0** terms: **claude-mem** (thedotmack), which informed `fabius-archivum`'s auto-recall loop, and the **hooks layer of n8n-skills**, which informed `fabius-machina`. In both cases fabius re-expresses the *pattern* in its own words — **no upstream code or prose is bundled from either** — so neither contributes a NOTICE. Three Apache-2.0 sources *are* genuinely vendored: the Google ADK agent corpus (a `LICENSE` and a changes-stated `NOTICE` in each of its six trees), and decor's **fabius-design** (Open Design) and **fabius-frames** (HyperFrames / HeyGen) trees, each carrying its upstream `LICENSE` plus a changes-stated `NOTICE`, as the rule above requires.

## Research grounding — the agent-research canon

fabius's routing policy is sourced to the literature, with a direct-vs-analogy honesty ledger. The full mapping is in [`skills/fabius/references/agent-research.md`](../skills/fabius/references/agent-research.md) and [RESEARCH.md](../RESEARCH.md); every arXiv id was checked against the paper's abstract. Primary sources:

- **Reasoning / acting:** ReAct (2210.03629), Tree of Thoughts (2305.10601), Reasoning-via-Planning / RAP (2305.14992), Graph of Thoughts (2308.09687), Chain of Abstraction (2401.17464).
- **Tools / self-improvement:** Toolformer (2302.04761), Reflexion (2303.11366), Self-Refine (2303.17651), Voyager (2305.16291), DSPy (2310.03714).
- **Memory:** MemGPT (2310.08560), LongMem (2306.07174), Generative Agents (2304.03442), *Memory for Autonomous LLM Agents* — Du, 2026 (2603.07670, CC-BY-4.0).
- **Efficiency / surveys:** *Toward Efficient Agents* — Yang et al., 2026 (2601.14192, CC-BY-4.0), and the Wang autonomous-agents survey.
- **Borrowed-by-analogy math (labelled as such):** Flow Matching (2210.02747), Consistency Models (2303.01469), Classifier-Free Guidance (2207.12598), grounded in the MIT diffusion course (diffusion.csail.mit.edu).
- **Living indexes / reading lists:** zjunlp/LLMAgentPapers, luo-junyu/awesome-agent-papers, e2b-dev/awesome-ai-agents.

## Closing

Names inside the bundled references were aligned to fabius for consistency; the ideas are theirs, the synthesis and the system are ours. That alignment has a cost worth stating: inside the bundled trees, some rewritten links, package names and import paths no longer resolve upstream. Read them as a corpus; go upstream for anything you intend to run. fabius stands on this open work and tries to credit it honestly. If you own one of these and want a change to the attribution — or a stronger license notice — open an issue on the repository or contact the author, and it will be fixed.
