# Fabius Iconarium — the icon-system map

Loaded on demand by `fabius-decor`. An icon is a *token*, not a decoration — it inherits the same laws (one accent, tokens-not-inline, restraint, designed states). This file is the map: which icon system to adopt, how to bind it to the token contract, and the one law that outranks all of it — **one family, one stroke width, per surface.** Mixing a 2px line set with a 1.5px one, or a line set with a filled one, is the single most common amateur tell. Pick one; earn every exception.

*(Licenses verified 2026 — but re-check before shipping a sealed/redistributed build. `MIT`/`ISC`/`Apache-2.0`/`CC0` are clean; `CC BY` needs **attribution**; `custom`/`proprietary` need reading the terms.)*

## The icon laws

1. **One family per surface.** All UI chrome comes from a single set. A second family fragments the eye exactly like a second accent color. Brand logos and emoji are *separate layers* (below), not exceptions to this.
2. **One stroke width.** Line sets have a grammar — Lucide/Tabler are 2px, Heroicons/Iconoir ~1.5px. Never intermix grammars; bind the width to an `--icon-stroke` token so every glyph obeys.
3. **`currentColor`, never a baked hex.** Good sets render `currentColor`, so icons ride `ink`/`muted` for free and only the *active* one takes `primary`. That's the one-accent law expressed in SVG.
4. **Size on a token.** `--icon-sm 16` / `--icon-md 20` / `--icon-lg 24`, snapped to the spacing base. Optical-size sets (Carbon, Fluent, Material) are *drawn per size* — pick the drawing that matches the grid, don't scale a 16px glyph to 32.
5. **An icon is not a label.** Icon-only controls need `aria-label`; decorative icons need `aria-hidden="true"`; interactive ones need a designed `:focus-visible` ring. Meaning never rides shape or color alone (a11y + colorblind law).
6. **Static by default.** A plain SVG is motion-restraint for free. Animate only on interaction, never idle-loop (the one exception: an indeterminate loader — below).

## Pick the line system

Default to **Lucide**; reach past it only for a reason in the right column.

