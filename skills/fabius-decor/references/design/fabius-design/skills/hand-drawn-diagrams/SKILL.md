---
name: fabius-decor-hand-drawn-diagrams
description: Generate hand-drawn Excalidraw diagrams from a prompt — animated SVG, hosted edit link, and PNG export.
triggers:
  - "excalidraw"
  - "hand drawn diagram"
  - "sketch diagram"
  - "whiteboard diagram"
---

# hand-drawn-diagrams

## What it does

Generate hand-drawn Excalidraw diagrams from a prompt — animated SVG, hosted edit link, and PNG export.

## How to use

This catalogue entry advertises the skill so the agent discovers it during planning. Invoke this skill by name (`hand-drawn-diagrams`) or with one of the trigger phrases listed in this skill's frontmatter.

Provide a description of the diagram you want. The skill will:

1. Parse the prompt into Excalidraw-compatible elements (shapes, arrows, labels).
2. Produce an animated SVG with hand-drawn stroke styling.
3. Return a hosted edit link and a PNG export.
