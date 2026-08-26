---
name: fabius-disciplina
description: >
  fabius's engineering-discipline layer — one repeatable procedure for HOW the agent builds,
  debugs, and finishes: scope → plan → source/test impact map → strengthen the oracle → prove, plus grilling ambiguity and
  root-cause debugging. Use before building any feature, fixing any bug, or refactoring — any
  task bigger than a one-line edit. Also use when the user says "plan this", "grill me",
  "debug this", "find the root cause", or "is this actually done?". Worked debug walkthrough and
  test anti-patterns live in references/process-playbook.md; the full process reference library — craft
  material (prototype, TDD, grill, handoff, writing) and discipline material (brainstorming,
  systematic-debugging, writing-plans, verification-before-completion, parallel agents) — lives in
  references/process/. The on-device prove loop for a UI app — build + assert state on a simulator,
  semantic-tree-first and token-cheap — lives in references/simulator-verify.md.
when_to_use: >
  "where do we start", "write the tests first", "it keeps regressing", "why is it slow",
  "why does it still fail", "walk me through the fix before coding".
license: UNLICENSED
metadata:
  author: Ariel Shemesh
---
<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · release evidence: PROVENANCE.md · github.com/shear559/fabius -->

# Fabius Disciplina — understand, plan, build proven, finish

*Disciplina* — training, the drilled habit. Discipline beats guessing. Six phases; each leaves something durable behind so the next task starts further along.

## 1. Scope in proportion to the decision

Start with enough context to make the next safe move; ceremony is not evidence:

- **Scout the context first** — read the files, the recent commits, the pattern already in use.
- **Scope check** — if the request is really several independent subsystems, say so and split it before refining any detail.
- **Proceed on clear, reversible work.** State any small assumption and implement; never demand a design approval for a trivial edit whose result is easy to inspect and undo.
- **Ask one question at a time only when the answer materially changes the artifact**, crosses an authorization boundary, or commits to an irreversible/high-risk choice.
- **Offer alternatives only when a real trade-off exists.** Lead with a recommendation. For a large or genuinely branching design, checkpoint at the decision boundary that changes the implementation.

## 2. Grill the ambiguity

When the plan leans on fuzzy words or domain terms, interrogate one question at a time until every branch of the decision tree is closed. A new term that collides with the project's existing vocabulary is a stop-and-resolve event, not a thing to guess past. The instant a fact crystallizes, write it down (→ `fabius-archivum`). Sharpening the language now is cheaper than the rewrite later.

## 3. Plan — for multi-step work

Write the plan as `step → verify` lines:

```
1. [step] → verify: [the check that proves it]
2. [step] → verify: [the check that proves it]
3. [step] → verify: [the check that proves it]
```

Two rules keep a plan working past the first few steps. **Re-state the remaining steps on a short cycle** — a plan written once at the top decays as the run gets long and the agent drifts into sub-goals nobody asked for; periodic re-injection measurably recovers the ground that drift costs. And **a plan with a phase missing is worse than no plan at all** — an incomplete skeleton actively steers the run wrong, where no plan at least leaves the model's own judgment intact. The phase that is never optional is *reproduce* (§5). The corollary is the lean one: don't pad the plan with phases this task doesn't need — a step bolted on early degrades the run instead of insuring it.

Strong, checkable criteria are what let you run the loop without a human in it. Keep each unit small and single-purpose — you reason better about code you can hold in your head at once, and a file growing fat is the signal it's doing too much.

## 4. Map impact, strengthen the oracle, then patch

A changed source file is protected only by a test that reaches the changed behavior and can fail for the regression. Before editing non-trivial behavior, build a compact **source → covering-test impact map**:

1. **Map the blast radius** — use imports/build graph, symbol search, test names, and coverage where available to list each touched source unit and its direct covering tests. Read those tests before the patch; proximity is not coverage.
2. **Audit the oracle** — identify the exact assertion that would catch the requested behavior. If none does, strengthen the nearest behavior-level test or add the smallest executable repro.
3. **Prove red on the intended behavior** — run the targeted check and observe the expected failure. A failure in setup, fixture, or unrelated code is not red.
4. **Patch the cause, then prove green** — make the smallest coherent change, run every mapped covering test, and refactor only while the same set remains green.
5. **Expand by impact** — run the broader suite/build/lint gate justified by the dependency map, not an arbitrary favorite command.

Cut vertical tracer-bullet slices: one thin end-to-end path that works beats five half-built layers that don't. Pure config, generated artifacts, throwaway prototypes, or a codebase with no viable test seam use the closest executable validator (schema/compiler/render/repro) and say what coverage is absent; they do **not** require approval theater or a boilerplate unit test. A generic “TDD” slogan never substitutes for the concrete impact map and oracle.

## 5. Debug by root cause — never patch the symptom

When something breaks, before proposing any fix:

