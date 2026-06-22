---
name: fabius-decor-venice-image-edit
description: Edit, upscale, and remove backgrounds from images via the Venice.ai API.
triggers:
  - "venice image edit"
  - "venice upscale"
  - "venice background removal"
---

# venice-image-edit

## What it does

Image edits, upscaling, and background removal via the Venice.ai API.

## When to use

Use when the user wants to edit an existing image, upscale resolution, or strip the background — all through Venice.ai.

## How to use

Invoke by name (`venice-image-edit`) or with a trigger phrase from the frontmatter. The agent will call the Venice.ai image-edit endpoints with the specified operation (edit / upscale / background-remove) and return the processed image.
