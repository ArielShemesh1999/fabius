---
name: fabius-decor-gsap-frameworks-gsap-frameworks
description: GSAP in Vue, Nuxt, Svelte, and SvelteKit — lifecycle-safe setup, selector scoping, and cleanup on unmount. For React use gsap-react.
triggers:
  - "gsap vue"
  - "gsap svelte"
  - "nuxt animation"
  - "sveltekit animation"
  - "framework animation"
license: MIT
---

# GSAP with Vue, Svelte, and Other Frameworks

## When to Use This Skill

Apply when writing or reviewing GSAP code in Vue (or Nuxt), Svelte (or SvelteKit), or other component frameworks with a mount/unmount lifecycle. For **React**, use **gsap-react** (useGSAP hook, gsap.context()).

**Related skills:** For tweens and timelines use **gsap-core** and **gsap-timeline**; for scroll-based animation use **gsap-scrolltrigger**; for React use **gsap-react**.

## Principles (All Frameworks)

- **Create** tweens and ScrollTriggers **after** the component's DOM is available (e.g. `onMounted`, `onMount`).
- **Kill or revert** them in the **unmount** cleanup so nothing runs on detached nodes and there are no leaks.
- **Scope selectors** to the component root so `.box` only matches elements inside that component.

## Vue 3 (Composition API)

Use **onMounted** to run GSAP after the component is in the DOM. Use **onUnmounted** to clean up.

```javascript
import { onMounted, onUnmounted, ref } from "vue";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger); // once per app, e.g. in main.js

export default {
  setup() {
    const container = ref(null);
    let ctx;

    onMounted(() => {
      if (!container.value) return;
      ctx = gsap.context(() => {
        gsap.to(".box", { x: 100, duration: 0.6 });
        gsap.from(".item", { autoAlpha: 0, y: 20, stagger: 0.1 });
      }, container.value);
    });

    onUnmounted(() => {
      ctx?.revert();
    });

    return { container };
  },
};
```

- ✅ **gsap.context(scope)** — pass the container ref as the second argument so selectors are scoped to that root. All animations and ScrollTriggers created inside are tracked and reverted when **ctx.revert()** is called.
- ✅ **onUnmounted** — always call **ctx.revert()** so tweens and ScrollTriggers are killed and inline styles reverted.

## Vue 3 (script setup)

Same pattern with `<script setup>` and refs:

```javascript
<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

const container = ref(null);
let ctx;

onMounted(() => {
  if (!container.value) return;
  ctx = gsap.context(() => {
    gsap.to(".box", { x: 100 });
    gsap.from(".item", { autoAlpha: 0, stagger: 0.1 });
  }, container.value);
});

onUnmounted(() => {
  ctx?.revert();
});
</script>

<template>
  <div ref="container">
    <div class="box">Box</div>
    <div class="item">Item</div>
  </div>
</template>
```

## Nuxt 4

Use a **reusable composable** to register GSAP plugins and lazy-load plugins that are not widely used:

```typescript
// composables/useGSAP.ts
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

const pluginMap = {
  CustomEase: () => import("gsap/CustomEase"),
  Draggable: () => import("gsap/Draggable"),
  CSSRulePlugin: () => import("gsap/CSSRulePlugin"),
  EaselPlugin: () => import("gsap/EaselPlugin"),
  EasePack: () => import("gsap/EasePack"),
  Flip: () => import("gsap/Flip"),
  MotionPathPlugin: () => import("gsap/MotionPathPlugin"),
  Observer: () => import("gsap/Observer"),
  PixiPlugin: () => import("gsap/PixiPlugin"),
  ScrollToPlugin: () => import("gsap/ScrollToPlugin"),
  ScrollTrigger: () => import("gsap/ScrollTrigger"),
  TextPlugin: () => import("gsap/TextPlugin"),
  DrawSVGPlugin: () => import("gsap/DrawSVGPlugin"),
  Physics2DPlugin: () => import("gsap/Physics2DPlugin"),
  PhysicsPropsPlugin: () => import("gsap/PhysicsPropsPlugin"),
  ScrambleTextPlugin: () => import("gsap/ScrambleTextPlugin"),
  CustomBounce: () => import("gsap/CustomBounce"),
  CustomWiggle: () => import("gsap/CustomWiggle"),
  GSDevTools: () => import("gsap/GSDevTools"),
  InertiaPlugin: () => import("gsap/InertiaPlugin"),
  MorphSVGPlugin: () => import("gsap/MorphSVGPlugin"),
  MotionPathHelper: () => import("gsap/MotionPathHelper"),
  ScrollSmoother: () => import("gsap/ScrollSmoother"),
  SplitText: () => import("gsap/SplitText"),
} as const;

type PluginMap = typeof pluginMap;
type LoadablePlugin = keyof PluginMap;
type PluginModule<K extends LoadablePlugin> = Awaited<ReturnType<PluginMap[K]>>;
type PluginExport<K extends LoadablePlugin> = PluginModule<K>[K & keyof PluginModule<K>];

export default function () {
  gsap.registerPlugin(ScrollTrigger);

  async function lazyLoadPlugin<K extends LoadablePlugin>(plugin: K): Promise<PluginExport<K>> {
    const loader = pluginMap[plugin];
    const m = await loader();
    const p = (m as any)[plugin];
    gsap.registerPlugin(p);
    return p;
  }

  return {
    gsap,
    ScrollTrigger,
    lazyLoadPlugin,
  };
}
```

