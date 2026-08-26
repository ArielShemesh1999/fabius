---
name: fabius-concilium
description: >
  fabius's cross-model deliberation layer — convene a COUNCIL of heterogeneous models on ONE
  question, then aggregate their answers into one evidence-aware synthesis: each model answers
  independently (first opinions) → each ranks ALL anonymized answers blind, its own included, while
  the backend removes its self-score (anonymized peer-review) → a chairman synthesizes the field.
  This is ensemble epistemics — it uses model diversity to expose possible single-model error and
  bias; whether it improves an answer must be measured for the task. Use when the user says "council" / "llm-council" / "ask several models" /
  "panel of models", or when a high-stakes question has already survived N samples of the single
  strongest model and they failed the SAME way — correlated error, not mere disagreement, is what
  earns at most 3N+1 completion calls including retries (M10). Distinct from fabius-cohors (which splits the WORK across
  task-specialist agents); concilium aggregates one ANSWER across whole models.
when_to_use: >
  "get a second opinion from other models", "cross-check this answer", "have the models vote",
  a high-stakes question where repeated samples of one strong model fail the same way.
license: UNLICENSED
metadata:
  author: Ariel Shemesh
---
<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/shear559/fabius -->

# Fabius Concilium — convene the council, synthesize one answer

*Concilium* — the summoned assembly, the council called to deliberate before the decision is taken. fabius's whole identity is *one set of rules above every model*; concilium seats several models, lets them answer and judge each other blind, and has a chairman fuse the field. Its aim is to expose disagreement and reduce idiosyncratic error; it does not guarantee superiority over the best single seat, so measure that on the task. Patterned on karpathy's *llm-council*.

## The lean gate first — does this need a council at all? (`fabius-parcus`)

A council is the **heaviest** thing in this whole system on cost and latency. With N configured seats, M surviving first opinions, and R malformed-ballot retries, it makes exactly **N + M + R + 1** completion calls: N first-opinion attempts, M initial reviews, R retries, and one chairman. Because `0 ≤ M ≤ N` and `0 ≤ R ≤ M`, reserve at most **3N + 1** calls; the clean all-live/no-retry path is `2N + 1`. So the question comes before the council does:

- **Convene when** the answer is high-stakes and a wrong one is expensive (a design/architecture call, a medical/legal/financial *analysis*, a contested factual claim, a research synthesis) **and** rung one below has already failed the *same* way, **or** the user explicitly asks for a panel.
- **Don't convene when** the task is mechanical, has one correct answer a single model reliably gets (arithmetic, a rename, boilerplate), is latency-sensitive, or when *one strong model + an independent verifier* (`fabius-disciplina`) already covers the risk. A council is not a substitute for running the code.

Rung one is **self-samples of the strongest seat**, not a panel: N samples of one strong model, reduced by vote or judge. Convene the heterogeneous council only when those samples fail the **same** way — correlated error, not mere disagreement (`fabius` M10; `fabius-parcus` owns the gate). Once seated, the council earns its cost through disagreement: if the seats won't disagree, you paid N× for one opinion. Seat diversity, not seat count — and never diversity bought *below* the bar (*Seating the council*, next).

## The three stages

1. **First opinions** — send the user's question, unmodified, to every council member in parallel. Each answers independently, never seeing the others. Same prompt, N models → N raw answers. (Fan-out; no barrier needed until stage 2.)
2. **Anonymized peer-review** — give each model **all** the answers (its own included), **every identity stripped** ("Response A / B / C…", order shuffled per reviewer), and ask it to rank them on accuracy and insight with a one-line reason each. Anonymity is the point: it kills the brand-name bias where models flatter a name they recognize (or their own text). This is the blind-judge discipline — `fabius-doctrina` owns *why* a blind judge is the honest one.
3. **Chairman synthesis** — one designated model receives the full field (all first opinions + all rankings, now de-anonymized for the chair) and writes the **final answer**: not a vote tally and not a copy of the top-ranked seat, but a reasoned merge that takes the strongest correct points, resolves the contradictions the council exposed, and flags anything the seats genuinely split on.

## Seating the council

