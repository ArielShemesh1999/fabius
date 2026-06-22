---
name: fabius-decor-gsap-plugins-gsap-plugins
description: GSAP plugins — registration, ScrollToPlugin, ScrollSmoother, Flip, Draggable, Inertia, Observer, SplitText, ScrambleText, SVG and physics plugins, CustomEase, EasePack, CustomWiggle, CustomBounce, GSDevTools. Use when asking about any GSAP plugin, scroll-to, flip animations, draggable, SVG drawing, or plugin registration.
triggers:
  - "gsap plugins"
  - "gsap plugin registration"
  - "flip animation"
  - "draggable"
  - "morphsvg"
  - "splittext"
license: MIT
---

# GSAP Plugins

## When to Use This Skill

Apply when using or reviewing code that uses GSAP plugins: registering plugins, scroll-to, flip/FLIP animations, draggable elements, SVG (DrawSVG, MorphSVG, MotionPath), text (SplitText, ScrambleText), physics, easing plugins (CustomEase, EasePack, CustomWiggle, CustomBounce), or GSDevTools. ScrollTrigger has its own skill (gsap-scrolltrigger).

**Related skills:** For core tweens use **gsap-core**; for ScrollTrigger use **gsap-scrolltrigger**; for React use **gsap-react**.

## Licensing & Install

Every GSAP plugin is **free**, including for commercial use. Since Webflow's acquisition of GSAP, Club GSAP is no longer a paid tier — no plugin requires a membership, license key, or auth token, including formerly Club-only plugins (**SplitText**, **MorphSVG**, etc.).

- ✅ Install everything from the public `gsap` npm package: `npm install gsap`. All plugins are included — import them as `gsap/SplitText`, `gsap/MorphSVGPlugin`, etc.
- ❌ Do **not** generate an `.npmrc` with a GreenSock auth token, suggest the private `npm.greensock.com` registry, or tell users to sign up for Club GSAP. Those instructions are outdated.

## Registering Plugins

Register each plugin once before first use:

```javascript
import gsap from "gsap";
import { ScrollToPlugin } from "gsap/ScrollToPlugin";
import { Flip } from "gsap/Flip";
import { Draggable } from "gsap/Draggable";

gsap.registerPlugin(ScrollToPlugin, Flip, Draggable);
```

- ✅ Register before using the plugin in any tween or API call.
- ✅ In React, register at top level or once in the app before first `useGSAP`; do not register inside a component that re-renders. `useGSAP` itself is a plugin that needs to be registered before use.

## Scroll

### ScrollToPlugin

Animates scroll position (window or a scrollable element). Use for "scroll to element" or "scroll to position" without ScrollTrigger.

```javascript
gsap.registerPlugin(ScrollToPlugin);

gsap.to(window, { duration: 1, scrollTo: { y: 500 } });
gsap.to(window, { duration: 1, scrollTo: { y: "#section", offsetY: 50 } });
gsap.to(scrollContainer, { duration: 1, scrollTo: { x: "max" } });
```

**ScrollToPlugin — key config (scrollTo object):**

| Option | Description |
|--------|-------------|
| `x`, `y` | Target scroll position (number), or `"max"` for maximum |
| `element` | Selector or element to scroll to (scroll-into-view) |
| `offsetX`, `offsetY` | Offset in pixels from the target position |

### ScrollSmoother

Smooth scroll wrapper (smooths native scroll). Requires ScrollTrigger and a specific DOM structure:

```html
<body>
	<div id="smooth-wrapper">
		<div id="smooth-content">
			<!-- ALL YOUR CONTENT HERE -->
		</div>
	</div>
	<!-- position: fixed elements can go outside -->
</body>
```

Register after ScrollTrigger. See GSAP docs for full setup.

## DOM / UI

### Flip

Capture state with `Flip.getState()`, apply DOM changes, then call `Flip.from()` to animate from the previous state to the new state (FLIP: First, Last, Invert, Play).

```javascript
gsap.registerPlugin(Flip);

const state = Flip.getState(".item");
// change DOM (reorder, add/remove, change classes)
Flip.from(state, { duration: 0.5, ease: "power2.inOut" });
```

**Flip — key config (Flip.from vars):**

