---
name: fabius-decor-fal-lip-sync
description: Sync audio to a talking-head video via fal.ai — explainer avatars, multilingual dubbing previews, and social cuts.
triggers:
  - "lip sync"
  - "talking head"
  - "audio to video"
  - "avatar video"
  - "fal lipsync"
---

# fal-lip-sync

## When to use

Invoke when you need to drive a person's mouth in a video to match a given audio track — dubbing, avatar generation, or explainer video production.

## How to use

### Lip sync (audio + video → synced video)

```js
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/wav2lip", {
  input: {
    video_url: "https://example.com/talking-head.mp4",
    audio_url: "https://example.com/voiceover.mp3",
  },
});
// result.video.url
```

### Talking head from image + audio

```js
const result = await fal.subscribe("fal-ai/sadtalker", {
  input: {
    source_image_url: "https://example.com/portrait.jpg",
    driven_audio_url: "https://example.com/speech.mp3",
    preprocess: "crop",       // "crop" | "resize" | "full"
    still_mode: false,        // true = minimal head motion
    use_enhancer: true,       // face restoration post-process
  },
});
// result.video.url
```

## Key endpoints

| Task | Endpoint |
|------|----------|
| Lip sync existing video | `fal-ai/wav2lip` |
| Animate portrait from audio | `fal-ai/sadtalker` |

## Key parameters (sadtalker)

| Parameter | Values | Notes |
|-----------|--------|-------|
| `preprocess` | `"crop"`, `"resize"`, `"full"` | `"crop"` works best for portraits |
| `still_mode` | boolean | Reduce head motion for static avatars |
| `use_enhancer` | boolean | Runs GFPGAN face restoration — recommended |

## Requirements

- `FAL_KEY` env var must be set.
- Input video/image and audio must be publicly accessible URLs.
- Audio should be clean mono or stereo MP3/WAV; background noise degrades lip accuracy.

## Output

`{ video: { url, content_type } }` — MP4. Download for persistence; CDN links expire.
