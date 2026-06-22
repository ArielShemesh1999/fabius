---
name: fabius-decor-platform-design
description: Apply 300+ design rules from Apple HIG, Material Design 3, and WCAG 2.2 to ship a single design correctly across iOS, Android, and the web.
triggers:
  - "platform design"
  - "cross platform design"
  - "material design"
  - "hig rules"
  - "wcag rules"
---

# platform-design

## What it does

Encodes 300+ platform-specific design rules from three authoritative sources:

- **Apple HIG** — iOS/macOS conventions: navigation patterns, safe areas, typography scale, haptics, dynamic type.
- **Material Design 3** — Android conventions: color roles, motion tokens, adaptive layouts, component states.
- **WCAG 2.2** — Cross-platform accessibility: contrast ratios, touch target sizes, focus indicators, semantic structure.

## When to use

Use this skill when a design must ship on more than one platform and you need to catch the platform-specific divergences before implementation — e.g. bottom tab bars on iOS vs. Navigation Rail on Android, or safe-area insets that differ per device class.

## How to invoke

Ask the agent to run `platform-design` or use a trigger phrase from the frontmatter. Provide the target platforms and the design artifact (screen, flow, or component) as context.

## Output

- Platform rule checklist for each target (iOS, Android, Web).
- Violations found in the provided design, with rule citation.
- Recommended fixes per violation.
- WCAG 2.2 accessibility gaps flagged separately with severity (A / AA / AAA).
