# Fabius Ludus — game playbook (entry)

The on-demand depth for `fabius-ludus`. Lean entry doc; the engine recipes and feel patterns live in the **fabius-ludus** library of the fabius corpus ([CORPUS.md](../../../CORPUS.md)), paged in on demand. **The loop is the game. Scout wide, strike narrow.**

---

## Core-loop template

Fill this before any art or menu exists:

```
Verb (what the player does):        ________
Feedback (the instant response):    ________   (sound + visual, every time)
Reward (why they do it again):      ________
Failure (the cost / the stakes):    ________
Loop length:                        ~__ seconds
Fun unpainted? (grey boxes test):   yes / not yet → fix the loop, not the art
```

If "not yet" — the fix is a loop change, never more content.

## Juice checklist (budget the most to the core verb)

```
[ ] input → instant sound + visual (nothing silent)
[ ] hit-stop: __ frames on impact
[ ] screen-shake: small, big events only (off by default)
[ ] easing on motion (no linear); anticipation + follow-through
[ ] particles / number-pop / flash on reward
[ ] the most-used verb gets the most feedback
```

## State-machine skeleton

```
states:  boot · menu · play · pause · win · lose
transitions:
  boot  --loaded-->     menu
  menu  --start-->      play
  play  --pause-->      pause     pause --resume--> play
  play  --died-->       lose      lose  --retry-->  play
  play  --goal-->       win       win   --next-->   menu
rule: each state owns update/render/input; no cross-state flags.
```

## Pixel-art constants

```
palette:        one fixed set (brand: green palette + red mascot), no drift
scale:          integer only (2× / 3× / 4×), never fractional
grid:           snap positions to whole device-pixels
unit:           one base tile/sprite size = the rhythm
text direction: RTL/Hebrew keeps left-arrow = back/next; don't flip
```

## Difficulty curve

`teach → test → twist`: introduce a mechanic in a safe room, demand it in the next, complicate it after. Tune **one** variable per playtest; lock before changing the next.

## Jam-scoping rule

Smallest shippable game that proves the loop. One mechanic, done well. For every proposed feature: *does this earn its build cost against the core loop?* If unsure, cut it — ship the slice, decide later.

## The engine & feel library (corpus — indexed, not bundled)

The deep library — engine recipes (input/loop/audio/render per platform), juice patterns, and the pixel-art kit — lives in the **fabius-ludus** library of the fabius corpus ([CORPUS.md](../../../CORPUS.md)), not bundled here. Query the index for the **one** recipe the task needs and page it in; never load the library wholesale (`fabius-parcus`; routing-policy R9 · M9).
