---
name: fabius-decor-after-hours-editorial-template
description: Luxury dark-editorial Fabius-Frames template — three-page cinematic storyboards with haute couture typography, magenta accent, and ambient grain transitions.
triggers:
  - "after hours editorial template"
  - "dark fashion fabius-frames template"
  - "haute couture motion pages"
  - "magazine style cinematic slides"
  - "高级暗黑时尚风模板"
  - "高定杂志风动效"
---

# After Hours Editorial Template

Produce a self-contained HTML editorial motion artifact in a dark luxury style — three short pages, cinematic typography, premium transition language.

## Resource map

```text
after-hours-editorial-template/
├── REFERENCE.md
├── assets/
│   └── template.html
├── references/
│   └── checklist.md
└── example.html
```

## Workflow

1. Read active `DESIGN.md` and map colors, typography tone, and layout rhythm into CSS variables while preserving a dark editorial baseline.
2. Copy `assets/template.html` to `index.html`.
3. Keep three narrative pages in sequence; do not increase default page dwell above 3 seconds.
4. Preserve premium motion behavior:
   - Staged text reveal hierarchy
   - Chapter wipe transitions
   - Ambient grain/vignette depth
   - Restrained cursor-light interaction for local preview
5. Keep output single-file HTML with inline CSS and JS.
6. Avoid sandbox-hostile browser APIs (e.g. `localStorage`, `confirm`).
7. Validate with `references/checklist.md` before emitting.

## Output contract

One short orientation sentence, then:

```xml
<artifact identifier="after-hours-editorial" type="text/html" title="After Hours Editorial Template">
<!doctype html>
<html>...</html>
</artifact>
```
