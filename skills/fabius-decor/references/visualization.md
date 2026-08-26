# Fabius Figura — data-visualization playbook (entry)

The shipped depth for `fabius-decor`'s visualization concern. This page is the current Figura knowledge surface; no separate pageable chart-recipe library is bundled. The presentation compositions built on these rules — decks (`slides.create`), infographics (`visual.infographic`), and measured reports — live in [`decks-and-infographics.md`](decks-and-infographics.md). **Maximize data-ink, strike narrow.** A chart obeys every `fabius-decor` law — one accent, tokens not inline values, type-led hierarchy, restraint — plus the rules here.

---

## Chart-type decision table — pick by the question

| The question | Chart | Don't |
|---|---|---|
| How did it change over time? | line (area only if magnitude matters) | bar-per-day clutter |
| How do categories compare? | horizontal bar, sorted | pie for >3 things |
| What's the part-of-whole? | 100% stacked bar; one pie ≤5 slices | a donut grid |
| Are two variables related? | scatter (+ trendline) | dual-axis tricks |
| What's the distribution? | histogram / box plot | a bar of raw values |
| One number vs a target? | big-number + delta, or bullet | a gauge |

When unsure: the boring, labelled bar beats the clever novel chart. Specific beats clever (the mercatus rule, applied to pixels).

## The data-ink checklist

```
[ ] every drop of ink encodes data — gridlines faint or gone, no 3-D, no shadow
[ ] one accent = the signal series; rest muted/hairline
[ ] color is meaning, not decoration; colorblind-safe (not red/green alone)
[ ] every series ≥ 3:1 on its background — a plotted line is a graphic, not
    text: WCAG 2.2 AA gates it at 3:1 (1.4.11), and it still has to clear it
[ ] direct labels on series; legend only when direct labels can't fit
[ ] bars start at zero; line axes may crop honestly (annotate if so)
[ ] title = the takeaway ("Signups doubled"), subtitle = the dimensions
[ ] units, source, and the one annotation the reader should leave with
[ ] readable at the smallest render size (mobile first applies to charts too)
```

## Accessible color ramps

Lean on a single-hue sequential ramp for magnitude, a diverging ramp only around a true midpoint, and a categorical set capped at ~6 distinguishable hues. Encode the critical contrast with **shape or position too**, never hue alone. Pull the actual values from `fabius-decor`'s token contract so charts match the product surface.

A chart obeys the same dark-mode contract as the rest of the surface: series colors are **tokens** authored once with `light-dark()`, axes, ticks and labels inherit `currentColor` so an inline SVG takes the color of wherever it's dropped, and a fill hard-coded for white paper is a bug waiting for the theme toggle. Dark is not the light ramp inverted — a series that clears 3:1 on white often fails on near-black, so re-check both schemes. Mechanism and fallbacks → `references/design-tokens.md`.

## The chart is a component, not a page

A tile in a dashboard grid has no idea what viewport it landed in — only how wide its slot is. So the chart's responsive unit is its **container**, not the window: `container-type: inline-size` on the tile, `@container` for the real breakpoints (drop the legend for direct labels → drop the axis labels → fall back to a sparkline with a big number), and `cqi` so label type scales with the slot instead of the page. Container queries are Baseline widely available — no fallback branch. The viewport ladder still owns the dashboard shell; it just doesn't own the chart.

## Reproducible SVG — the figura path

Generate charts as **tokenized SVG from data**, not screenshots: versionable, themeable, crisp at any scale. The repo ships the path in `assets/charts/` — `svgplot.py` (a dependency-light numpy→SVG plotter) and `render_figures.py` (re-renders every figure from source). Rule: a figure is **built from its data**, never hand-tweaked, so it re-renders identically and stays honest (the same prove-from-source discipline as the benchmark figures).

## Diagrams as code

Flowcharts, architecture, sequence, and state diagrams: prefer a text-defined source (Mermaid / Graphviz / hand-built SVG) committed alongside the code, so the diagram is diffable and regenerable. State machines pair with `fabius-ludus`; pipelines and plans pair with `fabius-disciplina`.

## Current recipe surface

Use the decision table and checklists above plus the deterministic helpers at [`assets/charts/`](../../../assets/charts/). Per-library recipes, a standalone SVG component kit, and brand-matched Figura palettes are not bundled; consult authoritative library documentation for the one missing recipe rather than claiming a phantom corpus page.
