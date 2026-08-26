---
name: fabius-decor-artifacts-builder
description: Build elaborate multi-component HTML artifacts using React, Tailwind CSS, and shadcn/ui.
triggers:
  - "artifacts builder"
  - "html artifact"
  - "multi component artifact"
  - "react artifact"
---

# artifacts-builder

## What it does

Build elaborate, multi-component HTML artifacts using modern frontend technologies — React, Tailwind CSS, and shadcn/ui. Use when a single-file HTML artifact needs interactive components, layout composition, or design system primitives.

## When to use

- User asks for a rich interactive HTML artifact.
- Output needs multiple UI components (tables, charts, forms, modals) in one file.
- Design fidelity requires Tailwind utilities or shadcn/ui component styles.

## Steps

1. Plan the component tree: identify distinct UI sections and their data contracts.
2. Scaffold the artifact with a single `<script type="text/babel">` entry using React 18 CDN + Tailwind CDN.
3. Build each component in isolation, then compose them in a root `App` component.
4. Apply shadcn/ui design tokens (CSS variables) in a `<style>` block for consistent visual identity.
5. Validate the artifact renders without build tools by previewing directly in the browser.

## Output

A single self-contained HTML file with embedded React components, ready to paste into any artifact canvas.
