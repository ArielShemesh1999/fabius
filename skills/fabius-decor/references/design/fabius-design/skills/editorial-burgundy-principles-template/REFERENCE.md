---
name: fabius-decor-editorial-burgundy-principles-template
description: Editorial studio deck in burgundy/blush/muted-gold — three slides with pill tags, typographic statements, principle cards, and keyboard/click navigation.
triggers:
  - "editorial burgundy template"
  - "studio salon deck"
  - "principles manifesto slides"
  - "pink burgundy premium presentation"
  - "酒红粉金编辑风模板"
---

# Editorial Burgundy Principles Template

A three-slide editorial deck for culture narratives, strategy storytelling, and internal manifestos.

## Resource map

```text
editorial-burgundy-principles-template/
├── REFERENCE.md
├── assets/
│   └── template.html
├── references/
│   └── checklist.md
└── example.html
```

## Workflow

1. Start from `assets/template.html`.
2. Keep the 3-slide sequence:
   - numeric headline
   - studio tags + title lockup
   - eight-principles card grid
3. Replace copy while preserving card and tag hierarchy.
4. Keep interactions:
   - Prev / Next buttons
   - dot navigation
   - keyboard navigation (`ArrowLeft` / `ArrowRight`)
5. Keep HTML self-contained and sandbox-safe.

## Output contract

Emit one concise orientation sentence and one HTML artifact:

```xml
<artifact identifier="editorial-burgundy-principles" type="text/html" title="Editorial Burgundy Principles Deck">
<!doctype html>
<html>...</html>
</artifact>
```
