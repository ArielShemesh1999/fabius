# fabius, locally

The agent, running on your machine. Same router, same rules, same contracts as the
console — with hands it can only have here: your files, your shell, your network.

```bash
node runtime/fabius.mjs doctor          # what is configured and what is missing
node runtime/fabius.mjs keys set anthropic sk-ant-…
node runtime/fabius.mjs run "read this repo and write the README it is missing"
```

No install step, no dependency tree, no build. Node 22 or newer and the repo you are
already holding. `npm test` runs **68 checks and spends nothing** — 61 of them offline, and
the 7 specification-vector tests skip until `npm run vectors` fetches the vectors once.
They skip loudly rather than passing quietly, because a crypto test that silently does
nothing is worse than no test.

## Why local at all

The console is the right place for a long-running operator: it survives your laptop
closing, it holds the org's memory, it is reachable from anything with a browser.

What it cannot be is *here*. It has no filesystem, so it cannot read the repository you
are working in. It runs code in someone else's sandbox, so it cannot run your test suite
against your toolchain. It sends your task to a server, so the task leaves the building.

This runtime is the other half. Your files never leave the machine unless a task sends
them; the only outbound traffic is the model provider you chose and URLs a task explicitly
names.

## The command surface

| | |
|---|---|
| `run "<task>"` | one task, end to end: route → sense → act → prove → compound |
| `chat` | the same loop, kept open, memory and directory persisting |
| `recon <domain>` | audit a domain you own — no API key, no account, nothing to sign up for |
| `route "<task>"` | print the routing decision and spend nothing |
| `memory list \| search \| add \| rm` | the on-disk knowledge base |
| `listen --owner <npub>` | reachable by encrypted message with no server in between |
| `send <npub> "<text>"` | send one encrypted message |
| `whoami` | this machine's agent address |
| `doctor` | providers, contracts, seal, paths |
| `keys set <provider> <key>` | store a key in `~/.fabius/config.json`, mode 0600 |

## Permission, which is the whole story

A cloud agent's blast radius is a container. A local agent's blast radius is your laptop.
So capability is not a setting here — it is a gate every tool passes through.

Four capabilities. `read` and `net` never prompt: they observe, they do not change
anything — and `net` is refused outright under `--read-only` (posture `never`), because a
run that cannot touch anything cannot reach out either. `write` and `exec` prompt, and are
not even offered unless you pass `--act`.

Three postures:

```bash
fabius run "…"                 # read-only. It can look and reason; it cannot touch.
fabius run "…" --act           # it may ask. Each write and each command, once, with the
                               #   command printed in full before you answer.
fabius run "…" --act --yes     # autonomous — except for what cannot be undone.
```

That last exception is the point, and it is an ALLOWLIST, not a list of banned words.
Autonomous mode approves only commands it recognises and can actually inspect — `npm test`,
`node build.mjs`, `pytest`, `git status`, `ls`, `grep` and their neighbours. A command line
carrying a pipe, a `;`, a `$(…)`, a backtick, a redirect, or an interpreter handed inline
code (`node -e`) cannot be inspected honestly, because the shell re-reads it after the gate
has looked, so it is never auto-approved. Everything else — `rm -rf` however it is spelled,
`git push`, `vercel --prod`, `sudo`, `DROP TABLE`, `curl … | sh` — stops and waits for a
human, and a non-interactive run refuses it rather than guessing. Releasing the irreversible
list needs `--dangerously-approve-everything`, and taking that step is written into the run's
audit log. The delivered artifact that the execution oracle runs goes through the same gate,
printed in full, counted against the same command budget.

Two boundaries hold regardless of posture:

- **The working directory is a jail.** Paths are resolved through symlinks before the
  check, so a link pointing outward is refused rather than followed.
- **Secrets are on a deny-list that no flag overrides.** `.ssh`, `.aws`, `.env`, `*.pem`,
  `.npmrc`, keychains — the agent cannot read them, `grep` and `list` skip them file by
  file rather than only at the directory, a command that names one is refused, and anything
  key-shaped that reaches an observation by another route is redacted before the model sees
  it. Be honest about the last part: screening a shell string for secret paths raises the
  bar, it does not seal it — arbitrary shell can always spell a path some other way. The
  boundary you can rely on is the allowlist above, and the fact that `exec` is not offered
  at all without `--act`.

`fetch` reaches the public internet only: loopback, RFC1918, link-local (including cloud
instance metadata at `169.254.169.254`), CGNAT and multicast are refused, hostnames are
resolved and checked before the request, and every redirect hop is re-checked.

Every decision, allowed or denied, lands in the run's journal under `~/.fabius/runs/`.

## What the loop actually does

Routing is the same three-axis classification the console runs — layer, machinery, model
tier — and it prints its reasoning:

```
Memory=false · Tools=true · Planning=true · Domain=true (→ praesidium)
R2 → smallest sufficient rung: subagent (stopped before swarm)
R11 → frontier: high-stakes domain (security) — reserved for money and security calls
```

