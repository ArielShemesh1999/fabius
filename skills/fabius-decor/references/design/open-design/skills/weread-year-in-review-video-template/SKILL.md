---
name: fabius-decor-weread-year-in-review-video-template
description: Vertical 9:16 HTML-to-MP4 annual reading report template — warm paper texture, editorial typography, book-page metaphors, reading stats, and deterministic motion.
triggers:
  - "WeRead year in review"
  - "WeRead annual report"
  - "reading year in review video"
  - "annual reading report template"
  - "微信读书年度报告"
  - "读书年度总结视频"
  - "阅读年报 HyperFrames"
---

# WeRead Year in Review Video Template

Create a vertical HyperFrames composition for annual reading reports: WeRead,
Goodreads, Readwise, Notion reading logs, book clubs, or personal learning
recaps. The template turns reading time, active days, bookshelf assets, notes,
keywords, and a reading persona into a shareable 9:16 video.

## Resource Map

```text
weread-year-in-review-video-template/
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
2. Replace the default report data in the `REPORT` object:
   - owner/title
   - reading hours and active days
   - bookshelf and completion stats
   - note composition
   - interest keywords
   - reading persona and share line
3. Preserve the 12-scene timeline unless the user asks for a shorter cut.
4. Keep the visual language:
   - warm paper background
   - ink-blue typography
   - restrained green accents
   - book pages, bookmarks, highlights, note cards, and shelf metaphors
5. Motion should feel like flipping through a reading journal. Avoid techy
   slide transitions, bouncy UI effects, and dashboard-loading motion.
6. Keep the composition deterministic:
   - direct `data-start`, `data-duration`, and `data-track-index` attributes
   - no unseeded randomness
   - no infinite loops or `repeat: -1`
   - no dependency on scroll, hover, localStorage, or runtime class discovery
7. Validate against `references/checklist.md` before emitting.

## Output Contract

Emit one short orientation sentence, then a single HTML artifact:

```xml
<artifact identifier="weread-year-in-review-video-template" type="text/html" title="WeRead Year in Review Video Template">
<!doctype html>
<html>...</html>
</artifact>
```
