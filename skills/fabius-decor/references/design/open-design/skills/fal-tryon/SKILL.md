---
name: fabius-decor-fal-tryon
description: Virtual try-on — overlay garments onto a person image via fal.ai hosted try-on models for ecommerce, lookbooks, and styling experiments.
triggers:
  - "virtual tryon"
  - "fal tryon"
  - "try on clothes"
  - "lookbook"
  - "ecommerce styling"
---

# fal-tryon

Virtual try-on — see how clothes look on a person via fal.ai's hosted try-on models. Useful for ecommerce, lookbooks, and styling experiments.

## When to use

Invoke when the task requires overlaying a garment image onto a model/person photo without manual compositing.

## How to use

Ask the agent to invoke this skill by name (`fal-tryon`) or with one of the trigger phrases in the frontmatter.

Provide:
- A **person image** (URL or uploaded file)
- A **garment image** (URL or uploaded file)

The fal.ai try-on model composites the garment onto the person and returns a result image URL.
