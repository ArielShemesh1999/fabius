---
name: fabius-decor-the-design-corpus
description: Create and manage DESIGN.md files as a single source of truth for design direction, tokens, and visual rules.
triggers:
  - "design.md"
  - "design doc"
  - "design tokens doc"
  - "visual rules doc"
---

# the design corpus

## What it does

Create and manage DESIGN.md files. Captures design direction, tokens, and visual rules in a single source of truth that agents and developers reference throughout a project.

## When to use

- Starting a new project and need a canonical visual reference.
- An existing project lacks a DESIGN.md and decisions are inconsistent across files.
- Updating design tokens (colors, spacing, typography) and need changes propagated clearly.

## How to invoke

Ask the agent by name (`the design corpus`) or with one of the trigger phrases in this skill's frontmatter.

The agent will:
1. Read any existing DESIGN.md or extract design tokens from the current codebase.
2. Produce or update a DESIGN.md covering: color palette, typography, spacing, component styles, layout model, responsive behavior, and agent prompt guide.
3. Flag any inconsistencies found between the existing code and the documented system.
