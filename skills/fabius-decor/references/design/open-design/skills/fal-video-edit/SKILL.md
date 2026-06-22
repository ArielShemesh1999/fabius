---
name: fabius-decor-fal-video-edit
description: Edit existing videos with AI — restyle, upscale, remove background, or add audio via fal.ai hosted video models.
triggers:
  - "fal video edit"
  - "video upscale"
  - "video style transfer"
  - "remove video bg"
  - "video remix"
---

# fal-video-edit

Edit existing videos using AI — remix style, upscale, remove background, and add audio via fal.ai's hosted video models.

## When to use

Invoke when a source video needs AI-driven editing: style transfer, resolution enhancement, background removal, or audio replacement/addition.

## How to use

Ask the agent to invoke this skill by name (`fal-video-edit`) or with one of the trigger phrases in the frontmatter.

Provide:
- A **source video URL** (or uploaded file)
- The **edit intent**: restyle / upscale / remove-bg / add-audio
- Any style or audio reference assets if applicable

The fal.ai video model processes the clip and returns an edited video URL.
