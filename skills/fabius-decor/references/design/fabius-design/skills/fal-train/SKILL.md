---
name: fabius-decor-fal-train
description: Train custom LoRA models on fal.ai for personalized image generation — brand identity, character, or style consistency.
triggers:
  - "fal train"
  - "train lora"
  - "custom model"
  - "personalized image gen"
  - "brand lora"
---

# fal-train

## When to use

Invoke when a project needs a custom fine-tuned model: consistent brand visuals, a recurring character, a specific photography style, or product renders that stock models cannot replicate.

## How to use

### 1. Prepare training data

- 10–20 images minimum; 15–25 is the sweet spot.
- Consistent subject, varied backgrounds and angles.
- Minimum 512×512; 1024×1024 preferred.
- Upload to any publicly accessible URL (R2, S3, CDN) or use a ZIP archive URL.

### 2. Start training (Flux LoRA)

```js
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/flux-lora-fast-training", {
  input: {
    images_data_url: "https://example.com/training-images.zip",
    trigger_word: "MYPRODUCT", // use in prompts to activate the LoRA
    steps: 1000,               // 500–1500; more = better fit, longer run
    rank: 16,                  // LoRA rank; 16 is a good default
    learning_rate: 0.0004,
  },
  onQueueUpdate: (update) => console.log(update.status, update.logs?.at(-1)?.message),
});

// result.diffusers_lora_file.url  — weights to store
// result.config_file.url          — training config
const loraWeightsUrl = result.diffusers_lora_file.url;
```

### 3. Run inference with the trained LoRA

```js
const generated = await fal.subscribe("fal-ai/flux-lora", {
  input: {
    prompt: "MYPRODUCT on a white marble surface, product photography",
    loras: [{ path: loraWeightsUrl, scale: 1.0 }],
    num_images: 4,
  },
});
// generated.images[0].url
```

## Key parameters

| Parameter | Notes |
|-----------|-------|
| `trigger_word` | Short ALLCAPS token that activates your LoRA in prompts |
| `steps` | 500 = fast/rough, 1000 = balanced, 1500 = high fidelity |
| `rank` | LoRA rank; 16 standard, 32 for complex styles |
| `loras[].scale` | Inference blend weight; 0.8–1.0 for trained subjects |

## Requirements

- `FAL_KEY` env var must be set.
- Training runs async — `fal.subscribe` polls until done (5–20 min typical).
- Store the returned `diffusers_lora_file.url` — it is your custom model weights; download and persist to your own storage.

## Output

Training: `{ diffusers_lora_file: { url }, config_file: { url } }`.
Inference: `{ images: [{ url, width, height }] }`.
