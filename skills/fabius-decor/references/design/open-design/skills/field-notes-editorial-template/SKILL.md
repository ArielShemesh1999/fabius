---
name: fabius-decor-field-notes-editorial-template
description: Premium editorial "Field Notes" report — soft paper background, serif hero type, pastel insight cards, and a retention chart panel — in a single self-contained HTML file.
triggers:
  - "field notes editorial template"
  - "editorial report template"
  - "magazine style business report"
  - "pastel insight dashboard"
  - "高级编辑风报告模板"
  - "奶油底粉彩卡片数据报告"
---

# Field Notes Editorial Template

Produce a premium editorial data report in a single self-contained HTML file.

## Resource map

```text
field-notes-editorial-template/
├── SKILL.md
├── assets/
│   └── template.html
├── references/
│   └── checklist.md
└── example.html
```

## Workflow

1. Read active `DESIGN.md` and map palette/typography to root CSS variables.
2. Copy `assets/template.html` to `index.html` as the working artifact.
3. Preserve the editorial frame:
   - Paper-like background with subtle vignette
   - Serif display headlines, clean sans-serif body
   - Rounded pastel metric/insight cards
   - Chart panel with legend and axis labels
4. Keep interactions lightweight and presentation-safe:
   - Page view switcher (metrics / insights / retention)
   - Number count-up animation for key metrics
   - Chart line reveal animation
5. Use honest placeholders (`—` or neutral labels) where data is unknown.
6. Validate against `references/checklist.md` before emitting.

## Output contract

One short orientation sentence, then:

```xml
<artifact identifier="field-notes-editorial" type="text/html" title="Field Notes Editorial Report">
<!doctype html>
<html>...</html>
</artifact>
```
