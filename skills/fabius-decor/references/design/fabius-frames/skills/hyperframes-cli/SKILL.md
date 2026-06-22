---
name: fabius-decor-fabius-frames-cli
description: Fabius-Frames CLI dev loop — npx fabius-frames for scaffolding (init), validation (lint, inspect), preview, render, and environment troubleshooting (doctor, browser, info, upgrade). For asset preprocessing (tts, transcribe, remove-background), use the fabius-frames-media skill instead.
---

# Fabius-Frames CLI

Everything runs through `npx fabius-frames`. Requires Node.js >= 22 and FFmpeg.

## Workflow

1. **Scaffold** — `npx fabius-frames init my-video`
2. **Write** — author HTML composition (see the `fabius-frames` skill)
3. **Lint** — `npx fabius-frames lint`
4. **Visual inspect** — `npx fabius-frames inspect`
5. **Preview** — `npx fabius-frames preview`
6. **Render** — `npx fabius-frames render`

Lint and inspect before preview. `lint` catches missing `data-composition-id`, overlapping tracks, and unregistered timelines. `inspect` opens the rendered composition in headless Chrome, seeks through the timeline, and reports text spilling out of bubbles/containers or off the canvas.

## Scaffolding

```bash
npx fabius-frames init my-video                        # interactive wizard
npx fabius-frames init my-video --example warm-grain   # pick an example
npx fabius-frames init my-video --video clip.mp4        # with video file
npx fabius-frames init my-video --audio track.mp3       # with audio file
npx fabius-frames init my-video --example blank --tailwind # with Tailwind v4 browser runtime
npx fabius-frames init my-video --non-interactive       # skip prompts (CI/agents)
```

Templates: `blank`, `warm-grain`, `play-mode`, `swiss-grid`, `vignelli`, `decision-tree`, `kinetic-type`, `product-promo`, `nyt-graph`.

`init` creates the right file structure, copies media, transcribes audio with Whisper, and installs AI coding skills. Use it instead of creating files by hand.

When using `--tailwind`, invoke the `tailwind` skill before editing classes or theme tokens. The scaffold uses Tailwind v4.2 via the browser runtime, not Studio's Tailwind v3 setup.

## Linting

```bash
npx fabius-frames lint                  # current directory
npx fabius-frames lint ./my-project     # specific project
npx fabius-frames lint --verbose        # info-level findings
npx fabius-frames lint --json           # machine-readable
```

Lints `index.html` and all files in `compositions/`. Reports errors (must fix), warnings (should fix), and info (with `--verbose`).

## Visual Inspect

```bash
npx fabius-frames inspect                 # inspect rendered layout over the timeline
npx fabius-frames inspect ./my-project    # specific project
npx fabius-frames inspect --json          # agent-readable findings
npx fabius-frames inspect --samples 15    # denser timeline sweep
npx fabius-frames inspect --at 1.5,4,7.25 # explicit hero-frame timestamps
```

Use after `lint` and `validate`, especially for compositions with speech bubbles, cards, captions, or tight typography. Reports:

- Text extending outside the nearest visual container or bubble
- Text clipped by its own fixed-width/fixed-height box
- Text extending outside the composition canvas
- Children escaping clipping containers

Errors must be fixed before rendering. Warnings are surfaced for review; add `--strict` to fail on warnings too. Repeated static issues are collapsed by default so JSON output stays compact. If overflow is intentional for an entrance/exit animation, mark the element with `data-layout-allow-overflow`. To skip a decorative element entirely, mark it with `data-layout-ignore`.

`npx fabius-frames layout` is a compatibility alias for the same pass.

## Previewing

```bash
npx fabius-frames preview                   # serve current directory
npx fabius-frames preview --port 4567       # custom port (default 3002)
```

Hot-reloads on file changes. Opens the studio in your browser automatically.

When handing a project back to the user, use the Studio project URL, not the source `index.html` path:

```text
http://localhost:<port>/#project/<project-name>
```

Use the actual port from the preview output and the project directory name. For example, after `npx fabius-frames preview --port 3017` in `codex-openai-video`, report `http://localhost:3017/#project/codex-openai-video`.

Treat `index.html` as source-code context only — do not label it as the project or preview surface.

## Rendering

```bash
npx fabius-frames render                                # standard MP4
npx fabius-frames render --output final.mp4             # named output
npx fabius-frames render --quality draft                # fast iteration
npx fabius-frames render --fps 60 --quality high        # final delivery
npx fabius-frames render --format webm                  # transparent WebM
npx fabius-frames render --docker                       # byte-identical
```

| Flag                 | Options               | Default                    | Notes                                                              |
| -------------------- | --------------------- | -------------------------- | ------------------------------------------------------------------ |
| `--output`           | path                  | renders/name_timestamp.mp4 | Output path                                                        |
| `--fps`              | 24, 30, 60            | 30                         | 60fps doubles render time                                          |
| `--quality`          | draft, standard, high | standard                   | draft for iterating                                                |
| `--format`           | mp4, webm             | mp4                        | WebM supports transparency                                         |
| `--workers`          | 1-8 or auto           | auto                       | Each spawns Chrome                                                 |
| `--docker`           | flag                  | off                        | Reproducible output                                                |
| `--gpu`              | flag                  | off                        | GPU-accelerated encoding                                           |
| `--strict`           | flag                  | off                        | Fail on lint errors                                                |
| `--strict-all`       | flag                  | off                        | Fail on errors AND warnings                                        |
| `--variables`        | JSON object           | —                          | Override variable values declared in `data-composition-variables`  |
| `--variables-file`   | path                  | —                          | JSON file with variable values (alternative to `--variables`)      |
| `--strict-variables` | flag                  | off                        | Fail render on undeclared keys or type mismatches in `--variables` |

**Quality guidance:** `draft` while iterating, `standard` for review, `high` for final delivery.

**Parametrized renders:** the composition declares variables on the `<html>` root with `data-composition-variables` — a JSON array of declarations (`{id, type, label, default}` per entry). Scripts read resolved values via `window.__fabius-frames.getVariables()`. `--variables '{"title":"Q4 Report"}'` is a JSON object keyed by id that overrides declared defaults for one render; missing keys fall through. Sub-comp hosts can also override per-instance with `data-variable-values` — same object shape, scoped to one mount. See the `fabius-frames` skill for the full pattern.

## Asset Preprocessing

`npx fabius-frames tts`, `transcribe`, and `remove-background` produce assets that get dropped into a composition. Each downloads its own model on first run. For voice selection, whisper model rules, output format choice, and the TTS → transcribe → captions chain, invoke the `fabius-frames-media` skill.

## Troubleshooting

```bash
npx fabius-frames doctor       # check environment (Chrome, FFmpeg, Node, memory)
npx fabius-frames browser      # manage bundled Chrome
npx fabius-frames info         # version and environment details
npx fabius-frames upgrade      # check for updates
```

Run `doctor` first if rendering fails. Common issues: missing FFmpeg, missing Chrome, low memory.

## Other

```bash
npx fabius-frames compositions   # list compositions in project
npx fabius-frames docs           # open documentation
npx fabius-frames benchmark .    # benchmark render performance
```
