---
name: fabius-disciplina
description: >
  fabius's engineering-discipline layer — one repeatable procedure for HOW the agent builds,
  debugs, and finishes: brainstorm → plan → test-first → prove, plus grilling ambiguity and
  root-cause debugging. Use before building any feature, fixing any bug, or refactoring — any
  task bigger than a one-line edit. Also use when the user says "plan this", "grill me",
  "debug this", "find the root cause", or "is this actually done?". Worked debug walkthrough and
  test anti-patterns live in references/process-playbook.md; the full process library — the craft
  skills (brainstorm, prototype, TDD, grill, handoff, writing) and the discipline skills
  (systematic-debugging, writing-plans, verification-before-completion, parallel agents) — lives in
  references/process/.
---
<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->

# Fabius Disciplina — understand, plan, build proven, finish

*Disciplina* — training, the drilled habit. Discipline beats guessing. Six phases; each leaves something durable behind so the next task starts further along.

## 1. Brainstorm — before any creative work

Don't open with code. Turn the idea into a design through dialogue:

- **Scout the context first** — read the files, the recent commits, the pattern already in use.
- **Scope check** — if the request is really several independent subsystems, say so and split it before refining any detail.
- **Ask clarifying questions one at a time**, multiple-choice where you can. Hunt for purpose, constraints, the definition of done.
- **Offer 2–3 approaches with trade-offs**, lead with your recommendation and the reason.
- **Present the design in sections sized to the complexity**; get a nod per section.
- **Gate:** no implementation until the design is shown and approved — even on "simple" jobs, because simple is exactly where an unexamined assumption costs the most rework.

## 2. Grill the ambiguity

When the plan leans on fuzzy words or domain terms, interrogate one question at a time until every branch of the decision tree is closed. A new term that collides with the project's existing vocabulary is a stop-and-resolve event, not a thing to guess past. The instant a fact crystallizes, write it down (→ `fabius-archivum`). Sharpening the language now is cheaper than the rewrite later.

## 3. Plan — for multi-step work

Write the plan as `step → verify` lines:

```
1. [step] → verify: [the check that proves it]
2. [step] → verify: [the check that proves it]
3. [step] → verify: [the check that proves it]
```

Strong, checkable criteria are what let you run the loop without a human in it. Keep each unit small and single-purpose — you reason better about code you can hold in your head at once, and a file growing fat is the signal it's doing too much.

## 4. Build test-first — the iron law

**No production code for non-trivial logic until a test fails first.**

Red → Green → Refactor:

1. **Red** — write the smallest test that fails for the right reason. Run it. Watch it fail.
2. **Green** — the minimum code that passes (climb the `fabius-parcus` ladder). Run it. Watch it pass.
3. **Refactor** — clean up with the test as your net. Green before, green after.

Cut vertical tracer-bullet slices: one thin end-to-end path that works beats five half-built layers that don't. The exceptions are narrow — throwaway prototypes, generated code, pure config — and each needs the human's sign-off. "Too simple to test" is a rationalization, not an exception.

## 5. Debug by root cause — never patch the symptom

When something breaks, before proposing any fix:

1. **Reproduce** — a reliable, minimal repro. Can't reproduce it → you don't understand it yet.
2. **Minimize** — strip the case until only the failing essence is left.
3. **Hypothesize** — list a few ranked, falsifiable causes before you test any one. Anchoring on a single guess fixes the wrong thing.
4. **Instrument** — add the one log or assert that confirms or kills the top hypothesis. Let the evidence choose.
5. **Fix the cause** — not the symptom. A fix you can't explain is a coincidence wearing a fix's clothes.
6. **Regression-test** — the repro from step 1 becomes a permanent test.

After roughly three failed fixes, stop patching: the bug is probably architectural. Question the coupling and the design — don't reach for fix number four.

## 6. Prove before "done"

A claim of success needs evidence. Before reporting complete:

- Run the thing. Show the passing check, the output, the live behavior — not "should work".
- Every acceptance criterion from the plan: demonstrably met.
- Skipped a step? say so. Tests failing? show the output. Report outcomes faithfully.

"Almost works" and a code-only answer don't count. Hit the real path and watch it.

The full process library — craft skills (brainstorm, prototype, TDD, grill, handoff, writing) and discipline skills (systematic-debugging, writing-plans, verification-before-completion, parallel agents) — is in `references/process/`; the worked debug walkthrough and test anti-patterns in `references/process-playbook.md`.

## Routing the reasoning — when to branch, when to reflect

From the agent-research canon (full set in the router's [routing-policy.md](../fabius/references/routing-policy.md)):

- **Reason → act → observe (R5).** In tool/sub-agent work, never act on an assumed result — one thought, one action, read the *real* observation, then continue. After ~3 cycles with no progress toward the verify condition, stop and re-plan (the same 3-strike trigger as the debug rule above). *(ReAct)*
- **Plan in placeholders (R6).** For any task that will call ≥2 tools, finish a tool-free plan naming each tool *output* as a placeholder before binding a call — so the skeleton can be grilled, independent calls parallelize, and a wrong result re-runs one tool, not the plan. *(Chain of Abstraction)*
- **Branch only when partials are scorable (R7).** Keep brainstorm/plan a single pass by default; escalate to a scored tree (generate → score → prune) only when a cheap evaluator can rank half-finished candidates and early mistakes are costly. No evaluator → single path. *(Tree of Thoughts)*
- **Reflect on a real signal (R8).** Enter a refine loop only on an attributable critique. A hard oracle (test/compiler/schema) earns ~3 iterations; soft self-critique caps at 1–2; no signal → ship once, route to human review. *(Reflexion + Self-Refine)*
- **Reflect-then-retry, escalate when hypotheses run out (M4).** On a verifiable failure, prepend a one-paragraph reflection (what was tried · the failure signal · inferred cause · one changed action) to the retry; if it repeats the prior cause with no new hypothesis, stop and escalate to a human (hard cap ~3 — the same trigger as the debug rule above). *(Reflexion)*

Pairs with: `fabius-parcus` (every artifact stays minimal), `fabius-archivum` (resolved facts and post-mortems get filed).
