---
name: fabius-decor-figma-code-connect-components
description: Connect Figma design components to code components via Code Connect so design-system updates flow into the codebase automatically.
triggers:
  - "figma code connect"
  - "design to code"
  - "figma components"
  - "code connect"
---

# figma-code-connect-components

Connect Figma design components to code components using Code Connect so design-system updates flow into the codebase automatically.

## When to use

Invoke when a Figma component needs a live mapping to its codebase counterpart — so developers see real code snippets in Figma's Dev Mode and design-system changes propagate reliably.

## How to use

Ask the agent to invoke this skill by name (`figma-code-connect-components`) or with one of the trigger phrases in the frontmatter.

The Figma MCP tools required:
- `get_code_connect_map` — read existing mappings
- `add_code_connect_map` — register new component mappings
- `get_code_connect_suggestions` — discover unlinked components
- `send_code_connect_mappings` — push mappings back to Figma

## Steps

1. Run `get_code_connect_suggestions` to list Figma components without a code link.
2. For each unlinked component, identify the matching code component (file path, export name, props).
3. Call `add_code_connect_map` with the Figma node ID → code component binding.
4. Call `send_code_connect_mappings` to publish the full map to the file.
5. Verify in Figma Dev Mode that the correct code snippet appears on the component.
