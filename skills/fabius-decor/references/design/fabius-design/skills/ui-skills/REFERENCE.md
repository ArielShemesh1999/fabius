---
name: fabius-decor-ui-skills
description: Opinionated UI constraints that keep agent-built interfaces coherent across many small components.
triggers:
  - "ui constraints"
  - "ui guide"
  - "opinionated ui"
  - "ui rules"
---

# ui-skills

## What it does

Provides evolving, opinionated constraints for agents building interfaces — spacing, color, component boundaries, interaction patterns. Keeps output consistent when building many small UI pieces in the same session.

## When to use

Invoke at the start of any UI build where consistency matters across multiple components or pages. Especially useful when output tends to drift in style between iterations.

## How to use

Ask the agent to invoke this skill by name (`ui-skills`) or with one of the trigger phrases in the frontmatter. The constraints activate for all subsequent UI generation in the session.
