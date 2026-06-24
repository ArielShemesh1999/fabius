# Fabius Ludus — engine recipes, feel patterns & the pixel-art kit

The deep, bundled library for `fabius-ludus`, indexed by [CORPUS.md](../../../CORPUS.md) and paged one slice at a time (routing-policy R9 · M9). Web/canvas-leaning, engine-agnostic in principle. Code is **illustrative pseudo-JS** — short skeletons to copy and adapt, not a full engine. The operating rules and the loop-first stance are in [game-playbook.md](game-playbook.md); don't restate them here, page the matching recipe and strike narrow. **Reach for the engine before any of this** (`fabius-parcus`) — these are the lean floor for when you're on raw canvas with nothing under you.

---

## 1. The game loop — fixed-timestep update, interpolated render

Decouple simulation from rendering so physics is deterministic regardless of frame rate, and rendering stays smooth. Fixed `dt` for `update`, accumulator drains it, `render` interpolates the leftover.

```js
const STEP = 1000 / 60;          // sim tick = 16.67ms, fixed
let acc = 0, prev = performance.now();

function frame(now) {
  acc += Math.min(now - prev, 250);   // clamp: never spiral after a tab-stall
  prev = now;
  while (acc >= STEP) { update(STEP / 1000); acc -= STEP; }  // 0+ sim steps
  render(acc / STEP);                                        // alpha 0..1, interpolate
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
```

- `update(dt)` runs at a fixed rate — collisions, motion, spawns. Deterministic.
- `render(alpha)` lerps between the previous and current sim state: `x = prevX + (x - prevX) * alpha`. Kills judder.
- **Clamp the accumulator** (the `Math.min(..., 250)`): after a tab-switch or breakpoint, don't run 500 catch-up steps — drop time instead (the "spiral of death" guard).
- One `requestAnimationFrame` loop owns everything; never two competing rAFs.

## 2. Input — buffered, edge-vs-held, remappable

Read input into a state object once per frame; never read the DOM mid-update. Distinguish **held** (down this frame) from **edge** (pressed *this* frame, not last).

```js
const down = new Set(), pressed = new Set(), MAP = { jump: ['Space','KeyW'], left: ['KeyA'] };
addEventListener('keydown', e => { if (!down.has(e.code)) pressed.add(e.code); down.add(e.code); });
addEventListener('keyup',   e => down.delete(e.code));

const held = a => MAP[a].some(k => down.has(k));      // is the action held?
const hit  = a => MAP[a].some(k => pressed.has(k));   // pressed THIS frame (edge)
function endFrame() { pressed.clear(); }              // call AFTER update; clears edges
```

- **Edge vs held** is the bug source: jump on `hit('jump')` (one jump per press), move on `held('left')` (continuous).
- **Input buffer** — forgive timing: stamp a press and let `update` consume it within a window, so a jump pressed 80ms early still fires on landing.
  ```js
  let jumpBuf = 0;
  if (hit('jump')) jumpBuf = 120;                 // ms of grace
  jumpBuf -= dt * 1000;
  if (jumpBuf > 0 && onGround) { jump(); jumpBuf = 0; }
  ```
- **Coyote time** — the mirror of buffering: allow a jump for ~80ms *after* leaving a ledge. Both make controls feel fair.
- **Remapping** is just editing `MAP`; persist it. Touch/gamepad: feed the same `down`/`pressed` sets, so the action layer never changes.

## 3. Audio — one-shot SFX pool, simple ducking

Pre-make a pool of clones per sound so rapid fire doesn't cut itself off, and so you never allocate during play.

```js
function sfxPool(src, size = 6) {
  const pool = Array.from({ length: size }, () => new Audio(src));
  let i = 0;
  return (vol = 1, rate = 1) => {
    const a = pool[i = (i + 1) % size];
    a.currentTime = 0; a.volume = vol; a.playbackRate = rate; a.play();
  };
}
const coin = sfxPool('coin.wav');
// vary pitch so repeats don't fatigue: coin(1, 0.97 + Math.random() * 0.06)
```

- **Pool, don't re-`new`** mid-loop; cap the pool; round-robin so overlapping plays coexist.
- **Pitch-vary repeats** (`playbackRate`) — identical SFX 5×/sec is grating; ±3% randomization reads as natural.
- **Ducking** — when a loud event fires (death, boss hit), briefly drop the music bus, then ramp back. With WebAudio: `music.gain.linearRampToValueAtTime(0.3, t+0.05)` then ramp to `1.0` over ~400ms. Without WebAudio: lerp `music.volume` down a frame, back up over ~0.4s.
- **Unlock on first gesture** — browsers block autoplay; `resume()` the AudioContext (or play a silent buffer) on the first click/keypress.

