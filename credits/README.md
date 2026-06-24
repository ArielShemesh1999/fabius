# Credits & inspiration

The fabius **system** — the nine skills, the router/dispatch policy, `AGENTS.md`, `CORPUS.md`, the architecture, and the evals — is original work, written from scratch under one stance (*scout wide, strike narrow*). Each skill is an original operating contract in fabius's own voice.

What we owe to the open community is the **learning**: the on-demand depth under each skill's `references/` was **informed by and adapted from** the open work below. We studied these projects and wrote our own version; credit where it's due. Two honest rules govern this file:

1. **Inspiration vs. bundling.** Most rows below are *informed-by* — concepts re-expressed in fabius's own words, no upstream files copied. Where actual upstream **files are bundled** under a `references/` tree, that project's original `LICENSE` travels with them (e.g. `skills/fabius-cohors/references/agents/orchestration/LICENSE`), and for Apache-2.0 sources the `NOTICE` is retained too.
2. **No silent relicensing.** fabius is MIT; that covers fabius's own code and prose. It does **not** re-license anyone else's bundled work — each keeps its upstream terms.

## Inspired / adapted from — by layer

| fabius layer | Inspired / adapted from | Upstream license |
|---|---|---|
| `fabius` (router · dispatch · model-tier) | claude-code-router (musistudio), cc-switch (farion1231) — model/route switching | see repos |
| `fabius` (long-horizon loop · R12) | the "Ralph" autonomous-loop technique (Geoff Huntley) via ralph-claude-code (frankbria) | see repo |
| `fabius-parcus` (lean guidelines) | the caveman (prose-trim) and ponytail (code-trim) disciplines | — |
| `fabius-disciplina` (process · method) | compound-engineering-plugin (EveryInc), get-shit-done (gsd-build), learn-claude-code (shareAI-lab), claude-code-best-practice (shanraisshan), gstack (garrytan) | see repos |
| `fabius-decor` (design library) | open design teardowns + skill bundles (open-design, GSAP animation, UI/UX, HyperFrames) | see repos |
| `fabius-decor` (figura / data-viz) | graphify (safishamsi) — chart/graph generation for agents | see repo |
| `fabius-cohors` (swarm orchestration) | claude-flow / ruflo by ruvnet — coordinator + specialized-worker swarms, anti-drift, worktree isolation ([repo](https://github.com/ruvnet/ruflo)) | see repo |
| `fabius-cohors` (agent catalog) | wshobson/agents, VoltAgent/awesome-claude-code-subagents, open production-agent corpora (Google ADK samples and similar) | MIT (wshobson) · see repos |
| `fabius-archivum` (memory, LLM-wiki) | Andrej Karpathy's "the wiki pattern" — incrementally-built personal knowledge bases ([gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)) | — |
| `fabius-archivum` (vector engine) | the `fabius-vec` knowledge engine, after open vector-search work (turbovec / ruvector) | see repos |
| `fabius-archivum` (memory mechanisms) | claude-mem (thedotmack), oh-my-claudecode (Yeachan-Heo) | see repos |
| `fabius-mercatus` (go-to-market) | marketingskills (coreyhaines31) | see repo |
| `fabius-praesidium` (defensive security) | Anthropic-Cybersecurity-Skills (mukul975) — defensive guidance only | **Apache-2.0** |
| `fabius-ludus` (game craft) | Claude-Code-Game-Studios (Donchitos) | see repo |

### Apache-2.0 note (security corpus)

The cybersecurity skills corpus (mukul975/Anthropic-Cybersecurity-Skills) is **Apache-2.0**. `fabius-praesidium` currently re-expresses its **defensive** concepts (STRIDE, the OWASP pass, the finding contract) in fabius's own voice — inspiration, no files carried, and nothing offensive imported. If any Apache-2.0 file is later bundled into the corpus, its `LICENSE` and `NOTICE` ship alongside it, with changes stated, per the license.

## Research grounding — the agent-research canon

fabius's routing policy is sourced to the literature, with a direct-vs-analogy honesty ledger. The full mapping is in [`skills/fabius/references/agent-research.md`](../skills/fabius/references/agent-research.md) and [RESEARCH.md](../RESEARCH.md); every arXiv id was checked against the paper's abstract. Primary sources:

- **Reasoning / acting:** ReAct (2210.03629), Tree of Thoughts (2305.10601), Reasoning-via-Planning / RAP (2305.14992), Graph of Thoughts (2308.09687), Chain of Abstraction (2401.17464).
- **Tools / self-improvement:** Toolformer (2302.04761), Reflexion (2303.11366), Self-Refine (2303.17651), Voyager (2305.16291), DSPy (2310.03714).
- **Memory:** MemGPT (2310.08560), LongMem (2306.07174), Generative Agents (2304.03442), *Memory for Autonomous LLM Agents* — Du, 2026 (2603.07670, CC-BY-4.0).
- **Efficiency / surveys:** *Toward Efficient Agents* — Yang et al., 2026 (2601.14192, CC-BY-4.0), and the Wang autonomous-agents survey.
- **Borrowed-by-analogy math (labelled as such):** Flow Matching (2210.02747), Consistency Models (2303.01469), Classifier-Free Guidance (2207.12598), grounded in the MIT diffusion course (diffusion.csail.mit.edu).
- **Living indexes / reading lists:** zjunlp/LLMAgentPapers, luo-junyu/awesome-agent-papers, e2b-dev/awesome-ai-agents.

## Closing

Names inside the bundled references were aligned to fabius for consistency; the ideas are theirs, the synthesis and the system are ours. fabius stands on this open work and tries to credit it honestly. If you own one of these and want a change to the attribution — or a stronger license notice — open an issue and it will be fixed.
