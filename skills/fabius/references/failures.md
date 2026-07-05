# Fabius — failures log

The verbal episodic memory of routing. A Reflexion-style lesson log: when a route fails in a way the [routing policy](routing-policy.md) didn't prevent, write the lesson here so the next attempt is conditioned on it — **no fine-tuning, the learning lives in this file.**

This file is **empty by design** and grows from *real incidents only* — never from anticipation (`fabius-parcus`: a rule that no failure has demanded yet does not exist). A repeated lesson here is the signal that a routing rule (R1–R13 / M1–M9) needs to change; promote it.

## How an entry is written

On a verifiable failed route, append one entry. Keep it to four lines — what was tried, the concrete failure signal, the inferred cause, the one changed action — so the retry can read it in seconds.

```markdown
## [YYYY-MM-DD] <one-line symptom>

- **Tried:** <the route / decision taken>
- **Signal:** <the concrete, attributable failure — a test, an error, an observation; not a vibe>
- **Cause:** <the inferred root cause>
- **Change:** <the single different action next time> → (if it recurs) promote to routing-policy.md as rule R<n>/M<n>
```

## The loop (R8 · M4)

1. A route fails against a **verifiable signal** (test, compiler, schema, a real observation). A vibe is not a signal — if there's none, ship once and route to human review.
2. Write the entry above. Prepend it to the retry's context.
3. Retry. If the new reflection repeats the prior cause with no new hypothesis, **stop and escalate** — don't loop (hard cap ~3).
4. When the same lesson appears ~twice, it's no longer an incident — it's a missing rule. Promote it into [`routing-policy.md`](routing-policy.md) and delete the duplicates here.

---

<!-- entries below, newest first -->

**FAB-025 · Stub collapse on long deliverables (Run 7, measured).**
What happened: under the full stance, a mid-tier model answered a long-deliverable probe (Postgres zero-downtime migration plan) with a 363-character stub referring to a plan it never included — 1.5/28 vs 28/28 for BASE and FAB_MEMORY.
Signal: judge score collapse on a single probe; the artifact was a pointer to the deliverable, not the deliverable.
Cause: the stance's compression instinct ("say less") tips into deliver-by-reference on LONG deliverables — the model satisfies terseness pressure by referencing work instead of doing it.
Changed action: the prove-before-done gate now checks the artifact IS the deliverable — rubric item one on every prose exit gate is existence/completeness (new M11), and long-deliverable routes state an explicit section/length floor before generation.

**FAB-026 · Memory is two-sided (Run 7, measured).**
What happened: recalled snapshots lifted design/product +4.91/28 (prior decisions bind correctly) but cost security −1.57 and error-recovery −1.37.
Signal: per-dimension score deltas with memory ON vs OFF carrying opposite signs by task family.
Cause: recalled context primes continuation of prior framing; security and incident work needs fresh-eyes rigor that recall actively distracts. The frontier mechanism matches: agents imitate whatever they retrieve (experience-following, arXiv:2505.16067 — direct).
Changed action: archivum recall is dampened or disabled on security/incident/error-recovery routes and stays verify-gated everywhere (new M12); R1 classification now sets the recall dial at intake.

**FAB-027 · Layer stacking pays on the fast tier (Run 7, measured).**
What happened: Haiku gained +0.73 from the stance and +0.73 more from memory (25.27→26.00→26.73) on 11–14% less output — monotonic across production-shaped tasks.
Signal: monotone score increase with each layer at reduced token cost, no dip.
Cause: the earlier "trivial one-liner dip" came from toy problems; on production-shaped tasks the small model benefits from both discipline and context everywhere.
Changed action: stance+memory stay ON for the fast tier on production-shaped tasks; the strip-layers-for-small-models heuristic is retired except for true one-liners.

**FAB-028 · The stance's largest objective edge is adversarial (Run 7, measured).**
What happened: stress-tier objective check-rate rose 89.9→93.7 under the stance across injection payloads, false premises, and conflicting instructions.
Signal: check-rate delta concentrated on adversarial probes — the largest objective edge in the run.
Cause: the stance's assume-less/verify discipline defends exactly the surface hostile prompts attack.
Changed action: the stance is mandatory — never trimmed for budget — on any input flagged injection-suspect, contradictory, or false-premise-shaped; stress-shaped prompts route through the full stance before any layer trimming.

**LIT-W1 · False green under a weak oracle (frontier warning).**
What could happen: a coding route reports done because inherited tests pass, but ~1 in 5 such passes is semantically wrong under weak suites (SWE-ABS, arXiv:2603.00520 — direct on agent patches).
Changed action: R15 — audit/strengthen the oracle first; a green from an unaudited gate ends the step, never the route.

**LIT-W2 · TDD boilerplate backfires (frontier warning).**
What could happen: injecting generic "write tests first" instructions without mapped covering tests INCREASED regressions to 9.94% vs 6.08% for doing nothing (TDAD, arXiv:2603.17973 — direct).
Changed action: R16 — disciplina's test-first step binds to the source→tests impact map or stays silent; TDD slogans removed from all prompt templates.

**LIT-W3 · Long green streak = decaying gate (frontier warning).**
What could happen: as a route's pass rate approaches the gate's ceiling, the agent starts satisfying the check instead of the task — reward hacking and signal saturation (The Verification Horizon, arXiv:2606.26300 — direct for coding agents, partly position-style evidence).
Changed action: R12 strengthen — a long green streak triggers gate tightening, and every generator upgrade forces a gate revision.

**LIT-W4 · Debate flips right answers wrong (frontier warning).**
What could happen: in a multi-model debate, accuracy decays over rounds as models conform to persuasive but incorrect peers — even when stronger models outnumber weaker ones (arXiv:2509.05396 — direct on LLM debate).
Changed action: M10 — concilium defaults to best-model self-samples; one debate round max, extended only when a verifiable signal improved after round one.

**LIT-W5 · Silent context rot before overflow (frontier warning).**
What could happen: accuracy degrades non-uniformly long before the window limit — even on trivially simple tasks — so a loop that compacts only at overflow has already been reasoning on rotten context (Chroma Context Rot 2025; Du et al., arXiv:2510.05381 — analogy, single-turn measurements).
Changed action: M13 — the resident-token budget is set below the advertised window at loop setup and compaction fires on the budget, never on overflow.

**LIT-W6 · Memory store pollution compounds (frontier warning).**
What could happen: one unverified bad record contaminates runs that lean on it, and their outputs re-enter the store — error propagation measured on LLM-agent memory (arXiv:2505.16067 — direct).
Changed action: M7/M12 — outcome-gated writes, in-session deletion of failure-implicated records, and a match+provenance check between every retrieval and the prompt.
