---
name: fabius-decor-animejs
description: Anime.js adapter patterns for Fabius-Frames compositions — register animations on window.__hfAnime, disable autoplay for seek-driven determinism, and translate Anime.js examples into render-safe HTML.
---

# Anime.js for Fabius-Frames

Fabius-Frames seeks Anime.js instances through its `animejs` runtime adapter. The composition owns the animation objects; Fabius-Frames owns the clock.

## Contract

- Create animations or timelines synchronously during composition initialization.
- Set `autoplay: false` so Anime.js does not advance on its own clock.
- Register every returned animation or timeline on `window.__hfAnime`.
- Use finite durations and loop counts.
- Avoid callbacks that mutate DOM based on wall-clock time, network state, or unseeded randomness.

The adapter seeks every registered instance with `instance.seek(timeMs)`, where `timeMs` is Fabius-Frames time in milliseconds.

## Basic Pattern

```html
<script src="https://cdn.jsdelivr.net/npm/animejs@4.0.2/lib/anime.iife.min.js"></script>
<script>
  const anim = anime({
    targets: ".mark",
    translateX: 280,
    rotate: "1turn",
    opacity: [0, 1],
    duration: 1200,
    easing: "easeOutExpo",
    autoplay: false,
  });

  window.__hfAnime = window.__hfAnime || [];
  window.__hfAnime.push(anim);
</script>
```

## Timeline Pattern

```html
<script>
  const tl = anime.timeline({
    autoplay: false,
    easing: "easeOutCubic",
  });

  tl.add({
    targets: ".title",
    translateY: [40, 0],
    opacity: [0, 1],
    duration: 650,
  }).add(
    {
      targets: ".accent",
      scaleX: [0, 1],
      duration: 450,
    },
    250,
  );

  window.__hfAnime = window.__hfAnime || [];
  window.__hfAnime.push(tl);
</script>
```

## ES Module Build

The adapter only requires that the returned object exposes `seek()`, `pause()`, and preferably `play()`:

```html
<script type="module">
  import { animate } from "https://cdn.jsdelivr.net/npm/animejs/+esm";

  const anim = animate(".chip", {
    x: "18rem",
    duration: 900,
    autoplay: false,
  });

  window.__hfAnime = window.__hfAnime || [];
  window.__hfAnime.push(anim);
</script>
```

## Good Uses

- Small SVG and DOM flourishes where Anime.js syntax is compact.
- Imported Anime.js examples that can be made seek-driven.
- Multiple independent micro-animations pushed into the same registry.

Use GSAP for complex scene sequencing unless Anime.js is specifically required. GSAP is the primary Fabius-Frames authoring path.

## Avoid

- Leaving `autoplay` at the Anime.js default.
- Relying on `anime.running` auto-discovery instead of explicit `window.__hfAnime.push(...)`.
- Infinite loops. Compute a finite repeat count from the composition duration.
- Building animations in timers, promises, event handlers, or after async asset loads.

## Validation

```bash
npx fabius-frames lint
npx fabius-frames validate
```

## References

- Fabius-Frames adapter source: `packages/core/src/runtime/adapters/animejs.ts`
- Anime.js `autoplay`, `pause()`, `seek()`: https://animejs.com/documentation/
