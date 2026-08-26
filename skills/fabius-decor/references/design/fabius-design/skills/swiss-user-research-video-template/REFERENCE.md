---
name: fabius-decor-swiss-user-research-video-template
description: Swiss-style user-research narrative template — warm-paper editorial aesthetics, minimalist typography, donut breakdowns, and keyboard/click slide navigation in a single self-contained HTML file.
triggers:
  - "swiss user research template"
  - "editorial research deck template"
  - "minimal user research slides"
  - "warm paper swiss style"
  - "research synthesis template"
  - "瑞士风用户研究模板"
  - "高级调性研究汇报"
---

# Swiss User Research Video Template

A premium Swiss-editorial user research template for narrative-heavy live artifacts. Visual language: warm paper, strict spacing rhythm, thin rules, and restrained micro-interactions that keep attention on the story.

## Resource map

```text
swiss-user-research-video-template/
├── REFERENCE.md
├── assets/
│   └── template.html
├── references/
│   └── checklist.md
└── example.html
```

## Workflow

1. Read `DESIGN.md`, then map tokens to the template CSS variables (`--paper`, `--ink`, `--muted`, rule colors, segment colors) without changing layout semantics.
2. Start from `assets/template.html`; keep the three-slide structure:
   - title / framing
   - participant breakdown donut
   - behavioral pattern + evidence panel
3. Preserve interactions:
   - click/keyboard slide navigation (`ArrowLeft`/`ArrowRight`)
   - bottom pagination dots with active state
   - donut legend hover highlight
   - subtle line-draw and panel-lift transitions
4. Keep all data realistic and internally consistent between copy, donut labels, and percentages.
5. Keep HTML self-contained (inline CSS/JS), with no external framework dependencies.
6. Validate using `references/checklist.md` before output.

## Output contract

Emit one concise orientation sentence and then a single HTML artifact:

```xml
<artifact identifier="swiss-user-research-deck" type="text/html" title="Swiss User Research Synthesis">
<!doctype html>
<html>...</html>
</artifact>
```
