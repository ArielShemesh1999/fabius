# The local agent runtime

How to build an agent that runs on the user's own machine — and why almost every hard
problem in one is a permission problem wearing a different hat.

A hosted agent's blast radius is a container someone else pays for. A local agent's blast
radius is the user's laptop: their repositories, their credentials, their shell. That one
change of setting rewrites the design. Everything below follows from it.

fabius ships a working implementation of this document at `runtime/` in this repository.
Read it when a claim here needs a referent.

---

## 1. Why local at all

Be honest about the trade, because "local" is not automatically better:

| | hosted | managed harness | local |
|---|---|---|---|
| survives the laptop closing | yes | yes | no |
| reads the repo you are in | no | no | yes |
| runs your test suite, your toolchain | no | no | yes |
| the task leaves the building | yes | yes | no |
| reachable from a phone | yes | yes | only via a channel you add |
| blast radius | a container | a container | your machine |
| who owns the loop, the sandbox, the state | you | the provider | you |

The two rows that decide it are **"reads the repo you are in"** and **"the task leaves the
building"**. If neither matters, host it — hosting is less work and it stays up. Build
local when the agent's value comes from touching the real working tree, or when the
material must not be transmitted at all.

The middle column is the newer option, and it changes what "host it" costs. A **managed
agent harness** — Claude Managed Agents is the current example, in beta — runs the loop,
the sandbox, the session state and a cron scheduler for you; you supply the agent
definition (model, system prompt, tools, MCP servers, skills) and an *environment*, which
is either the provider's cloud sandbox or a **self-hosted sandbox on infrastructure you
control**. Sessions are long-running, resume cleanly, and can be steered or interrupted
mid-run — which is most of what sections 2, 5 and 8 of this document tell you to build.

Two facts decide whether that trade is yours to take. **You stop owning the sandbox, and
you stop owning the state:** sessions persist conversation history, sandbox contents and
outputs server-side, which is exactly why that tier is **not eligible for zero-data-retention
or a HIPAA BAA**. The self-hosted sandbox narrows this rather than closing it — tool
*execution* moves onto your infrastructure, while orchestration, and therefore tool inputs
and outputs, still flow through the provider's control plane.

So the same two rows still decide it, only more sharply. If you went local because the
material must not be transmitted, stay local — the managed tier fails that row by
construction. If you went local *only* so the loop would survive the laptop closing, you
were building a runtime you can now rent.

The usual right answer is more than one of these, sharing one brain: the same router, the
same rules, the same contracts, with different hands.

## 2. The process model

Three shapes, in order of how much you should want them:

1. **A CLI.** One process, argv in, artifact out. No ports, no daemon, no update channel,
   nothing to leave running. Start here and stay here as long as you can.
2. **A CLI plus a local server**, when something needs to persist between invocations — a
   channel listener, a scheduler, a UI. Bind to `127.0.0.1` on an ephemeral port, and
   require a token even so: `localhost` is not a trust boundary on a shared machine, and a
   browser tab on any origin can reach an unauthenticated local port.
3. **A desktop shell wrapping that server** (Tauri or Electron), when non-technical users
   are the point. Now you have signing, notarisation, auto-update, and a supply chain —
   which is to say, you have a product, not a tool. Do not take this step to be impressive.

Whatever the shape, the child process must die with its parent. An orphaned agent holding
an API key and a shell is the worst failure mode in this document, and it is the one that
actually happens — a crash, a force-quit, a terminal closed. Watch the owning PID
explicitly rather than trusting `getppid()`, which lies the moment a launcher or a bundler
inserts an intermediate process.

## 3. Capability, not configuration

Declare a capability on every tool and gate on the capability. Not on the tool name — a
name list drifts the moment someone adds a tool.

```
read   inside the working directory, minus the secret deny-list.        never prompts
net    outbound GET, public addresses only. Denied under `never`.       never prompts
write  create or modify a file in the working directory.                prompts by default
exec   run a command; its path arguments face the jail and deny-list.   prompts by default
```

