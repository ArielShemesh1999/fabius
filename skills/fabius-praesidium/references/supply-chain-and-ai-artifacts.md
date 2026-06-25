# Fabius Praesidium — supply chain and the third-party AI-artifact surface

The on-demand depth for `fabius-praesidium`'s supply-chain leg — the OWASP "vulnerable dependencies" pass made first-class for the AI-tooling era. This is the surface fabius itself lives on. **Defensive only — audit before adopt, pin, sandbox, least-privilege. Scout wide, strike narrow.**

This composes with the STRIDE/OWASP playbook (`references/security-playbook.md` §5–6) — that file pins and audits *package* dependencies; this one extends the same exec/data/net/creds audit to the new artifacts that **run code and hold your tokens**: skills, plugins, agents, MCP servers, and the CI that builds them.

---

## 1. The core reframe — installing an AI artifact is running a stranger's code with your creds

A package you `import` is data until you call it. A **skill, plugin, agent, or MCP server is different in kind**: adopting one grants it execution and, usually, your credentials. Installing it *is* running someone else's code inside your trust boundary — with your tokens, your filesystem, your network.

So the decision rule is not "is this package popular?" It is the same exec/data/net/creds audit praesidium runs on any code, applied **before adoption, every time:**

- **exec** — what does it run? Shell-outs, `eval`, post-install hooks, spawned subprocesses, bundled binaries.
- **data** — what does it read and write? Files, env, history, the clipboard, other tools' state.
- **net** — what does it send, and where? Any outbound call to a host you didn't expect is the finding.
- **creds** — what tokens does it touch? Which scopes does it actually need vs. which it requests.

Documented in the wild (ARGAZ-catalogued, point-in-time early 2026): hundreds of mapped malicious skills and dozens of relevant CVEs across the AI-tooling ecosystem. The threat is not hypothetical; it is the fastest-growing under-defended surface.

## 2. The blind window — "auto-update from upstream" is a standing supply-chain risk

Some plugin registries auto-morph a third-party plugin to a new upstream SHA with **no human review** between versions. You audited SHA `A`; the registry silently advances you to SHA `B` that you never saw. That gap — code change you trust by inertia, not by inspection — is a **blind window**, and it is RCE-by-subscription.

The rule:

- **Pin the exact SHA / version**, never a moving tag (`@latest`, `main`, a floating major).
- **Treat auto-update on an untrusted artifact as a standing risk**, not a convenience. Disable it, or gate each bump on a re-audit of the diff.
- **Re-verify on every bump.** A new SHA is new code; run §1 again before it runs in your boundary.

