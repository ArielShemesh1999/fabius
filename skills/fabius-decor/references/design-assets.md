# Fabius Materia — design raw materials (illustrations · 3D · textures · fonts · color · HuggingFace)

Loaded on demand by `fabius-decor`. The *materials* an interface is built from — illustration, 3D, texture, gradient, shadow, type, color, and generated imagery. Every one of them is a place the amateur-vs-shipped gap opens, and every one bends to the same laws: **recolor to the ONE accent token, one family/style per surface, the asset serves the message (never fills space), static or entrance-only, and license honesty.** An asset that drags a second accent or a rainbow gradient into the page is decoration; delete it or bind it to a token.

**License legend** *(verified 2026 — re-check before a sealed/redistributed build)*: `CC0`/`MIT`/`Apache`/`BSD` = ship freely · `CC BY` = **attribution required** · `custom`/`freemium` = read the terms · `non-commercial` = **preview/internal only** unless separately licensed · `proprietary/dead` = don't build on it.

## The materia laws

1. **Recolor to tokens.** An SVG illustration, pattern, or gradient must read your `--accent` + neutrals, not its stock palette. Prefer SVG/CSS you can wire to `currentColor`/vars over baked raster.
2. **One family per surface.** One illustration style, one emoji set, one type family, one 3D look — mixing unDraw with Humaaans, or a line font with a slab, fragments exactly like a second accent.
3. **The asset serves the message.** Illustration/3D/texture earns its place by teaching or focusing, never by filling whitespace (whitespace is a feature — `fabius-decor` law 4).
4. **Static by default.** Most of these ship looping animation (Storyset, Lottie, GIF, idle 3D spin) — export the *static* frame and, if motion is wanted, do transform/opacity on entrance only (`fabius-decor` law 6 · **Fabius Motus**).
5. **License honesty.** A provenance-sealed skill can't quietly ship a `CC BY` asset without credit or a `non-commercial` model's output in a paid product. Flag it.

## Illustrations — recolorable SVG scenes

| Set | License | Note |
|---|---|---|
| **unDraw** *(default)* | custom (attribution-free, commercial) | Flat SVG scenes with a built-in accent picker — set it to your `--accent`, or swap the hardcoded hex for `fill:var(--accent)` so it tracks the token. Bans repackaging/AI-training. |
| **Open Peeps** · **Humaaans** · **Open Doodles** | CC0 | Pablo Stanley's mix-&-match people (line / flat / sketch). True public domain; map the hero garment to `--accent`, rest to neutrals. |
| **ManyPixels** | free (commercial, no attribution) | 20,000+ SVG/PNG across ~18 styles — a larger, style-varied unDraw alternative for empty states/marketing. |
| **Storyset** (Freepik) | Freepik (visible attribution) | Big themed styles (Rafiki/Bro/Amico…), in-browser recolor. **Its headline feature is looping animation — export the STATIC SVG** (law 4); free use needs the credit link. |
| **IRA Design** | MIT | Gradient-background + sketch builder — constrain gradient stops to `--accent` + a tint (not a rainbow). Repo `ira-design/ira-illustrations`. |
| **Lukasz Adam** | CC0 / MIT | One illustrator's regularly-updated SVG sets; consistent stroke within a set. |
| **DrawKit** · **Blush / Croods** | freemium | Themed 2D+3D packs / artist collections with per-layer color. Verify per-pack; SVG export often Pro. Recolor loud sets (Croods) toward neutrals + one accent. |
| ~~absurd.design~~ | non-commercial + attribution | Striking surrealist ink — but free tier is **non-commercial only, credit mandatory**. Comps/inspiration, not production. |
| ~~Reshot~~ | **dead** (Envato retired) | Don't send users here; substitute unDraw/Storyset/ManyPixels. |

## 3D & spatial

