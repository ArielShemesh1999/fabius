---
name: fabius-decor-figma-create-design-system-rules
description: Generate project-specific design system rules for Figma-to-code workflows — tokens, naming conventions, and lint rules in one source of truth.
triggers:
  - "figma rules"
  - "design system rules"
  - "figma to code rules"
  - "figma tokens"
---

# figma-create-design-system-rules

## When to use

Use this skill when you need to establish or document the contract between Figma and code: token naming, component naming, spacing scales, color semantics, or lint rules that keep design and implementation in sync.

## Steps

1. **Audit existing tokens** — call `get_variable_defs` on the target Figma file to pull all variable collections (color, spacing, typography, radius, motion).
2. **Map to code names** — for each variable, derive the code token name using the project's naming convention (e.g. `color/brand/primary` → `--color-brand-primary` in CSS, `colors.brand.primary` in JS).
3. **Write the rules file** — create `design-system-rules.md` (or `.json`) in the project root with:
   - Token name mapping table (Figma name → code name)
   - Component naming convention (e.g. PascalCase, prefix rules)
   - Layer/frame naming requirements Figma designers must follow
   - Lint rules: forbidden token bypasses, hardcoded color policy, spacing-only-via-tokens
4. **Verify round-trip** — run `search_design_system` to confirm named components match the documented naming convention.
5. **Commit the rules file** so it becomes the shared contract for all future design-to-code work.

## Output

A `design-system-rules.md` (or structured JSON) file that both designers and engineers reference. Downstream skills (`fabius-decor-figma-implement-design`, `fabius-decor-figma-generate-library`) consume these rules automatically.
