<!-- © 2026 shear559 · fabius · reference depth for skills/fabius-archivum/SKILL.md -->

# Fabius Spectator — video ingest: a URL or file into a timestamped, filed record

Loaded on demand by `fabius-archivum`. The ingest step in [`../SKILL.md`](../SKILL.md) already fixes the shape — captions first, frames only as the question demands, every claim at `t=MM:SS`; this file is how that shape runs. The boundary mirrors [`meeting-capture.md`](meeting-capture.md): fabius is rules, not a player. The harness's shell runs `yt-dlp`, `ffmpeg` and `ffprobe`; the model reads extracted frames through the harness's image-read tool and the transcript as text; fabius supplies the discipline. The one law that outranks the rest: **never say "I watched."** There are exactly two kinds of evidence — what a frame shows and what the transcript says — and every claim names one: a quoted line at `t=MM:SS`, or a frame by its timestamp. A claim with neither is a guess from the title (routing-policy R5 in [`../../fabius/references/routing-policy.md`](../../fabius/references/routing-policy.md): never act on an assumed result).

## 1 · The pipeline

1. **Probe captions** (URL only). One skip-download call asks the source for native or auto-generated subtitles — **English tracks only** (`en.*`); a video captioned only in another language falls through to step 5. A local file never has captions: there is no sidecar `.srt`/`.vtt` lookup.
2. **Download only what the run needs.** The video is skipped only when detail is `transcript`, captions were found, *and* no cue timestamps were requested. Audio-only download happens only at `transcript` detail without captions. Every frame mode pulls the video — ≤720p when the host offers it, else the best rendition — even when captions exist. `--no-playlist` is hard-wired: a playlist URL processes one video.
3. **Extract frames per the detail dial.** Under `efficient` only keyframes are decoded; `balanced` and `token-burner` decode fully and select scene changes (threshold 0.20). Under-production trips the uniform sampler: fewer than 8 scene candidates (frame 0 is forced in, so six or fewer real cuts), or fewer than 4 keyframes, and the clip is treated as static. Frames are at most 512 px wide by default — never upscaled — and clamped to 1998 px tall (an image-reader height limit).
4. **Collapse near-duplicates.** One ffmpeg pass shrinks every frame to a 16×16 grayscale thumbnail; a frame is dropped when its mean absolute pixel delta against the last *kept* frame is ≤ 2.0 (0–255): the file is deleted and survivors reindexed. The reference is the last frame that survived, not the frame just before — that is what makes a slow fade collapse. The cap is applied *after* this pass, so the cap buys distinct frames. Fail-open: an ffmpeg error skips dedup silently.
5. **Transcript.** Captions when found; else Whisper — Groq `whisper-large-v3` preferred, OpenAI `whisper-1` second — on a mono 16 kHz 64 kbps mp3 extracted locally. Audio is split at 24 MiB (a margin under the providers' 25 MB cap), per-chunk timestamps are shifted back to source time, and a failed chunk is skipped; the transcript fails only if every chunk fails.
6. **Read every frame in one batch** — parallel reads, one message. Frames arrive as `path (t=MM:SS, reason=…)` in chronological order; reasons are `first-frame`, `scene-change`, `keyframe`, `uniform`, `transcript-cue`.
7. **Answer grounded** — a timestamp on every claim; a structured summary when no question was asked.
8. **Delete the working directory** unless follow-ups are expected. A follow-up in the same session never re-runs the pipeline — frames and transcript are already in context.

## 2 · The detail dial — a budget decision

| Detail | Candidate source | Cap | Reach for it when |
|---|---|---|---|
| `transcript` | none — no frames | — | The question is about what was said. No download when captions exist — unless `--timestamps` is passed (§5). |
| `efficient` | keyframes only (no full decode) | 50 | A fast first pass; screen recordings, talking heads. |
| `balanced` *(default)* | scene changes, full decode | 100 | The general case. |
| `token-burner` | scene changes, full decode | none (soft warning past 250 frames) | Every cut matters on a cut-heavy clip that a cap would thin. |

- `--max-frames N` overrides any cap. Every capped engine detects **all** candidates over the full range, then even-samples down to the cap with the first and last frame always kept. Candidate source and survivor count vary by mode; the spread does not, so the sample reaches the final seconds.
- Rung by rung (R2, R11): `transcript` → `efficient` → `balanced` → a focused re-run; `token-burner` only when a capped pass demonstrably missed cuts. Escalate on a miss, not a hunch.
- `efficient` describes the decode, not the count: on low-motion footage keyframes can outnumber scene cuts, so `efficient` may return *more* frames than `balanced`. Its cap of 50 still bounds it.
- The default comes from `WATCH_DETAIL`: env var > `~/.config/watch/.env` > `balanced`; an invalid value silently falls back to `balanced`. The `--detail` flag beats both.
- `--no-dedup` keeps near-duplicates — only to judge subtle frame-to-frame motion.

## 3 · Duration → frame budget

| Full-video duration | Target frames |
|---|---|
| ≤ 30 s | one per second, floor 12 — under the 2 fps ceiling, so 6 at 3 s, 10 at 5 s, 12–30 from 6 s; dense |
| 30–60 s | 40 |
| 1–3 min | 60 |
| 3–10 min | 80 |
| > 10 min | the mode cap (50 or 100); sparse-scan warning |

Every target is min'd with the cap and clamped to a universal **2 fps** ceiling. Upstream's README rounds the first row to ~30 and the last to 100 for every capped mode; the sampler says 6–30 and 50 for `efficient` — trust the code, not the README.

The sparse-scan warning fires only when unfocused, duration > 600 s, and detail is neither `transcript` nor `token-burner`; it advises a focused re-run or `token-burner`. A 45-minute `token-burner` run gets only the >250-frame warning, and only if that many frames survived. Upstream's guidance: accuracy is best under ten minutes — a guideline for the capped modes; nothing hard-stops a longer clip.

Upstream-reported, one run (a 49:08 YouTube video, 1280×720, auto-captions, mostly static): `efficient` 50 frames in ~0.5 s · `balanced` 100 in ~20.9 s · `token-burner` 116 in ~21.0 s · `transcript` ~4.5 s with no download · the shared download ~37 s / 76 MB. fabius did not measure this.

## 4 · Focus mode — the answer to a long video

`--start` and/or `--end`, in `SS`, `MM:SS` or `HH:MM:SS`. Denser per-second budgets, still bounded by the mode cap. Below 40 s the 2 fps ceiling binds, so each count is a maximum reached only at the top of its band:

| Window | Target frames |
|---|---|
| ≤ 5 s | 2 fps → up to 10 |
| 5–15 s | 2 fps → up to 30 |
| 15–30 s | 2 fps → up to 60 |
| 30–60 s | up to 80 — 2 fps until 40 s, then 80 at ≈ 1.3–2 fps |
| > 60 s | the cap |

1. When the user names a moment, focus.
2. When the video is over 10 minutes and the question is local, focus.
3. After a sparse full pass, re-run focused rather than raising the cap.

The transcript is filtered to segments overlapping the window; frame timestamps stay absolute on the source timeline. Validation: end > start, start inside the video, unparseable time → hard stop. A cue timestamp outside the window is dropped and counted in the report — it never widens the window.

## 5 · Transcript-cue frames — what the presenter points at

Visual selection scores pixel change; a presenter pointing at something changes few pixels, so the moment that matters most is the one a scene engine skips.

1. Run at `transcript` detail (or any) to get the timestamped transcript.
2. The model reads it for deictic phrases — "as you can see", "notice this", "look here" — a judgment call, not a regex; a rhetorical "look, the point is" is not a cue.
3. Re-run with `--timestamps 3:05,11:40` pointed at the **already-downloaded local file** in the work dir — no second download.

Cue frames are extracted first and reserved against the cap (detail budget = cap − cues), so even-sampling never evicts them; they merge chronologically as `reason=transcript-cue`. `--detail transcript --timestamps …` yields cue-only frames — and forces a full video download, because frames need pixels. More cues than the cap → the cues themselves are even-sampled, first and last kept.

## 6 · Resolution and token arithmetic

512 px wide is the default. `--resolution 1024` only when on-screen text must be read — slides, terminals, code — at roughly 4× the image tokens per frame. Image tokens ≈ (width × height) / 750 — Anthropic's published formula as cited by upstream; a 720p frame at 512 wide is 512×288 ≈ 197 tokens, arithmetic from that formula, not a measurement. Carry no other per-frame figure: upstream's own documents disagree on it; the formula is the only checkable one. On a long captioned video the transcript, not the frames, is often the larger cost (upstream-reported ≈ 26.6k text tokens for 49 minutes).

## 7 · Transcript rules

- Source labels: `captions` · `whisper (groq)` · `whisper (openai)` · `none available`. The record names which.
- Both keys present → Groq. A forced `--whisper groq|openai` whose key is missing does **not** fall back to the other backend; it prints a hint and produces no transcript.
- Whisper runs only when: no caption segments, `--no-whisper` absent, a video file exists, and ffprobe found an audio stream. No audio stream → frames only; the notice lands on stderr and the report's closing line blames a missing key — read stderr before naming the cause.
- Transcript stamps are `[MM:SS]` and roll past 60 (`[75:12]`); frame markers switch to `H:MM:SS` after an hour. On a video over an hour align by seconds, not by string.
- At `transcript` detail the deliverable is still a timestamped summary — structure, key moments, what was said — with only the two or three lines worth quoting verbatim. Hand over the raw transcript only when asked.

## 8 · Routing — who consumes the record

| Consumer | Question | fabius's default |
|---|---|---|
| `fabius-mercatus` | competitor creative — hook, structure, offer | `balanced`, then focus on the opening seconds for the hook |
| `fabius-disciplina` | bug repro from a screen recording — "when does the UI break?" | `efficient` to locate, focus on the break; `--no-dedup` only for subtle motion |
| `fabius-scientia` / `fabius-doctrina` | a talk or lecture into notes | `transcript` first, cues for the slides, `--resolution 1024` for equations and code |
| `fabius-archivum` | a series of videos into per-video records | one run per URL — `--no-playlist` is hard-wired |

## 9 · The ingest contract — what gets filed

Under the write boundary in [`../SKILL.md`](../SKILL.md) (not restated here), one page per video — [`memory-schema.md`](memory-schema.md)'s frontmatter and index/log lines, the body in [`meeting-capture.md`](meeting-capture.md)'s record shape:

```
---
name · description · type · updated
---
# <title or URL> · <date filed>
Source     — URL or local path · uploader if present · duration · detail mode · transcript source
TL;DR      — 2–3 sentences, the outcome first
Claims     — each with t=MM:SS (transcript) or frame t= (screen)
Facts      — what the record settles; decisions if the video records any
Open       — what the video did not show or say
```

Rules: **frames are not stored** — cite them by `t=`; the page carries a transcript **excerpt**, never the full transcript; index line + log line as always; the work dir is deleted after filing. Nothing without a timestamp compounds into memory — the same gate as a meeting record.

## 10 · Gotchas

| Tell | Cause | Rule |
|---|---|---|
| A source beginning with `-` | option injection (upstream 0.1.3, issue #2) | `--` before the URL; reject `-`-prefixed sources; resolve every media path to absolute before ffmpeg/ffprobe |
| Title/Uploader blank on Windows | cp1252 default when reading yt-dlp's UTF-8 metadata | UTF-8 reads everywhere; `python`, not `python3`, on Windows |
| A held slide costs dozens of frames | dedup off, or failed open | check the "near-duplicates dropped" note; its absence on a static clip means dedup did not run |
| `efficient` returned more frames than `balanced` | keyframes outnumber cuts | expected on low-motion footage |
| Tail of a long video missing | early-exit scene detection (fixed in 0.2.0) | detect all, then sample; the last frame must land near the end |
| Non-English video, no transcript | captions requested `en.*` only | Whisper or `none available`; say which |
| `WATCH_DETAIL=balanced  # note` fell back to default | inline comment parsed as the value (fixed at HEAD) | no trailing comments in `.env` — the key readers still do not strip them |
| `.env` readable by others | chmod sits in try/except, so a filesystem that cannot honour it fails silently — inference, not upstream-documented | mode 0600; preflight warns on any group/other read bit, the session-start hook on anything but 600/400 |
| Uniform-mode timestamps slightly off | `offset + i/fps` and keyframe-snapped seeks | approximate; scene and keyframe modes read exact `pts_time` |
| Two flat slides differing only in hue | gray thumbnails compare luma only | upstream says colour pairs survive; equal-luma pairs are the untested corner — unknown, confirm with `--no-dedup` |
| yt-dlp exits non-zero, video present | a subtitle variant 429'd | success is "a video file landed", not the exit code |

## 11 · Privacy — stated exactly

- For a URL, only extracted **audio** ever leaves the machine — never the video — and only when captions are absent and `--no-whisper` is not set.
- For a **local file** captions never exist, so audio leaves whenever a key resolves, `--no-whisper` is absent and ffprobe found an audio stream; a silent recording sends nothing. `--no-whisper` keeps a local file fully local: frames only.
- Keys resolve env var → `~/.config/watch/.env` (mode 0600) → `./.env`. That third step means a project `.env` holding a provider key is used silently — run from a neutral directory or rely on the user config. The Groq key goes only to `api.groq.com`, the OpenAI key only to `api.openai.com`; keys are never logged. No platform login, no cookies. Nothing persists outside the work dir and the user config — and nothing under the fabius repo, ever.

## 12 · The open implementation

**claude-video** (MIT) — plugin `watch` 0.2.0, the strongest current tool for this pattern. In a harness with a plugin marketplace (Claude Code) two commands: `/plugin marketplace add bradautomates/claude-video`, followed by `/plugin install watch@claude-video`. Other Agent Skills hosts: `npx skills add bradautomates/claude-video -g`. It needs `ffmpeg`, `ffprobe` and `yt-dlp` on the path; pure-stdlib Python, no pip dependencies. fabius carries the laws above and bundles no scripts; the flags named on this page are that tool's identifiers, not fabius surface.

## Pairs with

`fabius-archivum` (the write boundary and the ingest loop this page runs inside), [`meeting-capture.md`](meeting-capture.md) (the same honesty for a spoken record), [`memory-schema.md`](memory-schema.md) (the page shape), [`external-recall.md`](external-recall.md) (when the source lives outside the store), `fabius-parcus` (the cheapest detail that holds), `fabius-praesidium` (keys, the `./.env` fallback, option injection), and the consumers in §8.

Informed by **claude-video** (bradautomates / Bradley Bonanno, MIT) — studied for the video-ingest pipeline, frame-budget dial, near-duplicate collapse and transcript-cue pinning, re-expressed in fabius's own voice; no upstream files bundled. See credits/README.md.
