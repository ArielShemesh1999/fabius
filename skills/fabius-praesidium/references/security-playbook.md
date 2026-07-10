# Fabius Praesidium — security playbook

The operational depth for `fabius-praesidium`. The skill is the contract (threat-model → audit → harden → prove); this file is how you actually run each step — full templates, every variant, worked examples. The **deep** hardening + audit library (HTTP headers, auth patterns, per-type validation cookbook, output-encoding by sink, supply-chain commands, per-stack quick-harden) lives in the companion [hardening-guides.md](hardening-guides.md), indexed by [CORPUS.md](../../../CORPUS.md) and paged in **one slice at a time** (routing-policy R9 · M9). **Defensive only — harden / detect / audit / test. Scout wide, strike narrow.**

---

## 1. STRIDE per trust boundary — the template

You can't harden a surface you haven't mapped. First name the three things, then walk STRIDE per boundary. Each cell is a question — *can they?* An empty cell is an **un-checked** threat, not a safe one.

**Scope it first (fill before the grid):**
```
Assets:           <data · money · identity · availability — what's worth stealing/breaking>
Trust boundaries: <every edge data crosses a privilege line: client→server, svc→svc, user→admin, untrusted→trusted>
Adversary:        <who · what access they start with · which asset they want>
```

**The grid** — one row per boundary, one mitigation note per threat:

| Boundary | Spoofing | Tampering | Repudiation | Info-disclosure | DoS | Elevation |
|---|---|---|---|---|---|---|
| client → server | | | | | | |
| service → service | | | | | | |
| user → admin | | | | | | |
| untrusted file/input → parser | | | | | | |

**Worked example row (filled — copy this depth):**

| Boundary | Spoofing | Tampering | Repudiation | Info-disclosure | DoS | Elevation |
|---|---|---|---|---|---|---|
| client → server (`POST /api/transfer`) | session cookie `HttpOnly`+`Secure`+`SameSite`; no auth-via-header-only ✅ | amount/recipient signed server-side, never trusted from body ✅ | audit log w/ user-id + request-id, append-only ✅ | error returns generic; no balance leak on 403 ✅ | rate-limit per-account 5/min; body-size cap ✅ | recipient + amount re-authorized against caller's own account — **no IDOR** ✅ |

Each filled cell ends in *mitigation present?* → ✅ yes / ❌ no / N-A. The **❌** rows are the work list, ranked by §5 severity. STRIDE letters: **S**poofing · **T**ampering · **R**epudiation · **I**nfo-disclosure · **D**enial-of-service · **E**levation-of-privilege.

---

## 2. The OWASP pass — runnable checklist (each item says HOW to verify)

Run this over the top risks. Each line is a thing to **verify present**, with the concrete check — not a name to nod at. Tick only after you've looked.

```
[ ] injection           HOW: grep for string-built SQL/shell/LDAP and eval()/exec() on input;
                             confirm every query uses parameterized bindings / prepared statements.
                             → encoding-by-sink + parameterization recipes: hardening-guides.md §5
[ ] access control      HOW: pick 3 object-by-id endpoints; call each as a DIFFERENT user's id —
                             must 403, not 200 (IDOR test). Confirm authZ is server-side on EVERY
                             route, deny-by-default, not just hidden in the UI. → guides §2
[ ] authentication      HOW: log in twice — session id must rotate on login + on privilege change;
                             confirm logout/expiry invalidates server-side; no creds/tokens in URLs
                             or logs; login is rate-limited + lockout/backoff. → guides §2
[ ] ssrf / unsafe fetch HOW: trace every outbound request built from user input; confirm an
                             allowlist of hosts/schemes and that link-local/metadata IPs
                             (169.254.169.254, 127.0.0.0/8, ::1, RFC-1918) are blocked. → guides §7
[ ] secrets             HOW: run the §3 secrets audit — git history + built bundle + logs.
                             Any hit = leaked = rotate. → guides §6
[ ] deserialization     HOW: confirm no untrusted bytes hit a native deserializer (pickle, Java
                             readObject, PHP unserialize, YAML unsafe_load); use data-only parsers
                             (JSON.parse, yaml.safe_load) + schema-validate after. → guides §3
[ ] dependencies        HOW: run the per-ecosystem audit (npm audit / pip-audit / cargo audit),
                             confirm a committed lockfile, triage highs/criticals. → guides §6
[ ] misconfiguration    HOW: confirm debug/stack-traces OFF in prod; security headers present
                             (CSP, HSTS, X-Content-Type, Referrer-Policy, Permissions-Policy —
                             curl -I the prod URL); defaults changed; dir-listing off. → guides §1
[ ] xss / output        HOW: inject a probe string (e.g. "><svg onload=...) into each rendered
                             field IN A TEST; confirm it lands inert (encoded for its sink), not
                             executed. Context-aware encoding per sink. → guides §5
[ ] logging/monitoring  HOW: confirm auth failures, authZ denials, and input-validation rejects
                             are logged WITH request-id and WITHOUT the secret/PII payload itself.
[ ] file upload         HOW: confirm type sniffed from content not extension, size-capped, stored
                             off web-root with a generated name, never executed. → guides §3
```

