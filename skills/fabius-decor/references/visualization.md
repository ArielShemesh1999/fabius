# Fabius Figura — data-visualization playbook (entry)

The on-demand depth for `fabius-decor`'s visualization concern. Lean entry doc; the full chart-recipe library (the **fabius-figura** library of the fabius corpus, [CORPUS.md](../../../CORPUS.md)) is paged in on demand. **Maximize data-ink, strike narrow.** A chart obeys every `fabius-decor` law — one accent, tokens not inline values, type-led hierarchy, restraint — plus the rules here.

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
[ ] direct labels on series; legend only when direct labels can't fit
[ ] bars start at zero; line axes may crop honestly (annotate if so)
[ ] title = the takeaway ("Signups doubled"), subtitle = the dimensions
[ ] units, source, and the one annotation the reader should leave with
[ ] readable at the smallest render size (mobile first applies to charts too)
```

## Accessible color ramps

Lean on a single-hue sequential ramp for magnitude, a diverging ramp only around a true midpoint, and a categorical set capped at ~6 distinguishable hues. Encode the critical contrast with **shape or position too**, never hue alone. Pull the actual values from `fabius-decor`'s token contract so charts match the product surface.

## Reproducible SVG — the figura path

Generate charts as **tokenized SVG from data**, not screenshots: versionable, themeable, crisp at any scale. The repo ships the path in `assets/charts/` — `svgplot.py` (a dependency-light numpy→SVG plotter) and `render_figures.py` (re-renders every figure from source). Rule: a figure is **built from its data**, never hand-tweaked, so it re-renders identically and stays honest (the same prove-from-source discipline as the benchmark figures).

## Diagrams as code

Flowcharts, architecture, sequence, and state diagrams: prefer a text-defined source (Mermaid / Graphviz / hand-built SVG) committed alongside the code, so the diagram is diffable and regenerable. State machines pair with `fabius-ludus`; pipelines and plans pair with `fabius-disciplina`.

## The recipe library (corpus — indexed, not bundled)

The deep library — per-library chart recipes, the SVG component kit, and brand-matched palettes (the **fabius-figura** library) — lives in the fabius corpus ([CORPUS.md](../../../CORPUS.md)). Query the index for the **one** recipe the task needs and page it in; never load the library wholesale (`fabius-parcus`; routing-policy R9 · M9).
