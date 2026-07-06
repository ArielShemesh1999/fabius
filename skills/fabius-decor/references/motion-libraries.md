# Fabius Motus — the motion-library map

Loaded on demand by `fabius-decor`. This is the **decision layer** over the motion corpus, not a replacement for it: the deep GSAP library lives in the **fabius-motion** bundle, and the per-technique recipes (Anime.js, CSS animations, WAAPI, Lottie, Three.js, TypeGPU, Tailwind) live in the **fabius-frames** bundle — both in `references/design/`. This file answers the question *before* those: **what mechanism should carry this motion at all?** The answer is almost always "the smallest one that reaches the browser's compositor."

*(Web-platform APIs are royalty-free standards; library licenses verified 2026 — re-check before a sealed build.)*

## The motion laws (restraint, made mechanical)

1. **Transform & opacity only.** Those two run on the compositor thread; `width`/`top`/`margin` force layout and jank. Every mechanism below is *chosen* to keep you on transform/opacity.
2. **One motion language.** One enter curve, one press feel, one set of durations — the same language at different volumes, never a zoo of bespoke animations.
3. **No idle loop, no pulse.** Motion is earned by a state change or bound to the user's scroll — it stops when they stop. The only sanctioned loop is an indeterminate loader.
4. **Reduced-motion is default, not an afterthought.** Design *assuming* `reduce` and opt **into** motion — no library respects `prefers-reduced-motion` for you (Motion and Lenis explicitly do not; you gate them).
5. **Timing lives in tokens.** `--dur-fast`/`--dur`/`--ease-standard`/`--ease-emphasized` — never an inline `300ms cubic-bezier(...)` scattered per component.

## Native-first ladder — climb only as high as you must

Reach for the lowest rung that does the job. A JS engine is the *last* resort, not the first.

| Rung | Mechanism | Use for | Support (2026) |
|---|---|---|---|
| 1 | **CSS `transition` + `@starting-style` + `transition-behavior: allow-discrete`** | enter **and** exit of dialogs/popovers/toasts/inserted nodes — no JS, replaces the old double-rAF/`setTimeout` hack | Baseline (Chrome/Edge 117+, Safari 17.5+, Firefox 129+); non-support = instant show/hide |
| 2 | **View Transitions API** (`document.startViewTransition`, `@view-transition`) | route/state morphs & shared-element crossfades without hand-wiring FLIP | Same-doc ~Baseline (Chrome 111+, Safari 18+, Firefox 144+); cross-doc MPA not in Firefox yet — degrades to a cut |
| 3 | **CSS scroll-driven animations** (`animation-timeline: scroll()`/`view()`) | scroll progress bars, parallax, reveal-on-enter — pure CSS, compositor-thread, zero scroll listeners | Chromium 115+, Safari 26; Firefox behind a flag → **progressively enhance** (rest state = final/visible) |
| 4 | **Web Animations API** (`element.animate`) | programmatic, cancelable, promise-aware (`.finished`) sequences; the substrate Motion compiles to | Baseline, all engines |
| 5 | **A JS engine** (below) | spring physics, complex orchestration, gesture/drag, timeline scrubbing that native can't express | per-library |

Rungs 1–4 are `@supports`/`matchMedia`-detectable and fail safe. Learn the recipes for rungs 1–4 in the **fabius-frames** bundle (`css-animations`, `waapi`).

## The JS engines — reach up only when native can't

| Engine | License | Paradigm · when |
|---|---|---|
| **Motion** (motion.dev, was Framer Motion) | MIT | *Default JS pick.* Hybrid engine — WAAPI where possible, JS fallback + real `spring()`, scroll, layout, gestures. Vanilla core `motion` (`animate`/`scroll`, ~2.5–5KB) is the web-native path; `motion/react` + `motion-v` are the framework bindings (heavier — import the split entrypoints). |
| **Anime.js v4** | MIT | Lightweight timeline engine, rewritten v4 with springs + a scroll module; framework-free. The other maintained engine when you want a timeline without GSAP's weight. *(Deep recipes: fabius-frames `animejs`.)* |
| **GSAP + ScrollTrigger** | free¹ | The timeline/scroll **heavyweight** — the industry standard for complex sequenced/scroll-scrubbed motion and `SplitText`. ¹Free under Webflow (all plugins free since 2024/25; GreenSock "no-charge" license, not SPDX). *The full library is the **fabius-motion** bundle — go there for depth.* |
| **AutoAnimate** (FormKit) | MIT | ~2KB, one line: animates list/DOM add·remove·move via WAAPI, framework-agnostic. The pragmatic fallback for "designed enter/exit" when `@starting-style` is too limited. |
| **react-spring** | MIT | Spring-physics for React (`@react-spring/web`) when you want interruptible, velocity-aware springs as the component's native idiom. |
| **Rive** | runtimes MIT (editor freemium) | *Interactive* vector motion — a state machine whose inputs map 1:1 to rest/hover/active/disabled. Tiny `.riv` runtime; motion is state-driven and finite. (Also the interactive-icon path — see **Fabius Iconarium**.) |
| **Lottie** (`lottie-web`, `@lottiefiles/dotlottie-web`) | MIT (runtime) | Play a designed After-Effects/JSON animation (empty states, success moments, hero illustration). `autoplay=false loop=false` for restraint. *(Deep recipes: fabius-frames `lottie`.)* |
| **Theatre.js** | core Apache-2.0² | Sequencing/animation **design tool** — scrub and keyframe complex motion (incl. Three.js scenes) in a visual editor, ship `@theatre/core`. ²Studio package is AGPL-3.0 but dev-only, excluded from the bundle. |
| **Mo.js** | MIT | Declarative *motion-graphics* (bursts, shape morphs) for playful accent moments — reserve for a deliberate hero beat, not UI chrome. |

