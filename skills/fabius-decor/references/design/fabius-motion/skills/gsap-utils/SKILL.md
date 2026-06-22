---
name: fabius-decor-gsap-utils
description: gsap.utils helpers — clamp, mapRange, normalize, interpolate, random, snap, toArray, wrap, pipe, distribute. Use when writing or reviewing code that uses any gsap.utils method.
---

# gsap.utils

## When to Use

Apply when code uses **gsap.utils** for math, value mapping, array handling, or unit parsing in animations (scroll-to-value mapping, randomizing, snapping to a grid, normalizing inputs). Pair with **gsap-core**, **gsap-timeline**, and **gsap-scrolltrigger** when building animations; easing utilities live in **gsap-plugins**.

## Overview

`gsap.utils` provides pure helpers — no registration required. Usable in tween vars, ScrollTrigger/Observer callbacks, or any JS driving GSAP. All methods are on `gsap.utils` (e.g. `gsap.utils.clamp()`).

**Function form.** Most utils accept the value as the **last** argument. Omit it and the util returns a reusable function — useful when the same config is applied many times (mousemove handler, tween callback). **Exception: `random()`** — pass `true` as the last arg for the reusable form; omitting the value does not work the same way.

```javascript
// Immediate: returns the result
gsap.utils.clamp(0, 100, 150); // 100

// Function form: returns a reusable function
const c = gsap.utils.clamp(0, 100);
c(150); // 100
c(-10); // 0
```

---

## Clamping and Ranges

### clamp(min, max, value?)

Constrains a value between min and max.

```javascript
gsap.utils.clamp(0, 100, 150); // 100
gsap.utils.clamp(0, 100, -10); // 0

const clampFn = gsap.utils.clamp(0, 100);
clampFn(150); // 100
```

### mapRange(inMin, inMax, outMin, outMax, value?)

Maps a value from one range to another. Use for converting scroll position or progress (0–1) to an animation value.

```javascript
gsap.utils.mapRange(0, 100, 0, 500, 50); // 250
gsap.utils.mapRange(0, 1, 0, 360, 0.5);  // 180

const mapFn = gsap.utils.mapRange(0, 100, 0, 500);
mapFn(50); // 250
```

### normalize(min, max, value?)

Returns a value normalized to 0–1 for the given range.

```javascript
gsap.utils.normalize(0, 100, 50);    // 0.5
gsap.utils.normalize(100, 300, 200); // 0.5

const normFn = gsap.utils.normalize(0, 100);
normFn(50); // 0.5
```

### interpolate(start, end, progress?)

Interpolates between two values at a given progress (0–1). Handles numbers, colors, and objects with matching keys.

```javascript
gsap.utils.interpolate(0, 100, 0.5);                              // 50
gsap.utils.interpolate("#ff0000", "#0000ff", 0.5);                // mid color
gsap.utils.interpolate({ x: 0, y: 0 }, { x: 100, y: 50 }, 0.5); // { x: 50, y: 25 }

const lerp = gsap.utils.interpolate(0, 100);
lerp(0.5); // 50
```

---

## Random and Snap

### random(minimum, maximum[, snapIncrement, returnFunction]) / random(array[, returnFunction])

Returns a random number in range, or a random element from an array. Optional `snapIncrement` snaps to the nearest multiple. Pass `true` as the last argument to get a reusable function.

```javascript
gsap.utils.random(-100, 100);       // e.g. 42.7
gsap.utils.random(0, 500, 5);       // 0–500, snapped to nearest 5

const randomFn = gsap.utils.random(-200, 500, 10, true);
randomFn(); // random, snapped to 10

gsap.utils.random(["red", "blue", "green"]); // one at random
const pick = gsap.utils.random([0, 100, 200], true);
pick(); // 0, 100, or 200
```

**String form in tween vars:** GSAP evaluates the string per target.

```javascript
gsap.to(".box",  { x: "random(-100, 100, 5)" });
gsap.to(".item", { backgroundColor: "random([red, blue, green])" });
```

### snap(snapTo, value?)

Snaps to the nearest multiple of `snapTo`, or to the nearest value in an array.

```javascript
gsap.utils.snap(10, 23);              // 20
gsap.utils.snap(0.25, 0.7);           // 0.75
gsap.utils.snap([0, 100, 200], 150);  // 100 or 200 (nearest)

const snapFn = gsap.utils.snap(10);
snapFn(23); // 20
```

In tweens for grid/step animation:

```javascript
gsap.to(".x", { x: 200, snap: { x: 20 } });
```

### shuffle(array)

Returns a new array with elements in random order.

```javascript
gsap.utils.shuffle([1, 2, 3, 4]); // e.g. [3, 1, 4, 2]
```

### distribute(config)

Returns a function that assigns a value to each target based on its position (flat or grid). Used for advanced staggers. The returned function signature is `(index, target, targets)` — pass it directly into a tween var or call manually.