`read` and `net` never prompt because they observe rather than change. Prompting on them
trains the user to hit `y` without reading, and that habit is what eventually approves the
`rm -rf`. Not prompting is not the same as always allowing: under the read-only posture
`net` is denied outright. A run that can read the working tree and then GET a URL of the
model's choosing, with what it read in the query string, is not read-only.

Three postures, and the third is where the design earns its keep:

- **ask** (default) — a human decides each write and each command, with the command
  printed in full first.
- **auto** — approve the ordinary work it recognises; hold what it does not, and what
  cannot be undone.
- **never** — read-only. The agent can look and reason and produce a plan, and cannot
  touch anything. This is the posture for a first run in an unfamiliar repository.

### Autonomy approves from an allowlist, never a denylist

Autonomy and reversibility are different axes, and conflating them is the common bug. But
a denylist is not the boundary, and reaching for one is the second bug. A regex list of
banned commands matched against a raw shell string is fail-open: `rm --recursive --force`,
`find . -delete`, `s''udo` and `echo cm0gLXJmIH4K | base64 -d | sh` all walk through it,
and every entry you add teaches the next spelling.

Invert it. Under `auto`, approve only an ALLOWLIST of commands you recognise and can
actually inspect — `npm test`, `pytest`, `node <file>`, `git status`, `ls`, `grep` and
their neighbours. Never auto-approve a line carrying a pipe, a `;`, an `&`, a `$(…)`, a
backtick, a redirect, a backslash or a newline: the shell re-reads the string after the
gate has looked at it, so what you inspected is not what runs. Never auto-approve an
interpreter handed inline code (`node -e`, `python -c`) — the command name says nothing
about the program it is being given. Everything the allowlist does not recognise goes to a
human, and a run with no terminal refuses it rather than guessing.

Keep the irreversible list on top of that as a warn-layer, never as the gate:

```
rm -rf …          git push          git reset --hard        npm publish
sudo …            vercel --prod     DROP TABLE              curl … | sh
mkfs / dd         shutdown          chmod 777               gh release create
```

`npm test` under `auto` should not prompt. `git push` under `auto` should — and so should
anything the allowlist does not recognise. Releasing the irreversible class needs a
separate, explicit, logged flag — and the fact that it was used belongs in the run's audit
trail, because "the agent pushed" and "the agent was allowed to push without asking" are
different post-mortems.

One trap worth stating because it is easy to get wrong: a pattern like
`\b(deploy|--prod)\b` never matches `vercel --prod`. The character before the dash is a
space, and space-to-dash is not a word boundary. Anchor flag-shaped alternatives without
the leading boundary and test every entry in the list against a real command line.

## 4. The three boundaries that are not negotiable

**A working-directory jail.** Resolve the target through symlinks *before* deciding, and
compare the real path against the real jail. A symlink inside the working directory that
points outside it is the classic escape, and a check on the literal string misses it. For
a file that does not exist yet — a create — walk up to the nearest existing ancestor,
resolve that, and re-attach the tail.

**A secret deny-list no posture overrides.** `.ssh`, `.aws`, `.gnupg`, `.kube`, `.env` and
its variants, `.netrc`, `.npmrc`, `*.pem`, `*.key`, `id_rsa`, `.git-credentials`,
keychains, and the agent's own config. Not a warning — a refusal, in every posture,
including the most permissive one. The agent has no legitimate need for these, and the
task that claims otherwise is the task to be suspicious of.

Pair it with **outbound redaction**: run every observation through a filter that replaces
known key values and key-shaped strings before the model ever sees them. The deny-list
stops the direct read; redaction catches the key that arrives through a log file, a
`printenv` in some build script, or a stack trace. Keep the key-shaped patterns narrow —
known vendor prefixes only — or ordinary base64 starts disappearing from observations and
the agent goes blind for no security gain.

