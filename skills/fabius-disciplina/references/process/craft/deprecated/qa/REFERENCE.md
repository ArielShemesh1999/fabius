---
name: fabius-disciplina-qa
description: Interactive QA session — user reports bugs conversationally, agent files durable GitHub issues using the project's domain language. Use when reporting bugs, doing QA, or filing issues conversationally.
---

# QA Session

Run an interactive QA session. The user describes problems; you clarify, explore the codebase for context, and file GitHub issues that are durable, user-focused, and use the project's domain language.

## For each issue the user raises

### 1. Listen and lightly clarify

Let the user describe the problem in their own words. Ask **at most 2-3 short clarifying questions** focused on:

- What they expected vs what actually happened
- Steps to reproduce (if not obvious)
- Whether it's consistent or intermittent

If the description is clear enough to file, move on.

### 2. Explore the codebase in the background

While talking to the user, kick off an Agent (subagent_type=Explore) to understand the relevant area. The goal is NOT to find a fix — it's to:

- Learn the domain language used in that area (check UBIQUITOUS_LANGUAGE.md)
- Understand what the feature is supposed to do
- Identify the user-facing behavior boundary

This context helps write a better issue. The issue itself must NOT reference specific files, line numbers, or internal implementation details.

### 3. Assess scope: single issue or breakdown?

Break down when:

- The fix spans multiple independent areas (e.g. "form validation is wrong AND success message is missing AND redirect is broken")
- Concerns are clearly separable — different people could work on them in parallel
- The user describes multiple distinct failure modes or symptoms

Keep as a single issue when:

- It's one behavior that's wrong in one place
- All symptoms share the same root cause

### 4. File the GitHub issue(s)

Create issues with `gh issue create`. Do NOT ask the user to review first — just file and share URLs.

Issues must be **durable** — still meaningful after major refactors. Write from the user's perspective.

#### Single issue template

```
## What happened

[Actual behavior the user experienced, in plain language]

## What I expected

[Expected behavior]

## Steps to reproduce

1. [Concrete, numbered steps a developer can follow]
2. [Use domain terms from the codebase, not internal module names]
3. [Include relevant inputs, flags, or configuration]

## Additional context

[Extra observations from the user or codebase exploration — e.g. "this only happens when using the Docker layer, not the filesystem layer" — use domain language but don't cite files]
```

#### Breakdown template (multiple issues)

Create issues in dependency order (blockers first) so you can reference real issue numbers.

```
## Parent issue

#<parent-issue-number> (if you created a tracking issue) or "Reported during QA session"

## What's wrong

[This specific behavior problem — just this slice, not the whole report]

## What I expected

[Expected behavior for this slice]

## Steps to reproduce

1. [Steps specific to THIS issue]

## Blocked by

- #<issue-number> (if this issue can't be fixed until another is resolved)

Or "None — can start immediately" if no blockers.

## Additional context

[Any extra observations relevant to this slice]
```

When creating a breakdown:

- **Prefer many thin issues over few thick ones** — each should be independently fixable and verifiable
- **Mark blocking relationships honestly** — if B can't be tested until A is fixed, say so; if independent, mark both "None — can start immediately"
- **Create in dependency order** so you can reference real issue numbers in "Blocked by"
- **Maximize parallelism** — multiple people (or agents) should be able to grab different issues simultaneously

#### Rules for all issue bodies

- **No file paths or line numbers** — these go stale
- **Use the project's domain language** (check UBIQUITOUS_LANGUAGE.md if it exists)
- **Describe behaviors, not code** — "the sync service fails to apply the patch" not "applyPatch() throws on line 42"
- **Reproduction steps are mandatory** — if you can't determine them, ask the user
- **Keep it concise** — a developer should be able to read the issue in 30 seconds

After filing, print all issue URLs (with blocking relationships summarized) and ask: "Next issue, or are we done?"

### 5. Continue the session

Keep going until the user says they're done. Each issue is independent — don't batch them.
