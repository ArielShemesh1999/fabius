---
name: fabius-decor-gsap-utils-gsap-utils
description: gsap.utils — clamp, mapRange, normalize, interpolate, random, snap, toArray, wrap, pipe, distribute, selector. Use when mapping values, randomizing, snapping, scoping selectors, or building animation helpers.
triggers:
  - "gsap utils"
  - "clamp animation value"
  - "maprange"
  - "snap animation"
  - "gsap random"
license: MIT
---

# gsap.utils

## When to Use This Skill

Apply when writing or reviewing code that uses **gsap.utils** for math, array/collection handling, unit parsing, or value mapping in animations (e.g. mapping scroll to a value, randomizing, snapping to a grid, or normalizing inputs).

**Related skills:** Use with **gsap-core**, **gsap-timeline**, and **gsap-scrolltrigger**; easing utilities are in **gsap-plugins**.

## Overview

**gsap.utils** provides pure helpers — no registration needed. Use in tween vars (function-based values), in ScrollTrigger/Observer callbacks, or in any JS that drives GSAP. All are on `gsap.utils` (e.g. `gsap.utils.clamp()`).

**Function form:** Most utils accept the value to transform as the **last** argument. Omit it and the util returns a **reusable function**. Use the function form when the same config is applied many times (e.g. in a scroll handler or tween callback).

**Exception:** `random()` — pass **true** as the last argument to get a reusable function; do not omit the value.

```javascript
// With value: returns the result immediately
gsap.utils.clamp(0, 100, 150); // 100

// Without value: returns a reusable function
let c = gsap.utils.clamp(0, 100);
c(150);  // 100
c(-10);  // 0
```

## Clamping and Ranges

### clamp(min, max, value?)

Constrains a value between min and max.

```javascript
gsap.utils.clamp(0, 100, 150); // 100
gsap.utils.clamp(0, 100, -10); // 0

let clampFn = gsap.utils.clamp(0, 100);
clampFn(150); // 100
```

### mapRange(inMin, inMax, outMin, outMax, value?)

Maps a value from one range to another. Use for converting scroll position, progress (0–1), or input range to an animation range.

```javascript
gsap.utils.mapRange(0, 100, 0, 500, 50);  // 250
gsap.utils.mapRange(0, 1, 0, 360, 0.5);   // 180

let mapFn = gsap.utils.mapRange(0, 100, 0, 500);
mapFn(50);  // 250
```

### normalize(min, max, value?)

Returns a value normalized to 0–1 for the given range.

```javascript
gsap.utils.normalize(0, 100, 50);    // 0.5
gsap.utils.normalize(100, 300, 200); // 0.5

let normFn = gsap.utils.normalize(0, 100);
normFn(50); // 0.5
```

### interpolate(start, end, progress?)

Interpolates between two values at a given progress (0–1). Handles numbers, colors, and objects with matching keys.

```javascript
gsap.utils.interpolate(0, 100, 0.5);                                    // 50
gsap.utils.interpolate("#ff0000", "#0000ff", 0.5);                       // mid color
gsap.utils.interpolate({ x: 0, y: 0 }, { x: 100, y: 50 }, 0.5);        // { x: 50, y: 25 }

let lerp = gsap.utils.interpolate(0, 100);
lerp(0.5); // 50
```

## Random and Snap

### random(minimum, maximum[, snapIncrement, returnFunction]) / random(array[, returnFunction])

Returns a random number in range or a random element from an array. Pass **true** as the last argument to get a reusable function.

```javascript
gsap.utils.random(-100, 100);         // e.g. 42.7
gsap.utils.random(0, 500, 5);         // 0–500, snapped to nearest 5

let randomFn = gsap.utils.random(-200, 500, 10, true);
randomFn();  // random value, snapped to nearest 10

gsap.utils.random(["red", "blue", "green"]);  // one at random
let randomFromArray = gsap.utils.random([0, 100, 200], true);
randomFromArray();  // 0, 100, or 200
```

**String form in tween vars** — GSAP evaluates per target:

```javascript
gsap.to(".box", { x: "random(-100, 100, 5)", duration: 1 });
gsap.to(".item", { backgroundColor: "random([red, blue, green])" });
```

### snap(snapTo, value?)

Snaps a value to the nearest multiple of **snapTo**, or to the nearest value in an array.

```javascript
gsap.utils.snap(10, 23);             // 20
gsap.utils.snap(0.25, 0.7);          // 0.75
gsap.utils.snap([0, 100, 200], 150); // 100 or 200 (nearest)

let snapFn = gsap.utils.snap(10);
snapFn(23); // 20
```

In tweens for grid/step-based animation:

```javascript
gsap.to(".x", { x: 200, snap: { x: 20 } });
```

### shuffle(array)

Returns a new array with the same elements in random order.

```javascript
gsap.utils.shuffle([1, 2, 3, 4]); // e.g. [3, 1, 4, 2]
```

### distribute(config)