1. **Reproduce** — a reliable, minimal repro. Can't reproduce it → you don't understand it yet.
2. **Minimize** — strip the case until only the failing essence is left.
3. **Hypothesize** — list a few ranked, falsifiable causes before you test any one. Anchoring on a single guess fixes the wrong thing.
4. **Instrument** — add the one log or assert that confirms or kills the top hypothesis. Let the evidence choose.
5. **Fix the cause** — not the symptom. A fix you can't explain is a coincidence wearing a fix's clothes.
6. **Regression-test** — the repro from step 1 becomes a permanent test.

After roughly three failed fixes, stop patching: the bug is probably architectural. Question the coupling and the design — don't reach for fix number four.

A **performance** regression runs the same six steps with a different instrument, because "slow" has no stack trace. Baseline on a fixed throttled profile, then **isolate by blocking one dependency at a time** and read the delta — never rank suspects by file size. **Compare medians of repeated runs, never a single sample** (identical runs swing wide enough to invent a regression), and **A/B the obvious optimization** before shipping it — a preload or a re-encode that measures as a no-op is a change, not an improvement. (Worked loop → `references/process-playbook.md`.)

## 6. Prove before "done"

A claim of success needs evidence. Before reporting complete:

- Re-read the source → covering-test map. Run the mapped tests plus the broader gate justified by the blast radius; name both.
- **Prove the oracle can catch the defect.** Where safe, make the targeted assertion fail by reverting/mutating the changed behavior, then restore it and show green. A test that stays green under the old behavior is not coverage.
- Run the thing. Show the passing check, the output, the live behavior — not "should work".
- Every acceptance criterion from the plan: demonstrably met.
- Treat suspicious test-runner output as a hypothesis: inspect the runner/config and reproduce the verdict before trusting it.
- Skipped a mapped test or could not strengthen an oracle? say so. Tests failing? show the output. Report outcomes faithfully.

"Almost works" and a code-only answer don't count. Hit the real path and watch it.

For a **UI app**, "hit the real path" means **run it on a device/simulator and assert the state** — the same prove rule `fabius-decor` ends on (verify live, not just in the code). Do it the cheap, robust way:

- **Assert via the semantic tree, not pixels.** Query the live UI by *meaning* (text / type / id) to check it reached the expected state — orders of magnitude cheaper than a screenshot and resilient to layout change. Reserve screenshots for visual-diff and bug reports.
- **Progressive-disclosure build output.** Don't dump the full build log — return a summary line + a result-bundle id, and fetch specific errors on demand. Cap and size everything you send the model.
- **The loop:** health-check the environment → build + test → boot/launch → assert state via the tree → screenshot only for visual confirmation → capture the full state (screenshot + hierarchy + logs) on failure.
- **Prove with a number where you can.** A before/after task-success rate beats "it built." (iOS `simctl`/`xcodebuild` workflow, the troubleshooting table, and the test recipes → `references/simulator-verify.md`.)

The full process reference library — prototype, TDD, grill, handoff, writing, debugging, planning, verification, and parallel-agent material — is in `references/process/`; those vendored pages are background patterns, while this root contract decides the active procedure. The worked debug walkthrough, performance-regression loop, and test anti-patterns are in `references/process-playbook.md`. On-demand depth for a large codebase, current-world fact, or browser UI — code graph, live-web checking, plan-as-files, real-browser verification, and test enforcement — is in `references/codebase-and-proof.md`. The tool stack — test frameworks, property/mutation testing, coverage, debuggers/profilers, and correctness linters → `references/testing-toolkit.md`.

## Routing the reasoning — when to branch, when to reflect

From the agent-research canon (full set in the router's [routing-policy.md](../fabius/references/routing-policy.md)):

- **Reason → act → observe (R5).** In tool/sub-agent work, never act on an assumed result — one thought, one action, read the *real* observation, then continue. After ~3 cycles with no progress toward the verify condition, stop and re-plan (the same 3-strike trigger as the debug rule above). *(ReAct)*
- **Plan in placeholders (R6).** For any task that will call ≥2 tools, finish a tool-free plan naming each tool *output* as a placeholder before binding a call — so the skeleton can be grilled, independent calls parallelize, and a wrong result re-runs one tool, not the plan. *(Chain of Abstraction)*
- **Branch only when partials are scorable (R7).** Keep brainstorm/plan a single pass by default; escalate to a scored tree (generate → score → prune) only when a cheap evaluator can rank half-finished candidates and early mistakes are costly. No evaluator → single path. *(Tree of Thoughts)*
- **Reflect on a real signal (R8).** Enter a refine loop only on an attributable critique. A hard oracle (test/compiler/schema) earns ~3 iterations; soft self-critique caps at 1–2; no signal → ship once, route to human review. *(Reflexion + Self-Refine)*
- **Reflect-then-retry, escalate when hypotheses run out (M4).** On a verifiable failure, prepend a one-paragraph reflection (what was tried · the failure signal · inferred cause · one changed action) to the retry; if it repeats the prior cause with no new hypothesis, stop and escalate to a human (hard cap ~3 — the same trigger as the debug rule above). *(Reflexion)*

Pairs with: `fabius-parcus` (every artifact stays minimal), `fabius-archivum` (resolved facts and post-mortems get filed).
