# Fabius Praesidium — hardening & audit guides

The deep, bundled library for `fabius-praesidium`: HTTP headers, auth & session patterns, input-validation cookbook, output-encoding by sink, dependency/supply-chain audits, secrets & cloud least-privilege, and per-stack quick-harden checklists. The [security-playbook.md](security-playbook.md) is the operating procedure (STRIDE → OWASP pass → finding format); this file is the *how-to-harden* depth it routes into. Page **one §** at a time (routing-policy R9 · M9). **Defensive only — every item is "verify present / harden / prove closed", never an attack.** Copy the skeletons; fill the `<…>`.

---

## §1 — HTTP security headers

Set these on every HTML response (and the API where noted). Verify with `curl -sI https://<host> | grep -i <header>`. Defaults below are safe starting points — tighten, don't loosen.

| Header | Recommended value | Why |
|---|---|---|
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'` | The XSS backstop. No inline script (`'self'` only) — externalize scripts. Add per-host sources only as proven needed. |
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` | Forces HTTPS for 2y; kills SSL-strip. Only on HTTPS responses. Preload-list it once stable. |
| `X-Content-Type-Options` | `nosniff` | Stops MIME-sniffing a response into executable script. |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Don't leak full URLs (with tokens/ids) to third parties. |
| `Permissions-Policy` | `geolocation=(), camera=(), microphone=(), payment=()` | Default-deny powerful features; enable only what the page uses. |
| `X-Frame-Options` | `DENY` | Clickjacking defense (legacy backstop for `frame-ancestors`). |
| `Cross-Origin-Opener-Policy` | `same-origin` | Process-isolates the page; closes XS-leaks. |
| `Cross-Origin-Resource-Policy` | `same-origin` | Blocks cross-origin embedding of your resources. |
| `Cache-Control` (auth'd responses) | `no-store` | Keep private/auth'd bodies out of shared caches. |

**CSP rollout (don't break the site):** ship `Content-Security-Policy-Report-Only` first with a `report-uri`/`report-to`, watch the violations, fix sources, *then* flip to enforcing. Never reach for `'unsafe-inline'`/`'unsafe-eval'` to "make it work" — externalize the script or use a per-response nonce: `script-src 'self' 'nonce-<random-per-response>'`.

```
[ ] all 5 core headers present on the prod HTML response (curl -I confirms)
[ ] CSP has no 'unsafe-inline' / 'unsafe-eval' in script-src
[ ] HSTS only on HTTPS, max-age >= 6 months, includeSubDomains
[ ] auth'd JSON responses send Cache-Control: no-store
```

---

## §2 — Auth & session patterns (defensive)

**Login flow (verify each gate present):**
```
[ ] identify  → constant-time credential compare; SAME generic error for bad-user vs bad-pass
                (no username-enumeration oracle)
