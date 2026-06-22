---
name: fabius-decor-fal-realtime
description: Stream real-time AI image generation via fal.ai — moodboard exploration, draft variations, and rapid creative iteration.
triggers:
  - "fal realtime"
  - "streaming image"
  - "realtime image gen"
  - "moodboard"
---

# fal-realtime

## When to use

Invoke when you need near-instant image output as the user types or adjusts parameters — moodboard exploration, live prompt iteration, or interactive design tools. Latency target is under 500ms per frame on supported endpoints.

## How to use

### Realtime connection (browser)

```js
import { fal } from "@fal-ai/client";

// Open a persistent realtime connection
const connection = await fal.realtime.connect("fal-ai/flux/schnell", {
  onResult: (result) => {
    // Called as each image streams in
    const imageUrl = result.images[0].url;
    document.querySelector("#preview").src = imageUrl;
  },
  onError: (error) => console.error(error),
});

// Send a new prompt (debounce in your UI)
connection.send({ prompt: "cyberpunk cityscape at night" });

// Clean up when done
connection.close();
```

### One-shot with streaming progress (Node)

```js
const result = await fal.subscribe("fal-ai/flux/schnell", {
  input: { prompt: "minimal flat icon of a mountain" },
  onQueueUpdate: (update) => {
    if (update.status === "IN_PROGRESS") {
      console.log("Generating…", update.logs?.at(-1)?.message);
    }
  },
});
```

## Supported realtime endpoints

- `fal-ai/flux/schnell` — fastest; best for live iteration
- `fal-ai/lcm-sd15-i2i` — image-to-image realtime
- `fal-ai/stable-diffusion-v3-medium` — balanced quality/speed

## Requirements

- `FAL_KEY` must be set (server-side) or a proxy token used in the browser.
- Do not expose `FAL_KEY` in browser bundles — use `fal.config({ proxyUrl: "/api/fal/proxy" })` and a thin server-side proxy route.
- Debounce prompt sends to ~300ms to avoid flooding the connection.

## Output

Each `onResult` callback receives `{ images: [{ url, width, height }] }`. Images are ephemeral CDN URLs — save to local state immediately if needed.
