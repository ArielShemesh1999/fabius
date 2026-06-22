---
name: fabius-decor-figma-generate-design
description: Build or update Figma screens from code or a description, using design system components and tokens.
triggers:
  - "figma generate design"
  - "code to figma"
  - "screen generation"
  - "figma from code"
---

# figma-generate-design

## When to use

Use when you need to translate an existing page, component tree, or written spec into Figma frames — keeping the result anchored to the design system library rather than raw shapes.

## Prerequisites

- A Figma file exists (run `fabius-decor-figma-create-new-file` if not).
- A design system library is attached (run `fabius-decor-figma-generate-library` if not).
- `fabius-decor-figma-use` has been invoked this session.

## Steps

1. **Read the design system** — call `search_design_system` to get available components and their node IDs.
2. **Gather source material** — either:
   - Read the code file/component tree to extract layout, variants, and content, or
   - Parse the written spec/prompt for screen intent, sections, and states.
3. **Map content to components** — match each UI element to its design system counterpart (e.g. `<Button variant="primary">` → `Button/Primary` component node).
4. **Call `use_figma`** with a plugin script that:
   - Creates a new frame at the target page with the correct device dimensions.
   - Inserts component instances via `figma.createInstance(nodeId)`.
   - Applies layout (auto-layout or absolute) matching the code structure.
   - Sets text content and fills using design tokens (variables), not hardcoded values.
5. **Iterate per screen/state** — repeat step 4 for each distinct screen or variant (empty state, error, loading).
6. **Verify** — call `get_screenshot` on the resulting frame and confirm visual accuracy.

## Output

One or more Figma frames that visually represent the screens, built entirely from library components and design tokens, ready for design review or further iteration.