The OWASP pass is the audit; STRIDE is what scoped the audit. Run STRIDE to find *which* boundaries matter, then run this list against each.

---

## 3. Secrets & least-privilege hygiene — fast audit

```
[ ] grep history + built bundle + logs for keys/tokens/passwords  → ANY hit = leaked = rotate now
[ ] all secrets via env + a secrets manager, referenced never inlined  (no committed .env)
[ ] no secret reaches the client bundle (server-only env; check the shipped JS)
[ ] every token scoped to least privilege — a read job gets a read token, a service only what it calls
[ ] default-deny permissions/IAM, add only as a use proves the need  (same contract as `fabius-cohors` agents)
[ ] rotation path exists — a leaked secret can be revoked + reissued without a redeploy of trust
```

**The last hard boundary lives *below* the model — never in a prompt.** Once an agent can touch tools, a rule that says "don't exfiltrate" is *vibes-based egress control*: the model is not a control plane, and one bad outbound call undoes a hundred clever tool rules. Put the real boundary where the model can't argue past it — an outbound **allowlist** (hosts/schemes), network/DNS egress filtering, a filesystem sandbox, a scoped token that only reaches what the job calls. A denylist of "bad" commands is not that boundary: the shell is unbounded, so gate by **allowlist, deny-by-default**. Every capability handed to an agent — repo write, a shell, an external send — is a privilege grant priced at its **worst case, not its average** (`fabius-cohors` owns the same least-privilege rule at the agent-tool layer).

Concrete grep starting points (defensive scan of your *own* repo):
```bash
git log -p | grep -nEi '(api[_-]?key|secret|token|password|bearer|AKIA[0-9A-Z]{16})'
grep -rEi 'AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|sk-[A-Za-z0-9]{20,}' ./dist ./build 2>/dev/null
```
A secret in git history is a leaked secret even after you delete the file — rotate, then scrub history. Full env-vs-manager and IAM-scoping recipes: [hardening-guides.md](hardening-guides.md) §6.

---

## 4. Secure-by-default review checklist

The review pass that catches the common holes. Each is *verify present / prove closed*:

```
[ ] Validate at the trust boundary   — type · range · length · format · allowlist (the WHAT for
                                        parcus's never-trim "validate input"). → cookbook: guides §4
[ ] Authenticate, THEN authorize      — two separate gates; fail CLOSED (error/ambiguity = deny)
[ ] Parameterize and encode           — input parameterized into queries; output encoded for its sink
[ ] Least surface                     — disable unused: close the port, drop the endpoint, remove the flag
[ ] No secret in the artifact         — §3 holds
[ ] Safe-by-default config            — debug off, headers on, errors generic, dir-listing off  → guides §1
[ ] Idempotent + replay-safe          — state-changing requests carry a nonce/idempotency key where it matters
```

