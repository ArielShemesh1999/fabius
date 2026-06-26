# fabius → voice agent — roadmap

*Research-backed plan to give fabius a natural voice — talk to it, it talks back, interruptibly (ChatGPT-Voice class). Synthesized from a 7-agent sweep of the open-source TTS / voice-cloning / realtime / cloud landscape (2026) + an adversarial feasibility review, grounded in fabius's real stack. Honors the owner cost rule: **FREE = build it; PAID/INFRA = flag it, OFF by default.***

## North star

> fabius is already the hard, expensive middle of every voice pipeline — the LLM, multi-provider routing, **tool-calling** (`runCode`/`fetch`/`web_search`), memory, and the operator loop. **Voice is an I/O shell bolted onto the edges**: audio-in (mic → text → task) and audio-out (deliverable → speech), with barge-in. Cascaded (STT → fabius → TTS), not speech-to-speech, so fabius stays the brain and Hebrew-specialized parts swap in independently.

## The honest constraint

A Cloudflare Worker **cannot run a TTS model** (PyTorch/ONNX need a CPU/GPU host) — same limit as the code sandbox. Two free paths sidestep it: **(1) the browser's Web Speech API** (on-device, $0, incl. Hebrew); **(2) open-source models the user self-hosts** (Piper/Kokoro/OpenVoice) that fabius calls via a `TTS_URL` env, exactly like `CODE_SANDBOX_URL`.

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

## What to take (ranked)

1. **Web Speech API** — Tier-0 default. Free, in-browser, Hebrew via Carmit. ✅ taken.
2. **Sentence-chunking** (RealtimeTTS technique, ~10 lines). ✅ taken.
3. **Silero VAD** (`@ricky0123/vad-web`, MIT) — free, instant barge-in. *Next.*
4. **Kokoro** (Apache-2.0, 82M) — natural English, **runs in the browser** (`kokoro-js`/Transformers.js, WebGPU/WASM) — a free premium-voice upgrade for non-Hebrew. **Piper** (MIT, CPU/WASM, ~20-75 MB) — cheap self-host, partial Hebrew.
5. **Cartesia** (cloud, low-latency, Hebrew) — the paid output upgrade.
6. **Whisper** (+ ivrit.ai for Hebrew) — the STT upgrade.
7. **OpenVoice V2** (MIT) — the commercially-clean cloning option.

## Cost breakdown (honest)

- **FREE** — Tier 0 (browser Web Speech): $0, no key, no worker call, no GPU. The only "cost" is privacy (STT audio leaves the device to the browser vendor) + quality (Chrome he-IL is robotic; Mac Carmit is good). Kokoro/Piper **in the browser** are also $0.
- **PAID** — cloud TTS/STT: pay-per-char/minute (Cartesia/ElevenLabs/Azure/OpenAI). Off behind an unset env var.
- **INFRA** — self-hosted models (Kokoro/Piper/OpenVoice/XTTS/Whisper on your own box): the software is free, but a **standing CPU/GPU host** (~$0.20-1.50/hr cloud GPU, or your own hardware) — "free software, not free to run." Off behind `TTS_URL`/`STT_URL`.

## What fabius already has (so voice is just the shell)
LLM · multi-provider routing · tool-calling (code/fetch/search) · verify-gated memory · the operator loop returning `{route, transcript[], output, usage}` from `POST /api/fabius/run`, rendered staged by `cockpit.js`. Voice adds only: audio-in, audio-out, VAD/barge-in, and (later) streaming.

---
*Sources: Coqui/XTTS (MPL code / CPML non-commercial weights, company defunct), Piper (MIT, archived Oct-2025, CPU/WASM), Kokoro-82M (Apache-2.0, browser-capable), espeak-ng (GPL, G2P front-end), OpenVoice V2 (MIT), CosyVoice/F5-TTS/Fish Speech, Web Speech API, Whisper + ivrit.ai, Cartesia/ElevenLabs/Azure/OpenAI-Realtime, Silero VAD. Grounded in `synapse/js/cockpit.js` + `worker/src/index.js`. Private strategy doc.*