| Source | License | Note |
|---|---|---|
| **Poly Haven** *(best free)* | CC0 | Models **+ HDRIs + PBR textures**, no attribution — the clean geometry+lighting source to feed model-viewer/Three.js. |
| **Quaternius** | CC0 | Cohesive low-poly MegaKits (GLTF/GLB/FBX/Blend), attribution-free. |
| **poly.pizza** | per-model CC (mostly CC-BY, some CC0) | Thousands of low-poly models incl. the rescued Google Poly; filter to CC0 to skip attribution. |
| **3dicons.co** | CC0 | 1,500+ hand-made 3D icon renders (PNG + Figma) — token-adjacent 3D accents, no attribution. |
| **Google `<model-viewer>`** | Apache-2.0 | The display *layer* — drop a `.glb` with one HTML element + AR. Gate `auto-rotate` behind `prefers-reduced-motion`; style chrome via tokens. |
| **Spline** | freemium (react-spline MIT) | Browser 3D *authoring*; from ~$12/mo (Starter) for clean GLB export — free web embed watermarks. Author materials/lighting on `--accent`; export GLB into model-viewer rather than the watermarked embed. |
| **Shapefest** | freemium | 100k+ pre-rendered 3D shape PNGs (free at 512²). Raster — can't recolor; pick a shape whose baked material sits near your palette, use as ONE focal object. |
| **Three.js** | MIT (engine + examples) | The WebGL engine for bespoke scenes — drive material/light from token values; gate idle animation on reduced-motion. Learning: Three.js Journey (portfolio repo MIT). |
| ~~Ready Player Me~~ | **dead** (shut down 2026-01-31, Netflix) | Avatars stopped working in host apps; don't build on it. |

## Textures, patterns & grain

| Resource | License | Note |
|---|---|---|
| **Open Props** *(token-native)* | MIT | Ships ready design tokens: 30 gradients (`--gradient-1..30`) **and** layered shadows (`--shadow-1..6`) that auto-adapt light/dark — drop straight into the token layer instead of pasting generator output. |
| **Hero Patterns** | CC BY 4.0 | ~90 tileable SVG data-URI patterns; foreground=`--accent`, bg=surface, keep opacity ~0.03–0.08, store the data-URI in one `--pattern-*` var. |
| **Pattern Monster** | MIT | 320+ customizable tileable SVG patterns — larger/freer than Hero Patterns, redistributable. |
| **Pattern.css** | MIT | Pure-CSS patterns (stripes/dots/zigzag) as utility classes — zero images, re-themes via `currentColor`; the most perf-safe pattern option. |
| **Transparent Textures** | per-texture CC attribution | 397 alpha-transparency tiles — layer over `background-color:var(--surface)` so the texture reads your token. Repo frozen since 2018; verify per-pattern credit. |
| **gggrain / fffuel suite** | fffuel custom (no redistribute raw SVG) | SVG grain/noise over a gradient (the "grainient" look) — **flatten to WebP** (feTurbulence is CPU-heavy). |
| **MagicPattern** · **Haikei** · **Blobmaker** · **Doodad** | freemium / verify | Generators (CSS backgrounds, waves, blobs, seamless patterns). Use the pure-CSS/SVG outputs, set colors to tokens first; rasterize blurry/filter-heavy exports. |

*(SVG Backgrounds — proprietary, no raw-file redistribution; embed-only.)*

## Gradients & mesh

Derive stops from your **accent + a tint/shade of it**, never two saturated stock hues (one-accent law). Interpolate in **OKLCH** to kill the muddy mid-zone.

- **gradient.style** (Adam Argyle) — wide-gamut/HDR gradients in OKLCH with an sRGB fallback (ship both; gate P3 behind `@supports`). The correct modern way to author a gradient token.
- **Josh Comeau Gradient Generator** — inserts mid-stops to remove the gray dead zone between two brand tokens; store the result as one `--gradient-*`.
- **uiGradients** (MIT) — ~360 presets + a `gradients.json` to seed tokens (as inspiration — re-derive stops from your accent).
- **Mesher** (CSS Hero) — mesh look as pure CSS radial-gradient stacks (themeable, resolution-free); **meshgradient.com** for the richer WebGL-warped look but it bakes to raster (lock colors, export WebP).
- **Codioful** (was Gradienta) — free with **attribution** (credit Codioful; *not* MIT); only its Unsplash-hosted mirror is attribution-free.

## Shadows, glass & soft-UI

