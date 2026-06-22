<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/logo/dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/logo/light.svg">
    <img alt="Fabius-Frames" src="docs/logo/light.svg" width="300">
  </picture>
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/fabius-frames"><img src="https://img.shields.io/npm/v/fabius-frames.svg?style=flat" alt="npm version"></a>
  <a href="https://www.npmjs.com/package/fabius-frames"><img src="https://img.shields.io/npm/dm/fabius-frames.svg?style=flat" alt="npm downloads"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License"></a>
  <a href="https://nodejs.org"><img src="https://img.shields.io/badge/node-%3E%3D22-brightgreen" alt="Node.js"></a>
  <a href="https://discord.gg/EbK98HBPdk"><img src="https://img.shields.io/badge/Discord-Join-5865F2?logo=discord&logoColor=white" alt="Discord"></a>
</p>

<p align="center"><b>Write HTML. Render video. Built for agents.</b></p>

<p align="center">
  <a href="https://fabius-frames.heygen.com/quickstart">Quickstart</a> |
  <a href="https://fabius-frames.heygen.com/showcase">Showcase</a> |
  <a href="https://www.fabius-frames.dev/">Playground</a> |
  <a href="https://fabius-frames.heygen.com/catalog/blocks/data-chart">Catalog</a> |
  <a href="https://fabius-frames.heygen.com/introduction">Docs</a> |
  <a href="https://discord.gg/EbK98HBPdk">Discord</a>
</p>

<p align="center">
  <img src="https://static.heygen.ai/fabius-frames-oss/docs/images/fabius-frames-logo-motion-1280.webp" alt="Fabius-Frames demo: HTML code on the left transforms into a rendered video on the right" width="800">
</p>

Fabius-Frames is an open-source framework for turning HTML, CSS, media, and seekable animations into deterministic MP4 videos. Use it locally with the CLI, from AI coding agents with skills, or as the rendering core behind hosted authoring workflows.

## Quick Start

### With an AI coding agent

Install the Fabius-Frames skills, then describe the video you want:

```bash
npx skills add heygen-com/fabius-frames
```

Try a prompt like:

> Using `/fabius-frames`, create a 10-second product intro with a fade-in title, a background video, and subtle background music.

The skills teach agents the Fabius-Frames production loop: plan the video, write valid HTML, wire seekable animations, add media, lint, preview, and render. They work with Claude Code, Cursor, Gemini CLI, Codex, and other coding agents that support skills.

