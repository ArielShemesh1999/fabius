---
name: fabius-decor-design-review
description: Visual audit followed by atomic code fixes and before/after screenshots. Use to tighten shipped UI before launch.
triggers:
  - "design review"
  - "visual audit"
  - "before after"
  - "pre launch design check"
---

# design-review

## What it does

Designer-who-codes workflow: visual audit then targeted fixes with atomic commits and before/after screenshots. Tightens shipped UI before launch.

## When to use

- UI is functionally complete but feels rough or inconsistent.
- Pre-launch polish pass: spacing, typography hierarchy, color contrast, component consistency.
- After a feature sprint when design debt has accumulated across multiple files.

## How to invoke

Ask the agent by name (`design-review`) or with one of the trigger phrases in this skill's frontmatter.

The agent will:
1. Screenshot or read the current UI files to identify visual issues.
2. Group findings into atomic fix batches (spacing, typography, color, alignment).
3. Apply each batch as a separate commit with a before/after description.
4. Produce a summary of changes made and any issues flagged for human decision.
