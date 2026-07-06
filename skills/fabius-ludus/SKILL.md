---
name: fabius-ludus
description: >
  fabius's game-craft layer — how to make a small game that's actually fun and actually ships:
  find the core loop first, add game feel (juice) deliberately, model state as an explicit machine,
  hold the pixel-art lane, balance one knob at a time, and scope to a jam-sized cut. Use when
  building a game, a game prototype, a game mechanic, a game loop, a playable, an interactive toy,
  a sticker/character game, or anything with win/lose/score state — or when the user says "make a
  game", "the loop isn't fun", "add juice", "balance this", or "make it feel good to play". The
  core-loop template, the juice checklist, the state-machine skeleton, and the pixel-art constants
  live in references/game-playbook.md; the engine recipes and feel patterns live in references/engine-recipes.md, bundled and indexed by CORPUS.md, paged in on demand.
---
<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->

# Fabius Ludus — the loop is the game; everything else is paint

*Ludus* — the game, and the school where you drill it. A game lives or dies on one thing: the second-to-second loop. Art, menus, story, and meta are paint on top of a loop that's either fun or isn't. Same Fabian stance: **scout wide on what the game could be, strike narrow on the one loop that's fun with grey boxes.** `fabius-parcus` owns YAGNI; this layer owns what makes play feel good.

## 1. Find the core loop first

Name the ~10-second cycle in one line: **act → feedback → reward → again.** *(Move → land hit → number pops + enemy dies → do it again.)* Build *only* that, with grey boxes and placeholder sound, and answer one question: **is it fun yet?** No art, no menu, no progression, no content until the loop is fun unpainted. A beautiful game on a dead loop is a dead game (`fabius-parcus`: the content doesn't need to exist until the loop holds).

## 2. Game feel (juice) — deliberate, not decorative

A flat loop becomes a fun loop through feedback on every action. The cheap, high-payoff moves:

- **Response on every input** — a sound and a visual the instant the player acts; nothing should feel silent.
- **Hit-stop** — a few frames of freeze on impact sells weight.
- **Screen-shake — sparingly** — a small kick on big events; constant shake is noise.
- **Easing, not linear** — things ease in/out; anticipation before, follow-through after.
- **Particles & pops** — a burst, a number, a flash on reward.
- **Juice the verbs the player does most** — the core action gets the most feedback budget.

(Animation *laws* — restraint, transform/opacity only — are `fabius-decor`; the game-feel *specifics* above live here. One micro-language, calm baseline, punch on the moments that matter.)

## 3. State as an explicit machine

No boolean soup. Model game state as a named finite-state machine and draw the transitions:

```
boot → menu → play → (pause ⇄ play) → win | lose → menu
```

Each state owns its update/render/input; transitions are named events, not scattered flags. (`fabius-parcus`: no `isPlaying && !isPaused && !isDead` tangles; `fabius-disciplina`: a state diagram you can hold in your head.)

## 4. Hold the pixel-art lane

For a pixel game, the discipline *is* the look:

- **One fixed palette** — lock the project's own brand palette and identity up front, then don't drift. One palette, one identity, applied consistently.
- **Integer scaling only** — 2×, 3×, 4× — never fractional, or it shimmers.
- **Snap to the pixel grid** — positions round to whole device-pixels; sub-pixel motion blurs the crispness that *is* the aesthetic.
- **One unit size** — a consistent base tile/sprite size; the grid is the rhythm.

(On RTL surfaces — Hebrew, Arabic — the UI keeps its own reading direction: left-pointing arrows are correct for "back/next" in that layout; don't flip them.)

## 5. Balance one knob at a time

Tune a single variable, playtest, lock it, move to the next. Changing three at once means you learn nothing from the result. Shape the difficulty curve as **teach → test → twist**: introduce a mechanic safely, demand it, then complicate it. The fun is in the climb, not the wall.

## 6. The studio pipeline — how a game ships under fabius

A game is a *vertical*: it composes several layers behind one goal. The dispatch order:

```
fabius-ludus       → the loop + the feel (this layer leads)
  → fabius-disciplina  → plan the build as step → verify; prove it runs
  → fabius-decor       → menus, HUD, the framing UI (tokens, states)
  → fabius-cohors      → only if NPCs/enemies need real agent behavior
  → fabius-parcus      → underneath all of it (lean code, reach for the engine)
```

This is the **studio pattern**: a domain skill leading a mini-pipeline. The router composes it; you don't pick one layer (routing-policy R13).

## 7. Scope the jam

Pick the **smallest shippable game that proves the loop** — a jam-sized cut. One mechanic done well beats five half-done. Cut ruthlessly: every feature past the core loop is a question of *does this earn its build cost?* Ship the vertical slice, then decide what's worth adding.

## When NOT to build the engine

- **Use the engine/platform; don't hand-roll it.** Physics, ECS, input, audio, the render loop — reach for the existing tool (`fabius-parcus` ladder: platform before app code). Hand-rolling a physics engine for a small game is the over-build trap in disguise.
- **Don't add systems the loop doesn't need.** No inventory, no skill tree, no save system until the core loop has earned them.

## References

- Core-loop template, the juice checklist, the FSM skeleton, the pixel-art constants, and jam-scoping rules → `references/game-playbook.md`.
- Engine recipes, feel patterns, and the pixel-art kit → `references/engine-recipes.md`, bundled and indexed by [CORPUS.md](../../CORPUS.md); page in the one slice the task needs (R9 · M9).
- The verified engine + asset stack — engines (Godot/Phaser/KAPLAY/Bevy), pixel/level/audio tools, CC0 asset sources (Kenney/Quaternius), and game-relevant HF models (with the OpenRAIL / FLUX-dev-base license traps flagged) → `references/game-toolkit.md`.

Boundary: lean code is `fabius-parcus`; plan + prove is `fabius-disciplina`; UI/animation laws are `fabius-decor`; enemy/NPC agents are `fabius-cohors`. This layer owns the loop, the feel, and the balance. The user's design and brand always win; `stop fabius` drops the stance (kill-switch owned by `fabius`).
