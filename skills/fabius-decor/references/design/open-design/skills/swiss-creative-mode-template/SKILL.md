---
name: fabius-decor-swiss-creative-mode-template
description: Swiss/brutalist editorial presentation template — bold typography, high-contrast geometric cards, theme switching, palette cycle, hotspot overlays, and slide navigation in a single self-contained HTML artifact.
triggers:
  - "swiss creative mode template"
  - "editorial presentation template"
  - "brutalist deck style html"
  - "creative mode deck"
  - "瑞士风演示模板"
  - "高级设计语言模板"
---

# Swiss Creative Mode Template

Produce a premium Swiss/editorial-style HTML template with strong visual rhythm and meaningful interactions, emitted as a single-file artifact.

## Resource map

```text
swiss-creative-mode-template/
├── SKILL.md
├── assets/
│   └── template.html
├── references/
│   └── checklist.md
└── example.html
```

## Workflow

1. Read active `DESIGN.md` and map palette/type/layout decisions into root CSS variables.
2. Copy `assets/template.html` to `index.html`.
3. Keep this structure intact:
   - Hero scene with bold title and geometric frame.
   - Four-step process card row.
   - Stack/architecture diagram scene.
4. Keep these interactions working:
   - Prev/next slide navigation + dot nav.
   - Theme toggle (paper/dark).
   - Palette cycle button (changes accent colors across the template).
   - Hotspot toggle for annotations/details.
5. Keep output self-contained (`<!doctype html>`, inline CSS/JS, no external runtime dependency).
6. Validate against `references/checklist.md` before emitting.

## Output contract

One short sentence before artifact, then:

```xml
<artifact identifier="swiss-creative-mode" type="text/html" title="Swiss Creative Mode Template">
<!doctype html>
<html>...</html>
</artifact>
```
