# Fabius Ludus — the game engine & asset toolkit

Loaded on demand by `fabius-ludus`. Engines, pixel/level/audio tools, free assets, and game-relevant HF models (2026), filtered to the maintained best-in-class. License headlines that matter for a skill whose whole point is **shipping**: engines are cleanly permissive; **Aseprite is paid** (Pixelorama is the maintained MIT alternative — LibreSprite has gone stale); asset sources split **CC0 (no strings) vs. mixed (attribution / non-commercial traps)** — filter to CC0; and the HF models carry the biggest flags (**OpenRAIL** behavioral restrictions, and the **FLUX.1-dev non-commercial base trap**).

## Engines & frameworks

| Engine | License | Reach for it when |
|---|---|---|
| **Godot** *(default)* | MIT | A small game needs an editor, scenes, physics, and a real export pipeline (incl. web), no royalties. 2D is its sweet spot; node/scene = the state-machine skeleton. |
| **Phaser** *(v4)* | MIT | Must ship as a **URL** (jams, itch.io) — batteries-included input/physics/**tweens/particles** (the juice primitives). `npm i phaser` now lands **v4**, a different renderer from every v3 tutorial — read the note below before you pin. |
| **KAPLAY** | MIT | Fastest zero-to-playable (maintained Kaboom successor) — terse API, jam-sized cut, more time on feel. |
| **LÖVE** (love2d) | zlib | Code-only 2D in Lua — explicit `update`/`draw` loop is the core-loop discipline in the raw. |
| **raylib** | zlib | Close-to-the-metal C (70+ bindings) — you own every frame; clean base for teaching game-feel timing. |
| **Bevy** | MIT/Apache | The modern Rust lane — ECS enforces *state-as-explicit-machine* at the type level. Pre-1.0 (breaks often). |
| **PixiJS** | MIT | Pure 2D WebGL/WebGPU **renderer** (the ceiling for particles/filters at 60fps) — supply your own game systems. |

> **Phaser installs as v4 now, and v4 is not v3.** `npm i phaser` resolves to the 4.x line (4.0 shipped April 2026; 3.90 was the last v3). The renderer was rebuilt around **RenderNodes**: v3 custom `Pipeline` code, `Mesh`, `Plane` and `Geom.Point` are gone, FX and Masks are unified into one **Filters** system, `setTintFill(c)` becomes `setTint(c).setTintMode(FILL)`, and the Canvas renderer is deprecated in favour of WebGL-only. Pin the major in `package.json`; never port a v3 tutorial's pipeline code.
>
> **The pixel lane changed with it.** The bare `roundPixels` game option now defaults to **`false`** — but `pixelArt: true` still switches it on for you (and forces `antialias`/`antialiasGL` off), so a pixel project configures `pixelArt`, not `roundPixels`. Rounding is now deliberately limited to **axis-aligned, unscaled** objects: do *not* hand-snap a rotating or scaling sprite to win it back, because that is the vertex wobble the limit exists to prevent (`vertexRoundMode: "full"` is offered as PS1-style jank, not as a fix). Retro art that must rotate or scale smoothly takes **`smoothPixelArt: true`** instead — blocky texels preserved, edges between them smoothed. The two configs are mutually exclusive; pick by whether the sprites transform.

## Pixel · level · audio tools

- **Aseprite** — still the de-facto sprite/animation tool, still **proprietary/paid** ($19.99; compile the source for personal use only). Free alternative: **Pixelorama** (**MIT**) — actively released (v1.2, July 2026) and Godot-based: animation timeline with onion skinning and frame tags, tilemap layers with autotiling (rectangular · isometric · hexagonal) exporting straight to Godot TileSet resources, and **import** of `.ase`/`.aseprite`, `.psd`, `.kra` and `.piskel` — so a paid-tool project can move without redrawing. Import only: no export back to those formats, and grayscale Aseprite projects convert to RGBA. **LibreSprite** (GPL) is a fallback, not a lane — it forked from Aseprite's last GPL commit in 2016 and its newest tag is a March 2025 pre-release.
- **Tiled** (GPL-2.0 editor / BSD format) — tile-map editor; *the GPL binds only redistributing Tiled — maps you make are yours.* **LDtk** (MIT) — friendlier rule-based auto-tiling with official engine loaders. (Pixelorama covers simple autotiled tilemap layers too; reach for a dedicated editor when the *level* is the work, not the tiles.)
- **jsfxr** (Unlicense / public domain) — one-click 8-bit SFX in the browser; the cheapest same-hour juice win (audio on every action).

## Free assets — filter to CC0

| Source | License | Note |
|---|---|---|
| **Kenney.nl** | **CC0** | First stop — cohesive 2D/3D/UI/audio, no attribution, drop-in. Zero copyleft risk. |
| **Quaternius** | **CC0** | ~2,000 stylized low-poly 3D models (many rigged) — the 3D counterpart to Kenney; ship art-complete. |
| **OpenGameArt** | ⚠️ mixed per-asset | Deep well for one exact asset — but many are CC-BY (attribution) or **CC-BY-SA/GPL (copyleft can force your assets open)**. Filter to CC0, keep an attribution record. |
| **Freesound** | ⚠️ mixed per-sound | 700k+ real-world SFX — but **CC-BY-NC can't ship in a paid game**. Filter to CC0. |

## HF game models — mind the base license

| Model (HF id) | License | Note |
|---|---|---|
| **fal/flux-2-klein-4b-spritesheet-lora** | **Apache-2.0** | The one fully commercial-clean pick — single image → 4-angle sprite sheet (base FLUX.2-klein-4B is Apache). *Don't swap to the 9B klein base — it's non-commercial.* |
| **nerijs/pixel-art-xl** | ⚠️ **OpenRAIL-M** | The de-facto pixel-art SDXL LoRA for draft sprites (downscale 8× nearest-neighbor; hand-clean in Aseprite / Pixelorama). OpenRAIL = behavioral-use restrictions, not OSI-open. |
| **gvecchio/StableMaterials** | ⚠️ **OpenRAIL** | Tileable PBR material maps from text/image (built-in tileability). Research-grade; check RAIL clauses before commercial ship. |

> **The trap:** a fantasy game-prop LoRA can be Apache while its **base** (`FLUX.1-dev`) is **non-commercial** — you still can't ship. Always check the *base* model's license, not just the adapter's.

## Pairs with

`fabius-ludus` (the core-loop-first + juice + scope playbook), `fabius-decor` (pixel-art constants, palette discipline), `fabius-doctrina` (run/serve the image LoRAs), and `fabius-parcus` (find the fun before adding an engine feature; CC0 to ship without an artist).
