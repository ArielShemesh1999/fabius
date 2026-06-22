---
name: fabius-decor-wpds
description: WordPress Design System — apply WordPress's official design tokens, typography scale, and component patterns to themes and block-based sites.
triggers:
  - "wpds"
  - "wordpress design"
  - "wp tokens"
  - "wp design system"
---

# wpds

WordPress Design System (WPDS). Apply WordPress's official design tokens, typography, and component patterns to themes and sites.

## When to use

- Building or auditing a WordPress block theme
- Applying consistent design tokens (colors, spacing, typography) across a WordPress project
- Ensuring component patterns match the WordPress editor (block editor / Gutenberg) conventions
- Creating custom blocks that blend seamlessly with core WordPress blocks

## Core concepts

### Design tokens
WordPress exposes tokens via `theme.json`. Key categories:
- **Color**: `color.palette` — define named colors referenced by blocks and the editor color picker
- **Typography**: `typography.fontFamilies`, `typography.fontSizes` — set the global type scale
- **Spacing**: `spacing.spacingScale` or `spacing.spacingSizes` — named spacing values
- **Shadow / border**: `shadow.presets`, `border.*` — consistent elevation and border styles

### `theme.json` structure
```json
{
  "version": 3,
  "settings": {
    "color": { "palette": [] },
    "typography": { "fontFamilies": [], "fontSizes": [] },
    "spacing": { "spacingSizes": [] }
  },
  "styles": {
    "color": {},
    "typography": {},
    "elements": {}
  }
}
```

### Component patterns
- Use block patterns (`register_block_pattern`) for reusable layout sections
- Use block styles (`register_block_style`) for variant styling on core blocks
- Prefer `theme.json` styles over CSS overrides; CSS overrides break editor parity

### Typography scale
Align with the WordPress default scale unless the brand requires a custom one:
`small (13px)` / `medium (20px)` / `large (36px)` / `x-large (42px)`

### Accessibility
- All interactive elements must meet WCAG AA contrast
- Use semantic block markup; avoid wrapping blocks in non-semantic containers
- Test keyboard navigation in the block editor and on the front end

## Checklist before shipping

- [ ] Colors defined in `theme.json` `color.palette` (not hardcoded in CSS)
- [ ] Type scale uses `theme.json` `fontSizes`
- [ ] Spacing uses `theme.json` `spacingSizes`
- [ ] Custom blocks render consistently inside and outside the editor
- [ ] Block patterns registered and named following `namespace/pattern-name` convention
- [ ] WCAG AA contrast verified for all text/background combinations

## Output

Apply these patterns to produce a `theme.json` snippet, block pattern, or component recommendation tailored to the user's WordPress project.