## 4. Render — pixel-perfect canvas, integer scaling, camera, layers

The setup that keeps pixels crisp:

```js
const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');
const W = 320, H = 180;                         // logical resolution (small!)
canvas.width = W; canvas.height = H;            // internal buffer = logical size
function fit() {                                // CSS-scale by an INTEGER factor only
  const s = Math.max(1, Math.floor(Math.min(innerWidth / W, innerHeight / H)));
  canvas.style.width = W * s + 'px';
  canvas.style.height = H * s + 'px';
  canvas.style.imageRendering = 'pixelated';    // no smoothing on upscale
}
addEventListener('resize', fit); fit();
ctx.imageSmoothingEnabled = false;              // crisp source draws
```

- **Render small, scale big with `Math.floor`** — fractional scale shimmers; integer scale stays sharp. Letterbox the remainder.
- **Snap world coords to whole pixels at draw time**: `ctx.drawImage(spr, Math.round(x - cam.x), Math.round(y - cam.y))`. Sub-pixel positions blur.
- **Camera** — translate everything by the camera, with dead-zone follow so it doesn't jitter on every step:
  ```js
  const cam = { x: 0, y: 0 };
  function follow(t) {                           // lerp toward target, dead-zone optional
    cam.x += (t.x - W / 2 - cam.x) * 0.1;
    cam.x = Math.max(0, Math.min(cam.x, levelW - W));   // clamp to level bounds
  }
  ```
- **Layers** — draw back-to-front in passes: `bg → parallax → world → entities → particles → HUD`. Parallax = draw a layer at `cam.x * factor` (factor < 1 = farther). HUD is drawn *without* the camera translate.

## 5. Collision — AABB, with a spatial-hash note

Axis-aligned bounding boxes cover most 2D games. Overlap test and a minimal-translation resolve:

```js
const hit = (a, b) =>
  a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;

function resolve(a, b) {                         // push `a` out of `b` along the shallow axis
  const dx = (a.x + a.w / 2) - (b.x + b.w / 2);
  const dy = (a.y + a.h / 2) - (b.y + b.h / 2);
  const ox = (a.w + b.w) / 2 - Math.abs(dx);     // x overlap
  const oy = (a.h + b.h) / 2 - Math.abs(dy);     // y overlap
  if (ox < oy) { a.x += dx < 0 ? -ox : ox; a.vx = 0; }
  else         { a.y += dy < 0 ? -oy : oy; a.vy = 0; if (dy < 0) a.onGround = true; }
}
```

- **Resolve on the shallow axis** so a moving body slides along a wall instead of snapping through it.
- **Swept/continuous** only when something is fast enough to tunnel (a bullet through a thin wall): test the ray of motion, not just the end position. Most games don't need it — add it when tunneling actually appears (`fabius-parcus`).
- **Spatial hash** (note, not a build): naive collision is O(n²). At a few hundred entities, bucket them into a grid keyed by `(x>>cell, y>>cell)` and only test pairs sharing a cell. Build the index when the n² cost shows up in the profiler, not before.

## 6. Juice patterns — with implementation

The feel checklist in [game-playbook.md](game-playbook.md) says *what* to do; here's *how*. Spend the loud ones on rare events (`fabius-decor` owns the restraint law).

**Hit-stop** — freeze a few frames on impact; the brain reads the pause as weight.
```js
let freeze = 0;                                  // frames remaining
function impact(frames) { freeze = frames; }     // 2–4 light, 5–8 heavy
function update(dt) { if (freeze > 0) { freeze--; return; } /* ...normal sim... */ }
```

**Screen-shake via trauma + decay** — additive `trauma`, squared for a snappy falloff, decays every frame. Beats a fixed-magnitude shake (smooth ramp-down, stacks naturally).
```js
let trauma = 0;
const kick = a => trauma = Math.min(1, trauma + a);   // 0.3 small, 0.7 big
function shake(ctx, dt) {
  trauma = Math.max(0, trauma - dt * 1.5);            // decay ~1.5/s
  const s = trauma * trauma * 8;                      // squared = punchy
  ctx.translate((Math.random() * 2 - 1) * s, (Math.random() * 2 - 1) * s);
}
```