For visual design handoff workflows, see the [Claude Design guide](https://fabius-frames.heygen.com/guides/claude-design) and [Open Design guide](https://fabius-frames.heygen.com/guides/fabius-design).

### Manually with the CLI

```bash
npx fabius-frames init my-video
cd my-video
npx fabius-frames preview      # preview in browser with live reload
npx fabius-frames render       # render to MP4
```

**Requirements:** Node.js 22+, FFmpeg

## What You Can Build

Need ideas? Browse the [Showcase](https://fabius-frames.heygen.com/showcase) for finished videos you can watch, read, run, and remix.

- Product launch videos and feature announcements
- PR walkthroughs with animated code diffs, narration, and captions
- Data visualizations, chart races, and map animations
- Social videos with kinetic captions, overlays, and music
- Docs-to-video, PDF-to-video, and website-to-video explainers
- Reusable motion graphics for automated content pipelines

## Frame.md

**frame.md — your design system, ready for video.**

Every brand has a `design.md`. None of them were written for a camera. `frame.md` is the missing translation layer: it takes your web-context design spec and inverts it for the frame — the same tokens, the same rules, but rewritten so an AI agent can compose a promo video without guessing at scale or reaching for web chrome.

The output is a `DESIGN.md` superset your whole toolchain can read. Atoms stay sacred. Composition stays free. Numbers come from the script.

<table>
  <tr>
    <td width="50%" align="center">
      <a href="https://www.fabius-frames.dev/design/biennale-yellow"><img src="https://static.heygen.ai/fabius-frames-oss/docs/images/design-templates/biennale-yellow.png" alt="Biennale Yellow" width="100%"></a>
      <br><b><a href="https://www.fabius-frames.dev/design/biennale-yellow">Biennale Yellow</a></b>
    </td>
    <td width="50%" align="center">
      <a href="https://www.fabius-frames.dev/design/blockframe"><img src="https://static.heygen.ai/fabius-frames-oss/docs/images/design-templates/blockframe.png" alt="BlockFrame" width="100%"></a>
      <br><b><a href="https://www.fabius-frames.dev/design/blockframe">BlockFrame</a></b>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://www.fabius-frames.dev/design/blue-professional"><img src="https://static.heygen.ai/fabius-frames-oss/docs/images/design-templates/blue-professional.png" alt="Blue Professional" width="100%"></a>
      <br><b><a href="https://www.fabius-frames.dev/design/blue-professional">Blue Professional</a></b>
    </td>
    <td width="50%" align="center">
      <a href="https://www.fabius-frames.dev/design/bold-poster"><img src="https://static.heygen.ai/fabius-frames-oss/docs/images/design-templates/bold-poster.png" alt="Bold Poster" width="100%"></a>
      <br><b><a href="https://www.fabius-frames.dev/design/bold-poster">Bold Poster</a></b>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://www.fabius-frames.dev/design/broadside"><img src="https://static.heygen.ai/fabius-frames-oss/docs/images/design-templates/broadside.png" alt="Broadside" width="100%"></a>
      <br><b><a href="https://www.fabius-frames.dev/design/broadside">Broadside</a></b>
    </td>
    <td width="50%" align="center">
      <a href="https://www.fabius-frames.dev/design/capsule"><img src="https://static.heygen.ai/fabius-frames-oss/docs/images/design-templates/capsule.png" alt="Capsule" width="100%"></a>
      <br><b><a href="https://www.fabius-frames.dev/design/capsule">Capsule</a></b>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://www.fabius-frames.dev/design/cartesian"><img src="https://static.heygen.ai/fabius-frames-oss/docs/images/design-templates/cartesian.png" alt="Cartesian" width="100%"></a>
      <br><b><a href="https://www.fabius-frames.dev/design/cartesian">Cartesian</a></b>
    </td>
    <td width="50%" align="center">
      <a href="https://www.fabius-frames.dev/design/cobalt-grid"><img src="https://static.heygen.ai/fabius-frames-oss/docs/images/design-templates/cobalt-grid.png" alt="Cobalt Grid" width="100%"></a>
      <br><b><a href="https://www.fabius-frames.dev/design/cobalt-grid">Cobalt Grid</a></b>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://www.fabius-frames.dev/design/coral"><img src="https://static.heygen.ai/fabius-frames-oss/docs/images/design-templates/coral.png" alt="Coral" width="100%"></a>
      <br><b><a href="https://www.fabius-frames.dev/design/coral">Coral</a></b>
    </td>
    <td width="50%" align="center">
      <a href="https://www.fabius-frames.dev/design/creative-mode"><img src="https://static.heygen.ai/fabius-frames-oss/docs/images/design-templates/creative-mode.png" alt="Creative Mode" width="100%"></a>
      <br><b><a href="https://www.fabius-frames.dev/design/creative-mode">Creative Mode</a></b>
    </td>
  </tr>
</table>

Browse and remix them all at [fabius-frames.dev/design](https://www.fabius-frames.dev/design).

## How It Works

Define a video as HTML. Add data attributes for timing and tracks. Use GSAP, CSS, Lottie, Three.js, Anime.js, WAAPI, or your own frame adapter for seekable animation.

```html
<div id="stage" data-composition-id="launch" data-start="0" data-width="1920" data-height="1080">
  <video
    class="clip"
    data-start="0"
    data-duration="6"
    data-track-index="0"
    src="intro.mp4"
    muted
    playsinline
  ></video>

  <h1 id="title" class="clip" data-start="1" data-duration="4" data-track-index="1">Launch day</h1>

  <audio
    data-start="0"
    data-duration="6"
    data-track-index="2"
    data-volume="0.5"
    src="music.wav"
  ></audio>

  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <script>
    const tl = gsap.timeline({ paused: true });
    tl.from("#title", { opacity: 0, y: 40, duration: 0.8 }, 1);
    window.__timelines = window.__timelines || {};
    window.__timelines.launch = tl;
  </script>
</div>
```

Preview instantly in the browser. Render locally or in Docker. The renderer seeks each frame in headless Chrome and encodes the result with FFmpeg, so the same input produces the same video.

## Fabius-Frames Stack

Fabius-Frames is the open-source rendering engine, plus a growing set of tools around HTML-native video creation.

| Piece                                           | Status              | What it does                                                                                      |
| ----------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------- |
| CLI                                             | Available           | Scaffold, preview, lint, inspect, and render local video projects                                 |
| Core / Engine / Producer                        | Available           | Parse compositions, drive headless Chrome, encode video, and mix audio                            |
| Catalog                                         | Available           | Reusable blocks and components for transitions, overlays, captions, charts, maps, and effects     |
| Agent skills                                    | Available           | Teach coding agents the video-production patterns that generic web docs miss                      |
| Studio                                          | Available, evolving | Browser surface for previewing and editing compositions                                           |
| AWS Lambda rendering                            | Available           | Deploy a distributed render stack and drive renders from your laptop or CI                        |
| [fabius-frames.dev](https://www.fabius-frames.dev/) | Available           | Community playground for previewing, iterating, sharing, and rendering HTML-native video projects |
| [frame.md](https://www.fabius-frames.dev/design)  | Available           | Invert your design system for the camera — a DESIGN.md superset an agent can compose video from   |

## Catalog

Install ready-to-use blocks and components:

```bash
npx fabius-frames add flash-through-white   # shader transition
npx fabius-frames add instagram-follow      # social overlay
npx fabius-frames add data-chart            # animated chart
```

Browse the catalog at [fabius-frames.heygen.com/catalog](https://fabius-frames.heygen.com/catalog/blocks/data-chart).

## Why Fabius-Frames?

- **HTML-native:** compositions are HTML files with data attributes. No React requirement, no proprietary timeline format.
- **Agent-friendly:** agents already write HTML, and the CLI is non-interactive by default.
- **Deterministic:** same input, same frames, same output. Built for CI, regression tests, and automated rendering.
- **No build step:** an `index.html` composition plays as-is and can be previewed directly in the browser.
- **Adapter-based animation:** bring GSAP, CSS animations, Lottie, Three.js, Anime.js, WAAPI, or a custom runtime.
- **Open source:** Apache 2.0 license, with no per-render fees or commercial-use thresholds.

## Fabius-Frames vs Remotion

Fabius-Frames is inspired by [Remotion](https://www.remotion.dev). Both tools render video with headless Chrome and FFmpeg. The main difference is the authoring model: Remotion's bet is React components; Fabius-Frames' bet is plain HTML that humans and agents can both write easily.

|                          | **Fabius-Frames**                       | **Remotion**                            |
| ------------------------ | ------------------------------------- | --------------------------------------- |
| Authoring                | HTML + CSS + seekable animation       | React components                        |
| Build step               | None; `index.html` plays as-is        | Bundler required                        |
| Agent handoff            | Plain HTML files                      | JSX / React project                     |
| Library-clock animations | Seekable, frame-accurate via adapters | Wall-clock animation patterns need care |
| Distributed rendering    | Local and AWS Lambda render paths     | Remotion Lambda, mature cloud renderer  |
| License                  | Apache 2.0                            | Source-available Remotion License       |

Read the full comparison in the [Fabius-Frames vs Remotion guide](https://fabius-frames.heygen.com/guides/fabius-frames-vs-remotion).

## Documentation

Full documentation: [fabius-frames.heygen.com/introduction](https://fabius-frames.heygen.com/introduction)

- [Quickstart](https://fabius-frames.heygen.com/quickstart)
- [Showcase](https://fabius-frames.heygen.com/showcase)
- [Guides](https://fabius-frames.heygen.com/guides/gsap-animation)
- [API Reference](https://fabius-frames.heygen.com/packages/core)
- [Catalog](https://fabius-frames.heygen.com/catalog/blocks/data-chart)
- [Examples](https://fabius-frames.heygen.com/examples)
- [AWS Lambda rendering](https://fabius-frames.heygen.com/deploy/aws-lambda)

## Packages

| Package                                                          | Description                                                       |
| ---------------------------------------------------------------- | ----------------------------------------------------------------- |
| [`fabius-frames`](packages/cli)                                    | CLI for creating, previewing, linting, and rendering compositions |
| [`@fabius-frames/core`](packages/core)                             | Types, parsers, generators, linter, runtime, and frame adapters   |
| [`@fabius-frames/engine`](packages/engine)                         | Seekable page-to-video capture engine using Puppeteer and FFmpeg  |
| [`@fabius-frames/producer`](packages/producer)                     | Full rendering pipeline for capture, encode, and audio mix        |
| [`@fabius-frames/studio`](packages/studio)                         | Browser-based composition editor UI                               |
| [`@fabius-frames/player`](packages/player)                         | Embeddable `<fabius-frames-player>` web component                   |
| [`@fabius-frames/shader-transitions`](packages/shader-transitions) | WebGL shader transitions for compositions                         |
| [`@fabius-frames/aws-lambda`](packages/aws-lambda)                 | AWS Lambda SDK and deployment surface for distributed renders     |

## Community

Fabius-Frames is used in production at [HeyGen](https://www.heygen.com), with community examples from teams like [tldraw](https://tldraw.com), [TanStack](https://tanstack.com), and others in [ADOPTERS.md](ADOPTERS.md). Open a PR if your team is using Fabius-Frames.

- Questions and ideas: [Discord](https://discord.gg/EbK98HBPdk)
- Bugs and feature requests: [GitHub Issues](https://github.com/ArielShemesh1999/fabiusissues)
- Security reports: [SECURITY.md](SECURITY.md)
- Contributions: [CONTRIBUTING.md](CONTRIBUTING.md)

## Development Note

The repo uses [Git LFS](https://git-lfs.com) for golden regression-test baselines under `packages/producer/tests/**/output.mp4` (about 240 MB of `.mp4` files). If you're cloning the full repo for development, install Git LFS first:

```bash
# macOS
brew install git-lfs

# Ubuntu / Debian
sudo apt install git-lfs

# Windows
winget install GitHub.GitLFS

# Then, once per machine
git lfs install
```

If you only need source files, you can skip LFS content:

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/ArielShemesh1999/fabius
```

## License

[Apache 2.0](LICENSE)
