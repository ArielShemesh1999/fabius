---
name: fabius-decor-venice-video
description: Generate video and transcribe audio via the Venice.ai API.
triggers:
  - "venice video"
  - "venice video gen"
  - "venice transcribe"
---

# venice-video

## What it does

Video generation and audio transcription via the Venice.ai API.

## When to use

Use when the user wants to generate a video from a prompt or transcribe audio/video content via Venice.ai.

## How to use

Invoke by name (`venice-video`) or with a trigger phrase from the frontmatter. For generation, the agent submits a prompt to Venice.ai's video endpoint. For transcription, it submits the media file and returns the transcript.