Both of those apply to `exec`, not only to `read` and `write` — screen the command's
arguments, not just the file tools' paths. The moment autonomy recognises `cat`, `head`,
`grep` or `node <file>`, a bare `cat /etc/passwd`, `head ~/Documents/notes.txt` or
`node /tmp/x.js` is approved unprompted and reads an arbitrary file straight into the
model's context — and the jail you built for the read tool bought nothing. Extract the
path-looking tokens of the command line, `~`- and `$HOME`-expanded and unquoted, and hold
each one to the same jail and the same deny-list. One trap inside the trap: `~someone/…` is
another account's home, but left alone the token looks *relative* and resolves back inside
the jail, so mark it absolute and let the check refuse it. State the limit out loud — for
`exec` this is a layer, not a seal, and `c""at $H""OME/.ssh/id_rsa` defeats it. What you
can rely on is what autonomy is permitted to recognise at all, plus the fact that `exec` is
not offered without the acting flag.

**A public-internet-only egress check.** This is the boundary people forget, because `net`
never prompts and reads like the harmless capability. It is not: a tool that will GET any
URL reaches `127.0.0.1` admin panels, LAN devices on the operator's own network, and cloud
instance metadata at `169.254.169.254` — where, on a cloud host, IAM credentials are served
to anything that asks. The agent is inside the firewall, so `net` is a hole in every
firewall the operator owns.

Resolve the hostname first and refuse the WHOLE answer set — if any returned address is
loopback, RFC1918, link-local, CGNAT, reserved or multicast, refuse, so a split-horizon
name cannot smuggle one address through behind a public one. Refuse local names by name as
well (`localhost`, `*.local`, `*.internal`, `*.intranet`, `home.arpa`). Then follow
redirects BY HAND — `redirect: 'manual'`, re-checking every hop — because a guard applied
only to the entry URL is bypassed by a single `302` to `169.254.169.254`, and the built-in
redirect follower will take that hop for you before you ever see it. Cap the hop count and
cancel each redirect's body, or the sockets stay held.

State the residual rather than hiding it: the name is resolved once for the check and again
for the connection, so a hostile name on a short TTL can answer public the first time and
link-local the second. Closing that needs the checked address pinned into the socket, which
`fetch` does not expose. What is here defeats a static private target and a redirect to one
— one layer, honestly labelled.

## 5. Non-interactive runs must not hang

The moment there is a channel, a scheduler, or a cron entry, there are runs with no
terminal attached. A gate that waits for input there does not fail — it hangs, silently,
holding a slot, forever.

Decide it once, in the gate: no TTY means an `ask` resolves to **deny**, the tool returns
its refusal as an observation, and the run continues and delivers what it could. A denial
the agent can route around beats a process that never returns.

## 6. Make the model call injectable

The single highest-leverage line in an agent runtime:

```js
const llm = options.callLLM || callLLM;
```

With it, the entire loop — routing, tool dispatch, the permission gate, every rule seam,
the verification oracle, the memory decision — runs against a scripted model with no key,
no network and no spend. A scripted model also lets you assert the things that actually
break in production and are otherwise unreachable: that a failed review earns *exactly*
one rework rather than a loop, that a denied write really does feed a refusal back into
the transcript, that the budget wall stops the run.

A loop that can only be tested by spending money is a loop that does not get tested.

## 7. The oracle is better locally

Hosted, verification means a language model's opinion, plus at best a remote sandbox
running a snippet with none of your dependencies.

Locally, run the delivered artifact against the real toolchain and let the exit status
overrule the judge. A generous reviewer can be talked past — including by an instruction
hidden in the deliverable it is reviewing. A non-zero exit cannot.

Run it in a throwaway directory, never in the working tree: verification must not be able
to leave a file behind, and an artifact that writes as a side effect is exactly the
artifact you want to discover this way. Strip credential-shaped environment variables
before spawning — `/KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|SESSION|COOKIE|AUTH|PRIVATE/i`
over the variable *names* — because verification needs a toolchain, not the operator's AWS
session. Inheriting `process.env` whole hands every key on the machine to a program the
model wrote.

And send the oracle through the same gate as every other command, because it is the one
command the model wrote itself. An ungated oracle is the shortest path from a prompt
injection in a source file to arbitrary local execution: the poisoned file steers the
delivered code block, and the oracle runs it. So it is printed in full, screened against
the deny-list and the irreversible list, counted against the same command budget, and
written into the same audit trail. Full autonomy must not release it either — no allowlist
can vouch for a whole program the way it can vouch for `npm test`, so the oracle asks even
under the autonomous flag. An unattended run therefore skips the execution check and falls
back to the reviewer's verdict, shipping the deliverable unverified-by-execution rather
than running authored code unread. Only the explicit dangerously-approve-everything flag
runs it unattended.

