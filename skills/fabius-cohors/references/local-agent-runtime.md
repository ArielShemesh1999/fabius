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

| | hosted | local |
|---|---|---|
| survives the laptop closing | yes | no |
| reads the repo you are in | no | yes |
| runs your test suite, your toolchain | no | yes |
| the task leaves the building | yes | no |
| reachable from a phone | yes | only via a channel you add |
| blast radius | a container | your machine |

The two rows that decide it are **"reads the repo you are in"** and **"the task leaves the
building"**. If neither matters, host it — hosting is less work and it stays up. Build
local when the agent's value comes from touching the real working tree, or when the
material must not be transmitted at all.

The usual right answer is both, sharing one brain: the same router, the same rules, the
same contracts, with different hands.

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
read   inside the working directory, minus the secret deny-list.   never prompts
net    outbound GET.                                               never prompts
write  create or modify a file in the working directory.           prompts by default
exec   run a command on this machine.                              prompts by default
```

`read` and `net` never prompt because they observe rather than change. Prompting on them
trains the user to hit `y` without reading, and that habit is what eventually approves the
`rm -rf`.

Three postures, and the third is where the design earns its keep:

- **ask** (default) — a human decides each write and each command, with the command
  printed in full first.
- **auto** — approve ordinary work; still hold what cannot be undone.
- **never** — read-only. The agent can look and reason and produce a plan, and cannot
  touch anything. This is the posture for a first run in an unfamiliar repository.

### The irreversibility hold

Autonomy and reversibility are different axes, and conflating them is the common bug. Even
under full autonomy, hold the actions no re-run can walk back:

```
rm -rf …          git push          git reset --hard        npm publish
sudo …            vercel --prod     DROP TABLE              curl … | sh
mkfs / dd         shutdown          chmod 777               gh release create
```

`npm test` under `auto` should not prompt. `git push` under `auto` should. Releasing the
second class needs a separate, explicit, logged flag — and the fact that it was used
belongs in the run's audit trail, because "the agent pushed" and "the agent was allowed to
push without asking" are different post-mortems.

One trap worth stating because it is easy to get wrong: a pattern like
`\b(deploy|--prod)\b` never matches `vercel --prod`. The character before the dash is a
space, and space-to-dash is not a word boundary. Anchor flag-shaped alternatives without
the leading boundary and test every entry in the list against a real command line.

## 4. The two boundaries that are not negotiable

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
artifact you want to discover this way.

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

## 10. Connectors, and when to stop adding them

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

## 11. The checklist

Before calling a local runtime finished:

- [ ] Every tool declares a capability; the gate reads the capability, not the name.
- [ ] Read-only is the default. Acting is a flag, and autonomy is a second flag.
- [ ] Irreversible actions are held even under autonomy; the override is separate and logged.
- [ ] The jail resolves symlinks; a link out of the working directory is refused.
- [ ] The secret deny-list is unconditional, and observations are redacted on the way out.
- [ ] No TTY means `ask` denies rather than hangs.
- [ ] The model call is injectable, and the loop is tested with no key.
- [ ] Verification runs the artifact in a throwaway directory; a non-zero exit overrules the judge.
- [ ] Both a step wall and a money wall; unknown models bill at the highest rate.
- [ ] Every permission decision lands in the run's journal.
- [ ] The child process dies with its parent — verified by killing the parent, not by reading the code.