- **Set the admission bar before the seating chart.** A weak seat can lower the aggregate even when it adds provider variety. Every seat must be a model you would have been willing to ask *alone* for this question, and the roster must be evaluated on the target task. If only one model clears the bar, don't pad the table: that *is* rung one — sample that model N times and aggregate its own answers.
- **Then pull diversity across providers**, not three checkpoints of one family — Claude · GPT · Gemini · DeepSeek · Mistral · Grok and the rest of the field fabius already runs above. Cross-provider disagreement is what the panel is buying — but only from seats that already cleared the bar; same-family seats correlate and waste the spend.
- **3–5 seats** is the working band. Two can't break a tie; past five, cost climbs and rankings flatten. Odd counts ease tie-breaks.
- **The chairman is a strong-tier model** (it does the hardest reasoning — the merge) and **may be a seat** or a separate model; `fabius` (R11) picks the tier. Seats all sit at **one** tier and only the chair may sit above it — never mix capability tiers inside the pool, and never seat a weaker model for *diversity* (M10).
- **Surface the seats and the chair** to the user — a council whose membership is hidden can't be trusted or reproduced.

## Aggregation — how rankings become an order

- Convert each reviewer's ranking to points (e.g. Borda: top of K seats scores K−1, next K−2, … last 0), **sum across reviewers**, present the leaderboard. Every model ranks **all K anonymized answers exactly once, its own included** because it cannot reliably identify itself; after de-shuffling, the backend discards the score in its self-slot so no seat can lift itself.
- The leaderboard **informs** the chairman; it does not *override* it. Majority-wrong is a real failure mode — if four weak seats converge on a plausible error and one strong seat is right, a pure vote loses. The chairman's job is to catch that, which is why the chair reasons over the *content*, not just the tally.
- **Ties / near-ties** → hand both to the chairman as a live disagreement to resolve, don't coin-flip.

## Anti-patterns — how a council goes wrong

- **Correlated seats in a convened council** — once you've paid for a panel, all-one-family seats give false consensus and no real review. Diversify or don't bother. (Deliberate self-samples of one model are the opposite case — that's rung one under M10, not this anti-pattern.)
- **A charity seat** — a cheaper or weaker model let in *because* it's different. It doesn't add a perspective, it lowers the pool's average quality, and the Borda tally can't tell those two apart. Diversity is a tiebreaker among equals, never a substitute for capability.
- **Leaked identities** — any "as Claude, I…" or unshuffled order in stage 2 reintroduces brand bias and voids the blind. Strip hard, shuffle per reviewer.
- **Chairman as parrot** — if the chair just restates the #1 answer, the synthesis added nothing; require it to *merge and resolve*, citing what it took from where.
- **Council as verifier** — N models agreeing that code is correct is not the same as running the code. Proof still comes from `fabius-disciplina` (run it, show the evidence).
- **Council for a one-answer task** — paid N× to confirm 2+2. The lean gate exists to stop this.

## Single-owner boundary

concilium owns exactly one concern: **cross-model deliberation — convening whole models on one question and aggregating their answers into one synthesized answer.** It is not the others:

- **`fabius-cohors`** splits the *work* across task-specialist agents (architect / coder / reviewer), each a different role on a different slice, then merges sub-results. concilium runs the *same* question through whole *models* and merges *answers*. cohors' "parallel fan-out → reduce" is the mechanical cousin; the difference is division-of-labor vs aggregation-of-judgment. A council member is not an agent with tools and a role — it's a model giving an opinion.
- **`fabius-doctrina`** owns LLM-evaluation rigor (held-out sets, blind judges, regression gates). concilium *borrows* the blind-judge discipline for stage 2 and points at doctrina for why it's honest; it doesn't own evaluation.
- **`fabius-disciplina`** still owns proving. A council produces a synthesized *answer*; disciplina turns "answer" into "verified".
- **`fabius`** (router) picks which seats and which tiers; **`fabius-parcus`** owns the gate above (convene at all?).

## Output contract

A council run returns, in order: **(1)** the seats + chairman named; **(2)** exact call accounting (configured/live seats, retries, actual, cap); **(3)** each first opinion (tabbed/collapsible, one per seat); **(4)** the anonymized ranking leaderboard with per-reviewer reasons; **(5)** the chairman's synthesized final answer, with the disagreements it had to resolve called out. The final answer leads when the user wants the result; the rest stays one expand away (progressive disclosure).

## Run it

The exact stage prompts, strict ballot schema, retry/drop policy, roster preflight, Borda aggregation, and a **zero-dependency runnable reference** — `references/council.mjs` (Node ≥18, every model through one OpenRouter key; `node references/council.mjs --selftest` checks the wiring with no key, no cost) — are in [`references/council-protocol.md`](references/council-protocol.md). The live tier is one API key the user configures; the protocol, prompts, and aggregation are pure.

Pairs with: `fabius-parcus` (the convene-at-all gate), `fabius` (seat + tier selection), `fabius-doctrina` (the blind-judge discipline it borrows), `fabius-cohors` (the orchestration cousin it's distinct from), `fabius-disciplina` (prove the final answer, don't just trust the consensus).
