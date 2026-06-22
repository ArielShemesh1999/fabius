---
name: fabius-decor-ai-music-album
description: Full-lifecycle AI music album production — concept, lyric drafting, track sequencing, and export notes for indie experiments and brand soundtracks.
triggers:
  - "ai music"
  - "music album"
  - "lyric writing"
  - "track sequencing"
  - "album production"
---

# AI Music Album

Drive end-to-end album production: concept → lyrics → track order → export-ready output notes.

## When to use

Use when the user wants to produce a cohesive AI-assisted music album — indie project, brand soundtrack, or creative experiment.

## Workflow

### 1. Concept

Define the album's identity before writing a single line:
- Genre and mood (e.g. lo-fi melancholy, cinematic orchestral, upbeat indie pop)
- Thematic through-line (what the album is "about" in one sentence)
- Target length — number of tracks and approximate runtime

### 2. Track list skeleton

Draft track titles and one-line summaries that map to the thematic arc. A 10-track album typically flows: opener → build → peak → descent → closer.

### 3. Lyric drafting

For each track:
- Write verse / pre-chorus / chorus / bridge structure unless the user specifies otherwise.
- Keep syllable rhythm consistent with the stated genre tempo.
- Flag lines the user should consider adapting for their vocal style.

### 4. Track sequencing

Review the full track list for energy arc and key/mood compatibility. Propose a final order with a one-line rationale for each placement.

### 5. Export notes

Output a production brief per track: suggested BPM range, key, instrumentation mood, reference artists (style only, not samples), and any AI music tool prompt that would generate a matching backing track (e.g. Suno, Udio prompt strings).

## Output format

Return a structured document:

```
# [Album Title]
Concept: …
Tracks: N | Runtime: ~X min

## Track List
1. [Title] — [one-line summary]
…

## Lyrics
### 1. [Title]
[Verse 1] …
[Chorus] …
…

## Production Briefs
### 1. [Title]
BPM: … | Key: … | Mood: …
References: …
AI prompt: "…"
```
