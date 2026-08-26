---
name: fabius-decor-brand-guidelines
description: Apply a defined brand's colors, typography, and visual rules to artifacts for consistent, professional identity.
triggers:
  - "brand guidelines"
  - "brand colors"
  - "brand typography"
  - "visual identity"
---

# brand-guidelines

## What it does

Applies a brand's visual identity system — colors, type scale, spacing, and component conventions — to any artifact or design output. Ensures every surface reads as intentionally on-brand rather than default.

## When to use

- Starting a new artifact and a brand design system is available.
- An existing artifact drifts off-brand and needs realignment.
- Building a reference sheet or style guide for a project.

## Steps

1. **Load the brand spec** — read the project's `DESIGN.md` or brand token file. If none exists, ask the user for primary color, typeface, and tone.
2. **Extract the token set** — identify: primary/secondary/accent colors, neutral scale, heading and body typefaces, base font size, spacing unit, border-radius, and shadow style.
3. **Apply to the artifact** — set CSS custom properties (`--color-primary`, `--font-heading`, etc.) at `:root`. Use only these variables in component styles; avoid hardcoded hex values.
4. **Validate contrast** — check foreground/background pairs meet WCAG AA (4.5:1 for body text, 3:1 for large text).
5. **Document deviations** — if the design requires a one-off value not in the token set, add a comment explaining why.

## Output

An artifact or stylesheet where every visual decision traces back to a named brand token. Optional: a living style-guide section showing the token palette and type scale.
