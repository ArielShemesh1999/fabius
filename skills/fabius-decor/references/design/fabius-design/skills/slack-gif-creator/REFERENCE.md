---
name: fabius-decor-slack-gif-creator
description: Create animated GIFs optimized for Slack — respects size constraints, composable animation primitives.
triggers:
  - "slack gif"
  - "animated gif"
  - "reaction gif"
  - "tiny gif"
---

# slack-gif-creator

## What it does

Produce animated GIFs sized and optimized for Slack: custom emoji (128×128 px, ≤128 KB) and inline message GIFs. Provides validators for size constraints and composable animation primitives.

## When to use

- Creating a custom Slack emoji from a logo, illustration, or icon.
- Generating a short reaction GIF for team use.
- Automating GIF output as part of a design or release workflow.

## Constraints

| Target | Max size | Dimensions |
|---|---|---|
| Custom emoji | 128 KB | 128×128 px |
| Inline GIF | ~2 MB | Any, keep < 480px wide |

## How to use

1. Prepare your frames as PNG or SVG (use a canvas or SVG animation for programmatic generation).

2. Encode with `gifski` (best quality) or `ffmpeg` (fastest):
   ```bash
   # gifski — high quality
   gifski --fps 12 --width 128 --output emoji.gif frame*.png

   # ffmpeg — quick
   ffmpeg -framerate 12 -i frame%03d.png -vf "scale=128:128" -loop 0 emoji.gif
   ```

3. Validate size before uploading:
   ```bash
   stat -f%z emoji.gif   # macOS
   stat -c%s emoji.gif   # Linux
   # must be ≤ 131072 bytes for emoji
   ```

4. If over budget, reduce fps (try 8), color palette (add `-colors 64` to gifski), or frame count.

5. Upload to Slack: **Workspace settings → Customize → Emoji → Add custom emoji**.

## Tips

- Limit to 16–32 colors when the palette is simple; it cuts file size without visible quality loss.
- Loop count: `0` = infinite (correct for emoji and reactions).
- Avoid dithering on solid-color animations — it bloats the palette unnecessarily.

## Output

An optimized `.gif` file ready for Slack emoji upload or inline use, under the target size budget.
