---
name: fabius-decor-fal-generate
description: Generate images and videos via fal.ai — Flux, SDXL, Ideogram, and other hosted endpoints.
triggers:
  - "fal generate"
  - "fal.ai image"
  - "flux image"
  - "sdxl"
  - "ideogram"
---

# fal-generate

## When to use

Invoke when the task calls for AI image or video generation using fal.ai-hosted models: Flux variants, SDXL, Ideogram, or community endpoints.

## How to use

1. **Pick a model endpoint** — choose by output type and quality target:
   - `fal-ai/flux/schnell` — fast drafts
   - `fal-ai/flux/dev` — quality generation
   - `fal-ai/stable-diffusion-xl` — SDXL
   - `fal-ai/ideogram/v2` — text-in-image, logos

2. **Call the endpoint** with a prompt and parameters:
   ```js
   import { fal } from "@fal-ai/client";

   const result = await fal.subscribe("fal-ai/flux/dev", {
     input: {
       prompt: "your prompt here",
       image_size: "landscape_4_3",
       num_images: 1,
     },
   });
   // result.images[0].url
   ```

3. **Set credentials** — `FAL_KEY` env var must be present before any call.

4. **Handle output** — all endpoints return `{ images: [{ url, width, height }] }` or `{ video: { url } }` for video models.

## Key parameters

| Parameter | Type | Notes |
|-----------|------|-------|
| `prompt` | string | Required. Be specific. |
| `image_size` | string | `square`, `landscape_4_3`, `portrait_4_3`, or `{ width, height }` |
| `num_images` | number | 1–4 depending on endpoint |
| `seed` | number | For reproducibility |

## Output

URL(s) to generated image(s) or video, plus metadata (width, height, content type). Files are hosted on fal.ai CDN — download and store locally if persistence is needed.
