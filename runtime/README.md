# fabius, locally

A zero-dependency local runner for the same rules. fabius is a plugin — one set of rules
above every model — and normally your harness (Claude Code, Codex, an AGENTS.md reader)
loads it. This folder is the convenience for when there is no harness: it reads the same
sealed `SKILL.md` contracts off disk and hands them to a model through your own API key,
with hands only a local process can have: your files, your shell, your network.

```bash
node runtime/fabius.mjs doctor          # what is configured and what is missing
printf '%s' "$ANTHROPIC_API_KEY" | node runtime/fabius.mjs keys set anthropic
node runtime/fabius.mjs run "review this repo and draft the README it is missing"
```

No install step, no dependency tree, no build. Use Node 22 or newer from a complete fabius
checkout: the runner intentionally depends on the sibling `skills/` and `provenance/`
trees and is not published as a standalone npm CLI. `npm test` derives its current check
count; specification-vector tests skip until `npm run vectors` fetches their upstream
vectors once. They skip loudly rather than passing quietly.

## Why a runner at all

Inside a harness the harness reads the routed contracts and drives the model; the plugin
needs nothing else. Without one you still want the same rules — and you want them to run
where the work is: a hosted sandbox has no filesystem, so it cannot read the repository you
are working in, cannot run your test suite against your toolchain, and sends your task to
a server, so the task leaves the building.

This runner keeps its state and tools local. The selected model provider still receives
the prompt and any observations placed in model context. Agent fetches are separate: each
exact origin must be approved for the run (or pre-authorized with repeatable
`--allow-origin`), and `--offline` removes the network tool entirely.

## The command surface

| | |
|---|---|
| `run "<task>"` | one task, end to end: route → sense → act → prove → compound |
| `chat` | the same loop kept open; conversation and directory persist, while durable memory writes still require `--remember` |
| `recon <domain>` | audit a domain you own — no API key, no account, nothing to sign up for |
| `route "<task>"` | print the routing decision and spend nothing |
| `memory list \| search \| add \| rm` | the on-disk knowledge base |
| `listen --owner <npub>` | reachable by encrypted message with no server in between |
| `send <npub> "<text>"` | send one encrypted message |
| `whoami` | this machine's agent address |
| `doctor` | providers, contracts, seal, paths |
| `keys set <provider>` | read a key privately from hidden TTY input or stdin; argv secrets are rejected |

## Permission, which is the whole story

A cloud agent's blast radius is a container. A local agent's blast radius is your laptop.
So capability is not a setting here — it is a gate every tool passes through.

Four capabilities. Jailed, non-secret `read` is passive and does not prompt. `net` is
egress: first contact with each exact origin prompts unless the operator supplied
`--allow-origin`; redirects repeat the origin check. `write` and `exec` are not offered
unless you pass `--act`. Posture `never` (`--read-only`) refuses all outbound network,
writes, and commands.

Three postures:

```bash
fabius run "…"                 # it can read; an exact-origin fetch asks; no write or shell.
fabius run "…" --act           # it may ask. Each write and each command, once, with the
                               #   command printed in full before you answer.
fabius run "…" --act --yes     # auto-write in-jail files; only tiny read-only probes auto-run.
fabius run "…" --offline       # no agent network tool.
```

`--read-only` is an explicit hard ceiling, not a precedence hint: the CLI rejects it
when combined with `--act`, `--yes`, `--dangerously-approve-everything`, `--remember`,
or `--allow-origin` instead of silently choosing one authority level.

That last exception is the point, and it is an allowlist, not a list of banned words.
Autonomous mode auto-runs only a tiny fixed set of argument-free diagnostics (`pwd`,
`whoami`, `uname`, `date`). File discovery and search use built-in jailed tools. Shells,
interpreters, package/task runners, repository scripts, globs, recursion, pipes,
substitutions, redirects, and unknown binaries always go to a human. Irreversible commands —
`rm -rf` however it is spelled, `git push`, `vercel --prod`, `sudo`, `DROP TABLE`,
`curl … | sh` — carry an additional hold, and a non-interactive run refuses every prompt
rather than guessing. Releasing the irreversible
list unprompted needs `--dangerously-approve-everything` **on top of** `--yes` — under the
default ask posture the flag only lowers the hold to the same prompt everything else gets —
and taking that step is written into the run's audit log. The delivered artifact that the execution oracle runs goes through the same gate,
printed in full, counted against the same command budget — and because a command label
cannot vouch for the model-authored program body, `--yes` does **not** release
it: the oracle asks even in autonomous mode, and an unattended run skips the execution check
rather than running authored code unread. `--dangerously-approve-everything` is what runs it
unattended.

Two boundaries hold regardless of posture:

- **The working directory is a jail.** Existing paths and the nearest existing ancestor
  of a new path are resolved through symlinks before the
  check, so a link pointing outward is refused rather than followed. For `read` and
  `write` that is absolute. For `exec` it is one layer, not a seal — the path-looking
  arguments of a command are held to the same jail, so `cat /etc/passwd` and
  `node /tmp/x.js` are never auto-approved and go to a human, but arbitrary shell can
  always spell a path some other way.