| System | License | Scale · grammar | Reach for it when |
|---|---|---|---|
| **Lucide** *(default)* | ISC | 1600+ · 24px / **2px** line | Modern line UI. Best tree-shaking (`lucide-react`/vue/svelte), permissive, supersedes Feather. |
| **Tabler Icons** | MIT (SVGs) | ~5900 · 24px / **2px** | Same grammar as Lucide but 3–4× coverage — you rarely break one-family to find a glyph. |
| **Phosphor** | MIT | ~1250 × **6 weights** · 16px grid | One family must span fine chrome → heavy display, or you want duotone. *Lock one weight per surface.* |
| **Heroicons** | MIT | ~300 · **1.5px** outline + 3 solid sizes | Already in Tailwind; want outline(default)/solid(active) with sizes pre-optimized. |
| **Iconoir** | MIT | 1600+ · **1.5px** line + solid | A more delicate stroke than Lucide, fully free, no upsell. |
| **Radix Icons** | MIT | 318 · **15×15** pixel-fit | Dense dashboards where crispness at ~15px matters. Frozen set — supporting role only. |
| **Remix Icon** | Remix Icon License v1.0¹ | 3200+ · line **+ fill** twins, 24px | Guaranteed line/fill pair per icon = clean default/active toggles. ¹Bespoke (was Apache); free commercial, re-read. |
| **Material Symbols** | Apache-2.0 | ~3600 · variable font, 4 axes | Want ONE variable font whose **weight axis IS your stroke token** (fill/grade/optical-size too). Self-host for CSP. |
| **Carbon (IBM)** | Apache-2.0 | ~2000 · per optical size 16/20/24/32 | Enterprise/data-dense; icons drawn per size. *Note: `@carbon/icons` bundles IBM Telemetry — a supply-chain flag.* |
| **Fluent System Icons** | MIT | ~2000 · Regular/Filled × optical sizes | Microsoft-aligned; matched outline/filled per size, MIT. |
| **Octicons** | MIT | GitHub's set · 16 & 24 optical | Third enterprise-grade, size-optimized, MIT set (`@primer/octicons`). |
| **Hugeicons (free)** | MIT (free) / proprietary Pro | 4600+ · one style (Stroke Rounded) | Large contemporary rounded line set, free = single style (enforces one-family). *Solid/duotone are paid.* |
| **Bootstrap Icons** | MIT | 2000+ · **fill-based**, 16px | Bootstrap stacks. Fill grammar — don't sit it beside a 2px line set. |
| **Ionicons** | MIT | 1300 · outline/filled/**sharp** | Ionic/mobile web. *Default variant is FILLED — set it explicitly.* |
| **MingCute** | Apache-2.0 | 3000+ · outline **+ fill**, 24px/2px | Clean Apache alternative to Remix/Boxicons; matched pairs. |
| **Myna UI Icons** | MIT | 1180+ · 24px / **1.5px** | Genuinely-MIT delicate-stroke set (alt to Untitled UI). |
| **Solar** | CC BY 4.0² | 7401 · **7 styles** | Warm rounded aesthetic, rich style range, via Iconify. ²Attribution required; lock one style. |
| **Iconsax** | custom free³ | 1000 × 6 styles | Popular multi-style peer of Phosphor. ³Non-SPDX (no resale) — flag as free/custom. |
| **Font Awesome (free)** | icons CC BY 4.0 · font OFL · code MIT | ~2000 free · mostly Solid | Legacy/CMS, or its **Brands** glyphs. Attribution required; most outline icons are Pro. |
| **Boxicons** | icons **CC BY 4.0** · font OFL · code MIT⁴ | ~1600 · Regular/Solid/Logos | Budget outline+solid+logos. ⁴Attribution required — **not** MIT despite common belief. |
| **Untitled UI Icons** | custom free⁵ | 1100+ free · 2px line | Figma-first SaaS look. ⁵Non-SPDX "free, no attribution"; solid/duotone paid. |
| **Streamline** | proprietary freemium | 100k+ | Enormous coverage + matched illustrations, *if you have budget.* Not license-clean for an open artifact. |

**The meta-loader — Iconify** (`code: MIT`, each set keeps its own license · 250k+ icons / 200+ sets). Not a set: one API/component (`@iconify/react`, `iconify-icon` web component) that renders almost every open set on demand. Use it to *trial* families then **commit** to one — its power is also the temptation to mix. Two cautions: (1) verify the license of the *set you ship*, not Iconify's code; (2) default rendering fetches SVGs from Iconify's API at runtime — for CSP/offline/sealed builds, self-host or bundle the offline `@iconify-json/<set>`.

## Animated icons — state-driven, never idle

Animation on an icon must obey the restraint law: **triggered by interaction/state, finite, transform/opacity only, gated behind `prefers-reduced-motion` (render the static first frame).** No idle loops, no pulse. The one legitimate loop is an indeterminate **loader**.

| Resource | License | What · fit |
|---|---|---|
| **pqoqubbw/icons** (lucide-animated.com) | MIT | *Best restraint fit.* Copy-paste React components on Lucide + Motion — same 24px/2px grammar as your static Lucide, animates transform/opacity only, lives in your repo under your tokens. |
| **Lottie runtime** (`lottie-web`, `@lottiefiles/dotlottie-web`) | MIT (runtime) | The tokenized embed layer for any Lottie (incl. Lordicon exports). Play `autoplay={false} loop={false}` on mount/interaction. |
| **LottieFiles assets** | per-file⁶ | Marketplace of Lottie animations. ⁶License varies per file — "free" ≠ one license; verify each. |
| **Rive** | runtimes MIT · editor freemium | Truly *interactive* icons — the state machine maps 1:1 to rest/hover/active/disabled inputs; motion is state-driven and finite. Binary `.riv`, needs the editor. |
| **Lordicon** | proprietary (player OSS) | 45k+ animated icons, hover/click/morph triggers. *License bars using it AS your core icon pack — accent moments only, not a redistributed system.* |
| **useAnimations** | CC BY (attribution) | ~40 clean toggle line icons (React). *Must attribute; can't redistribute the raw files.* |
| **SVGator** | proprietary SaaS | *Author* bespoke animated SVG/Lottie — enforce the laws at design time, export clean, self-host. Free tier watermarks. |
| **SVG Spinners** (n3r4zzurr0) | MIT | The token-clean **loaders**: pure-SVG spinners (`svg-spinners:` via Iconify), `currentColor`, no JS. The one allowed loop — a real progress indicator, still reduced-motion-gated. |

## Brand & logo marks — a separate layer

Company/tech logos are not your icon family and not governed only by a file license — **the marks are trademarks** (CC0/MIT covers the *drawing*, never the right to imply endorsement). Keep them on a dedicated "brand wall" surface; never let a colored logo leak into a monochrome UI-icon row.

- **Simple Icons** (`CC0-1.0`) — 3400+ *monochrome* single-path brand SVGs; `cdn.simpleicons.org/{slug}/{color}` so the tint is a token. The default logo layer for socials/integrations. Read `DISCLAIMER.md` (trademarks).
- **SVGL** (code `MIT`, logos per-brand) — full-*color* logos with light/dark variants + a public API. Treat as images (`--logo-h`), don't recolor.
- **gilbarbara/logos** (`CC0` drawings, via Iconify `logos:`) — full-color dev/tech logos through the same Iconify pipeline as your icons.
- **Devicon** (`MIT`) — language/framework/tool logos with plain(monochrome) *and* colored variants — pick plain for token-clean UI, colored for a stack wall.
- **Font Awesome Brands** (icons `CC BY 4.0`) — ~490 social/brand glyphs with a *font* path Simple Icons lacks; attribution required.
- **theSVG** (`MIT` code; AWS subset `CC BY-ND`) — brands + AWS/Azure/GCP architecture icons. Keep the no-derivatives AWS paths unmodified.

## Emoji & flags

One emoji set project-wide (they're a family too). Emoji are decorative accents — never carry meaning without a text label.

- **Fluent Emoji** (`MIT`) — *cleanest for a tokenized system*: Flat + High-Contrast styles slot into light/dark + a11y; no attribution. Default to Flat (skip 3D/animated — reads as AI-slop).
- **Noto Emoji** (font `OFL 1.1` · images `Apache-2.0`) — Unicode-complete; the **monochrome** variant inherits `currentColor` like an icon; color as a webfont.
- **OpenMoji** (`CC BY-SA 4.0`) — coherent house style, on-brand-able "black" outline variant; *share-alike is copyleft* — heavier to redistribute.
- **Twemoji** (jdecked fork; code `MIT`, graphics `CC BY 4.0`) — consistent cross-platform flat emoji tracking current Unicode; attribution required; use the jdecked fork (Twitter's is archived).

**Flags** — *a flag is not a language* (never flag "English"); pair with a text label, one aspect ratio per surface, designed focus on the control.

- **flag-icons** (lipis, `MIT`) — country flags + CSS classes keyed by ISO 3166-1 alpha-2 (`.fi-us`). The default.
- **circle-flags** (HatScripts, `MIT`) — 400+ *circular* SVG flags (incl. language/subdivision) — round locale chips/avatars.
- **country-flag-icons** (`MIT`, GitLab source) — tree-shakeable SVG + React + Unicode fallbacks; the de-facto layer under phone-number selects.
- **Flagpack** (`MIT`) — flags as typed React/Vue/Svelte components with a hairline border (a small contrast win on light surfaces).

## Token integration

```css
:root{
  --icon-sm:16px; --icon-md:20px; --icon-lg:24px;   /* size on a token */
  --icon-stroke:2;                                   /* one stroke width */
  --icon:var(--muted);                               /* default tone; active → var(--primary) */
}
.icon{ width:var(--icon-md); height:var(--icon-md); color:var(--icon); }
[data-active] .icon{ color:var(--primary); }         /* only the active glyph earns the accent */
@media (prefers-reduced-motion: reduce){ .icon-anim{ animation:none !important; } }
```

- Lucide/Tabler/Iconoir/Feather: pass `strokeWidth={var(--icon-stroke)}` (Lucide: `absoluteStrokeWidth` to stop scaling).
- Material Symbols: one `font-variation-settings` line sets weight(=stroke)/fill/optical-size for every icon.
- Icon-only button: `<button aria-label="Close">` + a `:focus-visible` ring; the SVG is `aria-hidden`.

## Pairs with

`fabius-decor` (the laws), **Fabius Motus** (the motion engines behind animated/Rive/Lottie icons), **Fabius Bidi** (which directional icons mirror in RTL — chevrons/arrows/send flip, clocks/checks/logos don't), **Fabius Materia** (illustrations/3D/fonts), and `fabius-parcus` (one family, `currentColor`, static-by-default is also the *smallest* icon layer).
