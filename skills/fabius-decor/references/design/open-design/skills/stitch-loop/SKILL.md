---
name: fabius-decor-stitch-loop
description: Iterative design-to-code feedback loop — critique, adjust, ship — for tightening visual fidelity between brief and built UI.
triggers:
  - "stitch loop"
  - "design to code"
  - "design iteration"
  - "fidelity loop"
---

# stitch-loop

Iterative design-to-code feedback loop. Critique → adjust → ship cycle for closing the gap between a visual brief and the implemented UI.

## When to use

Use when a built UI drifts from its design brief and needs structured, repeatable correction passes rather than ad-hoc fixes.

## How to use

1. **Critique** — compare the current implementation screenshot against the brief; list specific deltas (spacing, color, typography, interaction).
2. **Adjust** — make targeted code changes for each delta; keep each pass narrow and reviewable.
3. **Ship** — commit and verify the change closes the delta before moving to the next item.
4. Repeat until the implementation matches the brief within acceptable tolerance.

Trigger this skill by name (`stitch-loop`) or with one of the trigger phrases in the frontmatter.
