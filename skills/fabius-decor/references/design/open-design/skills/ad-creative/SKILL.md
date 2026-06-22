---
name: fabius-decor-ad-creative
description: Generate and iterate ad creative — headlines, descriptions, and primary text — for paid social and search campaigns.
triggers:
  - "ad creative"
  - "ad headline"
  - "ad copy"
  - "paid social ad"
  - "search ad"
---

# Ad Creative

Generate and iterate ad creative for paid social and search channels.

## When to use

Use this skill when the user needs headline variants, description copy, or primary text for Facebook/Instagram ads, Google Search ads, or similar paid placements.

## Workflow

1. **Gather inputs** — product/service name, target audience, unique value proposition, platform (Meta, Google, LinkedIn, etc.), character limits if known.
2. **Draft headline variants** — produce 5–10 options ranging from benefit-led to curiosity-gap to direct-response styles.
3. **Write descriptions** — match each headline with a description that expands the hook and closes with a clear CTA.
4. **Generate primary text** — for social ads, write 2–3 primary text options (short/medium/long) that open with a scroll-stopper line.
5. **Iterate** — if the user gives feedback, apply it across all variants in one pass and flag which changed and why.

## Output format

Return a structured block per variant:

```
--- Variant N ---
Headline: …
Description: …
Primary text: …
CTA: …
```

Keep copy within stated character limits. Note the platform limit if the user did not specify one (e.g. Google Search headline ≤ 30 chars).
