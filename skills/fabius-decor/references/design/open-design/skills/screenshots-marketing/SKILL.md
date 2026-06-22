---
name: fabius-decor-screenshots-marketing
description: Generate marketing screenshots with Playwright — landing-page hero shots, App Store screenshots, and changelog visuals.
triggers:
  - "marketing screenshot"
  - "playwright screenshot"
  - "hero shot"
  - "app store screenshot"
---

# screenshots-marketing

## What it does

Generate marketing screenshots with Playwright. Covers landing-page hero shots, App Store screenshots, and changelog visuals.

## When to use

- You need pixel-perfect promotional images from a live or local URL.
- You're preparing App Store or Play Store listing assets.
- You want automated changelog screenshots as part of a release flow.

## How to use

1. Install Playwright in your project if not already present:
   ```bash
   npm install -D playwright
   npx playwright install chromium
   ```
2. Write a screenshot script targeting your URL and desired viewport:
   ```js
   const { chromium } = require('playwright');
   const browser = await chromium.launch();
   const page = await browser.newPage();
   await page.setViewportSize({ width: 1280, height: 800 });
   await page.goto('https://your-app.example.com');
   await page.screenshot({ path: 'hero.png', fullPage: false });
   await browser.close();
   ```
3. For App Store sizing (e.g. 1290×2796 for iPhone 14 Pro Max), set the viewport accordingly and use `deviceScaleFactor: 3`.
4. Automate across multiple routes or states by looping over URLs and interaction sequences before capturing.

## Output

PNG or JPEG screenshots at the target viewport, ready for marketing pages, storefronts, or changelogs.
