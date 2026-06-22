---
name: fabius-decor-figma-generate-library
description: Build or update a professional-grade Figma component library from a codebase, keeping the Figma source of truth in sync with shipped components.
triggers:
  - "figma library"
  - "design system library"
  - "figma from codebase"
  - "sync figma"
---

# figma-generate-library

## When to use

Use when the codebase is the source of truth and Figma needs to reflect it: bootstrapping a new design system library, or syncing Figma after a round of component changes.

## Prerequisites

- A Figma Design file exists (run `fabius-decor-figma-create-new-file` if not).
- `fabius-decor-figma-use` has been invoked this session.
- Design system rules exist (run `fabius-decor-figma-create-design-system-rules` if not).

## Steps

1. **Inventory the codebase components** — list all exported components with their props/variants (e.g. read `src/components/index.ts` or equivalent barrel file).
2. **Pull existing Figma library** — call `get_libraries` to check what's already published; diff against the codebase inventory to find additions, renames, and deletions.
3. **Create/update variable collections** — call `use_figma` to write color, spacing, typography, and radius tokens as Figma variables in a `Primitives` collection, mapped per the design system rules.
4. **Generate component frames** — for each component:
   - Create a dedicated frame on the `Components` page named exactly as the code export.
   - Build the default variant using auto-layout and token-bound fills/strokes.
   - Add variants for each prop combination (size, state, theme) using the Figma variants panel API.
5. **Publish the library** — call `use_figma` to publish the file as a team library so `fabius-decor-figma-generate-design` can consume it.
6. **Verify** — call `search_design_system` and confirm all code components appear with matching names.

## Output

A published Figma library where every component and token maps 1:1 to the codebase, ready for design and code to stay in sync.
