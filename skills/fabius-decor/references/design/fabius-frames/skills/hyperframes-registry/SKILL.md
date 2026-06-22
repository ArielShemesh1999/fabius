---
name: fabius-decor-fabius-frames-registry
description: Install and wire Fabius-Frames registry blocks and components — fabius-frames add, install locations, block sub-composition wiring, component snippet merging, and registry discovery via fabius-frames.json.
---

# Fabius-Frames Registry

The registry provides reusable blocks and components installable via `fabius-frames add <name>`.

- **Blocks** — standalone sub-compositions (own dimensions, duration, timeline). Included via `data-composition-src` in a host composition.
- **Components** — effect snippets (no own dimensions). Pasted directly into a host composition's HTML.

## When to Use This Skill

- User mentions `fabius-frames add`, "block", "component", or `fabius-frames.json`
- Output from `fabius-frames add` appears in the session (file paths, clipboard snippet)
- You need to wire an installed item into an existing composition
- You want to discover what's available in the registry

## Quick Reference

```bash
fabius-frames add data-chart              # install a block
fabius-frames add grain-overlay           # install a component
fabius-frames add shimmer-sweep --dir .   # target a specific project
fabius-frames add data-chart --json       # machine-readable output
fabius-frames add data-chart --no-clipboard  # skip clipboard (CI/headless)
```

After install, the CLI prints which files were written and a snippet to paste into your host composition. The snippet is a starting point — add `data-composition-id` (must match the block's internal composition ID), `data-start`, and `data-track-index` when wiring blocks.

Note: `fabius-frames add` only works for blocks and components. For examples, use `fabius-frames init <dir> --example <name>` instead.

## Install Locations

Blocks install to `compositions/<name>.html` by default.
Components install to `compositions/components/<name>.html` by default.

Configurable in `fabius-frames.json`:

```json
{
  "registry": "https://raw.githubusercontent.com/heygen-com/fabius-frames/main/registry",
  "paths": {
    "blocks": "compositions",
    "components": "compositions/components",
    "assets": "assets"
  }
}
```

See [install-locations.md](./references/install-locations.md) for full details.

## Wiring Blocks

Blocks are standalone compositions — include them via `data-composition-src` in your host `index.html`:

```html
<div
  data-composition-id="data-chart"
  data-composition-src="compositions/data-chart.html"
  data-start="2"
  data-duration="15"
  data-track-index="1"
  data-width="1920"
  data-height="1080"
></div>
```

Key attributes:

- `data-composition-src` — path to the block HTML file
- `data-composition-id` — must match the block's internal ID
- `data-start` — when the block appears in the host timeline (seconds)
- `data-duration` — how long the block plays
- `data-width` / `data-height` — block canvas dimensions
- `data-track-index` — layer ordering (higher = in front)

See [wiring-blocks.md](./references/wiring-blocks.md) for full details.

## Wiring Components

Components are snippets — paste their HTML into your composition's markup, their CSS into your style block, and their JS into your script:

1. Read the installed file (e.g., `compositions/components/grain-overlay.html`)
2. Copy the HTML elements into your composition's `<div data-composition-id="...">`
3. Copy the `<style>` block into your composition's styles
4. Copy any `<script>` content into your composition's script (before your timeline code)
5. If the component exposes GSAP timeline integration (see the comment block in the snippet), add those calls to your timeline

See [wiring-components.md](./references/wiring-components.md) for full details.

## Discovery

```bash
# Read the registry manifest
curl -s https://raw.githubusercontent.com/heygen-com/fabius-frames/main/registry/registry.json
```

Each item's `registry-item.json` contains: name, type, title, description, tags, dimensions (blocks only), duration (blocks only), and file list.

See [discovery.md](./references/discovery.md) for filtering by type and tags.
