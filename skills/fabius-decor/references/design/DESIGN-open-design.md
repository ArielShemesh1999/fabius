---
version: alpha
name: Open Design
description: An open-source, local-first AI design workspace (open-design.ai · nexu-io/open-design). Editorial print aesthetic — warm parchment canvas (`#f5f4ed`), single ink-blue accent (`#1B365D`), serif-led hierarchy at a single weight (500), no italic, no second saturated color. Designed so generated artifacts feel like high-quality printed pages rather than typical web UI. Multilingual by design (EN · zh-CN · ja). Source brand spec lives inside the repo at `design-systems/kami/DESIGN.md`.

colors:
  primary: "#1B365D"
  primary-light: "#2D5A8A"
  canvas: "#f5f4ed"
  surface-card: "#faf9f5"
  surface-sand: "#e8e6dc"
  surface-dark: "#30302e"
  canvas-deep: "#141413"
  ink: "#141413"
  ink-secondary: "#3d3d3a"
  ink-olive: "#504e49"
  ink-stone: "#6b6a64"
  border: "#e8e6dc"
  border-soft: "#e5e3d8"
  tag-tint-08: "#EEF2F7"
  tag-tint-14: "#E4ECF5"
  tag-tint-18: "#E4ECF5"
  tag-tint-22: "#D0DCE9"
  tag-tint-30: "#D6E1EE"

forbidden-colors:
  - "#ffffff (page background)"
  - "#000000 (anywhere)"
  - "cool-gray surfaces (#f8f9fa, #f3f4f6, slate-*)"
  - "any second saturated accent color"

typography:
  family-en:
    fontFamily: "Charter, Georgia, Palatino, 'Times New Roman', serif"
  family-cn:
    fontFamily: "'TsangerJinKai02', 'Source Han Serif SC', 'Noto Serif CJK SC', 'Songti SC', 'STSong', Georgia, serif"
  family-ja:
    fontFamily: "'YuMincho', 'Yu Mincho', 'Hiragino Mincho ProN', 'Noto Serif CJK JP', 'Source Han Serif JP', 'TsangerJinKai02', Georgia, serif"
  family-mono:
    fontFamily: "'JetBrains Mono', 'SF Mono', 'Fira Code', Consolas, Monaco, 'TsangerJinKai02', 'Source Han Serif SC', monospace"

  hero:
    fontFamily: serif
    fontSize: 96-106px
    fontWeight: 500
    lineHeight: 1.05-1.10
    letterSpacing: -1.2px
  display-cjk:
    fontFamily: serif
    fontSize: 48-64px
    fontWeight: 500
    lineHeight: 1.10-1.12
    letterSpacing: 0-0.3px
  section-title:
    fontFamily: serif
    fontSize: 28-32px
    fontWeight: 500
    lineHeight: 1.20
    letterSpacing: 0.4px
  h2:
    fontFamily: serif
    fontSize: 22px
    fontWeight: 500
    lineHeight: 1.25
  h3:
    fontFamily: serif
    fontSize: 17-18px
    fontWeight: 500
    lineHeight: 1.30
  lede:
    fontFamily: serif
    fontSize: 15-16px
    fontWeight: 500
    lineHeight: 1.55
  body:
    fontFamily: serif
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "0 (EN) · 0.35px (CN) · 0.02em (JA)"
  body-dense:
    fontFamily: serif
    fontSize: 13-14px
    fontWeight: 400
    lineHeight: 1.40-1.45
  caption:
    fontFamily: serif
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1.45
  eyebrow:
    fontFamily: sans (= serif)
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 1.2px
    transform: uppercase
  label:
    fontFamily: sans
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1.35
    letterSpacing: 0.4px
    transform: uppercase
  mono:
    fontFamily: mono
    fontSize: 12-13px
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: 0.4px

type-rules:
  - "Serif uses only weights 400 and 500. No 600, 700, or 900."
  - "Set strong { font-weight: 500 } explicitly so browsers don't synthesize bold."
  - "No italic anywhere — switch to ink-blue color or wrap in a tag for emphasis."
  - "Forbidden line-heights: 1.6+ (floaty), 1.0–1.05 (collide)."
  - "All-caps overlines must add +0.5 to +1.2px tracking."
  - "Apply font-variant-numeric: tabular-nums to stacked numbers, slide counters, KPI grids, P&L tables, version numbers."

spacing:
  scale: "Tight print rhythm. Sections use generous outer whitespace; cards keep dense interior padding (28px 28px 24px)."
  density: "Denser than typical web body. Body line-height stays in the 1.40–1.55 print range."

