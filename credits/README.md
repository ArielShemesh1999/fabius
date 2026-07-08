# Credits & inspiration

The fabius **system** — the fifteen skills, the router/dispatch policy, `AGENTS.md`, `CORPUS.md`, the architecture, the provenance apparatus, and the evals — is original work, written from scratch under one stance (*scout wide, strike narrow*). Each skill is an original operating contract in fabius's own voice.

What we owe to the open community is the **learning**: the on-demand depth under each skill's `references/` was **informed by and adapted from** the open work below. We studied these projects and wrote our own version; credit where it's due. Two honest rules govern this file:

1. **Inspiration vs. bundling.** Most rows below are *informed-by* — concepts re-expressed in fabius's own words, no upstream files copied. Where actual upstream **files are bundled** under a `references/` tree, that project's original `LICENSE` travels with them (e.g. `skills/fabius-cohors/references/agents/orchestration/LICENSE`), and for Apache-2.0 sources the `NOTICE` is retained too.
2. **No silent relicensing.** fabius itself is **proprietary — all rights reserved** (see [LICENSE](../LICENSE)); that covers fabius's own code and prose. Bundled third-party work is **not** relicensed in either direction — each keeps its upstream terms.

## Inspired / adapted from — by layer

| fabius layer | Inspired / adapted from | Upstream license |
|---|---|---|
| `fabius` (router · dispatch · model-tier) | claude-code-router (musistudio), cc-switch (farion1231) — model/route switching | see repos |
| `fabius` (long-horizon loop · R12) | the "Ralph" autonomous-loop technique (Geoff Huntley) via ralph-claude-code (frankbria) | see repo |
| `fabius-parcus` (lean guidelines) | the caveman (prose-trim) and ponytail (code-trim) disciplines | — |
| `fabius-disciplina` (process · method) | compound-engineering-plugin (EveryInc), get-shit-done (gsd-build), learn-claude-code (shareAI-lab), claude-code-best-practice (shanraisshan), gstack (garrytan) | see repos |
| `fabius-disciplina` (on-simulator prove loop) | ios-simulator-skill (conorluddy) — accessibility-tree-first verification, progressive-disclosure build output, simctl recipes | MIT |
| `fabius-decor` (design library) | open design teardowns + skill bundles (open-design, GSAP animation, UI/UX, HyperFrames) | see repos |
| `fabius-decor` (figura / data-viz) | graphify (safishamsi) — chart/graph generation for agents | see repo |
| `fabius-decor` (generative imagery) | skill-prompt-generator (huangserva) — slot-based image-prompt schema, mandatory-lighting, era/culture cascades, conflict pass | MIT |
| `fabius-decor` (explanatory diagrams) | Understand-Anything (Yuxiang Lin / Infinite Universe, Egonex-AI) — deterministic-extract-then-LLM, typed-graph schema, topology-driven pedagogical tour | MIT |
| `fabius-decor` (Israeli / Hebrew localization — *Fabius Yisrael*) | Skills-IL (skills-il / YooTech · [agentskills.co.il](https://agentskills.co.il)) — the Israeli-market Agent Skills set (Hebrew RTL, IS 5568 accessibility, Chok HaSpam, PPA / Amendment-13 privacy, Israeli formats & i18n). Studied for *what an Israel-ready product must handle*, then re-authored original; no files bundled. | **MIT** |
| `fabius-cohors` (swarm orchestration) | claude-flow / ruflo by ruvnet — coordinator + specialized-worker swarms, anti-drift, worktree isolation ([repo](https://github.com/ruvnet/ruflo)) | see repo |
| `fabius-cohors` (agent catalog) | wshobson/agents, VoltAgent/awesome-claude-code-subagents, open production-agent corpora (Google ADK samples and similar) | MIT (wshobson) · see repos |
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

### Copyleft & fair-code note (integrated toolkits)

Three of the tools just added are **not plainly permissive**, and fabius flags them where they appear: **OpenMontage** is **AGPL-3.0** (network copyleft), **Open WebUI** carries a **branding-protection clause** (no white-labeling above 50 users without an enterprise license), and **Flowise** is **open-core** (Apache-2.0 community core + a proprietary Commercial enterprise partition). As with every other row here, fabius **re-expresses the pattern in its own words and bundles no upstream files** — so none of these terms are triggered by the fabius install today. If any such file is ever vendored into the corpus, its `LICENSE` travels with it and the constraint is honored in full: the AGPL's source-offer obligation, Open WebUI's branding lock, and Flowise's enterprise boundary each stand. `fabius-praesidium` owns treating a copyleft/branding/gated dependency in a shipped product as a licensing risk to surface.

### Apache-2.0 note (security corpus)

The cybersecurity skills corpus (mukul975/Anthropic-Cybersecurity-Skills) is **Apache-2.0**. `fabius-praesidium` currently re-expresses its **defensive** concepts (STRIDE, the OWASP pass, the finding contract) in fabius's own voice — inspiration, no files carried, and nothing offensive imported. If any Apache-2.0 file is later bundled into the corpus, its `LICENSE` and `NOTICE` ship alongside it, with changes stated, per the license.

Two more sources carry **Apache-2.0** terms: **claude-mem** (thedotmack), which informed `fabius-archivum`'s auto-recall loop, and the **hooks layer of n8n-skills**, which informed `fabius-machina`. In both cases fabius re-expresses the *pattern* in its own words — **no upstream code or prose is bundled** — so no NOTICE travels with the install today. If any Apache-2.0 file is later vendored, its `LICENSE`/`NOTICE` and a statement of changes ship with it.

## Research grounding — the agent-research canon

fabius's routing policy is sourced to the literature, with a direct-vs-analogy honesty ledger. The full mapping is in [`skills/fabius/references/agent-research.md`](../skills/fabius/references/agent-research.md) and [RESEARCH.md](../RESEARCH.md); every arXiv id was checked against the paper's abstract. Primary sources:

- **Reasoning / acting:** ReAct (2210.03629), Tree of Thoughts (2305.10601), Reasoning-via-Planning / RAP (2305.14992), Graph of Thoughts (2308.09687), Chain of Abstraction (2401.17464).
- **Tools / self-improvement:** Toolformer (2302.04761), Reflexion (2303.11366), Self-Refine (2303.17651), Voyager (2305.16291), DSPy (2310.03714).
- **Memory:** MemGPT (2310.08560), LongMem (2306.07174), Generative Agents (2304.03442), *Memory for Autonomous LLM Agents* — Du, 2026 (2603.07670, CC-BY-4.0).
- **Efficiency / surveys:** *Toward Efficient Agents* — Yang et al., 2026 (2601.14192, CC-BY-4.0), and the Wang autonomous-agents survey.
- **Borrowed-by-analogy math (labelled as such):** Flow Matching (2210.02747), Consistency Models (2303.01469), Classifier-Free Guidance (2207.12598), grounded in the MIT diffusion course (diffusion.csail.mit.edu).
- **Living indexes / reading lists:** zjunlp/LLMAgentPapers, luo-junyu/awesome-agent-papers, e2b-dev/awesome-ai-agents.

## Closing

Names inside the bundled references were aligned to fabius for consistency; the ideas are theirs, the synthesis and the system are ours. fabius stands on this open work and tries to credit it honestly. If you own one of these and want a change to the attribution — or a stronger license notice — contact the author (the repo is private, so an issue won't reach us) and it will be fixed.
