---
name: fabius-decor-8-bit-orbit-video-template
description: Fabius-Frames video template for retro pixel deck motion design — multi-scene, inline HTML/CSS/JS, deterministic timeline, ready to render.
triggers:
  - "fabius-frames video template"
  - "video template"
  - "pixel motion deck"
  - "retro presentation video"
  - "Fabius-Frames 模板"
  - "视频模板"
  - "像素风动效"
---

# 8-Bit Orbit Video Template

Ship a premium Fabius-Frames composition with a ready default showcase and deterministic timeline behavior.

## Resource map

```text
8-bit-orbit-video-template/
├── SKILL.md
├── assets/
│   ├── template.html
│   └── default-showcase.mp4
├── references/
│   └── checklist.md
└── example.html
```

## Workflow

1. Copy `assets/template.html` to `index.html`.
2. Keep the 3-scene structure and transition rhythm intact unless the user explicitly asks to change pacing.
3. Personalize titles, subtitle lines, labels, and palette while preserving the retro pixel aesthetic.
4. Keep timing constraint: every scene hold stays within 3 seconds.
5. Preserve deterministic behavior — no unseeded randomness, no infinite GSAP loops.
6. Keep all code self-contained in one HTML file with inline CSS/JS.
7. Validate against `references/checklist.md` before emitting the artifact.

## Output contract

One short sentence before the artifact, then a single HTML artifact:

```xml
<artifact identifier="8-bit-orbit-video-template" type="text/html" title="8-Bit Orbit Video Template">
<!doctype html>
<html>...</html>
</artifact>
```