- **Shadow Palette Generator** (Josh Comeau) *(token-native)* — emits a whole elevation scale as `--shadow-color` + `--shadow-elevation-{low,med,high}`; tint the color from a desaturated accent.
- **shadows.brumm.af** / **smoothshadows.com** — layered soft shadows (light-angle control on the latter); capture into `--shadow-md/-lg` once, reuse — never paste raw. **CSS Scan box-shadow gallery** for click-to-copy vetted shadows.
- **Glass UI / css.glass** — glassmorphism (`backdrop-filter`): tint from `rgba(var(--surface-rgb),.1)`, border = accent at low alpha, **always ship a solid `--surface` fallback and verify text contrast over the blur** (a11y). GPU-expensive — one recipe per surface.
- **Neumorphism.io** — soft-UI; base color **must equal** your surface token. *Warning: neumorphism fails contrast/affordance a11y — add real focus/hover states, avoid for primary controls.* **Claymorphism** (Hype4) for puffy decorative cards.

## Fonts

Type is a family too — one display + one body, max. Prefer **self-host** (CSP/GDPR/offline); a hosted Google Fonts `<link>` leaks client IPs.

- **Fontsource** (`MIT` tooling, fonts OFL/Apache) — self-host open fonts as version-locked npm packages; `@fontsource-variable/*` ships one variable file so weight/optical-size become token axes.
- **Bunny Fonts** — drop-in GDPR-safe Google Fonts mirror (same URL shape, no tracking) when self-host isn't practical. **Google Fonts** itself: grab the OFL file to self-host, don't hotlink.
- **Fontshare** (ITF EULA, free commercial, *not* OFL) — foundry-quality display faces (Satoshi, Clash Display, General Sans) for the ONE brand voice; can't rehost the files.
- **Modern Font Stacks** (CC0) — OS-native system-font-stack CSS, zero downloads/requests/FOUT — the privacy/perf-purest option, fits the no-third-party-request law.
- **Open substitutes for proprietary fonts** (all OFL, self-hostable): SF Pro/Helvetica → **Inter** or **Geist** (Vercel); Gilroy → **Manrope**; Circular → **Figtree**/**Hanken Grotesk**; Proxima Nova → **Mona Sans**; Avenir → **Nunito Sans**. Metrics differ — retest line-length/leading, don't assume 1:1.
- **Tools**: **Wakamai Fondue** (drop a font → axis ranges + `font-variation-settings`), **Fontjoy**/**Fontpair** (disciplined display+body pairing).
- **RTL scripts**: a Latin webfont has no Hebrew/Arabic glyphs → silent tofu fallback. Script-covering open fonts and the missing-glyph rule live in **Fabius Bidi**.

## Color tooling

Laws: **one accent**, **ink ≠ `#000`** (near-black reads photographic), **WCAG ≥ 4.5:1** body text (APCA for dark UI/thin text), **colorblind-safe** (never hue alone).

- **Token systems (adopt wholesale)**: **Radix Colors** (`MIT`, 12-step role-based, APCA-tuned, same index light/dark), **Open Color** (`MIT`, gray-9 is a real near-black), **Tailwind palette** (`MIT`, OKLCH in v4), **Reasonable Colors** (`CC0`, any two steps 5 apart clear AA — a11y baked into the ramp).
- **Palette generators**: **Coolors** (fast + built-in WCAG/CVD checks), **Realtime Colors** (judge a palette *in a page mockup*, forces role assignment), **Huemint** (role-aware ML), **Adobe Color** (harmony wheel + image extract + WCAG + colorblind-safe checker in one).
- **Contrast-first / OKLCH**: **Adobe Leonardo** (`Apache`, generate from a target contrast ratio — powers Spectrum), **ColorBox** (algorithm `lyft/coloralgorithm` **Apache-2.0**, not MIT), **oklch.com** (`MIT`, OKLCH picker + P3 gamut warnings), **Harmonizer** (APCA-consistent OKLCH palettes).
- **Contrast checkers**: **WebAIM** (canonical WCAG-2 gate, ≥4.5 body), **APCA Calculator** (Myndex — perceptual Lc for dark/thin text, WCAG-3-bound; target Lc 75–90), **Colour Contrast Analyser** (TPGi — desktop eyedropper on *rendered* pixels).
- **Colorblind sims**: **Color Oracle** (full-screen filter, Win/Mac/Linux), **Coblis** (in-browser), **Sim Daltonism** (macOS) — run token palettes and chart series through one before locking.

## HuggingFace — the generative-imagery pipeline

Generating imagery is a *design* act under the same restraint (the slot-fill prompt method is in `references/generative-imagery.md`). These models are the machinery; chain them: **generate → constrain to layout → cut out → relight → upscale → vectorize → score.** License is the first question — ship only `Apache/MIT/BSD` output; anything `non-commercial` is **preview/internal only** and the sealed skill must say so.

