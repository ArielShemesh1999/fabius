---
name: fabius-decor-fal-image-edit
description: Edit images with AI via fal.ai — inpainting, style transfer, background removal, and object removal.
triggers:
  - "fal image edit"
  - "inpaint"
  - "style transfer"
  - "background removal"
  - "object removal"
---

# fal-image-edit

## When to use

Invoke when an existing image needs targeted editing: remove or replace a region (inpainting), change visual style, strip the background, or erase an object.

## How to use

### Inpainting (replace a region)

```js
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/flux/inpainting", {
  input: {
    image_url: "https://example.com/source.jpg",
    mask_url: "https://example.com/mask.png", // white = repaint area
    prompt: "a red sports car",
  },
});
// result.images[0].url
```

### Background removal

```js
const result = await fal.subscribe("fal-ai/birefnet", {
  input: { image_url: "https://example.com/photo.jpg" },
});
// result.image.url — PNG with transparent background
```

### Style transfer

```js
const result = await fal.subscribe("fal-ai/style-transfer", {
  input: {
    content_image_url: "https://example.com/content.jpg",
    style_image_url: "https://example.com/style.jpg",
    strength: 0.7,
  },
});
```

## Key endpoints

| Task | Endpoint |
|------|----------|
| Inpainting | `fal-ai/flux/inpainting` |
| Background removal | `fal-ai/birefnet` |
| Style transfer | `fal-ai/style-transfer` |
| Object removal | `fal-ai/sd-inpainting` |

## Requirements

- `FAL_KEY` env var must be set.
- Input images must be publicly accessible URLs or base64 data URIs.
- Masks are grayscale PNGs: white = edit zone, black = preserve.

## Output

URL to edited image (PNG or JPEG). Download immediately if persistence is needed — CDN links are not permanent.
