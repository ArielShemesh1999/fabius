---
name: fabius-decor-pptx-generator
description: Create and edit PowerPoint presentations from scratch using PptxGenJS — a production-tested deck pipeline that outputs real .pptx files.
triggers:
  - "pptx generator"
  - "deck generator"
  - "auto pptx"
  - "pptxgenjs"
---

# pptx-generator

## What it does

Generates `.pptx` files programmatically via PptxGenJS. Covers slide creation, text/image/chart placement, theme colors, and multi-slide decks — without requiring PowerPoint or LibreOffice to be installed.

## When to use

Use when the output must be a real `.pptx` file (not an HTML slide deck or PDF) — e.g. a client deliverable, a templated report, or an automated deck pipeline.

## How to invoke

Ask the agent to run `pptx-generator` or use a trigger phrase from the frontmatter. Provide the content (outline, data, or prompt describing slides) as context.

## Output

- A `.pptx` file at the path you specify (default: `./output.pptx`).
- Console summary: slide count, file size, any shape overflow warnings.

## Key PptxGenJS usage

```js
const pptx = new PptxGenJS();
const slide = pptx.addSlide();
slide.addText("Hello World", { x: 1, y: 1, w: 8, h: 1, fontSize: 36 });
await pptx.writeFile({ fileName: "output.pptx" });
```

Install: `npm install pptxgenjs`
Docs: https://gitbrent.github.io/PptxGenJS/
