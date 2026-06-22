---
name: fabius-decor-fal-3d
description: Generate 3D models from text or images via fal.ai — for game assets, AR previews, product mockups, and concept sculpting.
triggers:
  - "fal 3d"
  - "text to 3d"
  - "image to 3d"
  - "3d model gen"
  - "game asset 3d"
---

# fal-3d

## What it does

Generates 3D models from a text description or a reference image using the fal.ai API. Output formats suit game assets, AR previews, product mockups, and concept sculpts.

## When to use

When the task requires a 3D artifact — not a flat render — and the source is either a text description or a 2D reference image.

## How to use

Provide a text prompt or image URL. Specify the intended use (game asset / AR / mockup / concept) if it affects mesh density or format. Invoke by name (`fal-3d`) or with a trigger phrase from the frontmatter. The skill calls the fal.ai generation endpoint and returns the model file URL.