**Easing / tween** — never move linearly; ease and overshoot.
```js
const easeOutCubic  = t => 1 - Math.pow(1 - t, 3);
const easeInOutQuad = t => t < .5 ? 2*t*t : 1 - Math.pow(-2*t+2, 2)/2;
const easeOutBack   = t => { const c = 1.70158; return 1 + (c+1)*Math.pow(t-1,3) + c*Math.pow(t-1,2); }; // overshoot
const lerp = (a, b, t) => a + (b - a) * t;
function tween(obj, key, to, ms, ease = easeOutCubic) {
  const from = obj[key], t0 = performance.now();
  (function step(now) {
    const t = Math.min(1, (now - t0) / ms);
    obj[key] = lerp(from, to, ease(t));
    if (t < 1) requestAnimationFrame(step);
  })(t0);
}
```

**Particle pool** — pre-allocate, recycle; never `new` per spawn.
```js
const P = Array.from({ length: 200 }, () => ({ life: 0 }));
function burst(x, y, n = 12, color = '#fff') {
  for (let k = 0, c = 0; k < P.length && c < n; k++) if (P[k].life <= 0) {
    const a = Math.random() * Math.PI * 2, sp = 30 + Math.random() * 60;
    Object.assign(P[k], { x, y, vx: Math.cos(a)*sp, vy: Math.sin(a)*sp, life: .4, color });
    c++;
  }
}
function stepParticles(dt) { for (const p of P) if (p.life > 0) {
  p.x += p.vx*dt; p.y += p.vy*dt; p.vy += 120*dt; p.life -= dt;   // gravity + fade
}}
```

**Number-pop** — a floating, rising, fading number on reward; the single highest-ROI piece of juice.
```js
const pops = [];
const pop = (x, y, text) => pops.push({ x, y, text, life: .8, vy: -40 });
function drawPops(ctx, dt) { for (let i = pops.length - 1; i >= 0; i--) {
  const p = pops[i]; p.y += p.vy * dt; p.life -= dt;
  ctx.globalAlpha = Math.max(0, p.life / .8);
  ctx.fillText(p.text, Math.round(p.x), Math.round(p.y));
  ctx.globalAlpha = 1;
  if (p.life <= 0) pops.splice(i, 1);
}}
```

Wire them together on the moment that matters — e.g. enemy death: `impact(6); kick(0.6); burst(x, y); pop(x, y, '+10'); coin()`.

## 7. The pixel-art kit — palette, scale, sprite-sheets

**Palette discipline** — define the whole palette once, index by name, never hand-type a hex mid-draw. One identity, no drift (a project's brand — e.g. a green palette + a red mascot — is *an example of* locking a lane, not a rule).
```js
const PAL = { ink:'#1a1c2c', mid:'#5d275d', accent:'#ef7d57', mascot:'#e43b44', paper:'#f4f4f4' };
// 16–32 colors total for a cohesive look; pick a named ramp (e.g. a 16-color set) and stay in it.
```

**Integer-scale setup** — covered in §4: logical buffer of e.g. `320×180`, CSS-upscaled by `Math.floor` only, `imageRendering: pixelated`, `imageSmoothingEnabled = false`. This is the *whole* secret to crisp pixels.

**Sprite-sheet conventions** — one sheet, fixed cell, index by frame:
```
- one base UNIT (e.g. 16×16); every sprite is a multiple of it — the grid is the rhythm.
- pack frames left-to-right, rows = animations (row 0 idle, row 1 run, row 2 hit).
- blit by index:
    const U = 16;
    drawImage(sheet, (frame % cols)*U, row*U, U, U,  Math.round(x), Math.round(y), U, U);
- animate by stepping `frame` on a timer: frame = (t / frameMs | 0) % frameCount.
- keep a 1px transparent gutter only if you see bleeding at non-integer scale; with integer
  scale + smoothing off you usually don't need it.
```

**Crispness checklist** (the look *is* the discipline):
```
[ ] logical resolution small (e.g. 320×180 or smaller)
[ ] CSS scale is an integer (Math.floor), letterbox the remainder
[ ] imageSmoothingEnabled = false; imageRendering: pixelated
[ ] draw positions Math.round()'d to whole device-pixels
[ ] one locked palette, one base unit size
[ ] camera clamped + dead-zone so the world doesn't jitter
```

Boundary reminder: animation *laws* and UI tokens are `fabius-decor`; lean-code/use-the-engine is `fabius-parcus`; plan + prove the build is `fabius-disciplina`. This library is the loop's engine and feel only.
