---
name: fabius-decor-remotion
description: Programmatic video creation with React. Use for branded explainers, social cuts, dashboards-to-video, and reproducible motion graphics.
triggers:
  - "remotion"
  - "react video"
  - "programmatic video"
  - "motion graphics"
  - "video composition"
---

# remotion

## What it does

Programmatic video creation with React. Compose frame-accurate video from JSX components, animate with `useCurrentFrame`, and render to MP4 or GIF.

## When to use

Invoke when the user needs a reproducible, code-driven video: branded explainers, social cuts, data-driven motion graphics, or dashboard recordings.

## How to use

Ask the agent to invoke this skill by name (`remotion`) or with one of the trigger phrases in the frontmatter.

Key Remotion concepts the skill applies:
- `<Composition>` defines width, height, fps, and duration
- `useCurrentFrame()` + `interpolate()` drive all animation
- `<AbsoluteFill>` for full-frame layers
- `renderMedia()` CLI or Node API for headless export
