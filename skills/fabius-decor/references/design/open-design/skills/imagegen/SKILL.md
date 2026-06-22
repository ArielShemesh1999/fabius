---
name: fabius-decor-imagegen
description: Generate and edit images using OpenAI's Image API for project assets — UI mockups, icons, illustrations, social cards, and visual references.
triggers:
  - "generate image"
  - "create image"
  - "image gen"
  - "openai image"
  - "icon design"
  - "mockup"
---

# imagegen

## What it does

Generate and edit images using OpenAI's Image API for project assets — UI mockups, icons, illustrations, social cards, and visual references.

## How to use

Invoke this skill by name (`imagegen`) or with one of the trigger phrases listed in the frontmatter.

Provide a text prompt describing the image. The skill will:

1. Route the request through the built-in image generation path by default.
2. Fall back to a CLI path if the built-in path is unavailable (confirmation required before falling back).
3. Return the generated image for use in the project.

Requires `OPENAI_API_KEY`.
