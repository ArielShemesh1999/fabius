---
name: fabius-disciplina-to-prd
description: Synthesize the current conversation and codebase into a structured PRD, then publish it to the project issue tracker.
---

Produce a PRD from what you already know. Do NOT interview the user — synthesize from conversation context and codebase exploration.

The issue tracker and triage label vocabulary should have been provided — run `/setup-the-craft-set-skills` if not.

## Process

1. **Explore the repo.** Understand current state. Use the project's domain glossary throughout the PRD. Respect any ADRs in the area being touched.

2. **Sketch test seams.** Identify where you'll test the feature. Prefer existing seams over new ones; prefer higher seams over lower ones. If new seams are needed, propose them at the highest point possible. Confirm with the user that these seams match their expectations.

3. **Write the PRD** using the template below, then publish it to the project issue tracker with the `ready-for-agent` triage label — no additional triage needed.

<prd-template>

## Problem Statement

The problem the user is facing, from the user's perspective.

## Solution

The solution, from the user's perspective.

## User Stories

A numbered list covering all aspects of the feature. Each entry:

1. As a `<actor>`, I want `<feature>`, so that `<benefit>`

Example:
1. As a mobile bank customer, I want to see my account balance, so that I can make better-informed spending decisions.

Be exhaustive — cover edge cases, error states, and secondary actors.

## Implementation Decisions

Decisions made about how to build this. May include:

- Modules to build or modify
- Interface changes
- Technical clarifications
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include file paths or code snippets — they go stale fast.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note it came from a prototype. Trim to the decision-rich parts only.

## Testing Decisions

- What makes a good test for this feature (test external behavior, not implementation details)
- Which modules will be tested
- Prior art in the codebase for similar tests

## Out of Scope

What this PRD explicitly does not cover.

## Further Notes

Any remaining context or open questions.

</prd-template>
