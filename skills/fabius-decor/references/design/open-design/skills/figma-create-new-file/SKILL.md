---
name: fabius-decor-figma-create-new-file
description: Create a new blank Figma Design or FigJam file as the first step in a scripted design-system or workshop workflow.
triggers:
  - "figma new file"
  - "figjam new"
  - "create figma file"
---

# figma-create-new-file

## When to use

Use this skill at the start of any scripted design workflow that needs a clean Figma canvas: new design system, new prototype, new FigJam board for a workshop.

## Steps

1. **Determine file type** — `DESIGN` for UI/component work, `FIGJAM` for diagrams and workshops.
2. **Call `create_new_file`** with:
   - `name` — descriptive project name (e.g. `"Acme Design System v1"`)
   - `fileType` — `"DESIGN"` or `"FIGJAM"`
3. **Store the returned `fileKey`** — every subsequent Figma skill call in this session targets this key.
4. **Set up initial structure** (Design files only):
   - Create a `Cover` page for thumbnails/metadata.
   - Create a `Components` page for the component library.
   - Create one `Screens` page per major product area.
5. **Verify** — call `get_metadata` with the new `fileKey` to confirm the file is accessible and named correctly.

## Output

A live Figma file with the correct type and initial page structure, ready for `fabius-decor-figma-generate-library` or `fabius-decor-figma-generate-design` to populate.
