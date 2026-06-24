# Fabius Praesidium — security playbook (entry)

The on-demand depth for `fabius-praesidium`. Lean entry doc; the hardening guides and audit library live in the **fabius-praesidium** library of the fabius corpus ([CORPUS.md](../../../CORPUS.md)), paged in on demand. **Defensive only. Scout wide, strike narrow.**

---

## STRIDE per trust boundary (the template)

For each boundary, fill the row. An empty cell is an un-checked threat, not a safe one.

| Boundary | Spoofing | Tampering | Repudiation | Info-disclosure | DoS | Elevation |
|---|---|---|---|---|---|---|
| client → server | | | | | | |
| service → service | | | | | | |
| user → admin | | | | | | |

For each filled threat: *mitigation present?* → yes / no / N-A. The "no" rows are the work list, ranked by §severity.

## OWASP pass — runnable checklist

```
[ ] injection            — queries parameterized; no eval on input; no shell-from-string
[ ] access control       — every request authorized server-side; deny by default; no IDOR
[ ] authentication       — sessions rotate/expire/invalidate; login rate-limited; no creds in URLs
[ ] ssrf / unsafe fetch  — outbound allowlisted; no raw user-supplied URL fetch
[ ] secrets              — none in code/logs/history/client bundle; manager + scoped tokens
[ ] deserialization      — no untrusted data into live objects; safe parsers only
[ ] dependencies         — lockfile pinned; audit clean (or highs triaged); provenance verified
[ ] misconfiguration     — debug off in prod; security headers set; errors don't leak traces
[ ] xss / output         — context-aware output encoding; rich input sanitized
[ ] logging/monitoring   — security events logged; secrets never logged
```

## Secrets hygiene — fast audit

```
[ ] grep history + bundle for keys/tokens/passwords   → any hit = leaked = rotate now
[ ] all secrets via env + manager, referenced not inlined
[ ] every token scoped to least privilege (read job = read token)
[ ] default-deny permissions, added only as used
```

## The finding format (every issue, no exceptions)

```
## [SEVERITY] <vulnerability> @ <file:line / endpoint / boundary>
- Risk:   <what an attacker gains>
- Fix:    <the specific change — code/config, not advice>
- Proof:  <regression check that fails before, passes after>
```

Order by severity. A **critical** at a trust boundary is a ship-stopper (escalate, don't auto-merge).

## The hardening & audit library (corpus — indexed, not bundled)

The deep library — hardening guides and audit checklists (auth patterns, header configs, framework-specific guides, the cyber-skills corpus) — lives in the **fabius-praesidium** library of the fabius corpus ([CORPUS.md](../../../CORPUS.md)), not bundled here. Query the index for the **one** guide the task needs and page it in; never load the library wholesale (`fabius-parcus`; routing-policy R9 · M9). Everything stays defensive — guides to *harden and detect*, never to attack.