**Decision heuristic.** State change between two DOM states → **native rung 1–2**. Scroll-bound → **rung 3** (native) or **GSAP ScrollTrigger** when you need scrubbing/pinning/complex sequences. Spring feel on a few elements → **Motion** (or **react-spring** in React); baked into native output → a `linear()` token (below). A long, art-directed, scrubbed timeline → **GSAP** (fabius-motion) or **Theatre.js** to author it. A designer handed you an AE file → **Lottie**. The icon must react to input/data → **Rive**. Physics on *hundreds* of concurrent elements → reconsider: springs run on the main thread (WAAPI has no spring primitive).

## Smooth scroll

**Lenis** (`MIT`, darkroom.engineering) — lerps the *real* scroll position (not a fake bar), so anchors, `position:sticky`, scroll-driven timelines and a11y keep working; composes with GSAP ScrollTrigger. Two hard rules: it does **not** respect `prefers-reduced-motion` — you must `destroy()` it under `reduce`, or you've overridden an accessibility setting; and smooth-scroll is a taste call many users dislike — treat it as opt-in polish, put duration/lerp/easing in config.

## Easing & springs — converge on a few tokens

The goal is 2–3 named `--ease-*` tokens, not sprinkled beziers. For the fabius/Apple-default taste, prefer smooth sine/quad/cubic ease-outs; reserve overshoot (back/elastic/bounce) for a deliberate accent.

- **easings.net** — the cheat-sheet to *choose* your named curves (copy the `cubic-bezier()` values — they're facts; don't vendor the GPL source).
- **cubic-bezier.com** (Lea Verou, MIT) — *author* one custom curve when the presets don't fit; freeze it as a token.
- **linear() Easing Generator** (Jake Archibald, Apache-2.0) — turn a spring/bounce into a native CSS `linear(...)` value: physics feel, **zero runtime, zero main-thread cost**, baked into one `--ease-spring` token. (`linear()`: Chrome/Edge 113+, FF 112+, Safari 17.2+.)
- **spring-easing** (okikio, MIT) — programmatic bridge: `SpringEasing()` → WAAPI keyframes, `CSSSpringEasing()` → a `linear()` string, from a stiffness/damping config. Stable-but-quiet (v2.3.3).

```css
:root{
  --dur-fast:.14s; --dur:.22s;
  --ease-standard:cubic-bezier(.2,0,0,1);      /* chosen once, from easings.net */
  --ease-spring:linear(0,.63,1.02,.99,1);      /* spring baked to native via the linear() generator */
}
.enter{ transition:opacity var(--dur) var(--ease-standard), transform var(--dur) var(--ease-standard); }
@starting-style{ .enter{ opacity:0; transform:translateY(4px) scale(.98); } }
@media (prefers-reduced-motion: reduce){
  .enter{ transition-duration:.01ms; transform:none; }   /* keep the opacity, drop the movement */
}
```

## Reduced-motion — the non-negotiable

`prefers-reduced-motion` (Media Queries L5, Baseline everywhere) is the single source of truth, backing WCAG **2.3.3** (Animation from Interactions) and **2.2.2** (Pause/Stop/Hide). The discipline:

- **Default to no motion; add it under `@media (prefers-reduced-motion: no-preference)`** (or zero a `--dur` token in the `reduce` query) so new components are safe by construction.
- `reduce` ≠ *zero* — a jarring instant snap can be worse than a short opacity fade. **Keep** opacity/color fades (vestibular-safe); **drop** large translations, scale, parallax, autoplay, spin.
- Libraries don't do this for you — **gate Motion, Lenis, WAAPI, and any spring** on `matchMedia('(prefers-reduced-motion: reduce)')` yourself. Also expose an in-page control for anything auto-playing/looping (2.2.2), since not every user sets the OS flag.

## Pairs with

**fabius-motion** (the deep GSAP library — timelines, ScrollTrigger, Flip, MotionPath), **fabius-frames** (per-technique recipes: `animejs`, `css-animations`, `waapi`, `lottie`, `three`, `typegpu`, `tailwind`), **Fabius Iconarium** (the motion engines behind animated/Rive/Lottie icons), **Fabius Bidi** (flip `translateX`/transforms under `[dir=rtl]` — motion has a direction too), `fabius-decor` (law 6: restraint in motion), and `fabius-parcus` (native-first is also the *least code* — climb the ladder no higher than you must).