Then the difference from the console: the routed `SKILL.md` contracts are **read off disk
and handed to the model**, verbatim from the files the provenance seal covers. In a
harness like Claude Code the harness does that. Here there is no harness, so the runtime
does it — which is what makes a local run *fabius* rather than a generic loop.
`fabius doctor` reports whether those files still match the sealed manifest.

The rules that were measured, and fire here too:

- **R8** — one rework on a reviewer's cited miss. One, not a loop.
- **R14** — a repeated probe earns a nudge: real feedback beats imagined feedback.
- **M11** — a deliverable that points at content it does not contain is sent back.
- **M12** — security and incident work reads no memory. Recalled context measurably
  helps design work and measurably hurts this; a stale precedent is the wrong prior.
- **M13** — when context outgrows the window, the oldest observations are *blanked*
  rather than summarised. A summary loses exactly the detail a dispute turns on.

**The oracle runs here.** When the deliverable contains a runnable block and you are
acting, the runtime executes it in a throwaway directory. A non-zero exit overrules the
reviewer's score — a judge can be talked past, a failing process cannot.

**Two walls.** Steps, and money. The run stops at its budget rather than through it,
counting an unknown model at its provider's highest published rate so the error is
always toward stopping early.

## Memory

Plain markdown in `~/.fabius/memory/` — one page per fact, an index, an append-only log.
A knowledge base you cannot open in a text editor is one you cannot correct.

Writes are gated: only a deliverable that passed review at 70 or better may compound. An
unverified answer that becomes precedent poisons every later recall, which is a slower
and worse failure than simply forgetting.

## Recon

```bash
fabius recon areta.co.il
```

DNS and CAA, the TLS certificate and what it negotiated, security headers graded by
directive, cookie flags, mail authentication (SPF, DMARC, DKIM selectors, BIMI), DNSSEC,
`robots.txt` and `security.txt`, page metadata, the CDN and stack fingerprint. Findings
come out ranked by severity, each with the fix.

No key. No account. Everything comes from `node:dns`, `node:tls` and one HTTP request,
because a security check you have to register somewhere to run is a check you will not
run.

Two deliberate choices. Findings you cannot act on are demoted: on `yourapp.vercel.app`
the DNS and mail records belong to Vercel, so they are shown as context rather than as
tasks. And the CSP is parsed per directive — `'unsafe-inline'` in `style-src` is ordinary,
the same keyword in `script-src` is the whole attack, and a tool that cannot tell them
apart teaches you to ignore it.

Everything above is passive: it reads what the host already publishes to any client. The
one active check, a TCP connect on common service ports, is off unless you pass `--ports`
against a host you are authorised to test.

## The channel with no server

```bash
fabius whoami                                    # npub1…  — this agent's address
fabius listen --owner npub1yourphone…            # now message it from anywhere
```

Telegram works, and Telegram can suspend it. A WhatsApp bridge works, and it needs a host
and carries a ban risk. This third option has no owner: a keypair is the identity, relays
are public and interchangeable, and there is no account to suspend or number to ban.

Messages are end-to-end encrypted and metadata-wrapped, so a relay sees only that some
ephemeral key sent something to you.

- **BIP-340 signing** — verified against the specification's own vectors.
- **NIP-44 v2 encryption** — verified against its official vectors, ciphertext reproduced
  byte for byte.
- **Sealed and gift-wrapped messages** — your key never appears on the wrapper.

An allow-list is mandatory; the listener refuses to start without one. Acting stays opt-in.
A message reaches the model as a task string and nothing more — it cannot raise its own
permissions, and the gate sits upstream of every tool no matter what the message says.

Inbound signature verification is deliberately *not* implemented: it needs elliptic-curve
point addition this module does not carry. Authenticity rests on two other things instead.
NIP-44 is authenticated encryption, so a seal that decrypts under your conversation key
proves its author held that private key; and the rumour's author must equal the seal's
author, which is the check that blocks impersonation. Both are tested.

## Providers

Eight, one call shape: Anthropic · OpenAI · Google · Mistral · Groq · HuggingFace ·
OpenRouter · Ollama. Keys come from the environment first, then `~/.fabius/config.json`.
A custom model id overrides the tier default only when you also named the provider it
belongs to, so a HuggingFace repo id can never be pasted onto a fallback Anthropic call.

Ollama needs no key and costs nothing; it also has no frontier tier, and the runtime says
so rather than pretending a 7B model is one.

## Testing

```bash
npm test                        # 68 checks — 61 run offline, 7 skip without the vectors
npm run vectors && npm test     # fetch the BIP-340 and NIP-44 vectors once → 68/68
```

The vectors are never vendored: they belong to their upstream projects, and a stale copy
would quietly stop testing what it claims to test.

The model call is injectable, so the whole loop — routing, tools, the gate, every rule,
the oracle, the memory decision — is exercised by a scripted model. A loop that can only
be tested by spending money does not get tested.
