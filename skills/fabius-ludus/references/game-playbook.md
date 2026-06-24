# Fabius Ludus — the loop is the game; everything else is paint

The on-demand depth for `fabius-ludus`. This file is the full playbook: the core-loop template (worked), the budgeted juice checklist, the FSM skeleton, the pixel-art constants, the difficulty method, the jam-scoping test, and the studio dispatch order. The DEEP library — engine recipes, feel patterns with implementation, the pixel-art kit — lives in the companion [engine-recipes.md](engine-recipes.md), indexed by [CORPUS.md](../../../CORPUS.md) and paged one slice at a time (routing-policy R9 · M9). **Scout wide on what the game could be, strike narrow on the one loop that's fun with grey boxes.**

---

## 1. Core-loop template

Fill this before any art, menu, or content exists. A game is the ~10-second cycle **act → feedback → reward → again** — build only that, with grey boxes and placeholder sound, and answer one question: is it fun yet?

```
Verb (what the player does):        ________
Feedback (the instant response):    ________   (sound + visual, every time)
Reward (why they do it again):      ________
Failure (the cost / the stakes):    ________
Loop length:                        ~__ seconds
Fun unpainted? (grey-box test):     yes / not yet → fix the LOOP, not the art
```

If "not yet" — the fix is a loop change, never more content. A beautiful game on a dead loop is a dead game (`fabius-parcus`: the content doesn't need to exist until the loop holds).

**Worked example** — a one-button dodge-and-grab:

```
Verb:        tap to flip gravity; ride the floor/ceiling, scoop coins
Feedback:    snap-flip with a 60ms ease, a "tick" SFX, coin pops + chime
Reward:      coin count ticks up; a near-miss with a spike pulses the score
Failure:     touch a spike → hit-stop, shake, run ends; score is the stake
Loop length: ~3 seconds (flip, thread a gap, grab, repeat)
Fun unpainted? yes — flipping through grey rectangles already reads as tense
```

The verb is the whole game. Everything below is in service of making *that one verb* feel good.

## 2. Juice checklist — budget the most to the core verb

Juice is feedback on every action, deliberately spent, not sprinkled. Budget the biggest feedback to the verb the player does most; the rare events get the loud effects. Tick each, with the number you chose:

```
[ ] input → instant sound + visual           (nothing the player does is silent)
[ ] hit-stop on impact: ____ frames           (2–4 light, 5–8 heavy; sells weight)
[ ] screen-shake: trauma ____ , big events    (OFF by default; constant shake = noise)
[ ] easing on motion (no linear)              (anticipation before, follow-through after)
[ ] reward burst: particles / number-pop / flash
[ ] the most-used verb carries the most feedback budget
[ ] audio: every one-shot has a sound; layer/duck on density
```

Spend asymmetrically: the once-a-run *death* can shake hard and freeze long; the once-a-second *grab* gets a tight pop and a tick — a heavy effect on a frequent verb fatigues fast. Animation *laws* (restraint, transform/opacity only) are `fabius-decor`; the game-feel *specifics* are here. One micro-language, calm baseline, punch on the moments that matter. Implementation (trauma curve, hit-stop, easing functions, particle pool) → [engine-recipes.md](engine-recipes.md).

## 3. State-machine skeleton

No boolean soup. Model game state as a named finite-state machine; each state owns its own update/render/input, and transitions are named events — not scattered flags.

```
states:  boot · menu · play · pause · win · lose
transitions:
  boot  --loaded-->   menu
  menu  --start-->    play
  play  --pause-->    pause      pause --resume--> play
  play  --died-->     lose       lose  --retry-->  play
  play  --goal-->     win        win   --next-->   menu
rule: each state owns update(dt) / render() / input(ev); no cross-state flags.
```

The rule that keeps it clean — **each state owns its three methods**:

```
state Play {
  update(dt) { /* sim, collisions, spawn */ }
  render()   { /* world + HUD */ }
  input(ev)  { if (ev == ESC) machine.go('pause') }   // transitions are named
}
```

No `isPlaying && !isPaused && !isDead` tangles (`fabius-parcus`); a diagram you can hold in your head (`fabius-disciplina`). The transition table *is* the spec — if a transition isn't on the table, it can't happen. Full machine skeleton in [engine-recipes.md](engine-recipes.md).

## 4. Pixel-art constants

For a pixel game the discipline *is* the look. Lock these and don't drift:

```
palette:        ONE fixed set, no drift across the game
                (this project's brand example: green palette + red mascot — one identity)
scale:          integer only (2× / 3× / 4×), never fractional (fractional shimmers)
grid:           snap positions to whole device-pixels (sub-pixel motion blurs the crispness)
unit:           one base tile/sprite size = the rhythm of the whole layout
text direction: RTL/Hebrew keeps left-arrow = back/next — DON'T flip it
```

The brand line and the RTL line are *examples of holding a lane*, not hard rules — a different project locks its own palette and its own reading direction. The discipline (lock one palette, integer-scale, snap to grid, one unit) is the rule. Canvas setup, integer scaling, sprite-sheet conventions → the pixel-art kit in [engine-recipes.md](engine-recipes.md).

## 5. Difficulty — teach → test → twist, one knob at a time

Shape the curve in three beats per mechanic:

| Beat | What it does | Example (the flip game) |
|---|---|---|
| **Teach** | introduce the mechanic in a safe room — no failure possible | wide gaps, no spikes; player learns the flip |
| **Test** | demand the mechanic — failure now costs | tighter gaps, first spikes; flip on time or die |
| **Twist** | complicate it — combine, invert, or speed it | moving spikes + coins that pull you off-line |

**Tune one knob per playtest.** Changing three variables at once means you learn nothing from the result.

```
how to tune ONE knob:
  1. pick the variable (e.g. scroll speed)
  2. playtest 3–5 runs at the current value; note where it breaks
  3. change ONLY that value; playtest again
  4. lock it; write the locked value down
  5. move to the next knob
the fun is in the climb, not the wall — if players quit, the curve spiked.
```

## 6. Jam-scoping rule — the cut/keep test

Pick the **smallest shippable game that proves the loop**. One mechanic done well beats five half-done. Run every proposed feature through the test:

```
KEEP if:  it makes the CORE LOOP more fun, or the slice can't ship without it.
CUT  if:  it's content/meta/polish the loop doesn't need to prove itself,
          or it answers "wouldn't it be cool if…" instead of "the loop needs…".
when unsure → CUT. Ship the slice, then decide what's worth adding.
```

Worked: for the flip game — **keep** the flip, spikes, coins, one death state, a score (that's the loop + its stake). **Cut** the shop, the second character, the level select, the save system, the leaderboard — none of them prove the loop is fun. They're post-slice questions (`fabius-parcus`: does it earn its build cost yet?).

## 7. The studio pipeline — ludus leads

A game is a *vertical*: it composes several layers behind one goal. **`fabius-ludus` leads**; the router composes the rest in this dispatch order (routing-policy R13) — you don't pick one layer:

```
fabius-ludus       → the loop + the feel            (THIS layer leads)
  → fabius-disciplina  → plan the build as step → verify; prove it runs
  → fabius-decor       → menus, HUD, framing UI (tokens, states, animation laws)
  → fabius-cohors      → ONLY if NPCs/enemies need real agent behavior
  → fabius-parcus      → underneath all of it (lean code; reach for the engine)
```

`fabius-parcus` is always-on beneath the whole pipeline — it doesn't take a turn in the order, it sits under every step.

## When NOT to build the engine

- **Use the engine/platform; don't hand-roll it.** Physics, ECS, input, audio, the render loop — reach for the existing tool (`fabius-parcus` ladder: platform before app code). Hand-rolling a physics engine for a small game is the over-build trap in disguise. The recipes in [engine-recipes.md](engine-recipes.md) are for when you're *already* on raw canvas with no engine — they're the lean floor, not a license to rebuild Unity.
- **Don't add systems the loop doesn't need.** No inventory, no skill tree, no save system until the core loop has earned them.

## The engine & feel library (companion — bundled, paged on demand)

The deep library — the fixed-timestep loop, buffered input, the SFX pool, pixel-perfect render, AABB collision, the juice patterns with implementation, the pixel-art kit — is bundled at [engine-recipes.md](engine-recipes.md), indexed by [CORPUS.md](../../../CORPUS.md). Page in the **one** recipe the task needs; never load it wholesale (`fabius-parcus`; routing-policy R9 · M9).

Boundary: lean code is `fabius-parcus`; plan + prove is `fabius-disciplina`; UI/animation laws are `fabius-decor`; enemy/NPC agents are `fabius-cohors`. This layer owns the loop, the feel, and the balance. The user's design and brand always win.
