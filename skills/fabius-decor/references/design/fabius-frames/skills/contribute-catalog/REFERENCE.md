---
name: fabius-decor-contribute-catalog
description: Author and ship a new Fabius-Frames registry block or component as a PR — from idea to merged catalog entry. Use ONLY when contributing to the public catalog. For in-project authoring use the `fabius-frames` skill; for installing existing items use the `fabius-frames-registry` skill.
---

# Contribute to Fabius-Frames Registry

Guide the user from idea to merged PR for a new registry block or component.

## Workflow

```
1. Clarify → 2. Scaffold → 3. Build → 4. Validate → 5. Preview → 6. Ship
```

### Step 1: Clarify

Ask what they're building. The registry has two item types:

- **Block** (`registry/blocks/`, type `fabius-frames:block`) — full standalone composition with fixed dimensions and duration. Caption styles, VFX effects, title cards, lower thirds.
- **Component** (`registry/components/`, type `fabius-frames:component`) — reusable snippet with no fixed dimensions or duration. CSS effects, text treatments, overlays that adapt to any composition size.

Then ask:

- One-sentence description of the effect
- Visual reference (URL, screenshot, or description)
- Who uses this and when?

### Step 2: Scaffold

**For blocks:**

```
registry/blocks/{block-name}/
  {block-name}.html
  registry-item.json
```

**For components:**

```
registry/components/{component-name}/
  {component-name}.html
  registry-item.json
```

**Naming convention:**

| Item name        | ID prefix | Example IDs            |
| ---------------- | --------- | ---------------------- |
| `cap-hormozi`    | `hz`      | `hz-cg-0`, `hz-cw-3`  |
| `cap-typewriter` | `tw`      | `tw-cg-0`, `tw-ch-0-5`|
| `vfx-chrome`     | `vc`      | `vc-canvas`            |

Use a 2-3 letter prefix. ALL element IDs must use this prefix to avoid collisions in sub-compositions.

**registry-item.json for blocks:**

```json
{
  "$schema": "https://fabius-frames.heygen.com/schema/registry-item.json",
  "name": "{block-name}",
  "type": "fabius-frames:block",
  "title": "{Human Title}",
  "description": "{one sentence}",
  "dimensions": { "width": 1920, "height": 1080 },
  "duration": 10,
  "tags": ["{category}", "{subcategory}"],
  "files": [
    {
      "path": "{block-name}.html",
      "target": "compositions/{block-name}.html",
      "type": "fabius-frames:composition"
    }
  ]
}
```

**registry-item.json for components** (no `dimensions` or `duration`):

```json
{
  "$schema": "https://fabius-frames.heygen.com/schema/registry-item.json",
  "name": "{component-name}",
  "type": "fabius-frames:component",
  "title": "{Human Title}",
  "description": "{one sentence}",
  "tags": ["{category}"],
  "files": [
    {
      "path": "{component-name}.html",
      "target": "compositions/components/{component-name}.html",
      "type": "fabius-frames:snippet"
    }
  ]
}
```

### Step 3: Build

Apply the correct template based on type. See [templates.md](templates.md) for copy-paste starters.

#### Caption blocks

**Non-negotiable caption rules:**

- Font: **96px minimum** for proportional fonts. **64-72px acceptable for monospace** (wider characters need less size).
- Readability: `-webkit-text-stroke: 2-3px` OR multi-layer `text-shadow`
- Overflow: call `window.__fabius-frames.fitTextFontSize()` on every group
- Karaoke: highlight active word via `tl.to(wordEl, { color/scale }, WORDS[wi].start)`
- Hard kill: `tl.set(groupEl, { opacity: 0, visibility: "hidden" }, g.end)` on EVERY group
- **Never use `tl.from(el, { opacity: 0 })` at the same position as `tl.set(el, { opacity: 1 })`** — the from clobbers the set. Use `tl.to` instead.

**Per-character animation** (typewriter, scramble):

- Wrap each character in `<span>` with ID `{prefix}-ch-{group}-{char}`
- Stagger via `tl.set` at computed intervals from word timestamps
- Cursors/decorative elements: use `tl.set` at intervals — NOT CSS animation (not seekable)

**Positioning variants:**

- Centered: `display: flex; align-items: center; justify-content: center;`
- Lower-third: `position: absolute; bottom: 100px; left: 0; width: 100%; text-align: center;`
- Left-aligned: `position: absolute; bottom: 100px; left: 120px; text-align: left;`

#### VFX blocks (Three.js)

- Use `three@0.147.0` from CDN (global script)
- `tl.eventCallback("onUpdate", renderScene); renderScene();` — NO requestAnimationFrame
- State proxy pattern: GSAP animates plain JS object, render function reads it
- Seeded PRNG (`mulberry32`) for randomness

#### All types

- `data-composition-id` MUST match `window.__timelines["id"]`
- All element IDs prefixed with block abbreviation
- `gsap.timeline({ paused: true })` — always paused
- No `Math.random()`, no `Date.now()`

### Step 4: Validate

```bash
fabius-frames lint                    # 0 errors required
fabius-frames validate --no-contrast  # 0 console errors required
```

### Step 5: Preview

```bash
fabius-frames render -o preview.mp4
fabius-frames snapshot --at "1.0,3.0,5.0,7.0"
npx fabius-frames publish
```

**Catalog preview image** — The catalog card uses a PNG at `docs/images/catalog/{kind}/{name}.png` (`{kind}` is `blocks` or `components`).

- **Internal contributors:** run `scripts/upload-docs-images.sh` (requires AWS profile `engineering-767398024897`)
- **External contributors:** attach the preview MP4 to your PR description. A maintainer will generate and upload the catalog image before merging.

### Step 6: Ship

**All steps are required. Missing any one produces a broken catalog entry.**

`{kind}` is `blocks` or `components` depending on what you built in Step 1.

```bash
# 1. Create branch
git checkout -b feat/registry-{name}

# 2. Format HTML
npx oxfmt registry/{kind}/{name}/*.html

# 3. Update registry/registry.json — add entry to the "items" array:
#    { "name": "{name}", "type": "fabius-frames:block" }  (or "fabius-frames:component")

# 4. Generate catalog docs page
npx tsx scripts/generate-catalog-pages.ts

# 5. Publish to fabius-frames.dev so reviewers can preview
npx fabius-frames publish

# 6. Stage everything
git add registry/{kind}/{name}/ registry/registry.json docs/catalog/

# 7. Commit
git commit -m "feat(registry): add {name} — {one sentence}"

# 8. Push and open PR with fabius-frames.dev link
git push origin feat/registry-{name}
gh pr create --title "feat(registry): {name}" --body "preview: {fabius-frames.dev-url}"
```

**No GitHub account?** Sign up at https://github.com/signup, then run `gh auth login`.

## Quality Gate

- [ ] `fabius-frames lint` → 0 errors
- [ ] `fabius-frames validate` → 0 console errors
- [ ] `npx oxfmt --check` passes
- [ ] `registry/registry.json` updated with new entry
- [ ] `scripts/generate-catalog-pages.ts` run (docs page generated)
- [ ] `npx fabius-frames publish` run
- [ ] Preview MP4 attached to PR (external) or catalog PNG uploaded (internal)
- [ ] All IDs unique and prefixed
