---
name: fabius-decor-slides
description: Create and edit .pptx presentation decks with PptxGenJS — sales decks, kickoff briefs, and design-system showcases.
triggers:
  - "slides"
  - "pptxgenjs"
  - "sales deck"
  - "design showcase deck"
---

# slides

## What it does

Build `.pptx` presentation decks programmatically with PptxGenJS. Full control over layout, typography, shapes, charts, and images — without PowerPoint installed.

## When to use

- Generating a sales deck or investor brief from code or data.
- Automating recurring report decks (weekly, sprint review, release notes).
- Producing a design-system showcase with consistent slide layouts.

## How to use

1. Install PptxGenJS:
   ```bash
   npm install pptxgenjs
   ```

2. Create a basic deck:
   ```js
   const PptxGenJS = require('pptxgenjs');
   const pptx = new PptxGenJS();

   const slide = pptx.addSlide();
   slide.addText('Hello, World!', {
     x: 1, y: 1, w: 8, h: 1,
     fontSize: 36, bold: true, color: '363636'
   });

   pptx.writeFile({ fileName: 'deck.pptx' });
   ```

3. Add images, shapes, and charts:
   ```js
   // Image
   slide.addImage({ path: 'logo.png', x: 0.5, y: 0.5, w: 2, h: 1 });

   // Bar chart
   slide.addChart(pptx.ChartType.bar, [
     { name: 'Q1', labels: ['Jan','Feb','Mar'], values: [4,6,8] }
   ], { x: 1, y: 2, w: 8, h: 3 });
   ```

4. Use slide masters for consistent branding:
   ```js
   pptx.defineSlideMaster({
     title: 'BRAND_MASTER',
     background: { color: 'FFFFFF' },
     objects: [
       { rect: { x: 0, y: 6.9, w: '100%', h: 0.1, fill: { color: '1DB954' } } }
     ]
   });
   const slide2 = pptx.addSlide({ masterName: 'BRAND_MASTER' });
   ```

## Layout reference

- Default slide size: 10 × 7.5 inches (widescreen: 13.33 × 7.5).
- All dimensions are in inches by default; set `pptx.layout = 'LAYOUT_WIDE'` for 16:9.
- Coordinates: `x` = from left, `y` = from top, `w` = width, `h` = height.

## Output

A `.pptx` file compatible with PowerPoint, Keynote (via import), and Google Slides (via upload).
