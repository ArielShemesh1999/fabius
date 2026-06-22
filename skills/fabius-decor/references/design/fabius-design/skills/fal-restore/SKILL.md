---
name: fabius-decor-fal-restore
description: Restore and enhance image quality via fal.ai — deblur, denoise, fix faces, and recover old or degraded images.
triggers:
  - "fal restore"
  - "restore image"
  - "deblur"
  - "denoise"
  - "fix faces"
  - "document restore"
---

# fal-restore

## When to use

Invoke when a source image is degraded: blurry, noisy, compressed artifacts, damaged faces, or a scanned old document. Also use for upscaling while preserving detail.

## How to use

### Face restoration (GFPGAN)

```js
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/gfpgan", {
  input: {
    image_url: "https://example.com/damaged-portrait.jpg",
    upscale: 2, // 1–4
  },
});
// result.image.url
```

### General image upscale + restore (Real-ESRGAN)

```js
const result = await fal.subscribe("fal-ai/esrgan", {
  input: {
    image_url: "https://example.com/low-res.jpg",
    scale: 4,         // 2 or 4
    face_enhance: false,
  },
});
```

### Deblur / denoising

```js
const result = await fal.subscribe("fal-ai/nafnet", {
  input: {
    image_url: "https://example.com/blurry.jpg",
    task_type: "deblur", // "deblur" | "denoise"
  },
});
```

## Key endpoints

| Task | Endpoint |
|------|----------|
| Face restoration | `fal-ai/gfpgan` |
| General upscale | `fal-ai/esrgan` |
| Deblur / denoise | `fal-ai/nafnet` |

## Key parameters

| Parameter | Endpoint | Notes |
|-----------|----------|-------|
| `upscale` | gfpgan | 1–4× output resolution |
| `scale` | esrgan | 2 or 4 |
| `face_enhance` | esrgan | Run face restoration pass before upscale |
| `task_type` | nafnet | `"deblur"` or `"denoise"` |

## Requirements

- `FAL_KEY` env var must be set.
- Input must be a publicly accessible URL or base64 data URI.
- Very large inputs may time out — resize to under 2048px on the long edge before sending if the original is enormous.

## Output

`{ image: { url, width, height, content_type } }` — typically a higher-resolution JPEG or PNG. Download immediately; CDN links are not permanent.
