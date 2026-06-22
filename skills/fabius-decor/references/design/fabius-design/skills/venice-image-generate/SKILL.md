---
name: fabius-decor-venice-image-generate
description: Generate images in various styles via the Venice.ai API.
triggers:
  - "venice image"
  - "venice generate"
  - "venice ai image"
---

# venice-image-generate

## What it does

Image generation across available styles via the Venice.ai API.

## When to use

Use when the user wants to generate a new image from a text prompt using Venice.ai.

## How to use

Invoke by name (`venice-image-generate`) or with a trigger phrase from the frontmatter. The agent selects an appropriate Venice.ai style and calls the image generation endpoint, returning the generated image.