| Property | Type | Description |
|----------|------|-------------|
| `base` | Number | Starting value. Default `0`. |
| `amount` | Number | Total to distribute across all targets (splits among N). |
| `each` | Number | Fixed step per target. Use `amount` to split a total instead. |
| `from` | Number \| String \| Array | Where distribution starts: index, `"start"`, `"center"`, `"edges"`, `"random"`, `"end"`, or ratios like `[0.25, 0.75]`. Default `0`. |
| `grid` | String \| Array | `[rows, columns]` or `"auto"` to use grid position instead of flat index. |
| `axis` | String | For grid: limit to `"x"` or `"y"`. |
| `ease` | Ease | Distribute values along an ease curve. Default `"none"`. |

```javascript
// Middle elements 0.5, outer edges 3 (amount 2.5 from center)
gsap.to(".class", {
  scale: gsap.utils.distribute({ base: 0.5, amount: 2.5, from: "center" })
});
```

Manual use:

```javascript
const distributor = gsap.utils.distribute({ base: 50, amount: 100, from: "center", ease: "power1.inOut" });
const targets = gsap.utils.toArray(".box");
const val = distributor(2, targets[2], targets);
```

See [distribute()](https://gsap.com/docs/v3/GSAP/UtilityMethods/distribute/).

---

## Units and Parsing

### getUnit(value)

Returns the unit string (`"px"`, `"%"`, `"deg"`, etc.) or `""` for unitless.

```javascript
gsap.utils.getUnit("100px"); // "px"
gsap.utils.getUnit("50%");   // "%"
gsap.utils.getUnit(42);      // ""
```

### unitize(value, unit)

Appends a unit to a number; returns the value unchanged if it already has a unit.

```javascript
gsap.utils.unitize(100, "px");    // "100px"
gsap.utils.unitize("2rem", "px"); // "2rem"
```

### splitColor(color, returnHSL?)

Converts a color string to `[r, g, b]` (0–255), or `[r, g, b, a]` when alpha is present. Pass `true` for `[h, s, l]` (HSL). Works with `rgb()`, `rgba()`, `hsl()`, `hsla()`, hex, and named colors. See [splitColor()](https://gsap.com/docs/v3/GSAP/UtilityMethods/splitColor/).

```javascript
gsap.utils.splitColor("red");                     // [255, 0, 0]
gsap.utils.splitColor("#6fb936");                 // [111, 185, 54]
gsap.utils.splitColor("rgba(204, 153, 51, 0.5)"); // [204, 153, 51, 0.5]
gsap.utils.splitColor("#6fb936", true);           // [94, 55, 47] (HSL)
```

---

## Arrays and Collections

### selector(scope)

Returns a scoped selector function that finds elements only within the given element or ref. Prevents selector leaks across component boundaries.

```javascript
const q = gsap.utils.selector(containerRef);
q(".box"); // .box elements inside container only
gsap.to(q(".circle"), { x: 100 });
```

### toArray(value, scope?)

Converts selector string, NodeList, HTMLCollection, or single element to a plain array.

```javascript
gsap.utils.toArray(".item");            // array of elements
gsap.utils.toArray(".item", container); // scoped to container
gsap.utils.toArray(nodeList);           // from NodeList
```

### pipe(...functions)

Composes functions left-to-right: `pipe(f1, f2, f3)(value)` → `f3(f2(f1(value)))`.

```javascript
const fn = gsap.utils.pipe(
  (v) => gsap.utils.normalize(0, 100, v),
  (v) => gsap.utils.snap(0.1, v)
);
fn(50); // normalized then snapped
```

### wrap(min, max, value?)

Wraps a value into the range `[min, max)`. Use for infinite scroll or cyclic values.

```javascript
gsap.utils.wrap(0, 360, 370); // 10
gsap.utils.wrap(0, 360, -10); // 350

const wrapFn = gsap.utils.wrap(0, 360);
wrapFn(370); // 10
```

### wrapYoyo(min, max, value?)

Wraps with a yoyo (bounces at ends). Use for back-and-forth within a range.

```javascript
gsap.utils.wrapYoyo(0, 100, 150); // 50

const wrapY = gsap.utils.wrapYoyo(0, 100);
wrapY(150); // 50
```

---

## Best Practices

- Use the function form (`let mapFn = gsap.utils.mapRange(0, 1, 0, 360)`) when the same config applies many times — avoids recreating on every call.
- Use `snap` for grid-aligned or step-based values; `toArray` when a real array is required from a selector or NodeList.
- Use `gsap.utils.selector(scope)` in components to scope selectors to a container or ref.

## Avoid

- Passing units to `mapRange` / `normalize` — they operate on numbers only. Strip units first with `getUnit` / `unitize`.
- Relying on undocumented behavior; stick to the documented API.

## Reference

https://gsap.com/docs/v3/HelperFunctions
