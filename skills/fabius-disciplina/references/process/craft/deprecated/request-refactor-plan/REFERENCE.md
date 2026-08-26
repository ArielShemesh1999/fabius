---
name: fabius-disciplina-request-refactor-plan
description: Create a detailed refactor plan with tiny safe commits via user interview, then file it as a GitHub issue. Use when planning a refactor, writing a refactoring RFC, or breaking a refactor into incremental steps.
---

# Request Refactor Plan

Guide the user through a structured refactor planning interview, then file the plan as a GitHub issue. Skip steps that clearly don't apply.

## Steps

1. **Gather the problem.** Ask for a long, detailed description of what's wrong and any initial solution ideas.

2. **Verify in the codebase.** Explore the repo to confirm their assertions and understand current state.

3. **Present alternatives.** Ask whether they've considered other options; propose any you see. Make sure they're choosing the right solution.

4. **Deep implementation interview.** Be thorough — drill into specifics until the implementation is unambiguous.

5. **Lock scope.** Agree on exactly what will and won't change. Be explicit about the boundary.

6. **Assess test coverage.** Check coverage for the affected area. If insufficient, ask what their testing plan is before proceeding.

7. **Break into tiny commits.** Each commit must leave the codebase in a working state. Prefer the smallest possible steps — every refactoring step should keep the program working.

8. **File the GitHub issue** using `gh issue create` with this template:

```
## Problem Statement

The problem the developer is facing, from their perspective.

## Solution

The chosen solution, from the developer's perspective.

## Commits

A detailed, commit-by-commit implementation plan in plain English. Each commit leaves the codebase working.

## Decision Document

Implementation decisions made during the interview:

- Modules being built or modified
- Interface changes
- Technical clarifications
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include file paths or code snippets — they go stale.

## Testing Decisions

- What makes a good test for this area (test external behavior, not implementation details)
- Which modules will be tested
- Prior art in the codebase for similar tests

## Out of Scope

What is explicitly NOT being changed in this refactor.

## Further Notes (optional)

Anything else worth recording.
```