- **Secrets are on a case-insensitive, canonical-path deny-list that no flag overrides.** `.ssh`, `.aws`, `.env`, `*.pem`,
  `.npmrc`, keychains — the agent cannot read them, `grep` and `list` skip them file by
  file rather than only at the directory, a command that names one is refused, and anything
  key-shaped that reaches an observation by another route is redacted before the model sees
  it. Model-initiated processes receive a scrubbed environment. Shell-string screening is
  defense in depth; the enforceable autonomous boundary is that interpreters and general
  shell commands are not auto-approved, and `exec` does not exist without `--act`.

The model-visible `fetch` tool reaches only an operator-approved exact origin on the public
internet: loopback, RFC1918, link-local (including cloud instance metadata at
`169.254.169.254`), CGNAT and multicast are refused, hostnames are resolved and checked
before the request, and every redirect hop is re-checked. One residual, stated rather than
hidden: the name is resolved for the check and again for the connection, so a hostile name on
a very short TTL can answer differently the second time.

`recon` is not in the model's tool menu. `fabius recon <domain>` typed at the prompt is
operator authority, and
the gate is narrower there. Its HTTP surface holds to the same rule — the entry request,
every redirect hop, and the plain-HTTP probe all refuse a private address — but the TLS
handshake and the `--ports` scan connect to whatever host you name, private or not. Point
them only at hosts you are authorised to test — that is what the `--ports` warning is for.

Every decision, allowed or denied, lands in the run's journal under `~/.fabius/runs/`.

## What the loop actually does

Routing first classifies the three process loads in the fabius rule—Memory, Tools/Action,
Planning—and any domain owner; it then chooses machinery and model tier. It prints the
reasoning:

```
Memory=false · Tools=true · Planning=true · Domain=true (→ praesidium)
R2 → smallest sufficient rung: subagent (stopped before swarm)
R11 → frontier: high-stakes domain (security) — reserved for money and security calls
```

Then the routed `SKILL.md` contracts are **read off disk and handed to the model**,
verbatim from the files the provenance seal covers. In a harness like Claude Code the
harness does that. Here there is no harness, so the runner does it — which is what makes
a local run *fabius* rather than a generic loop. `fabius doctor` reports whether those
files still match the sealed manifest.

The rules that were measured, and fire here too:

- **R8** — one rework on a reviewer's cited miss. One, not a loop.
- **R14** — a repeated probe earns a nudge: real feedback beats imagined feedback.
- **M11** — a deliverable that points at content it does not contain is sent back.
- **M12** — security and incident work reads no memory. Recalled context measurably
  helps design work and measurably hurts this; a stale precedent is the wrong prior.
- **M13** — when context outgrows the window, the oldest observations are *blanked*
  rather than summarised. A summary loses exactly the detail a dispute turns on.

**The oracle runs here.** When the deliverable contains a runnable block and you are
acting, the runtime executes it in a throwaway directory, with credential-shaped
environment variables stripped, once you approve the body it prints. A non-zero exit
overrules the reviewer's score — a judge can be talked past, a failing process cannot.

**Two walls.** Steps, and money. Before each model or reviewer call, the runtime reserves
a conservative upper bound for the whole input and maximum output, shrinking the output
ceiling or refusing the call when it cannot fit. Missing usage is charged at that
reservation; unknown models use the provider's highest listed rate. The audit receipt
separates reserved authorization from provider-reported cost.

## Memory

Plain markdown in `~/.fabius/memory/` — one page per fact, an index, an append-only log.
A knowledge base you cannot open in a text editor is one you cannot correct.

Recall treats every record as a suspect prior and current evidence wins. Security,
incident, outage, rollback, and recovery routes stand recall down. Writes require both a
deliverable that passed review at 70 or better **and** an explicit `--remember` on this run;
the default is no memory mutation. `--no-memory` disables recall and writes together.
Read/list/search and `doctor` do not create a memory store. First creation happens only on
an explicit write; update/delete keeps a recoverable local history instead of erasing the
previous bytes.

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

A bot hosted by a messaging platform can be suspended by that platform. A bridge into a
closed network needs a host and carries a ban risk. This channel has no owner: a keypair
is the identity, relays are public and interchangeable, and there is no account to
suspend or number to ban.

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

Eight provider adapters, one call shape: Anthropic, OpenAI, Google, Mistral, Groq,
HuggingFace, OpenRouter and Ollama — and through the two routers, any model they reach.
Keys come from the environment first, then `~/.fabius/config.json`.
A custom model id overrides the tier default only when you also named the provider it
belongs to, so a HuggingFace repo id can never be pasted onto a fallback Anthropic call.

Ollama needs no key and costs nothing; it also has no frontier tier, and the runtime says
so rather than pretending a 7B model is one.

## Testing

```bash
npm test                        # derives the current total; vector checks may skip loudly
npm run vectors && npm test     # fetch BIP-340/NIP-44 vectors once, then run every check
```

The vectors are never vendored: they belong to their upstream projects, and a stale copy
would quietly stop testing what it claims to test.

The model call is injectable, so the whole loop — routing, tools, the gate, every rule,
the oracle, the memory decision — is exercised by a scripted model. A loop that can only
be tested by spending money does not get tested.
