---
name: fabius-decor-gsap-timeline-gsap-timeline
description: GSAP timelines — gsap.timeline(), position parameter, labels, nesting, defaults, and playback control. Use when sequencing animations or choreographing multi-step motion.
triggers:
  - "gsap timeline"
  - "animation timeline"
  - "sequenced animation"
  - "motion choreography"
license: MIT
---

# GSAP Timeline

## When to Use This Skill

Apply when building multi-step animations, coordinating several tweens in sequence or parallel, or when the user asks about timelines, sequencing, or keyframe-style animation in GSAP.

**Related skills:** For single tweens and eases use **gsap-core**; for scroll-driven timelines use **gsap-scrolltrigger**; for React use **gsap-react**.

## Creating a Timeline

```javascript
const tl = gsap.timeline();
tl.to(".a", { x: 100, duration: 1 })
  .to(".b", { y: 50, duration: 0.5 })
  .to(".c", { opacity: 0, duration: 0.3 });
```

By default, tweens are appended one after another. Use the **position parameter** to place tweens at specific times or relative to other tweens.

## Position Parameter

Third argument (or `position` in vars) controls placement:

- **Absolute**: `1` — start at 1 second.
- **Relative**: `"+=0.5"` — 0.5s after end; `"-=0.2"` — 0.2s before end.
- **Label**: `"labelName"` — at that label; `"labelName+=0.3"` — 0.3s after label.
- **Anchored**: `"<"` — same start as recently-added animation; `">"` — after recently-added animation ends (default); `"<0.2"` — 0.2s after recently-added animation start.

```javascript
tl.to(".a", { x: 100 }, 0);           // at 0
tl.to(".b", { y: 50 }, "+=0.5");      // 0.5s after last end
tl.to(".c", { opacity: 0 }, "<");     // same start as previous
tl.to(".d", { scale: 2 }, "<0.2");    // 0.2s after previous start
```

## Timeline Defaults

Pass defaults into the timeline so all child tweens inherit:

```javascript
const tl = gsap.timeline({ defaults: { duration: 0.5, ease: "power2.out" } });
tl.to(".a", { x: 100 }).to(".b", { y: 50 }); // both use 0.5s and power2.out
```

## Timeline Options (constructor)

- **paused: true** — create paused; call `.play()` to start.
- **repeat**, **yoyo** — same as tweens; apply to the whole timeline.
- **onComplete**, **onStart**, **onUpdate** — timeline-level callbacks.
- **defaults** — vars merged into every child tween.

## Labels

```javascript
tl.addLabel("intro", 0);
tl.to(".a", { x: 100 }, "intro");
tl.addLabel("outro", "+=0.5");
tl.to(".b", { opacity: 0 }, "outro");
tl.play("outro");                      // start from "outro"
tl.tweenFromTo("intro", "outro");      // animate playhead from intro to outro
```

## Nesting Timelines

```javascript
const master = gsap.timeline();
const child = gsap.timeline();
child.to(".a", { x: 100 }).to(".b", { y: 50 });
master.add(child, 0);
master.to(".c", { opacity: 0 }, "+=0.2");
```

## Controlling Playback

- **tl.play()** / **tl.pause()**
- **tl.reverse()**
- **tl.restart()** — from start.
- **tl.time(2)** — seek to 2 seconds.
- **tl.progress(0.5)** — seek to 50%.
- **tl.kill()** — kill timeline and (by default) its children.

## Best Practices

- ✅ Prefer timelines for sequencing; use the **position parameter** instead of chaining delays.
- ✅ Add **labels** with `addLabel()` for readable, maintainable sequencing.
- ✅ Pass **defaults** in the timeline constructor so child tweens inherit duration, ease, etc.
- ✅ Put ScrollTrigger on the timeline (or top-level tween), not on tweens inside a timeline.

## Do Not

- ❌ Chain animations with **delay** when a **timeline** can sequence them.
- ❌ Skip **defaults** when many child tweens share the same duration or ease.
- ❌ Confuse `duration` in the timeline constructor with tween duration; timeline duration is determined by its children.
- ❌ Nest animations that contain a ScrollTrigger; ScrollTriggers belong only on top-level tweens/timelines.