[ ] throttle  → per-account + per-IP rate-limit; exponential backoff / lockout after N fails
[ ] verify    → password checked against a vetted KDF hash (below); MFA second factor if enabled
[ ] issue     → NEW session id minted on successful login (never reuse the pre-login one)
[ ] respond   → set cookie HttpOnly; Secure; SameSite=Lax (or Strict for pure same-site apps)
```

**Session lifecycle:**
```
[ ] id is cryptographically-random, >=128 bits, server-side opaque (not user data)
[ ] ROTATE the id on login and on any privilege change (prevents fixation)
[ ] absolute expiry (e.g. 12–24h) AND idle expiry (e.g. 30m); both enforced server-side
[ ] logout invalidates server-side, not just clears the cookie
[ ] store a revocation handle so a compromised session can be killed without a redeploy
```

**Password storage — vetted KDF, never a bare hash:**

| KDF | Use when | Notes |
|---|---|---|
| **Argon2id** | new systems (preferred) | memory-hard; tune memory/iterations/parallelism to your hardware budget |
| **scrypt** | Argon2 unavailable | also memory-hard; good fallback |
| **bcrypt** | legacy/widely-available | cost factor ≥ 12; cap input length (pre-hash long inputs with SHA-256 to dodge the 72-byte truncation) |

Never: MD5/SHA-1/SHA-256 *alone*, no salt, "encryption" of passwords, or a homegrown scheme. The library salts per-user automatically — use its verify function (constant-time) for the compare. Don't roll your own crypto (`fabius-parcus` ladder: reach for the vetted primitive).

**MFA / tokens (defensive notes):**
- Prefer WebAuthn/passkeys or TOTP (RFC-6238) over SMS. Verify TOTP within a small time-window; reject reuse of a consumed code.
- Password-reset tokens: single-use, short-lived (≤ 30m), random ≥ 128 bits, invalidated on use and on a new request.
- API tokens: scope to least privilege (§6), expirable, revocable, never in a URL/query-string (logs capture those).
- CSRF: state-changing requests on cookie-auth need a same-site cookie **and** a per-session CSRF token (double-submit or synchronizer) — verified server-side, fail-closed.

---

## §3 — Hardening parsers, deserialization & file upload

**Deserialization — data-only parsers, then schema-validate:**

| Language | Avoid on untrusted input | Use instead |
|---|---|---|
| Python | `pickle.loads`, `yaml.load`, `eval` | `json.loads`, `yaml.safe_load` + a schema check |
| JS/Node | `eval`, `Function()`, `vm` on input | `JSON.parse` + a validator (zod/ajv) |
| Java | native `readObject` | JSON binding with type-allowlist; disable polymorphic typing |
| PHP | `unserialize` on input | `json_decode` |

Rule: never let untrusted bytes become a *live object graph*. Parse to plain data, then validate against a schema (§4), then build your objects.

**File upload (verify present):**
```
[ ] type from CONTENT (magic-byte sniff), not the filename extension or client MIME
[ ] allowlist of accepted types; reject everything else
[ ] hard size cap (reject early, stream don't buffer-all)
[ ] store OFF web-root, with a server-generated random name; never the user's filename
[ ] never serve uploads from a path that can execute (no .php/.jsp/.cgi exec context)
[ ] images: re-encode through a trusted library to strip embedded payloads/metadata
[ ] set Content-Disposition: attachment + X-Content-Type-Options: nosniff when serving back
```

---

## §4 — Input-validation cookbook (per type)

Validate **at the trust boundary**: type → range → length → format → allowlist. Reject, don't sanitize-and-hope, when the value should be from a closed set. (This is the *what* behind `fabius-parcus`'s never-trim "validate input".)

| Type | Validate | Skeleton |
|---|---|---|
| **string** | length bounds; charset/format; reject control chars; normalize Unicode (NFC) before compare | `assert 1 <= len(s) <= MAX and re.fullmatch(r'[\w .\-]+', s)` |
| **number** | is-a-number, integer-if-int, finite, range; parse don't coerce strings silently | `n = int(raw); assert MIN <= n <= MAX` (reject NaN/Inf/overflow) |
| **email** | single `@`, length ≤ 254, RFC-ish pattern — then **verify by sending**, don't over-trust regex | `re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', e) and len(e) <= 254` |
| **url** | scheme allowlist (`https` only usually); parse + reject creds/fragments you don't expect; for outbound see §7 | `u=urlparse(raw); assert u.scheme in {'https'} and u.hostname` |
| **id / uuid** | exact format (uuid v4 / int range); **and authorize against the caller** (an id that parses is not an id they own) | `assert UUID(raw).version == 4` then owner-scope the query (IDOR) |
| **file** | see §3 — content-sniff, size cap, off-web-root | — |
| **enum / choice** | membership in a closed allowlist; reject on miss | `assert raw in ALLOWED` |
| **date/time** | strict parse to a known format; range-bound; store UTC | `datetime.strptime(raw, FMT)` |

Default-deny: define what's *allowed* and reject the rest, rather than blocklisting known-bad (blocklists always miss a variant). Validate on the **server**; client-side validation is UX, never a control.

---

## §5 — Output-encoding by sink

The same value is safe in one sink and an injection in another. Encode **for the destination**, at the moment of output — never "pre-sanitize once" and reuse everywhere.

| Sink | Encode as | Do / Don't |
|---|---|---|
| **HTML body** | HTML-entity encode `< > & " '` | use the framework's auto-escaping (JSX `{}`, Jinja `{{ }}`, Razor `@`); don't build HTML by string-concat |
| **HTML attribute** | attribute-encode + always quote the attribute | never put untrusted data into an unquoted attr or an event-handler attr |
| **JavaScript context** | JSON-encode into a data island, read from JS | never interpolate untrusted data into a `<script>` body or `eval` |
| **URL / query param** | percent-encode each component | `encodeURIComponent` per component; validate scheme (§4) for full URLs |
| **CSS / style** | avoid untrusted data in CSS; if unavoidable, strict allowlist | never `style="<user>"` or `url(<user>)` |
| **SQL** | **parameterize — never encode** | bind values as parameters/placeholders; allowlist for identifiers (table/column names can't be bound) |
| **Shell / OS command** | avoid; pass argv array, never a string | use exec-with-args APIs; never `shell=True`/string-built commands on input |
| **Log line** | neutralize newlines/control chars | strip `\r\n` to stop log-forging; never log the secret/PII itself |

SQL parameterization (the canonical one):
```python
# YES — value is bound, never part of the SQL text
cur.execute("SELECT * FROM users WHERE email = %s", (email,))
# Identifier (can't bind) → allowlist:
assert col in {"created_at", "name"}; cur.execute(f"ORDER BY {col}")
```

---

## §6 — Dependency, supply-chain & secrets

**Audit commands per ecosystem (run in CI, fail the build on critical/high):**

| Ecosystem | Audit | Lockfile | Notes |
|---|---|---|---|
| npm / pnpm / yarn | `npm audit --omit=dev` · `pnpm audit` · `yarn npm audit` | `package-lock.json` / `pnpm-lock.yaml` | `npm ci` (not `install`) in CI for a reproducible tree; `--ignore-scripts` to block install-time code |
| Python | `pip-audit` (or `safety scan`) | `requirements.txt` pinned `==` / `poetry.lock` / `uv.lock` | `--require-hashes` to pin by content |
| Rust | `cargo audit` (+ `cargo deny`) | `Cargo.lock` | `cargo deny` also enforces license + source allowlists |
| Go | `govulncheck ./...` | `go.sum` | checks *reachable* vulns, lower noise |
| Containers | `trivy image <img>` / `grype <img>` | pinned base by digest | scan base + app layers |

**Supply-chain hygiene:**
```
[ ] a committed lockfile; CI installs from it (npm ci / --require-hashes), not a fresh resolve
[ ] audit runs in CI and FAILS on unresolved critical/high
[ ] dependencies pinned (exact or by digest); renovate/dependabot opens the bumps
[ ] install scripts disabled by default (npm --ignore-scripts) where the workflow allows
[ ] provenance verified for anything you didn't write — signatures / SLSA / publisher
[ ] MINIMIZE vendor count — every dep + external service is delegated trust + attack surface
```
Fewer, audited, pinned. (Same minimize-dependencies principle the rest of fabius runs on.)

**Secrets — env + manager:**
```
[ ] secrets via env vars injected from a manager (Vault / cloud secret store / platform env)
[ ] NEVER inlined in source, .env committed, client bundle, logs, or error responses
[ ] a rotation path: revoke + reissue without redeploying trust
[ ] scan: git history + built bundle + logs (security-playbook §3 greps); any hit = rotate
```

---

## §7 — Cloud least-privilege & SSRF egress

**IAM scoping (default-deny, grant by proven need):**
```
[ ] one identity per service/job; no shared "god" key reused across services
[ ] grant the minimum action set on the minimum resources (no Action:*, no Resource:*)
[ ] read job → read-only policy; writer → write only its own bucket/table/prefix
[ ] separate prod / staging / dev credentials; no prod key on a dev box
[ ] short-lived, auto-rotated credentials (OIDC/workload-identity) over long-lived keys
[ ] audit/log the privileged actions; alert on use of an unused permission
```
(Same least-privilege contract `fabius-cohors` applies to agents — a token gets only what the job calls.)

**SSRF egress allowlist (when you must fetch a user-influenced URL):**
```
[ ] scheme allowlist (https only); host allowlist where feasible
[ ] resolve the host and BLOCK link-local + private + loopback:
    169.254.169.254 (cloud metadata), 127.0.0.0/8, ::1, 10/8, 172.16/12, 192.168/16, fc00::/7
[ ] block redirects to a newly-private target (re-validate after each redirect hop)
[ ] timeout + response-size cap; no following arbitrary redirect chains
[ ] fetch from a network segment with no access to internal services / metadata endpoint
```

---

## §8 — Per-stack quick-harden checklists

Copy the block for the stack you're shipping. Each item is *verify present*.

**Node / Express**
```
[ ] helmet() for the §1 headers (then tighten CSP off the defaults)
[ ] express-rate-limit on auth + expensive routes; body size cap (express.json({limit}))
[ ] parameterized queries (pg/knex placeholders); NEVER string-built SQL
[ ] cookies: httpOnly + secure + sameSite; sessions rotate on login (§2)
[ ] npm ci + npm audit in CI; --ignore-scripts; no secret in process.env baked into client
[ ] trust proxy set correctly so rate-limit + secure cookies see the real client
[ ] errors → generic message to client; stack only to server logs (NODE_ENV=production)
```

**Python (Django / Flask / FastAPI)**
```
[ ] DEBUG = False in prod; ALLOWED_HOSTS set; SECRET_KEY from env
[ ] ORM / parameterized queries; never .raw() / f-string SQL on input
[ ] SecurityMiddleware + SECURE_HSTS / SECURE_SSL_REDIRECT / secure+httponly cookies (§1/§2)
[ ] passwords via the framework hasher (Argon2/PBKDF2), never a bare hash (§2)
[ ] CSRF middleware on; pydantic/marshmallow schema-validate request bodies (§4)
[ ] pip-audit in CI; pinned + hashed requirements (§6)
```

**Static site + CDN**
```
[ ] HTTPS-only + HSTS; security headers via the CDN/host config (§1) since there's no server
[ ] no secret in the shipped JS (it's all public — server-side only for anything sensitive)
[ ] SRI (integrity=) on any third-party <script>/<link>; pin the version
[ ] CSP locks script-src to 'self' (+ explicit hosts/nonce); externalize inline scripts
[ ] immutable, content-hashed asset URLs; sensible Cache-Control
```

**Cloudflare Worker**
```
[ ] secrets via `wrangler secret put`, read from env binding — never in wrangler.toml or source
[ ] bindings scoped to the one KV/D1/R2/queue the worker needs (least privilege)
[ ] validate + size-cap the request before doing work; set §1 headers on the Response
[ ] verify any signed/HMAC payload before trusting it; constant-time compare
[ ] rate-limit / turnstile on abuse-prone routes; fail closed on a verify error
[ ] no stack-trace / internal detail in the error Response body
```

---

Every guide above is for **hardening and detection** only. A sample malicious *input* inside a defensive validation or regression test (security-playbook §6) is the only "attack-shaped" thing here — and it exists to **prove a hole closed**. No working exploits, no attack tooling, ever. If in doubt, leave it out. Routes back: [security-playbook.md](security-playbook.md) · index: [CORPUS.md](../../../CORPUS.md) (R9 · M9).