(Pin-and-lockfile is the same contract as the playbook's package supply chain — extended here to artifacts that update *outside* the lockfile.)

## 3. The adoption gate — audit → pin → sandbox → least-privilege

A four-step gate any skill/plugin/MCP/dependency clears **before** it touches real work:

1. **Audit** — run §1's exec/data/net/creds read. Read what it execs, trace what it sends, list the creds it touches. If you can't tell, that *is* the finding — opacity is disqualifying for something that runs with your tokens.
2. **Pin** — lock the exact SHA (§2). No moving targets.
3. **Sandbox** — run it where it can't reach what it doesn't need: a container, a scratch repo, network egress restricted, filesystem scoped. First run is the riskiest; let it run somewhere it can't hurt you.
4. **Least-privilege the creds** — default-deny, then grant only the scopes the audit proved it uses. A read-only artifact gets a read-only token. (Same least-privilege contract as the playbook §3 and `fabius-cohors` for agents.)

Fail any step → don't adopt, or quarantine until it passes. Severity and the fix→proof triple are the playbook's (`security-playbook.md` §5–6); a malicious artifact in your boundary is **critical** by default.

## 4. MCP servers are a privileged trust grant

An MCP server is not a library — it is a process you hand tools and tokens to, that the model then drives. Audit it as the most privileged thing in the chain:

- **Enumerate its tools** — every tool is a capability the model can be talked into invoking. Unbounded `exec`/`write_file`/`fetch` tools are the surface.
- **Scope its credentials** — the server gets the minimum token, not your full session. Default-deny.
- **Pin and sandbox it** like any other artifact (§2–3); its updates carry the same blind window.
- **The diff that reaches the model is untrusted input** — an MCP tool returning attacker-controlled text can carry prompt injection (cross-link: the AI-review prompt-injection caveat, `references/ai-review.md`). Agent-side tool/credential scoping is owned by `fabius-cohors` — route the *agent's* permission model there; this layer owns auditing the *server artifact* you install.

## 5. Broaden the audit to where real bugs actually hide

Package-CVE scanning is table stakes. The high-value findings (trailofbits-class breadth) sit in the surrounding machinery — audit these as part of the supply chain, not after it:

- **Supply-chain integrity** — typosquats, dependency confusion (a public package shadowing your private one), unsigned/unverified artifacts, compromised maintainer accounts. Verify provenance for anything you didn't write.
- **CI / GitHub Actions hardening** — a poisoned workflow is **RCE on your repo and a path to your secrets**. Pin actions to a full commit SHA (not `@v4`), set least-privilege `permissions:` on `GITHUB_TOKEN` (default-deny, read-only baseline), never run untrusted code in a `pull_request_target` context, and don't expose secrets to fork PRs.
- **Timing side-channels** — non-constant-time comparison of secrets/tokens/HMACs leaks them a bit at a time. Use constant-time compare for any secret equality check.
- **Language-specific footguns** — C/C++ memory safety (UAF, overflow), unsafe deserialization (pickle, Java `readObject`, YAML unsafe-load), unchecked FFI boundaries. These don't show in a dependency audit; they show in a read of the code.

## 6. Make it repeatable in CI — rule packs, not one-off reads

A one-time audit rots on the next bump (§2). Encode the checks so they re-run on every change:

- **Semgrep-style rule packs** make the §5 classes repeatable — supply-chain integrity, injection, hardcoded secrets, dangerous sinks — as a CI gate that fails the build, not a memory you have to re-perform.
- **Per-ecosystem package audit in CI** — `npm audit` / `pip-audit` / `cargo audit` on every PR, acting on highs/criticals (playbook §6).
- **Action-pinning lint** — assert workflows pin SHAs and scope `permissions:`.

Tool names and versions here are a **point-in-time snapshot (early 2026), not law** — Semgrep, the per-ecosystem auditors, the registries' auto-update behavior all move. Encode the decision (audit → pin → sandbox → least-privilege → re-verify on bump); re-verify the tool and the version number when you run it.

## 7. Credit, not bundle

These are capabilities fabius **applies**, drawn from named ecosystem tools — Semgrep's rule packs, the per-ecosystem auditors, trailofbits-class breadth in what to look at. fabius bundles **no runtime**: it carries the decision rules and the audit method, not the scanners. The optional live tier is in `ARCHITECTURE.md`. Present every one of these as "how to do X well, crediting tool Y" — never as a fabius-shipped binary.

---

## When NOT to over-do it

- **The threat-model sets the depth, not paranoia** (`fabius-parcus`: does this control need to exist?). A first-party internal package on a pinned lockfile doesn't need the full §3 sandbox dance; an unknown third-party MCP server that wants your prod token does. Scale the gate to the trust grant.
- **Never drop below the never-trim floor** to save effort — auditing what executes with your creds is floor, not polish (`fabius-parcus`).
- **Don't bury the load-bearing finding** — a single unaudited artifact with full credential access outranks fifty stale-transitive-dependency notes. Report the standing supply-chain risk first.

---

See the owning skill (`../SKILL.md`) §5 for the supply-chain contract, `references/security-playbook.md` §6 for the package-audit commands, `references/ai-review.md` for the prompt-injection caveat on artifact-returned text, and [CORPUS.md](../../../CORPUS.md) for where this library sits in the index. Cross-links: `fabius-scientia` routes third-party science-skill risk here; `fabius-cohors` routes agent tool/credential scoping here. On-chain audit → `fabius-catena`. Defensive only — audit, pin, sandbox, least-privilege, never weaponize.
