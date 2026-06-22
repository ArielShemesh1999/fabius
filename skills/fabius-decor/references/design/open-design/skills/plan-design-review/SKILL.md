---
name: fabius-decor-plan-design-review
description: Senior Designer review — rates each design dimension 0–10, explains what a 10 looks like, and flags AI Slop signals. Use as a quality gate before merging UI work.
triggers:
  - "plan design review"
  - "senior designer review"
  - "design rating"
  - "ai slop check"
---

# plan-design-review

## What it does

Scores each design dimension 0–10, explains the standard a 10 meets, and surfaces AI Slop signals — the telltale patterns (over-generic layouts, mismatched whitespace, hollow copy) that indicate a design was accepted without a critical eye.

## When to use

Run this before merging any UI work or shipping a design handoff. It acts as a structured senior-designer gate so obvious quality failures don't reach production.

## How to invoke

Ask the agent to run `plan-design-review` or use a trigger phrase from the frontmatter. Provide the design artifact (screenshot, Figma link, or HTML file) as context.

## Output

- Per-dimension score table (0–10) with brief justification per row.
- "What a 10 looks like" note for every dimension that scored below 8.
- AI Slop flag list — specific callouts with location and recommended fix.
- Overall verdict: **Pass / Revise / Reject**.