| Option | Description |
|--------|-------------|
| `absolute` | Use `position: absolute` during the flip (default: `false`) |
| `nested` | When true, only the first level of children is measured |
| `scale` | When true, scale elements to fit (avoids stretch); default `true` |
| `simple` | When true, only position/scale are animated (faster, less accurate) |
| `duration`, `ease` | Standard tween options |

See: https://gsap.com/docs/v3/Plugins/Flip

### Draggable

Makes elements draggable, spinnable, or throwable with mouse/touch.

```javascript
gsap.registerPlugin(Draggable, InertiaPlugin);

Draggable.create(".box", { type: "x,y", bounds: "#container", inertia: true });
Draggable.create(".knob", { type: "rotation" });
```

**Draggable — key config options:**

| Option | Description |
|--------|-------------|
| `type` | `"x"`, `"y"`, `"x,y"`, `"rotation"`, `"scroll"` |
| `bounds` | Element, selector, or `{ minX, maxX, minY, maxY }` to constrain drag |
| `inertia` | `true` to enable throw/momentum (requires InertiaPlugin) |
| `edgeResistance` | 0–1; resistance when dragging past bounds |
| `cursor` | CSS cursor during drag |
| `onDragStart`, `onDrag`, `onDragEnd` | Callbacks; receive event and target |
| `onThrowUpdate`, `onThrowComplete` | Callbacks when inertia is active |

### Inertia (InertiaPlugin)

Works with Draggable for momentum after release, or tracks velocity of any property so it can glide to a stop.

```javascript
gsap.registerPlugin(Draggable, InertiaPlugin);
Draggable.create(".box", { type: "x,y", inertia: true });
```

Track velocity of a property:
```javascript
InertiaPlugin.track(".box", "x");
```

Use `"auto"` to continue the current velocity and glide to a stop:

```javascript
gsap.to(obj, { inertia: { x: "auto" } });
```

### Observer

Normalizes pointer and scroll input across devices. Use for swipe, scroll direction, or custom gesture logic without tying directly to scroll position like ScrollTrigger.

```javascript
gsap.registerPlugin(Observer);

Observer.create({
  target: "#area",
  onUp: () => {},
  onDown: () => {},
  onLeft: () => {},
  onRight: () => {},
  tolerance: 10
});
```

**Observer — key config options:**

| Option | Description |
|--------|-------------|
| `target` | Element or selector to observe |
| `onUp`, `onDown`, `onLeft`, `onRight` | Callbacks when swipe/scroll passes tolerance in that direction |
| `tolerance` | Pixels before direction is detected; default 10 |
| `type` | `"touch"`, `"pointer"`, or `"wheel"` (default: `"touch,pointer"`) |

## Text

### SplitText

Splits an element's text into characters, words, and/or lines for staggered or per-unit animation. Returns an instance with **chars**, **words**, **lines** (and **masks** when `mask` is set). API: **SplitText.create(target, vars)**.

```javascript
gsap.registerPlugin(SplitText);

const split = SplitText.create(".heading", { type: "words, chars" });
gsap.from(split.chars, { opacity: 0, y: 20, stagger: 0.03, duration: 0.4 });
// later: split.revert() or let gsap.context() cleanup revert
```

With **onSplit()** (v3.13.0+), animations run on each split and on re-split when **autoSplit** is used:

```javascript
SplitText.create(".split", {
  type: "lines",
  autoSplit: true,
  onSplit(self) {
    return gsap.from(self.lines, { y: 100, opacity: 0, stagger: 0.05, duration: 0.5 });
  }
});
```

**SplitText — key config (SplitText.create vars):**

