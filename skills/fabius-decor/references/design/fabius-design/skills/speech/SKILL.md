---
name: fabius-decor-speech
description: Generate spoken audio from text via OpenAI's TTS API — narrated explainers, lecture audio, and voiceover tracks from built-in voices.
triggers:
  - "openai speech"
  - "tts openai"
  - "narrated audio"
  - "voice over"
---

# speech

Generate spoken audio from text using OpenAI's TTS API and its built-in voices. Use for narrated explainers, lecture audio, and quick voiceover tracks.

## When to use

Invoke when a user needs a voiceover: tutorial narration, slide read-through, podcast draft, or any text that needs to be heard rather than read.

## How to use

1. Provide the text to be spoken and choose a voice (`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`).
2. Set speed and output format (`mp3`, `opus`, `aac`, `flac`) as needed.
3. Call the OpenAI TTS endpoint and receive the audio file.
4. Integrate the audio into the target project (video edit, slide deck, app).

Trigger this skill by name (`speech`) or with one of the trigger phrases in the frontmatter.