| Stage · model (HF id) | License | Role |
|---|---|---|
| **T2I** · `black-forest-labs/FLUX.1-schnell` | Apache-2.0 | *Default shippable* generator — photoreal/stylized in 1–4 steps (`guidance_scale=0`). |
| **T2I** · `black-forest-labs/FLUX.1-dev` | **non-commercial** | Higher fidelity for design exploration — flag output preview-only unless a BFL commercial license is on file. |
| **T2I** · `Qwen/Qwen-Image` | Apache-2.0 | *Best legible in-image text* (wordmarks/labels) — reach here over SD3.5 for lettering. |
| **T2I** · `stabilityai/stable-diffusion-3.5-large` | Community (<$1M rev) | Strong prompt-adherence; clean fit for indie/agency. |
| **T2I** · `stabilityai/stable-diffusion-xl-base-1.0` | OpenRAIL++ | The **ecosystem anchor** — the base ControlNet/IP-Adapter/LoRA attach to. |
| **Layout-lock** · `xinsir/controlnet-union-sdxl-1.0` | Apache-2.0 | One net for canny/depth/pose/lineart/scribble/seg — feed a map from your grid/wireframe so gen lands on token positions (on-composition, not slop). |
| **Style transfer** · `h94/IP-Adapter` | Apache-2.0 | Transfer a brand reference/style onto generation (SD1.5 + SDXL). |
| **Edit** · `black-forest-labs/FLUX.1-Kontext-dev` | **non-commercial** | Instruction editing of an approved comp (add/remove/restyle, keep composition) — preview-only. |
| **Cutout** · `ZhengPeng7/BiRefNet` | MIT | *Shippable* background removal / matting — clean alpha over token backgrounds. |
| **Cutout** · `briaai/RMBG-2.0` | **non-commercial** | Excellent product edges — preview/internal only. |
| **Upscale** · `ai-forever/Real-ESRGAN` | BSD-3 (upstream) | Fast, faithful 2×/4× to retina without inventing detail. |
| **Restore** · `Fanghua-Yu/SUPIR` | **non-commercial** | Generative restoration (invents plausible detail) — the open Magnific, preview-only. |
| **Relight** · `lllyasviel/IC-Light` | Apache-2.0 (SD1.5 wts) | Match a cut-out subject's lighting to the scene — drive light toward `--accent` so it reads as lit by the brand's world. Chains after BiRefNet. |
| **Vectorize** · `starvector/starvector-8b-im2svg` | Apache-2.0 | Raster **icon/logo/diagram → clean SVG code** you can recolor/stroke-normalize (not photos). |
| **Gen-vector** · `OmniSVG/OmniSVG` | Apache-2.0 (wts) | Text/image → SVG — generate a brand icon born-vector, on-token from the start. |
| **Vectorize (deterministic)** · VTracer (`ovi054/image-to-vector` Space) | MIT | Fast, GPU-free raster→SVG trace of flat art — run the MIT lib locally; Spaces get paused. |
| **Aesthetic gate** · `shunk031/aesthetics-predictor-v2-*` | Apache-2.0 (upstream) | Score N candidates, auto-reject low/AI-slop before human review — operationalizes the anti-slop law. A floor, not a brand-fit judge. |

## Token & integration

```css
/* recolor any SVG asset to the accent instead of its stock palette */
.illus [data-accent]{ fill:var(--accent); }        /* one accent; rest → neutrals */
.pattern{ background:var(--surface); background-image:var(--pattern-hero); }  /* data-URI in a var */
.card{ box-shadow:var(--shadow-md); }               /* captured once, never pasted raw */
@font-face{ /* self-hosted via Fontsource; weight is a token axis on a variable font */ }
```

## Pairs with

`fabius-decor` (the laws these serve), **Fabius Iconarium** (icons, brand marks, emoji), **Fabius Motus** (Lottie/Rive/3D motion, entrance-only), **Fabius Bidi** (script-covering fonts, the missing-glyph rule), `references/generative-imagery.md` (the slot-fill prompt method for the HF T2I stage), `fabius-praesidium` (a `non-commercial` model shipping in a paid product is a licensing risk to flag), and `fabius-parcus` (CSS/SVG you can tokenize beats a baked raster — the least-weight material).