shadows:
  rule: "No hard drop shadows. Use 1px rings as edges, whisper shadows as halos."
  whisper: "0 4px 24px rgba(0,0,0,0.05)"
  ring: "0 0 0 1px var(--brand) | 0 0 0 1px var(--border)"

radius:
  default: 8px
  featured-card: 12px
  hero: 16-24px

components:
  card:
    background: "var(--ivory) — never parchment, cards lift one shade"
    border: "1px solid var(--border)"
    radius: 8px
    padding: "28px 28px 24px"
    hover: "whisper shadow only — no transform, no brightness shift"
  button-primary:
    background: "#1B365D"
    color: "#faf9f5"
    boxShadow: "0 0 0 1px #1B365D"
    padding: "8px 14px"
    radius: 8px
    font: "500 12px/1 sans"
    letterSpacing: 0.4px
  button-secondary:
    background: "#e8e6dc"
    color: "#3d3d3a"
    boxShadow: "0 0 0 1px var(--border)"
  tag:
    background: "solid hex pre-blended over parchment — never rgba()"
    default-fill: "#E4ECF5"
    reason: "Print renderers (WeasyPrint et al.) double-paint alpha fills"

gradients:
  rule: "Gradient-free by default."
  only-sanctioned: "Soft tag brush #D6E1EE → #E4ECF5 → #EEF2F7 left-to-right, very low contrast, at most once per page on one decorative tag."
  forbidden: ["hero gradients", "brand-color washes", "backdrop-filter blurs"]

visual-signature:
  - "Warm parchment background (#f5f4ed) instead of #ffffff — sets the editorial-print tone before a single word lands."
  - "Single chromatic accent (ink-blue #1B365D) covering ≤ 5% of any document surface."
  - "Serif type at one weight (500) carrying the entire hierarchy — no bold, no italic, no second family."
  - "Numbered section system (I through VIII) and tabular-nums numerals stacked under chapter heads."
  - "Geographic / coordinate motifs on the marketing site (e.g. 52.52°N Berlin) — editorial cartography feel."
  - "Dark theme uses warm charcoal (#30302e) and olive-tinted near-black (#141413), never #000."
  - "Multilingual by construction — EN / zh-CN / ja stacks swap as alternative values of --serif on :root, not chained inside one font-family."

product-context:
  what-it-is: "Open-source, local-first alternative to Claude Design. Web-deployable, BYOK at every layer. 16 coding-agent CLIs auto-detected on PATH (Claude Code, Codex, Devin, Cursor Agent, Gemini CLI, OpenCode, Qwen, Qoder, GitHub Copilot CLI, Hermes, Kimi, Pi, Kiro, Kilo, Mistral Vibe, DeepSeek TUI) become the design engine."
  bundled: "139 composable skills · 152 brand-grade design systems · 5 curated visual directions (Editorial Monocle · Modern Minimal · Warm Soft · Tech Utility · Brutalist Experimental) · sandboxed iframe preview · HTML/PDF/PPTX/MP4/ZIP export."
  media-generation: "Image (gpt-image-2) · video (Seedance 2.0) · HTML→MP4 motion (HyperFrames)."
  license: "Apache-2.0"
  install: "git clone https://github.com/ArielShemesh1999/fabius && cd open-design && pnpm install && pnpm tools-dev run web"
  site: "https://open-design.ai"
  repo: "https://github.com/ArielShemesh1999/fabius"
  stars: "53.8k (May 2026)"
  bundled-here: "Knowledge subset vendored at open-design/ in this repo: skills/, design-systems/, specs/, prompt-templates/, templates/. Heavy app code (apps/, plugins/, packages/, tools/, design-templates/, assets/, docs/) stripped — clone the upstream repo to run the daemon + web app."

do:
  - "Always start from parchment (#f5f4ed), never #ffffff."
  - "Cap ink-blue surface coverage at 5%."
  - "Use serif at weight 500 for every hierarchy level."
  - "Use solid hex tag tints, never rgba()."
  - "Apply tabular-nums to stacked numerals, KPI grids, slide counters."
  - "Lift cards via whisper shadow (0 4px 24px rgba(0,0,0,0.05)) — never transform/scale."
  - "Set strong { font-weight: 500 } explicitly to block synthesized bold."

dont:
  - "No #ffffff page backgrounds."
  - "No #000000 anywhere."
  - "No cool-gray surfaces (slate, #f3f4f6, #f8f9fa)."
  - "No italic — switch color or wrap in a tag for emphasis."
  - "No 600/700/900 serif weights."
  - "No second saturated accent color — ink-blue or nothing."
  - "No hard drop shadows, no hero gradients, no backdrop-filter blurs."
  - "Don't chain EN+CN+JA fonts inside one font-family — set the dominant-language stack on :root and scope overrides per section."