Returns a function that assigns a value to each target based on its position in an array or grid. Used for advanced staggers and spreading values across elements.

The returned function receives `(index, target, targets)` — pass it directly as a tween property value; GSAP calls it per target.

**Config (all optional):**

| Property | Type | Description |
|----------|------|-------------|
| `base` | Number | Starting value. Default `0`. |
| `amount` | Number | Total to distribute across all targets (added to base). |
| `each` | Number | Fixed step per target (added to base). Use `amount` to split a total instead. |
| `from` | Number \| String \| Array | Where distribution starts: index, `"start"`, `"center"`, `"edges"`, `"random"`, `"end"`, or ratios like `[0.25, 0.75]`. Default `0`. |
| `grid` | String \| Array | `[rows, columns]` or `"auto"` to detect. Omit for flat array. |
| `axis` | String | For grid: limit to one axis (`"x"` or `"y"`). |
| `ease` | Ease | Distribute values along an ease curve. Default `"none"`. |

```javascript
// Scale: middle elements 0.5, outer edges 3
gsap.to(".class", {
  scale: gsap.utils.distribute({
    base: 0.5,
    amount: 2.5,
    from: "center"
  })
});
```

Manual use:

```javascript
const distributor = gsap.utils.distribute({ base: 50, amount: 100, from: "center", ease: "power1.inOut" });
const targets = gsap.utils.toArray(".box");
const valueForIndex2 = distributor(2, targets[2], targets);
```

See: https://gsap.com/docs/v3/GSAP/UtilityMethods/distribute/

## Units and Parsing

### getUnit(value)

Returns the unit string of a value (`"px"`, `"%"`, `"deg"`, etc.).

```javascript
gsap.utils.getUnit("100px");  // "px"
gsap.utils.getUnit("50%");    // "%"
gsap.utils.getUnit(42);       // "" (unitless)
```

### unitize(value, unit)

Appends a unit to a number, or returns the value unchanged if it already has a unit.

```javascript
gsap.utils.unitize(100, "px");      // "100px"
gsap.utils.unitize("2rem", "px");   // "2rem" (unchanged)
```

### splitColor(color, returnHSL?)

Converts a color string into `[red, green, blue]` (0–255), or `[red, green, blue, alpha]` for RGBA. Pass `true` as the second argument for HSL/HSLA.

```javascript
gsap.utils.splitColor("red");                       // [255, 0, 0]
gsap.utils.splitColor("#6fb936");                   // [111, 185, 54]
gsap.utils.splitColor("rgba(204, 153, 51, 0.5)");  // [204, 153, 51, 0.5]
gsap.utils.splitColor("#6fb936", true);             // [94, 55, 47] (HSL)
```

See: https://gsap.com/docs/v3/GSAP/UtilityMethods/splitColor/

## Arrays and Collections

### selector(scope)

Returns a scoped selector function that finds elements only within the given element or ref. Use in components to avoid matching outside the component.

```javascript
const q = gsap.utils.selector(containerRef);
q(".box");  // only .box elements inside container
gsap.to(q(".circle"), { x: 100 });
```

### toArray(value, scope?)

Converts selector strings, NodeLists, HTMLCollections, or single elements to a true array.

```javascript
gsap.utils.toArray(".item");           // array of elements
gsap.utils.toArray(".item", container); // scoped to container
gsap.utils.toArray(nodeList);          // array from NodeList
```

### pipe(...functions)

Composes functions left-to-right: `pipe(f1, f2, f3)(value)` returns `f3(f2(f1(value)))`.

```javascript
const fn = gsap.utils.pipe(
  (v) => gsap.utils.normalize(0, 100, v),
  (v) => gsap.utils.snap(0.1, v)
);
fn(50); // normalized then snapped
```

### wrap(min, max, value?)

Wraps a value into the range min–max (inclusive min, exclusive max). Use for cyclic/infinite values.

```javascript
gsap.utils.wrap(0, 360, 370);  // 10
gsap.utils.wrap(0, 360, -10);  // 350

let wrapFn = gsap.utils.wrap(0, 360);
wrapFn(370); // 10
```

### wrapYoyo(min, max, value?)

Wraps value in range with a yoyo (bounces at ends).

```javascript
gsap.utils.wrapYoyo(0, 100, 150); // 50

let wrapY = gsap.utils.wrapYoyo(0, 100);
wrapY(150); // 50
```

## Best Practices

- ✅ Omit the value argument to get a reusable function when the same range/config is applied many times.
- ✅ Use **snap** for grid-aligned or step-based values; use **toArray** when a real array is needed from a selector or NodeList.
- ✅ Use **gsap.utils.selector(scope)** in components so selectors are scoped to a container.

## Do Not

- ❌ Assume **mapRange** / **normalize** handle units; they work on numbers. Use **getUnit** / **unitize** when units matter.
- ❌ Rely on undocumented behavior; stick to the documented API.

See: https://gsap.com/docs/v3/HelperFunctions
