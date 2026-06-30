---
name: fabius-concilium
description: >
  fabius's cross-model deliberation layer — convene a COUNCIL of heterogeneous models on ONE
  question, then aggregate their answers into a single better one: each model answers
  independently (first opinions) → each ranks the others' answers blind, with identities stripped
  (anonymized peer-review) → a chairman model synthesizes the ranked field into the final answer.
  This is ensemble epistemics — it spends model diversity to cut the single-model error and bias a
  lone answer carries. Use when the user says "council" / "llm-council" / "ask several models" /
  "panel of models", or when a question is high-stakes or genuinely contested and one model's miss
  is costly enough to pay N+N+1 calls. Distinct from fabius-cohors (which splits the WORK across
  task-specialist agents); concilium aggregates one ANSWER across whole models. The exact stage
  prompts, the anonymization + ranking math, and a zero-dependency runnable reference
  (references/council.mjs, every model via one OpenRouter key) live in references/council-protocol.md.
---
<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->

# Fabius Concilium — convene the council, synthesize one answer

*Concilium* — the summoned assembly, the council called to deliberate before the decision is taken. fabius's whole identity is *runs on every major model, one console*; concilium is the layer that turns that into an epistemic advantage — instead of routing a question to the single best model, it seats several, lets them answer and judge each other blind, and has a chairman fuse the field. The product is one answer that is more accurate and less idiosyncratic than any single seat produced. Patterned on karpathy's *llm-council*.

## The lean gate first — does this need a council at all? (`fabius-parcus`)

A council is the **heaviest** thing in this whole system on cost and latency: **N + N + 1** model calls (N first opinions, N reviews, one chairman) where a single strike is one call. So the question comes before the council does:

- **Convene when** the answer is high-stakes and a wrong one is expensive (a design/architecture call, a medical/legal/financial *analysis*, a contested factual claim, a research synthesis), **or** the question is genuinely open and you want disagreement surfaced rather than one model's house style, **or** the user explicitly asks for a panel.
- **Don't convene when** the task is mechanical, has one correct answer a single model reliably gets (arithmetic, a rename, boilerplate), is latency-sensitive, or when *one strong model + an independent verifier* (`fabius-disciplina`) already covers the risk. A council is not a substitute for running the code.

The value of a council is **disagreement**. If the seats won't disagree, you paid N× for one opinion. Seat diversity, not seat count.

## The three stages

1. **First opinions** — send the user's question, unmodified, to every council member in parallel. Each answers independently, never seeing the others. Same prompt, N models → N raw answers. (Fan-out; no barrier needed until stage 2.)
2. **Anonymized peer-review** — give each model the *other* answers with **every identity stripped** ("Response A / B / C…", order shuffled per reviewer), and ask it to rank them on accuracy and insight with a one-line reason each. Anonymity is the point: it kills the brand-name bias where models flatter a name they recognize (or their own text). This is the blind-judge discipline — `fabius-doctrina` owns *why* a blind judge is the honest one.
3. **Chairman synthesis** — one designated model receives the full field (all first opinions + all rankings, now de-anonymized for the chair) and writes the **final answer**: not a vote tally and not a copy of the top-ranked seat, but a reasoned merge that takes the strongest correct points, resolves the contradictions the council exposed, and flags anything the seats genuinely split on.

## Seating the council

- **Pull diversity across providers**, not three checkpoints of one family — Anthropic · OpenAI · Google · Mistral · Groq, the same roster the `fabius` router already speaks to. Cross-provider disagreement is the signal; same-family seats correlate and waste the spend.
- **3–5 seats** is the working band. Two can't break a tie; past five, cost climbs and rankings flatten. Odd counts ease tie-breaks.
- **The chairman is a strong-tier model** (it does the hardest reasoning — the merge) and **may be a seat** or a separate model; `fabius` (R11) picks the tier. Seats can run a cheaper tier than the chair.
- **Surface the seats and the chair** to the user — a council whose membership is hidden can't be trusted or reproduced.

## Aggregation — how rankings become an order

- Convert each reviewer's ranking to points (e.g. Borda: top of K seats scores K−1, next K−2, … last 0), **sum across reviewers**, present the leaderboard. A model **never ranks its own** answer (it can't see which is its own — that's what anonymization buys, but exclude-self on the back end too).
- The leaderboard **informs** the chairman; it does not *override* it. Majority-wrong is a real failure mode — if four weak seats converge on a plausible error and one strong seat is right, a pure vote loses. The chairman's job is to catch that, which is why the chair reasons over the *content*, not just the tally.
- **Ties / near-ties** → hand both to the chairman as a live disagreement to resolve, don't coin-flip.

## Anti-patterns — how a council goes wrong

- **Correlated seats** — all one provider/family → false consensus, no real review. Diversify or don't bother.
- **Leaked identities** — any "as Claude, I…" or unshuffled order in stage 2 reintroduces brand bias and voids the blind. Strip hard, shuffle per reviewer.
- **Chairman as parrot** — if the chair just restates the #1 answer, the synthesis added nothing; require it to *merge and resolve*, citing what it took from where.
- **Council as verifier** — N models agreeing that code is correct is not the same as running the code. Proof still comes from `fabius-disciplina` (run it, show the evidence).
- **Council for a one-answer task** — paid N× to confirm 2+2. The lean gate exists to stop this.

## Single-owner boundary

concilium owns exactly one concern: **cross-model deliberation — convening whole models on one question and aggregating their answers into a better single answer.** It is not the others:

- **`fabius-cohors`** splits the *work* across task-specialist agents (architect / coder / reviewer), each a different role on a different slice, then merges sub-results. concilium runs the *same* question through whole *models* and merges *answers*. cohors' "parallel fan-out → reduce" is the mechanical cousin; the difference is division-of-labor vs aggregation-of-judgment. A council member is not an agent with tools and a role — it's a model giving an opinion.
- **`fabius-doctrina`** owns LLM-evaluation rigor (held-out sets, blind judges, regression gates). concilium *borrows* the blind-judge discipline for stage 2 and points at doctrina for why it's honest; it doesn't own evaluation.
- **`fabius-disciplina`** still owns proving. A council produces a better *answer*; disciplina turns "answer" into "verified".
- **`fabius`** (router) picks which seats and which tiers; **`fabius-parcus`** owns the gate above (convene at all?).

## Output contract

A council run returns, in order: **(1)** the seats + chairman named; **(2)** each first opinion (tabbed/collapsible, one per seat); **(3)** the anonymized ranking leaderboard with per-reviewer reasons; **(4)** the chairman's synthesized final answer, with the disagreements it had to resolve called out. The final answer leads when the user wants the result; the rest stays one expand away (progressive disclosure).

## Run it

The exact stage prompts, the anonymization + shuffling scheme, the Borda aggregation, the de-anonymization-for-chair step, and a **zero-dependency runnable reference** — `references/council.mjs` (Node ≥18, every model through one OpenRouter key; `node references/council.mjs --selftest` checks the wiring with no key, no cost) — are in [`references/council-protocol.md`](references/council-protocol.md). The live tier is one API key the user configures; the protocol, prompts, and aggregation are pure.

Pairs with: `fabius-parcus` (the convene-at-all gate), `fabius` (seat + tier selection), `fabius-doctrina` (the blind-judge discipline it borrows), `fabius-cohors` (the orchestration cousin it's distinct from), `fabius-disciplina` (prove the final answer, don't just trust the consensus).