`fabius-parcus` owns the *never-trim* floor (don't cut validation/auth/security to save effort); praesidium names *what* to check and *proves* it closed. Don't add a control no adversary model justifies (parcus: *does it need to exist?*) — but never drop below the floor.

---

## 5. Severity rubric — what each level means

Severity sets order *and* the ship decision. Rate by **impact × reachability** (can a real adversary, from their starting access, actually reach it?).

| Severity | Meaning | Ship rule |
|---|---|---|
| **Critical** | Remote, unauthenticated path to full compromise / mass data loss / money movement — or any of those at an exposed trust boundary. RCE, auth bypass, secret leak in prod, IDOR exposing all records. | **Ship-stopper.** Block release; escalate; do not auto-merge. Fix before anything else. |
| **High** | Real compromise but gated — needs auth, a specific role, a non-default config, or user interaction. Stored XSS, privilege escalation within a tenant, SSRF to internal services. | Fix before this release ships externally; no new feature stacks on top until closed. |
| **Medium** | Limited blast radius or hard preconditions — info-disclosure of non-sensitive data, missing hardening header, weak rate-limit, verbose errors. | Schedule + track; fix this cycle; don't let it rot into a chain. |
| **Low** | Defense-in-depth gap, no direct exploit path — missing belt-and-braces header, minor config drift, cosmetic. | Note it; batch-fix; never let it drown the real findings. |

**Ship-stopper rule:** a **critical** anywhere, OR a **high** at a trust boundary that crosses a privilege line, blocks the ship. Everything else is scheduled, not blocking. When uncertain between two levels, rate up and say why — under-rating a reachable hole is the expensive mistake.

---

## 6. The finding format — severity → fix → proof

A finding isn't closed until it's **proven** closed. Every issue ships as the triple, never a vague "be careful". Order findings by severity; the load-bearing ones first (don't bury the critical under lint nits).

```
## [SEVERITY] <vulnerability> @ <file:line / endpoint / boundary>
- Risk:   <what an attacker gains, from what starting access>
- Fix:    <the specific change — code/config diff, not advice>
- Proof:  <a regression check that FAILS before the fix and PASSES after>
```

**Worked example finding:**

```
## [CRITICAL] IDOR on GET /api/orders/:id @ routes/orders.js:42
- Risk:   Any authenticated user fetches ANY order by guessing/iterating ids —
          full PII + payment-meta disclosure across all tenants. Reachable with a
          normal logged-in account, no special role.
- Fix:    Scope the query to the caller: load the order WHERE id = :id
          AND owner_id = req.user.id; return 404 (not 403) on miss to avoid an
          existence oracle. routes/orders.js:42.
- Proof:  Regression test — as user A, request user B's order id; assert 404.
          Fails on old code (returns 200 + body), passes after the owner-scope.
          A malicious INPUT (B's id) inside a defensive test is fine; it proves
          the hole closed, it is not an exploit.
```

The proof is the line that separates praesidium from a checklist. Prove-before-done is `fabius-disciplina`'s discipline; praesidium supplies the security-specific evidence — a test that encodes the bad input and asserts it now lands inert / denied.

---

## 7. Routing — when to page the deep library

| You're doing… | Page in (one slice) |
|---|---|
| Setting / verifying HTTP security headers | [hardening-guides.md](hardening-guides.md) §1 |
| Auth, session, password storage, MFA design | §2 |
| Hardening file upload / deserialization / parsers | §3 |
| Per-type input validation (string/number/email/url/id/file) | §4 |
| Output encoding by sink (HTML/attr/JS/URL/SQL) | §5 |
| Dependency + supply-chain audit (npm/pip/cargo) | §6 |
| Secrets + cloud IAM least-privilege | §6–7 |
| Quick-hardening a Node/Python/static/Worker stack | §8 |

Query the index for the **one** guide the task needs and page it; never load the library wholesale (`fabius-parcus`; routing-policy R9 · M9). Everything stays defensive — guides to *harden and detect*, never to attack. The never-trim floor is `fabius-parcus`; the test discipline is `fabius-disciplina`; agent least-privilege is `fabius-cohors`.
