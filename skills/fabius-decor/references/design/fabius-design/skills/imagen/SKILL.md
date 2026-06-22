---
name: fabius-decor-imagen
description: Generate images using Google Gemini's image generation API for UI mockups, icons, illustrations, and visual assets.
triggers:
  - "gemini image"
  - "imagen"
  - "google image gen"
  - "illustration"
  - "icon"
---

# imagen

## What it does

Generate images using Google Gemini's image generation API for UI mockups, icons, illustrations, and visual assets.

## How to use

Invoke this skill by name (`imagen`) or with one of the trigger phrases listed in the frontmatter.

Provide a text prompt describing the image. The skill will:

1. Send the prompt to the Gemini image generation API.
2. Return the generated image for use in the project.

Requires a Google Gemini API key (`GEMINI_API_KEY` or `GOOGLE_API_KEY`).
