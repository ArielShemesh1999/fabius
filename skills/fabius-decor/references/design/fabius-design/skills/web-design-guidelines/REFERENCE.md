---
name: fabius-decor-web-design-guidelines
description: Web design guidelines for product UI — layout, typography, color, motion, and accessibility standards used by high-quality engineering teams.
triggers:
  - "web design guidelines"
  - "vercel design"
  - "product ui standards"
  - "design checklist"
---

# web-design-guidelines

Web design guidelines and standards for product UI. Covers layout, typography, color, motion, and accessibility.

## When to use

Invoke this skill when:
- Setting up design standards for a new product or component library
- Auditing existing UI against best-practice guidelines
- Answering questions about layout grids, type scales, color tokens, or motion rules
- Running a design checklist before shipping a feature

## Core areas

### Layout
- Use a consistent grid (12-column on desktop, 4-column on mobile)
- Maintain predictable spacing using a base-8 scale (8, 16, 24, 32, 48, 64px)
- Avoid fixed heights; let content define height

### Typography
- Limit typefaces to two: one for headings, one for body
- Define a type scale (e.g. 12/14/16/20/24/32/48px) and stick to it
- Minimum body size: 16px; minimum touch target: 44×44px

### Color
- Establish semantic tokens: `--color-bg`, `--color-fg`, `--color-accent`, `--color-error`, `--color-success`
- Maintain WCAG AA contrast (4.5:1 for text, 3:1 for large text and UI)
- Never communicate information by color alone

### Motion
- Default to `ease-out` for entrance, `ease-in` for exit
- Enter ~200ms, exit ~140ms — asymmetric feels decisive
- Respect `prefers-reduced-motion`; provide a no-animation fallback

### Accessibility
- All interactive elements must be keyboard-navigable and have visible focus rings
- Use semantic HTML; add ARIA only when native semantics fall short
- Test with a screen reader (VoiceOver/NVDA) before shipping

## Design checklist

Before marking a UI change ready:

- [ ] Spacing follows the base-8 scale
- [ ] Color contrast passes WCAG AA
- [ ] All text uses defined type-scale tokens
- [ ] Motion respects `prefers-reduced-motion`
- [ ] Interactive elements have visible focus states
- [ ] Component tested on mobile viewport (≥375px wide)
- [ ] Images have meaningful `alt` text

## Output

Apply these guidelines to produce a concrete recommendation, token set, or checklist result for the user's specific UI context.
