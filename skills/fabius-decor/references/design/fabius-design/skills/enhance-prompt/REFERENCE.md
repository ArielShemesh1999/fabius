---
name: fabius-decor-enhance-prompt
description: Sharpen a rough prompt with precise design specs and UI/UX vocabulary for design-to-code workflows.
triggers:
  - "enhance prompt"
  - "design prompt"
  - "ui prompt"
  - "design vocabulary"
---

# enhance-prompt

## What it does

Takes a rough or ambiguous prompt and rewrites it with precise design specifications: layout intent, spacing, color tokens, typography, component names, interaction states, and accessibility requirements. Output is ready to feed directly into a design-to-code agent or visual generator.

## When to use

When a prompt is too vague to produce consistent UI output, or when bridging a designer's intent to a coding agent that needs exact vocabulary.

## How to use

Provide the rough prompt. The skill returns a rewritten version with expanded design specs. Invoke by name (`enhance-prompt`) or with a trigger phrase from the frontmatter.
