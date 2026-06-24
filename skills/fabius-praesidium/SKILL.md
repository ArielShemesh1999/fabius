---
name: fabius-praesidium
description: >
  fabius's defensive-security layer — how to find and fix what an attacker would exploit, before
  they do: threat-model first (STRIDE per trust boundary), run the OWASP pass, enforce secrets and
  least-privilege hygiene, review secure-by-default, check the supply chain, and ship every finding
  with a severity, a fix, and a regression test. Use when building or reviewing anything that
  touches auth, user input, secrets, payments, file upload, external requests, or dependencies — or
  when the user says "is this secure?", "threat-model this", "audit this", "harden this", "review
  for vulnerabilities", or "security review". Defensive only — it hardens, never weaponizes. The
  STRIDE template, the OWASP checklist, and the finding format live in references/security-playbook.md;
  the hardening guides and audit library live in references/hardening-guides.md, bundled and indexed by CORPUS.md, paged in on demand.
---
<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->

# Fabius Praesidium — find it and fix it before someone finds it for you

*Praesidium* — the garrison, the protecting force. This layer is the standing guard on the work: it scouts the whole attack surface and strikes the specific holes. **Scope is strictly defensive** — praesidium threat-models, audits, hardens, and fixes. It does **not** write exploits, malware, intrusion tooling, or anything whose purpose is to attack a system it doesn't own. `fabius-parcus` owns the *never-trim* security floor (don't cut validation/security); this layer owns the *active* work of modelling the threat and proving the hole is closed.

## 1. Threat-model before you secure (STRIDE)

You can't harden a surface you haven't mapped. Before touching code, name the pieces:

- **Assets** — what's worth stealing or breaking (data, money, identity, availability).
- **Trust boundaries** — every edge where data crosses a privilege line (client→server, service→service, user→admin, untrusted→trusted).
- **Adversary** — who, with what access, wants which asset.

Then walk **STRIDE** per boundary: **S**poofing · **T**ampering · **R**epudiation · **I**nfo-disclosure · **D**enial-of-service · **E**levation-of-privilege. Each box is a question: *can they?* The unanswered boxes are your work list.

## 2. The OWASP pass — audit, don't assume

Run the concrete checklist over the top risks. Each is a thing to *verify present*, not hope for:

- **Injection** — every query parameterized; no string-built SQL/shell/LDAP; no `eval` on input.
- **Broken access control** — authorize *every* request server-side (an authenticated user is not an authorized one); deny by default; no IDOR (object IDs checked against the caller).
- **Broken authentication** — sessions rotate, expire, and invalidate; no credentials in URLs; rate-limit the login.
- **SSRF / unsafe fetch** — allowlist outbound targets; never fetch a user-supplied URL raw.
- **Secrets exposure** — none in code, logs, history, or client bundles (§4).
- **Insecure deserialization / unsafe parsing** — don't deserialize untrusted data into live objects.
- **Vulnerable dependencies** — audited and pinned (§6).
- **Security misconfiguration** — defaults changed, debug off in prod, headers set (CSP, HSTS), errors don't leak stack traces.
- **XSS / output handling** — encode on output, context-aware; sanitize rich input.
- **Logging & monitoring gaps** — security events are logged (without logging the secrets themselves).

## 3. Secrets & least privilege

- **No secret in the artifact** — not in source, not in a log line, not in a committed `.env`, not in client-side code. A secret in git history is a leaked secret; rotate it.
- **A manager, not a constant** — env + a secrets manager; reference, never inline.
- **Scope every token to the minimum** — a read job gets a read token; a service gets only the permissions it uses. Default-deny, then add. (Same least-privilege contract as `fabius-cohors` for agents.)

## 4. Secure-by-default review

The review checklist that catches the common holes:

- **Validate at the trust boundary** — the specific check `fabius-parcus`'s never-trim list demands; praesidium names *what* to validate (type, range, length, format, allowlist).
- **Authenticate, then authorize** — two separate gates. Fail **closed**: on error or ambiguity, deny.
- **Parameterize and encode** — input parameterized into queries, output encoded for its sink.
- **Least surface** — disable what you don't use; close the port, drop the endpoint, remove the flag.

## 5. Supply chain

Pin dependencies with a lockfile; audit them (`npm audit` / `pip-audit` / `cargo audit`) and act on highs; verify provenance for anything you didn't write; and **minimize vendor count** — every dependency and every external service is attack surface and trust you've delegated. Fewer, audited, pinned (this is the same minimize-dependencies principle the rest of fabius runs on).

## 6. The fix contract — a finding isn't closed until it's proven closed

Every finding ships as a triple, never a vague warning:

```
[severity: critical/high/medium/low]  the concrete vulnerability + where
→ fix:    the specific remediation (the change, not "be careful")
→ proof:  a regression test / check that fails before the fix and passes after
```

Severity sets order: critical/high first, and a critical at a trust boundary stops the ship. (Prove-before-done is `fabius-disciplina`; praesidium gives it the security-specific evidence.)

## When NOT to over-secure

- **The threat-model sets the bar, not paranoia.** Don't add crypto, controls, or ceremony a real adversary model doesn't justify (`fabius-parcus`: does this control need to exist?) — but **never** drop below the never-trim floor to save effort.
- **Don't roll your own crypto/auth.** Reach for the vetted library or platform primitive (parcus ladder); hand-rolled security is a vulnerability with extra steps.
- **Don't bury the real risk in a hundred lint nits.** Report the load-bearing findings first; note the cosmetic ones, don't drown the signal.

## References

- STRIDE-per-boundary template, the OWASP checklist as a runnable list, the secrets-hygiene checklist, and the severity→fix→proof format → `references/security-playbook.md`.
- Hardening guides and the audit library → `references/hardening-guides.md`, bundled and indexed by [CORPUS.md](../../CORPUS.md); page in the one slice the task needs (R9 · M9). Defensive only — guides to harden and detect, never to attack.

Boundary: defensive only — no offensive tooling, ever. The never-trim security floor is `fabius-parcus`; the test discipline is `fabius-disciplina`; agent least-privilege is `fabius-cohors`. This layer owns the threat model and the audit. The user's instruction wins on everything except cutting a guardrail; `stop fabius` drops the stance.
