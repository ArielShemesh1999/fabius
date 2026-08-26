---
name: fabius-decor-replicate
description: Discover, compare, and run AI models via Replicate's API. Use for image, audio, and video generation pipelines that swap models frequently.
triggers:
  - "replicate"
  - "run ai model"
  - "model comparison"
  - "replicate api"
---

# replicate

## What it does

Discover, compare, and run AI models using Replicate's API. Strong fit for generation pipelines where the model needs to be swappable (image, audio, video).

## When to use

Invoke when the user wants to run a hosted AI model, compare outputs across models, or build a pipeline that calls `replicate.run()`.

## How to use

Ask the agent to invoke this skill by name (`replicate`) or with one of the trigger phrases in the frontmatter.

Core API pattern:
```js
import Replicate from "replicate";
const replicate = new Replicate({ auth: process.env.REPLICATE_API_TOKEN });
const output = await replicate.run("owner/model:version", { input: { prompt: "..." } });
```

The skill handles model discovery, version pinning, input schema validation, and output polling.