## 8. Two walls, not one

Bound steps *and* money. On someone's own key, a loop that will not converge is a bill.

Count an unknown model at its provider's **highest** published rate. Over-counting stops a
run early; under-counting spends the owner's money. When one of the two errors is
recoverable and the other is not, choose the recoverable one deliberately and say why.

## 9. Reaching it — the channel, and who owns it

An agent on a laptop is unreachable from a phone unless you add a channel. There are three
ownership models, and the difference between them is who can take it away:

| | infrastructure | who can revoke it |
|---|---|---|
| a bot platform (Telegram-class) | none — they host it | the platform |
| a bridge to a consumer network (WhatsApp-class) | a host you pay for | the platform, and the account |
| a keypair on public relays (Nostr-class) | none | nobody — relays are interchangeable |

The third is worth understanding even if you never ship it, because it removes the
dependency rather than moving it: the identity *is* a keypair, relays are disposable and
substitutable, there is no account to suspend and no phone number to ban. Cost is a
smaller ecosystem and no delivery guarantee — a relay may simply not have your message.
Publish to several and treat any single one as unreliable.

Three rules make a channel safe enough to leave running:

- **An allow-list is mandatory.** Refuse to start without one. A public inbox that
  executes what it is told is not a feature.
- **Acting stays opt-in**, exactly as on the command line. By default an inbound message
  can make the agent read and reason; it cannot make it write a file or run a command.
- **Inbound text is a task, never an instruction to the runtime.** It reaches the model as
  the task string and nothing more. It cannot raise its own permissions, and the gate sits
  upstream of every tool regardless of what the message says.

Two implementation notes that cost real debugging time. Metadata-hiding envelopes fuzz the
outer timestamp *backwards* — up to two days in the NIP-59 design — so a narrow "since the
last five minutes" relay filter silently drops messages sent seconds ago. Filter wide and
judge freshness on the inner, unfuzzed timestamp after opening the envelope. And because
you are then accepting a wide window, keep a seen-set: relays replay history on connect,
and re-executing yesterday's instructions is its own kind of incident.

Reviewing the cryptography of such a transport — what the metadata still leaks, where
forward secrecy is absent, what a persistent per-device identifier gives up — is
`fabius-praesidium`'s call, not this layer's. This layer owns *whether the agent is
reachable and under what authority*.

## 10. If the contracts are sealed, let the loader enforce it

A local runtime that reads its instructions off disk inherits a provenance question the
hosted one never had: *are these the files that were sealed?* Report it in `doctor`, and
offer a mode that refuses anything outside the sealed set rather than merely noting it.

The trap is the same one every manifest checker starts with: re-hashing each listed file
proves nothing listed changed, and cannot see a contract that was **added** afterwards.
Check set membership separately from content, or a dropped-in skill is loaded and handed
to the model with a clean report. (The verification primitive, and the two-leg check →
`../../fabius-catena/references/sealing.md`.)

Keep the gate opt-in. A working copy mid-edit is a normal state, and a runtime that
refuses to start in it would be theatre — the useful posture is *report by default, refuse
when the provenance claim has to hold.*

## 11. Connectors, and when to stop adding them

The temptation in a local agent is a long list of service integrations. Resist by asking
what each one buys that a generic HTTP tool plus a credential does not.

Three tiers, in order:

1. **Generic tools** — read, write, shell, fetch. Most "integrations" are one authenticated
   HTTP call the agent can already make.
2. **MCP servers** for anything with real protocol surface. It is one acquisition path
   instead of N bespoke clients, and the tools arrive with schemas. Audit before adopting:
   a server that reads your filesystem and talks to the network is a supply-chain
   dependency, and `fabius-praesidium` owns that gate.
3. **A hand-written connector** only where the first two genuinely fail.

