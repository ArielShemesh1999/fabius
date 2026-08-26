---
name: fabius-decor-youtube-clipper
description: Pull a YouTube video, slice highlight clips, add captions, and export — automated clip generation workflow.
triggers:
  - "youtube clip"
  - "video clip"
  - "highlight reel"
  - "auto caption clip"
---

# youtube-clipper

Automated workflow for YouTube clip generation: pull source video, slice highlights, add captions, and export shareable clips.

## When to use

- Extracting highlight moments from a long YouTube video
- Creating short-form clips (Shorts, Reels, TikTok) from existing footage
- Adding auto-generated captions to a clip
- Building a highlight reel from multiple timestamps

## Workflow

1. **Identify source** — provide a YouTube URL or a local video file path.
2. **Define clip points** — list timestamp ranges in `HH:MM:SS–HH:MM:SS` format, or describe the moments to extract (the tool will locate them).
3. **Slice** — each range is cut to a separate clip file (MP4/WebM).
4. **Caption** — auto-generate or provide a caption track (SRT/VTT); burn in or attach as a sidecar.
5. **Export** — output clips to the specified directory with a consistent naming convention: `<source-title>_clip-<N>.<ext>`.

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `source` | YouTube URL or local file path | required |
| `clips` | Array of `{start, end, label}` objects | required |
| `format` | Output container (`mp4`, `webm`) | `mp4` |
| `captions` | `auto`, `srt:<path>`, or `none` | `auto` |
| `burn_captions` | Burn captions into video vs. sidecar | `false` |
| `output_dir` | Directory for exported clips | `./clips/` |

## Example

```json
{
  "source": "https://www.youtube.com/watch?v=EXAMPLE",
  "clips": [
    { "start": "00:02:10", "end": "00:02:45", "label": "intro-hook" },
    { "start": "00:15:30", "end": "00:16:00", "label": "key-insight" }
  ],
  "format": "mp4",
  "captions": "auto",
  "output_dir": "./clips/"
}
```

## Output

Returns a list of exported clip file paths and a caption file path (if generated) for each clip. Clips are named `<label>.mp4` inside `output_dir`.
