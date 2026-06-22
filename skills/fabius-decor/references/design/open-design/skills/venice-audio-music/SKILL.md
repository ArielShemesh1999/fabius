---
name: fabius-decor-venice-audio-music
description: Queue, retrieve, and complete music generation jobs via Venice.ai — suited for jingles, background loops, and prototype scoring.
triggers:
  - "venice music"
  - "music gen"
  - "jingle"
  - "background loop"
  - "score"
---

# venice-audio-music

## What it does

Wraps Venice.ai music generation endpoints: submit a generation job, poll for completion, and retrieve the audio result. Suited for jingles, looping background tracks, and rough prototype scoring.

## When to use

Invoke when a project needs generated music — background ambience, a short jingle, or a scored clip — without a manual DAW session.

## How to use

Ask the agent to invoke this skill by name (`venice-audio-music`) or with one of the trigger phrases in the frontmatter. Provide a description of the desired mood, tempo, and length; the skill handles queueing and retrieval.