Deterministic service-to-service wiring — the "when X happens, do Y" plumbing — is
`fabius-machina`. This layer owns the agent that decides; that layer owns the pipe.

## 12. Pulling the final answer out of a noisy CLI stream

A harnessed coding CLI driven as a worker mixes everything into stdout: reasoning, tool
chatter, intermediate JSON that looks exactly like the answer. The disambiguator is a
**reserved sentinel field** — a schema const the FINAL object must carry, re-injected into
the schema if the caller's version lacks it. Mid-reasoning JSON does not carry it; the
answer does.

Collect candidates three ways — the raw stripped text, every fenced JSON block, and a
balanced-brace scanner that respects strings and escapes — then prefer the candidate
carrying the sentinel, then any structurally-plausible one, and unwrap the known wrapper
shapes the harness adds around results.

When the final answer arrives corrupted, do not re-run the expensive task. **Resume the
same session** with a terse instruction to skip any further analysis and re-emit only the
final JSON object, restating the schema and the validity rules. The resume path itself
layers fallbacks before giving up: the declared output file, then JSONL stdout, then the
agent's on-disk session files — and only then is the run classified as invalid output
(the typed failure class that decision feeds → `agent-evaluation-and-durability.md`).

## 13. The disposable per-job container recipe

When the runtime farms jobs out over untrusted code, the unit of containment is **one
throwaway container per job**: `--rm --init`, a per-job network and mount namespace,
`--pids-limit`, `--memory` equal to `--memory-swap` (a hard cap that includes swap) plus a
reservation, a tmpfs `/tmp` (`nosuid,nodev`, sized), and exactly two bind-mounts — the
repo checkout and a per-job HOME. Nothing else. (Which sandbox tier to reach for at all →
the §4 table in `agent-evaluation-and-durability.md`; this is the Docker row, spelled out.)

The isolation invariants: the job sees ONLY its checkout, its job HOME, and the single
provider credential it needs — environment variables explicitly allow-listed, never
inherited wholesale. The Docker socket, the database, and the project `.env` stay with the
privileged engine outside the container. One gotcha costs an afternoon: Claude Code
refuses bypass-permissions as root unless `IS_SANDBOX=1` — safe to set here precisely
because the container is already the boundary.

Budget concurrency by memory, not by count: effective workers =
min(configured, (total RAM − reserve) ÷ per-runner bytes), falling back to the configured
ceiling when memory info is unavailable. The pool cannot over-commit RAM while each runner
keeps its own hard cap. Label the sandbox containers, and reap stale ones on startup — an
orphaned container is §2's orphaned process wearing a namespace.

## 14. The checklist

Before calling a local runtime finished:

- [ ] Every tool declares a capability; the gate reads the capability, not the name.
- [ ] Read-only is the default. Acting is a flag, and autonomy is a second flag.
- [ ] Autonomy approves from an ALLOWLIST of recognised, inspectable commands; a pipe, a `;`, a `$(…)`, a backtick, a redirect or an interpreter given inline code is never auto-approved, and anything unrecognised goes to a human.
- [ ] Irreversible actions are held even under autonomy; the override is separate and logged.
- [ ] The jail resolves symlinks; a link out of the working directory is refused — for commands as well as files: a recognised command naming a path outside the jail, or a secret-bearing one, still stops for a human.
- [ ] The secret deny-list is unconditional, and observations are redacted on the way out.
- [ ] Outbound requests resolve-and-check before connecting, every redirect hop is re-checked, and a read-only run makes no outbound request at all.
- [ ] No TTY means `ask` denies rather than hangs.
- [ ] The model call is injectable, and the loop is tested with no key.
- [ ] Verification runs the artifact in a throwaway directory with credentials stripped, through the same gate as any other command and against the same budget; a non-zero exit overrules the judge.
- [ ] Both a step wall and a money wall; unknown models bill at the highest rate.
- [ ] Every permission decision lands in the run's journal.
- [ ] The seal is reported, and a mode exists that refuses anything outside the sealed set.
- [ ] The child process dies with its parent — verified by killing the parent, not by reading the code.