Access in components via `useGSAP()`:

```javascript
const { gsap, ScrollTrigger, lazyLoadPlugin } = useGSAP();
```

- ✅ **`useGSAP()`** provides typed access to the gsap instance and lazy load method.
- ✅ **Lazy-load any plugin** (SplitText, MorphSVG, etc.) that is not widely used to reduce initial bundle size.
- ✅ Use **gsap.context(scope)** and **onUnmounted → ctx.revert()** in components, same as Vue 3.

## Svelte

Use **onMount** to run GSAP after the DOM is ready. Return a cleanup function from `onMount` to revert. Svelte 5 uses a different lifecycle API; the same principle applies: create in "mounted," revert in "destroyed."

```javascript
<script>
  import { onMount } from "svelte";
  import { gsap } from "gsap";
  import { ScrollTrigger } from "gsap/ScrollTrigger";

  let container;

  onMount(() => {
    if (!container) return;
    const ctx = gsap.context(() => {
      gsap.to(".box", { x: 100 });
      gsap.from(".item", { autoAlpha: 0, stagger: 0.1 });
    }, container);
    return () => ctx.revert();
  });
</script>

<div bind:this={container}>
  <div class="box">Box</div>
  <div class="item">Item</div>
</div>
```

- ✅ **bind:this={container}** — get a reference to the root element to pass as scope.
- ✅ **return () => ctx.revert()** — Svelte's `onMount` cleanup function; runs when the component is destroyed.

## Scoping Selectors

Always pass the **scope** (container element or ref) as the second argument to **gsap.context(callback, scope)** so selectors are limited to that subtree.

- ✅ `gsap.context(() => { gsap.to(".box", ...) }, containerRef)` — `.box` is searched only inside `containerRef`.
- ❌ `gsap.to(".box", ...)` without a context scope can affect other instances or the rest of the page.

## ScrollTrigger Cleanup

ScrollTrigger instances created inside **gsap.context()** are reverted when **ctx.revert()** is called. Call **ScrollTrigger.refresh()** after layout changes that affect trigger positions (e.g. after data loads, after `nextTick` in Vue or `tick` in Svelte).

## When to Create vs Kill

| Lifecycle             | Action                                                                                                            |
| --------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Mounted**           | Create tweens and ScrollTriggers inside **gsap.context(scope)**.                                                  |
| **Unmount / Destroy** | Call **ctx.revert()** — kills all animations and ScrollTriggers in that context, reverts inline styles. |

Do not create GSAP animations in synchronous top-level script that runs before the root element exists.

## Do Not

- ❌ Create tweens or ScrollTriggers before the component is mounted; the DOM nodes may not exist yet.
- ❌ Use selector strings without a **scope**; pass the container to `gsap.context()` as the second argument.
- ❌ Skip cleanup; always call **ctx.revert()** in `onUnmounted` / `onMount`'s return.
- ❌ Register plugins inside a component body that runs every render; register once at app level.

**Related skills:** **gsap-react** for React-specific patterns (useGSAP, contextSafe).
