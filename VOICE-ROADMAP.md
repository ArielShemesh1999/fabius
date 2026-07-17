# fabius → voice agent — roadmap

*Research-backed plan to give fabius a natural voice — talk to it, it talks back, interruptibly (ChatGPT-Voice class). Synthesized from a 7-agent sweep of the open-source TTS / voice-cloning / realtime / cloud landscape (2026) + an adversarial feasibility review, grounded in fabius's real stack. Honors the owner cost rule: **FREE = build it; PAID/INFRA = flag it, OFF by default.***

*Refreshed **2026-07-17** — landscape re-verified against live sources; stale claims corrected in place (see “Landscape 2026-07” + “Corrections”). New: the **polish-layer** thesis, reverse-engineered from Wispr Flow.*

## North star

> fabius is already the hard, expensive middle of every voice pipeline — the LLM, multi-provider routing, **tool-calling** (`runCode`/`fetch`/`web_search`), memory, and the operator loop. **Voice is an I/O shell bolted onto the edges**: audio-in (mic → text → task) and audio-out (deliverable → speech), with barge-in. Cascaded (STT → fabius → TTS), not speech-to-speech, so fabius stays the brain and Hebrew-specialized parts swap in independently.

## The honest constraint

A Cloudflare Worker **cannot run a TTS model** (PyTorch/ONNX need a CPU/GPU host) — same limit as the code sandbox. Two free paths sidestep it: **(1) the browser's Web Speech API** (on-device, $0, incl. Hebrew); **(2) open-source models the user self-hosts** (Piper/Kokoro/OpenVoice) that fabius calls via a `TTS_URL` env, exactly like `CODE_SANDBOX_URL`.

## The pattern worth stealing — the POLISH LAYER (Wispr Flow, reverse-engineered)

> **Raw STT is a commodity. The polish layer is the product.**

The owner dictates Hebrew into Wispr Flow (Control key) and gets *clean* text. Clean is not an ASR win — it's a **second LLM pass over the transcript**, conditioned on context. Read straight off its local schema (`~/Library/Application Support/Wispr Flow/flow.sqlite`, table `History`), the pipeline is a **staged funnel where every stage is stored separately**:

`asrText` (raw) → `formattedText` (LLM cleanup) → `toneMatchedText` → `editedText` → `pastedText` (what landed)

What each moving part buys — and the fabius read:

| Wispr mechanism | Evidence (schema/product) | fabius already has? |
|---|---|---|
| **Disfluency + auto-punctuation cleanup** | `asrText` vs `formattedText` kept side-by-side | ✅ the LLM — it's a prompt |
| **Context-awareness of the active app** | `app`, `url`, `textboxContents`, `axText`, `axHTML`, `screenshot`; ships `ax-inspect-lib.mjs` (a11y-tree reader). Docs: reads nearby text, on-screen proper nouns, code identifiers; password fields excluded | ⚠️ browser-only analogue |
| **Tone-matching** | `toneMatchedText`, `toneMatchPairs`, `UserContext.writingSamples` + `polishPrompts`, `UserVoicePreferences(preference, filter)` | ✅ memory + prompt |
| **Custom dictionary / snippets** | `Dictionary(phrase→replacement, isSnippet, observedSource, manualEntry)`; auto-learns from your corrections | ✅ trivial (verify-gated memory) |
| **Edit-by-voice / Command Mode** | `Polish(polishInitialText→polishedText, instruction, diffCount)`; select text → "make this concise" | ✅ **this is just fabius** |
| **Dictation-vs-command router** | `InstructHistory(wasAutoRouted, classificationMode, shortCircuitRoute, classifierRouteData, toolCalls)` | ✅ the operator loop |
| **Revertibility + honesty telemetry** | `hasRevertedAI`, `formattingDivergenceScore`, `numWordsCorrected` — it *measures how much it changed your words* | ➕ **steal this** |
| **Dual-ASR fallback chain** | `defaultAsrText`/`fallbackAsrText`, `usedFallbackAsr`, `fallbackLevel`, `calledExternalAsr` | ➕ mirrors multi-provider routing |

**Verified architecture** (read-only inspect, v1.6.7, Electron `com.electron.wispr-flow`): **no local ASR model ships in the bundle** — `app.asar.unpacked` holds only native modules (`jabra-device-connector`), and all inference goes to first-party cloud (`api.wisprflow.ai`, `api-east.wisprflow.ai`, `inference-info.wisprflow.com/dictation`). It is **cloud STT + cloud LLM polish**, not on-device. Entitlements: audio-input only. Also exposes `api.wisprflow.ai/connect/mcp`.

