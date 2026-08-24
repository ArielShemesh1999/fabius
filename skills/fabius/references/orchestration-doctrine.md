<!-- © 2026 Ariel Shemesh · fabius · reference depth for skills/fabius/SKILL.md -->

# The orchestration doctrine — the goal is the user's; the machinery is fabius's

This file is the router's deepest contract, from fabius's own research: how a stated goal
becomes the *smallest sufficient set of machinery* that achieves it at high quality. The
proven core (R1–R13 · M1–M9) and the researched frontier layer (R14–R16 · M10–M13) —
[`routing-policy.md`](routing-policy.md) — govern each decision;
this file states the doctrine they add up to — one flow, capability-first, priced at every
step, stopped the moment another step can no longer change the outcome.

**The premise.** The user chooses the goal. fabius chooses the machinery. Never the reverse:
the user is never asked to pick tools, tiers, or research depth — naming the outcome is the
whole interface. fabius is loyal to the result, never to a provider.

## The flow — one spine for every task

```
Intent → Understand → Plan → Select capabilities → Select providers & tier
       → Execute → Evaluate → Research more ONLY while it pays → Stop → Deliver
```

This is the Sense → Classify → Route → Strike → Prove → Compound loop of the router contract,
written as an orchestration spine. A trivial task collapses the spine to one action; a complex
one expands it — the spine flexes, the gates on it never do.

## 1 · Capability-first — name the job, not the tool

Never architect around a tool's name. Name the *capability* the task needs —
`research.web` · `research.deep` · `data.analyze` · `code.execute` · `document.create` ·
`slides.create` · `visual.diagram` · `visual.infographic` · `image.generate` ·
`meeting.capture` · `sales.gtm` · `browser.execute` · `memory.recall` · `message.draft` —
then fill it with whatever the harness actually exposes: an MCP server, a CLI, an API the user
connected, or the model's own native ability. The provider behind a capability can change
without touching a single routing decision; that indirection is what keeps the doctrine stable
while the tool landscape churns. Corollary: **no external tool is the default.** The first
candidate for any capability is native ability at zero marginal cost; a tool must beat it
(R3).

## 2 · Provider selection — when several tools fill one capability

Choose by measured fit, not familiarity: quality on this task shape · specialization · cost ·
latency · reliability · privacy (where the data travels) · granted permissions · what the
current context already holds · track record in the failure log. When the choice is close,
prefer the one already warm in context — switching has a price too.

**Graceful fallback is part of the selection.** A provider failing is a routing event, not a
task failure: fall to the next provider, then to native ability, then to a different approach
to the same goal. No single dependency is allowed to kill a workflow.

## 3 · Model routing — best model for the step, not one model for everything

The same doctrine, applied to the engine itself: a cheap tier for mechanical low-judgment
steps, a reasoning tier for ambiguity and architecture, a specialized tier where one is
genuinely stronger (R11). Escalate on a *miss*, never on a guess. A multi-step task may
legitimately cross tiers mid-flight.

## 4 · Adaptive planning — depth follows stakes

No fixed workflow. Plan depth is set by: complexity · risk · importance · information already
in hand · confidence the decision needs · time · cost · permissions available. A simple task
ends in one action. A high-stakes one composes layers, verifiers, and — rarely — a council.
The plan is placeholders first, bindings last (R6), so independent steps run in parallel.

## 5 · Adaptive research and the stopping logic

Research aggressively while it creates value — stop when it doesn't. After *every* research
step, one question: **what is the highest-value next action, and is it still worth taking?**

```
EV(next action) ≈ information gain × importance × decision impact
                  − cost − latency − redundancy
```

Stop when any of these holds: confidence suffices for the decision at hand · evidence has
saturated (new sources repeat known ones) · the decision is already stable · marginal gain
has gone flat · cost now exceeds expected value · no remaining research path is likely to
change the outcome. This is the same expected-loss inequality that governs every machinery
call (R3 · M1), pointed at research itself; the long-horizon form is the dual exit gate (R12).
The aim is never maximum research — it is the smallest sufficient evidence base for a
high-quality answer.

## 6 · Decision stability — the stop that outranks confidence

Before any further step, ask: **could anything I can still plausibly find change the
decision?** If no — stop, even mid-plan. Stability beats score-polish: once the answer is
already determined, spending twenty more searches to move confidence from 94% to 96% is pure
waste. A stable *negative* ends research just as decisively as a stable positive.

## 7 · Execute → evaluate — no output is trusted on arrival

Every action's result is observed and judged before the next binds (R5 · R8): did it succeed ·
does it answer the need · does it contradict anything held · does it need verification ·
retry, or a different provider, or one more layer — or is the task already done? Evaluation is
what turns a pile of tool calls into a run.

## 8 · Verification — priced like everything else

Significant work never rides on a single unchecked output: cross-source checks, a second
independent pass, deterministic validation (tests, schema, execution — a failing exit
overrules any favorable review), source-quality weighting. But the verifier obeys the same
inequality it enforces — spawn a reviewer only when the expected loss it removes clears its
cost (M1). Verification is a value decision, not a ritual.

## 9 · Permission — availability is never authority

Having a capability and being allowed to fire it are different facts, kept separate. Actions
climb a ladder — **READ → ANALYZE → DRAFT → WRITE → EXECUTE** — and each rung is granted
separately; drafting a message is not sending it. Irreversible or outward-facing actions sit
behind explicit approval regardless of rung (the runner's gate holds them even in autonomous
mode). Least privilege is the default posture, per the cohors schema.

## 10 · Shared context — no stage starts from zero

One task state travels the whole spine: the goal · findings and evidence · decisions made ·
artifacts produced · confidence · open questions. Every capability reads it and writes back to
it; the scout's findings feed the plan, the plan feeds the strike, the strike's result feeds
the proof — nothing re-derives what the run already knows. Across sessions this is
`fabius-archivum`: what survives the verify gate compounds.

## 11 · Decision receipts — routing is stated, never silent

Every significant routing choice is visible in the run itself: which capability fired and why
· why this provider · roughly what it cost in steps · the signal that kept research going and
the one that stopped it. A route must be a documented decision, not a mood — that is what makes a bad
route debuggable and a good one repeatable.

## 12 · Learning from execution — routes improve

Outcomes feed back: which provider actually delivered on which task shape · which workflow
shape keeps failing · where extra research genuinely flipped a decision and where retries were
waste. Verified lessons land in memory (M6 · M7); a route that failed in a way the policy
didn't prevent goes in [`failures.md`](failures.md). The router the next task meets is
sharper than the one this task met.

## The maxim, priced

Scout wide — explore broadly enough to truly understand the problem. Strike narrow — deploy
only the machinery that materially improves the outcome, and stop exactly when additional work
stops paying for itself. Not maximum reasoning, maximum agents, or maximum tools:
**maximum decision quality per unit of complexity, cost, and time.**
