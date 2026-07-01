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