| Option | Description |
|--------|-------------|
| **type** | Comma-separated: `"chars"`, `"words"`, `"lines"`. Default `"chars,words,lines"`. Only split what is needed. |
| **charsClass**, **wordsClass**, **linesClass** | CSS class on each split element. Append `"++"` for an incremented class (e.g. `linesClass: "line++"` → `line1`, `line2`, …). |
| **aria** | `"auto"` (default), `"hidden"`, or `"none"`. `"auto"` adds `aria-label` on the split element and `aria-hidden` on sub-elements so screen readers read the label. |
| **autoSplit** | Reverts and re-splits when fonts load or element width changes. Animations must be created inside `onSplit()`. Return the animation from `onSplit()` for automatic cleanup on re-split. |
| **onSplit(self)** | Callback when split completes (and on each re-split if `autoSplit: true`). Returning a GSAP tween or timeline enables automatic revert/sync. |
| **mask** | `"lines"`, `"words"`, or `"chars"`. Wraps each unit with `overflow: clip` for mask/reveal effects. Access wrappers on the instance's **masks** array. |
| **tag** | Wrapper element tag; default `"div"`. Use `"span"` for inline (transforms may not render on inline elements in some browsers). |
| **deepSlice** | When `true` (default), nested elements (e.g. `<strong>`) spanning multiple lines are subdivided so lines don't stretch vertically. Only applies when splitting lines. |
| **ignore** | Selector or element(s) to leave unsplit (e.g. `ignore: "sup"`). |
| **smartWrap** | When splitting **chars** only, wraps words in `white-space: nowrap` to avoid mid-word line breaks. Default `false`. |
| **wordDelimiter** | Word boundary: string (default `" "`), RegExp, or `{ delimiter: RegExp, replaceWith: string }`. |
| **prepareText(text, parent)** | Function to modify raw text before splitting (e.g. insert break markers for languages without spaces). |
| **propIndex** | When `true`, adds a CSS variable with index on each split element (e.g. `--word: 1`, `--char: 2`). |
| **reduceWhiteSpace** | Collapse consecutive spaces; default `true`. |
| **onRevert** | Callback when the instance is reverted. |

**Tips:** Split only what is animated. For custom fonts, split after they load (e.g. `document.fonts.ready.then(...)`) or use `autoSplit: true` with `onSplit()`. To avoid kerning shift when splitting chars, use `font-kerning: none; text-rendering: optimizeSpeed;`. Avoid `text-wrap: balance`. SplitText does not support SVG `<text>`.

See: https://gsap.com/docs/v3/Plugins/SplitText/

### ScrambleText

Animates text with a scramble/glitch effect.

```javascript
gsap.registerPlugin(ScrambleTextPlugin);

gsap.to(".text", {
  duration: 1,
  scrambleText: { text: "New message", chars: "01", revealDelay: 0.5 }
});
```

## SVG

### DrawSVG (DrawSVGPlugin)

Reveals or hides the stroke of SVG elements by animating `stroke-dashoffset`/`stroke-dasharray`. Works on `<path>`, `<line>`, `<polyline>`, `<polygon>`, `<rect>`, `<ellipse>`.

**drawSVG value:** Describes the **visible segment** as start and end positions. Format: `"start end"` in percent or length. `"0% 100%"` = full stroke; `"20% 80%"` = stroke only between 20% and 80%.

**Required:** The element must have a visible stroke — set `stroke` and `stroke-width` in CSS or as SVG attributes.

```javascript
gsap.registerPlugin(DrawSVGPlugin);

// draw from nothing to full stroke
gsap.from("#path", { duration: 1, drawSVG: 0 });
// explicit segment
gsap.fromTo("#path", { drawSVG: "0% 0%" }, { drawSVG: "0% 100%", duration: 1 });
// stroke only in the middle
gsap.to("#path", { duration: 1, drawSVG: "20% 80%" });
```

**Caveats:** Only affects stroke. Prefer single-segment `<path>` elements. **DrawSVGPlugin.getLength(element)** and **DrawSVGPlugin.getPosition(element)** return stroke length and current position.

See: https://gsap.com/docs/v3/Plugins/DrawSVGPlugin

### MorphSVG (MorphSVGPlugin)

Morphs one SVG shape into another by animating the `d` attribute. Start and end shapes do not need the same number of points. Works on `<path>`, `<polyline>`, and `<polygon>`; `<circle>`, `<rect>`, `<ellipse>`, and `<line>` can be converted via **MorphSVGPlugin.convertToPath(selector | element)**.

```javascript
gsap.registerPlugin(MorphSVGPlugin);

MorphSVGPlugin.convertToPath("circle, rect, ellipse, line");

gsap.to("#diamond", { duration: 1, morphSVG: "#lightning", ease: "power2.inOut" });
// object form:
gsap.to("#diamond", {
  duration: 1,
  morphSVG: { shape: "#lightning", type: "rotational", shapeIndex: 2 }
});
```

**MorphSVG — key config (morphSVG object):**

