---
name: fabius-decor-algorithmic-art
description: Create reproducible generative art with p5.js and seeded randomness — procedural posters, motion-style stills, and artistic frame studies.
triggers:
  - "algorithmic art"
  - "generative art"
  - "p5js"
  - "procedural art"
  - "seeded randomness"
  - "生成艺术"
---

# Algorithmic Art

Generate p5.js sketches where every render is reproducible via a fixed seed.

## When to use

Use when the user wants procedural/generative visuals: abstract posters, motion-style stills, particle systems, geometric studies, or data-driven art.

## Core rules

- **Always seed randomness.** Use `randomSeed(SEED)` and `noiseSeed(SEED)` at the top of `setup()`. Default seed: `42`. Expose it as a named constant so the user can swap it without hunting.
- **No external assets unless requested.** Keep the sketch self-contained — all shapes, colors, and motion from code.
- **One file.** Emit a single `.html` file with p5.js loaded from CDN (`https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.4/p5.min.js`) and the sketch inline.
- **No `random()` outside `draw()` context.** Call `randomSeed` before any random draw calls to guarantee determinism across re-runs.

## Workflow

1. Clarify (or assume) canvas size, color palette, and visual style.
2. Choose a generative technique matching the style (flow fields, L-systems, recursive subdivision, particle trails, Voronoi, etc.).
3. Implement with a named `SEED` constant and deterministic draw loop.
4. Add a `keyPressed()` handler: `S` key saves the canvas as PNG, `R` key re-seeds with `Math.floor(Math.random()*99999)` and redraws.
5. Validate: run mentally — confirm no unseeded `random()` calls outside the seeded context.

## Output contract

One sentence describing the technique, then a single HTML artifact:

```xml
<artifact identifier="algorithmic-art" type="text/html" title="Algorithmic Art">
<!doctype html>
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.4/p5.min.js"></script>
</head>
<body>
<script>
const SEED = 42;
function setup() {
  createCanvas(800, 800);
  randomSeed(SEED);
  noiseSeed(SEED);
  // …
}
function draw() { /* … */ }
</script>
</body>
</html>
</artifact>
```