**Owner's real numbers** (aggregates only, no transcript contents read): 29 sessions, **17 detected `he`** — Hebrew is the real workload; avg **e2e latency ~2.8 s** for ~22.8 s of speech; `calledExternalAsr` on 13/29; dictionary 8 entries / 3 snippets. **~2.8 s stop-speaking→text is the bar to match**, and it is *cloud* latency — so a cloud round-trip is not disqualifying.

**The strategic point:** fabius already owns the expensive half (LLM, routing, tool-calls, memory). Wispr's moat is a **prompt + context capture** bolted onto commodity STT. For fabius, the polish layer is ~a prompt and a dictionary — **the cheapest real capability on this roadmap**, and the one that turns flaky browser STT into usable text *without* paying for better STT.

## Tiers

### Tier 0 — FREE, in-browser — **SHIPPED (2026-06-26)**
fabius **speaks its deliverable** (`speechSynthesis`) and you **talk to it** (`SpeechRecognition` → fills the task → runs). Pure `cockpit.js`, **zero cost, zero infra, zero worker change**. In the console: a **🔊 Voice toggle** + a **🎙 mic button** beside Operator-mode. Barge-in (cancel on new run / mic), sentence-chunking (dodges Chrome's ~200-char / 15-s cutoff, no regex lookbehind for Safari), iOS gesture-priming, code-blocks stripped from speech. **Hebrew is genuinely natural and free on macOS/iOS via Apple's Carmit (he-IL).** Commit `29ad0e6`.
- *Honest limits:* `SpeechRecognition` is Chrome/Safari (not Firefox) and routes audio to the browser vendor (Google/Apple) — not offline; Chrome's bundled he-IL TTS is robotic (Carmit on Safari/Mac is good); TTS speaks the **finished** deliverable (the worker is single-POST, no streaming yet — so no true "speak while thinking").

### Tier 1 — Premium cloud TTS — PAID, opt-in, OFF
Natural cloud voice on the output side via a new `synthTTS()` + `POST /api/fabius/tts` worker proxy (mirrors the `CODE_SANDBOX_URL` pattern, gated on `TTS_URL`/`CARTESIA_KEY`; unset → 204 → client falls back to Tier-0). Take: **Cartesia** (Sonic, native Hebrew, ~75-90 ms first audio, agent-focused) or **ElevenLabs** / **Azure** (native he-IL Hila/Avri) / **OpenAI TTS**. *Cost: pay-per-char.* Add a per-session char budget + rate-limit the new route.

### Tier 1b — Better STT (Whisper) — PAID or INFRA, opt-in, OFF
Replace flaky/privacy-leaky browser STT with **Whisper** for accurate Hebrew: OpenAI `gpt-4o-transcribe` API (~$0.006/min) **or** self-hosted `faster-whisper` + **ivrit.ai** (Hebrew SOTA) / `whisper.cpp` on Apple Silicon. `POST /api/fabius/stt` gated on `STT_URL`/`OPENAI_KEY`; unset → free `SpeechRecognition`. Add **Silero VAD** (MIT, in-browser ONNX) for endpointing + instant barge-in.

### Tier 2 — Voice cloning — INFRA, opt-in, OFF
Speak in a chosen/uploaded voice. Needs a **GPU host** the worker calls via `TTS_URL` (never on the Worker). Take **OpenVoice V2 (MIT — the only commercially-clean clone)** paired with a Hebrew base TTS, or **Fish Speech / OpenAudio S2** (quality + real Hebrew, self-host license). *Avoid **XTTS v2** for anything commercial — its weights are **CPML / non-commercial** and Coqui Inc. is gone, so no license is purchasable; and it has no Hebrew.*

### Tier 3 — True speech-to-speech — PAID, reference only
**OpenAI Realtime API** (one model: audio↔audio, built-in VAD + barge-in) for the lowest-latency feel — but it **bypasses fabius's brain** (no tool-calls/memory/route), so keep it experimental. Or wrap fabius as the LLM stage in **Pipecat / LiveKit Agents** to inherit VAD + turn-taking while keeping the loop.

## Landscape 2026-07 (re-verified)

Hebrew = **REAL** support, not claimed. "Worker?" = can a Cloudflare Worker do it (no model runtime, no GPU).

| Thing | Status 2026-07 | License | Hebrew (real) | Cost | Browser / Worker / GPU |
|---|---|---|---|---|---|
| **Web Speech API** (STT) | Chrome/Edge/Safari/Opera. **Firefox still off by default** (`dom.webspeech.recognition.enable`, since FF22 — never shipped). **NEW: on-device** via `processLocally` + `available()`/`install()` (SODA packs) | browser | ⚠️ **cloud he-IL yes; on-device NO** — Chrome's on-device list is **17 langs** (de/en-US/es/fr/hi/id/it/ja/ko/pl/pt-BR/ru/th/tr/vi/zh-CN/zh-TW) — **no `he`** | **$0** | Browser ✅ / Worker n/a / GPU ✗ |
| **Web Speech API** (TTS) | stable | browser | ✅ **Apple Carmit he-IL is genuinely good**; Chrome he-IL robotic | **$0** | Browser ✅ |
| **Whisper + ivrit.ai** | ivrit.ai = Hebrew open SOTA: `whisper-large-v3-turbo-ct2` (295 h crowd + 93 h pro); public HF leaderboard | Apache-2.0 (Whisper) | ✅ **best open Hebrew** | free SW, host costs | Browser ✗ / **Worker ✗** / CPU-or-GPU host |
| **Silero VAD** | active (rel. 2026-02, commits 2026-03); `vad-node` winding down, **`vad-web` is the lane** | **MIT** (model); vad-web ISC | n/a (VAD is language-agnostic) | **$0** | **Browser ✅** (ONNX/WASM) |
| **Kokoro-82M** (TTS) | v1.0; **WebGPU now shipped** (was "coming soon"); 54 voices / 9 langs | **Apache-2.0** | ❌ **no Hebrew** | **$0** | **Browser ✅** (WebGPU→WASM) / Worker ✗ |
| **Piper** (TTS) | ⚠️ `rhasspy/piper` **archived Oct-2025**; live fork **`OHF-Voice/piper1-gpl` v1.4.2 (Apr-2026)** | ⚠️ **GPL-3.0** (fork) — *not* MIT | ❌ **no Hebrew voice** in official list | free SW, host costs | Browser (WASM) ~ / Worker ✗ / CPU host |
| **Cartesia Sonic** | **Sonic 3.5**, 42 langs, sub-90 ms TTFA (Turbo ~40 ms) | commercial | ✅ **`he` explicitly listed** | ~$0.03/min at scale; from $4/mo | Worker **proxy-only** ✅ / model ✗ |
| **ElevenLabs** | v3 (70+ langs), Flash v2.5 ~75 ms | commercial | ✅ `heb` in v3 | **$0.10/1k ch** (v3) · **$0.05/1k ch** (Flash/Turbo) | Worker proxy-only ✅ |
| **OpenAI transcribe/realtime** | `gpt-4o-transcribe` GA; realtime GA | commercial | ✅ (Whisper-lineage) | **$0.006/min** · **mini $0.003/min** · realtime ~**$0.017/min** | Worker proxy-only ✅ |
| **Deepgram** | Nova-3 | commercial | ✅ (36+ langs incl. Hebrew) | **$0.0043/min** batch · **$0.0077/min** stream | Worker proxy-only ✅ |
| **AssemblyAI** | **Universal-2 added Hebrew 2026-04 (−37% WER)**; Universal-3.5 Pro lists `he` in its 18 langs | commercial | ✅ **batch only** — ⚠️ **no Hebrew streaming** | **$0.0025/min** batch (cheapest) | Worker proxy-only ✅ |

## Corrections — what this roadmap got WRONG or now STALE

1. **Piper "MIT" — WRONG for the live code.** The maintained fork is **GPL-3.0**. MIT applies only to the archived, dead `rhasspy/piper`. Copyleft now matters if Piper is ever linked.
2. **Piper "partial Hebrew" — WRONG.** No Hebrew voice in the official voice list. Piper is **not** a Hebrew path.
3. **Tier-0 "not offline" — NOW HALF-STALE.** Chrome shipped on-device Web Speech (`processLocally: true`). **But the on-device list is 17 languages and Hebrew is not one** — so *for the owner's actual Hebrew workload the original claim still holds*: Hebrew audio still leaves the device to Google. English could go fully on-device/private today. (Caveats: was disabled until 142.0.7403.0; macOS `available()` bug — crbug 444393111.)
4. **"whisper.cpp on Apple Silicon" — MISLEADING here.** The owner's Mac is **Intel i9-9980HK, no Neural Engine**. whisper.cpp still runs (AVX2 present → the optimized CPU path; OpenVINO encoder optional), just **CPU-only and slow** — no Metal/ANE. Local Whisper is a *fallback*, not a good fit on this machine.
5. **AssemblyAI was missing entirely** — now a live Hebrew option (batch) and the **cheapest STT at $0.0025/min**, but **no Hebrew streaming** → unusable for realtime turn-taking.
6. **Kokoro "WebGPU coming soon" → shipped.** Still **no Hebrew** — so it stays an English-only upgrade, exactly as ranked.
7. **Cartesia Hebrew — CONFIRMED** (`he` explicit in Sonic 3.5's 42). The Tier-1 pick survives verification.
8. **OpenAI now has a cheaper tier** — `gpt-4o-mini-transcribe` at **$0.003/min**, half the roadmap's quoted $0.006.

## What to take (ranked)

*Re-ranked 2026-07-17: the **polish layer** jumps to #1 — it is free, it is pure prompt, and it fixes Hebrew text quality **without** buying better STT.*

1. **Web Speech API** — Tier-0 default. Free, in-browser, Hebrew via Carmit. ✅ taken.
2. **Sentence-chunking** (RealtimeTTS technique, ~10 lines). ✅ taken.
3. **🔥 The polish layer** (Wispr's actual moat) — one LLM pass: `rawTranscript → cleaned`, stripping disfluencies, fixing punctuation, applying a **custom dictionary** and the user's tone. **$0 marginal** (fabius is already the LLM). Keep `asrText` **and** `formattedText`, make it revertible, and log a divergence score so it can't silently rewrite the owner's meaning. **Biggest quality-per-token win on this page.**
4. **Silero VAD** (`@ricky0123/vad-web`, MIT) — free, instant barge-in, in-browser. *Next after #3.*
5. **Kokoro** (Apache-2.0, 82M) — natural English, **runs in the browser** (`kokoro-js`, WebGPU shipped) — free premium voice for **non-Hebrew only**. ~~Piper~~ **dropped: GPL-3.0 + no Hebrew.**
6. **Cartesia Sonic 3.5** (cloud, sub-90 ms, `he` verified) — the paid output upgrade.
7. **STT upgrade, Hebrew** — cheapest-first: **AssemblyAI $0.0025/min** (batch only) → **Deepgram $0.0043/min** (streams) → **OpenAI mini $0.003/min**. Self-hosted **ivrit.ai** only if a box exists — **not this Intel Mac** for realtime.
8. **OpenVoice V2** (MIT) — the commercially-clean cloning option.

## Cost breakdown (honest)

- **FREE** — Tier 0 (browser Web Speech): $0, no key, no worker call, no GPU. The only "cost" is privacy (STT audio leaves the device to the browser vendor) + quality (Chrome he-IL is robotic; Mac Carmit is good). Kokoro/Piper **in the browser** are also $0.
- **PAID** — cloud TTS/STT: pay-per-char/minute (Cartesia/ElevenLabs/Azure/OpenAI). Off behind an unset env var.
- **INFRA** — self-hosted models (Kokoro/Piper/OpenVoice/XTTS/Whisper on your own box): the software is free, but a **standing CPU/GPU host** (~$0.20-1.50/hr cloud GPU, or your own hardware) — "free software, not free to run." Off behind `TTS_URL`/`STT_URL`.

## What fabius already has (so voice is just the shell)
LLM · multi-provider routing · tool-calling (code/fetch/search) · verify-gated memory · the operator loop returning `{route, transcript[], output, usage}` from `POST /api/fabius/run`, rendered staged by `cockpit.js`. Voice adds only: audio-in, audio-out, VAD/barge-in, and (later) streaming.

---
*Sources: Coqui/XTTS (MPL code / CPML non-commercial weights, company defunct), Piper (MIT, archived Oct-2025, CPU/WASM), Kokoro-82M (Apache-2.0, browser-capable), espeak-ng (GPL, G2P front-end), OpenVoice V2 (MIT), CosyVoice/F5-TTS/Fish Speech, Web Speech API, Whisper + ivrit.ai, Cartesia/ElevenLabs/Azure/OpenAI-Realtime, Silero VAD. Grounded in `synapse/js/cockpit.js` + `worker/src/index.js`. Private strategy doc.*