| Option | Description |
|--------|-------------|
| **shape** | _(Required.)_ Target shape: selector, element, or raw path string. |
| **type** | `"linear"` (default) or `"rotational"`. Try rotational when linear looks wrong. |
| **map** | Segment matching: `"size"` (default), `"position"`, or `"complexity"`. |
| **shapeIndex** | Offsets point mapping to avoid shape "crossing over." Use `"log"` once to get the auto-calculated value. Array for multi-segment paths. |
| **smooth** | (v3.14+) `"auto"`, number, or object: `{ points, redraw, persist }`. Adds smoothing when the morph looks jagged. |
| **curveMode** | (v3.14+) Interpolates control-handle angle/length to avoid mid-morph kinks. |
| **origin** | Rotation origin for `type: "rotational"`. Default `"50% 50%"`. |
| **precision** | Decimal places for output path data; default `2`. |
| **precompile** | Array of precomputed path strings or `"log"`. Skips expensive startup calculations for complex morphs. |
| **render** | Function(rawPath, target) called each update (e.g. draw to canvas). |
| **updateTarget** | When using `render` for canvas-only, set `false` so the original `<path>` is not updated. |

See: https://gsap.com/docs/v3/Plugins/MorphSVGPlugin

### MotionPath (MotionPathPlugin)

Animates an element along an SVG path.

```javascript
gsap.registerPlugin(MotionPathPlugin);

gsap.to(".dot", {
  duration: 2,
  motionPath: { path: "#path", align: "#path", alignOrigin: [0.5, 0.5] }
});
```

**MotionPath — key config (motionPath object):**

| Option | Description |
|--------|-------------|
| `path` | SVG path element, selector, or path data string |
| `align` | Path element or selector to align the target to |
| `alignOrigin` | `[x, y]` origin (0–1); default `[0.5, 0.5]` |
| `autoRotate` | Rotate element to follow path tangent |
| `curviness` | 0–2; path smoothing |

### MotionPathHelper

Visual editor for MotionPath — use during development to tune path alignment.

```javascript
gsap.registerPlugin(MotionPathPlugin, MotionPathHelperPlugin);

const helper = MotionPathHelper.create(".dot", "#path", { end: 0.5 });
```

## Easing

### CustomEase

Custom easing curves (cubic-bezier or SVG path):

```javascript
gsap.registerPlugin(CustomEase);
const ease = CustomEase.create("name", ".17,.67,.83,.67");
gsap.to(".el", { x: 100, ease: ease, duration: 1 });
```

### EasePack

Adds more named eases (e.g. SlowMo, RoughEase, ExpoScaleEase). Register and use the ease names in tweens.

### CustomWiggle

Wiggle/shake easing — multiple oscillations.

### CustomBounce

Bounce-style easing with configurable strength.

## Physics

### Physics2D (Physics2DPlugin)

2D physics with velocity, angle, and gravity:

```javascript
gsap.registerPlugin(Physics2DPlugin);

gsap.to(".ball", {
  duration: 2,
  physics2D: {
    velocity: 250,
    angle: 80,
    gravity: 500
  }
});
```

### PhysicsProps (PhysicsPropsPlugin)

Applies physics to property values:

```javascript
gsap.registerPlugin(PhysicsPropsPlugin);

gsap.to(".obj", {
  duration: 2,
  physicsProps: {
    x: { velocity: 100, end: 300 },
    y: { velocity: -50, acceleration: 200 }
  }
});
```

## Development

### GSDevTools

UI for scrubbing timelines, toggling animations, and debugging. Use during development only — do not ship to production.

```javascript
gsap.registerPlugin(GSDevTools);
GSDevTools.create({ animation: tl });
```

## Other

### Pixi (PixiPlugin)

Integrates GSAP with PixiJS for animating Pixi display objects.

```javascript
gsap.registerPlugin(PixiPlugin);

const sprite = new PIXI.Sprite(texture);
gsap.to(sprite, { pixi: { x: 200, y: 100, scale: 1.5 }, duration: 1 });
```

## Best Practices

- ✅ Register every plugin with **gsap.registerPlugin()** before first use.
- ✅ Use **Flip.getState()** → DOM change → **Flip.from()** for layout transitions.
- ✅ Use **Draggable** + **InertiaPlugin** for drag with momentum.
- ✅ Revert plugin instances (e.g. `split.revert()`) when components unmount or elements are removed.

## Do Not

- ❌ Use a plugin in a tween or API call without registering it first.
- ❌ Ship GSDevTools or development-only plugins to production.

See: https://gsap.com/docs/v3/Plugins/
