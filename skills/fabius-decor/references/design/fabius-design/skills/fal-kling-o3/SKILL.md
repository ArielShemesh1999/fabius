---
name: fabius-decor-fal-kling-o3
description: Generate high-quality images and videos with Kling O3 via fal.ai — Kling's most capable model family.
triggers:
  - "fal kling"
  - "kling o3"
  - "kling video"
  - "kling image"
---

# fal-kling-o3

## When to use

Invoke for high-quality video generation or image generation where Kling O3 quality is needed. Best for cinematic motion, consistent character scenes, and image-to-video workflows.

## How to use

### Text-to-video

```js
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/kling-video/v1.6/pro/text-to-video", {
  input: {
    prompt: "A lone astronaut walks across a red desert at golden hour",
    duration: "5",        // "5" or "10" seconds
    aspect_ratio: "16:9", // "16:9", "9:16", "1:1"
  },
});
// result.video.url
```

### Image-to-video

```js
const result = await fal.subscribe("fal-ai/kling-video/v1.6/pro/image-to-video", {
  input: {
    image_url: "https://example.com/frame.jpg",
    prompt: "camera slowly zooms in",
    duration: "5",
  },
});
```

### Image generation (Kling O3)

```js
const result = await fal.subscribe("fal-ai/kling-video/v1.6/standard/image-to-video", {
  input: {
    prompt: "product photo on marble surface",
    aspect_ratio: "1:1",
  },
});
```

## Key parameters

| Parameter | Values | Notes |
|-----------|--------|-------|
| `duration` | `"5"`, `"10"` | Seconds of video |
| `aspect_ratio` | `"16:9"`, `"9:16"`, `"1:1"` | Output ratio |
| `cfg_scale` | `0.0–1.0` | Prompt adherence; 0.5 is a good default |

## Requirements

- `FAL_KEY` env var must be set.
- Video generation runs asynchronously — `fal.subscribe` handles polling automatically.
- Longer durations and pro tier take more time (30–120s typical).

## Output

`{ video: { url, content_type } }` — MP4 hosted on fal.ai CDN. Download immediately for persistence.
