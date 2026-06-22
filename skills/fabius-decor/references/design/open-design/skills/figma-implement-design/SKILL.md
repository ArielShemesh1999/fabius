---
name: fabius-decor-figma-implement-design
description: Translate Figma designs into production-ready code with 1:1 visual fidelity, handing off Figma frames directly to frontend implementation.
triggers:
  - "figma to code"
  - "implement figma"
  - "figma fidelity"
  - "1:1 figma"
---

# figma-implement-design

## When to use

Use when a Figma frame is approved and needs to become production code. This skill drives design-to-code translation with pixel accuracy.

## Prerequisites

- `fabius-decor-figma-use` has been invoked this session.
- The target Figma file key and frame node ID are known.

## Steps

1. **Extract design context** — call `get_design_context` with the frame node ID to get the full component tree: layout mode, spacing, fills, typography, effects, and variable bindings.
2. **Resolve tokens** — call `get_variable_defs` to map every variable binding to its resolved value and its code token name (per the design system rules).
3. **Extract assets** — call `download_assets` for any image fills, icons, or illustrations; save to the project's asset directory.
4. **Write the component** — implement the frame as code:
   - Use the project's component framework (React, Flutter, SwiftUI, etc.).
   - Replace hardcoded values with design token references.
   - Match auto-layout direction → flex/column/row; spacing → gap; padding → padding tokens.
   - Implement all visible variants and states present in the Figma frame.
5. **Pixel-check** — call `get_screenshot` on the Figma frame, render the implemented component, and compare. Fix deviations above 2px or visible color drift.
6. **Check Code Connect** — call `get_code_connect_map` to see if a mapping already exists for this component; update or create the mapping so the Figma component links back to the code file.

## Output

A production component file with 1:1 visual fidelity to the Figma frame, using design tokens throughout, with a Code Connect mapping registered.
