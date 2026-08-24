# Security policy

## Reporting a vulnerability

Use **[private vulnerability reporting](https://github.com/shear559/fabius/security/advisories/new)** — Security → Report a vulnerability. It opens a channel visible only to you and the maintainer, so nothing is disclosed while a fix is being made.

Please do not open a public issue for a security problem.

A first response should arrive within 72 hours. If a report is accepted, a fix and an advisory are published together; if it is declined, you get the reasoning rather than silence.

## What is in scope

fabius is a set of skill contracts, a plugin manifest and a zero-dependency local runner (`runtime/`) that hands the same sealed rules to a model through the user's own API key. The interesting surface is:

- **The runtime's gates.** `--dangerously-approve-everything`, the ask posture, and the deny-list around the resolved config path. A path that releases an irreversible command without a prompt is a real finding — one such path was fixed in v2.3.1.
- **Secret redaction.** `redact()` is meant to cover every secret the runtime holds, the nostr identity key included. A secret that reaches a log or an artifact is in scope.
- **The provenance apparatus.** `provenance/verify.sh`, the seal manifest and the signed tag. A way to make `verify.sh` report a valid seal over content that was not sealed is the highest-severity class of bug in this repository.
- **Skill contracts that instruct an agent to take an unsafe action.** The skills are executable instructions; treat them as code.

## What is not in scope

- The behaviour of the underlying models. fabius is a rule set loaded above whatever model the user already runs — Claude, GPT, Gemini or any other; the model's outputs are not this project's attack surface.
- Anything requiring an already-compromised machine, since the runner holds the user's own API keys by design.
- The fact that a public repository can be cloned. [PROVENANCE.md](PROVENANCE.md) states this plainly: the design defends provenance and enforcement, not access.

## Supported versions

The current sealed release, and that release only. Each is tagged `vX.Y.Z-sealed` with an Ed25519 signature and an OpenTimestamps proof anchoring it into Bitcoin; `bash provenance/verify.sh` reports the live state of every mechanism, including the ones that are legitimately pending.
