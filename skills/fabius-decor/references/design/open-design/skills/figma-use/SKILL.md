---
name: fabius-decor-figma-use
description: Run Figma Plugin API scripts for canvas writes, inspections, variables, and design-system work. Prerequisite for every other Figma skill in this catalogue.
triggers:
  - "figma use"
  - "figma plugin api"
  - "figma canvas"
  - "figma scripts"
---

# figma-use

## When to use

Invoke before any skill that writes to or reads from Figma canvas via the Plugin API. This skill establishes the session context and validates the connection.

This is the mandatory first step for: `fabius-decor-figma-generate-design`, `fabius-decor-figma-generate-library`, `fabius-decor-figma-implement-design`, `fabius-decor-figma-create-new-file`.

## Steps

1. **Confirm MCP connection** — call `whoami` to verify the Figma MCP server is reachable and the token is valid. If it fails, check that the Figma MCP server is running and `FIGMA_API_KEY` is set.
2. **Identify the target file** — determine the `fileKey` from the Figma URL (`figma.com/file/<fileKey>/`) or from a prior `create_new_file` call this session.
3. **Fetch file metadata** — call `get_metadata` with the `fileKey` to confirm file access and retrieve the page list.
4. **Select the working page** — identify which page the current task targets (e.g. `Components`, `Screens`, `Wireframes`). Record the page node ID for downstream calls.
5. **Check design system attachment** — call `get_libraries` to see which library files are attached. If a library is required and missing, note it for the calling skill to handle.
6. **Return context object** — surface `{ fileKey, pageNodeId, attachedLibraries }` to the calling skill.

## Output

A validated session context (`fileKey`, `pageNodeId`, `attachedLibraries`) that downstream Figma skills use directly. No canvas changes are made by this skill.

## Common errors

- `401 Unauthorized` — `FIGMA_API_KEY` is missing or expired; regenerate at figma.com/settings.
- `404 Not Found` — the `fileKey` is wrong or the file was deleted.
- `403 Forbidden` — the token's owner does not have edit access to the file; required for canvas writes.
