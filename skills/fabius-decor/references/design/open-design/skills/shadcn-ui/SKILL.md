---
name: fabius-decor-shadcn-ui
description: Build accessible UI components with shadcn/ui — copy components into your project, customize freely, no runtime dependency.
triggers:
  - "shadcn"
  - "shadcn ui"
  - "shadcn components"
  - "accessible components"
---

# shadcn-ui

## What it does

Scaffold and compose UI components using shadcn/ui. Components are copied directly into your codebase (not installed as a package), so you own the code and can customize without constraints.

## When to use

- Starting a new UI feature that needs accessible, styled primitives (buttons, dialogs, forms, tables).
- Replacing ad-hoc HTML with consistent, composable components.
- Building a design system layer on top of Tailwind CSS + Radix UI.

## How to use

1. Initialize shadcn/ui in your project:
   ```bash
   npx shadcn@latest init
   ```
   Choose your style (Default or New York), base color, and CSS variable preference.

2. Add individual components as needed:
   ```bash
   npx shadcn@latest add button
   npx shadcn@latest add dialog
   npx shadcn@latest add form
   ```
   Each command copies the component source into `components/ui/`.

3. Import and use directly:
   ```tsx
   import { Button } from "@/components/ui/button";
   <Button variant="outline">Click me</Button>
   ```

4. Customize by editing the copied files — no upstream to conflict with.

## Output

Accessible, Tailwind-styled React components in `components/ui/`, owned by your codebase and ready to extend.
