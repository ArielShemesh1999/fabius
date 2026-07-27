# External recon — auditing the surface you already publish

Everything here reads what a host tells any client that asks: DNS records, a TLS
handshake, response headers, files the site serves on purpose. No payload, no credential,
no vulnerability probe. It is the outside view of something you own, and it is the cheapest
security work available — most of these findings are a DNS record or a header away from
fixed.

**Authorisation.** Passive reading of published records needs none. The one active check —
a TCP connect on service ports — is different: run it only against hosts you own or have
written permission to test. fabius keeps it off by default for that reason.

fabius ships this as `fabius recon <domain>` in `runtime/` — no API key, no account,
built on `node:dns`, `node:tls` and one HTTP request. A security check you must register
somewhere to run is a check you will not run.

---

## 1. What to look at, and what each finding actually means

Ordered by how often it is both wrong and consequential.

### Mail authentication — the most-missed high-severity finding

A domain with no SPF and no DMARC can be spoofed by anyone, and this is true of domains
that send no mail at all — arguably *especially* those, because nobody is watching.

- **SPF absent** → anyone may send as you. Even a non-sending domain should publish
  `v=spf1 -all`.
- **SPF ending `~all` or `?all`** → a soft fail asks the receiver to please consider it.
  Once the sending hosts are confirmed, tighten to `-all`.
- **DMARC absent** → the receiver has no instruction for mail that fails both SPF and
  DKIM, and most will deliver it.
- **DMARC at `p=none`** → monitoring only. That is the correct *first* state and a bad
  permanent one. Read the `rua` reports, then move to `quarantine`, then `reject`.
- **No `rua=`** → nobody sees who is sending as you, which is the whole early-warning value.
- **DKIM** → selectors are arbitrary, so probing common ones (`default`, `google`,
  `selector1`, `selector2`, `k1`, `mail`) proves presence but never absence. Report a miss
  as a hint, never as a verdict.

### TLS

Validate the chain as a client does, then read what was actually negotiated. Expiry inside
30 days is a finding and inside 14 is urgent — not because the certificate is weak, but
because expiry is the single most common way a site goes hard-down. An RSA key under 2048
bits, or a negotiated TLS 1.0/1.1, is a configuration nobody chose on purpose and everyone
forgets they still serve.

### Security headers, graded per directive

Missing HSTS, CSP, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` —
each with a concrete value to ship, not a lecture.

Two subtleties separate a useful report from a noisy one:

- **Clickjacking is covered by either** `frame-ancestors` in the CSP **or**
  `X-Frame-Options`. Demanding both produces a finding on a correctly configured site.
- **Parse the CSP into directives.** `'unsafe-inline'` in `style-src` is ordinary and
  low-risk; the identical keyword in `script-src` is most of what CSP exists to prevent.
  Grading the header as one flat string reports the first as if it were the second, and a
  tool that cannot tell them apart teaches its operator to ignore it. Follow the
  `default-src` fallback, and recognise that `'strict-dynamic'` with a nonce makes host
  sources and `'unsafe-inline'` inert — flagging them there is also a false positive.

Grade HSTS on quality, not presence: `max-age` under 180 days fails preload, and without
`includeSubDomains` a subdomain can still be reached over plain HTTP and set cookies for
the parent.

### Cookies

`Secure` missing → sent in clear text if a request is ever downgraded. `HttpOnly` missing
→ any XSS exfiltrates it. `SameSite` missing → the CSRF precondition. Three flags, three
one-line fixes, and they are wrong on production sites constantly.

### Plain HTTP

Availability on port 80 is not the finding — the *absence of a redirect* is. Check that
`http://` answers 301, and that the target is the `https://` origin directly rather than
another hop, because each extra hop is another chance to be intercepted.

### The files you publish deliberately

- **`security.txt`** (RFC 9116) absent → a researcher who finds a flaw has no documented
  way to report it, so they post it publicly. `Contact:` is required; `Expires:` is
  required and is routinely stale.
- **`robots.txt`** → read what it *advertises*. `Disallow: /admin`, `/backup`, `/internal`
  is a public file naming exactly what you wanted hidden, and it is the first thing an
  attacker reads. The fix is authentication, never a longer robots file.

### DNS hygiene

**CAA absent** → any certificate authority in the world may issue for your name; one
record restricts that to the CAs you actually use. **DNSSEC absent** → responses are not
signed, so a resolver cannot detect a forged answer. **A single nameserver** → the whole
domain has one point of failure.

### The edge

No CDN or WAF signature in the response means requests reach your origin directly and the
origin absorbs any flood alone. This is information, not a vulnerability — report it as
such.

## 2. Two rules that decide whether the report gets read

**Every finding carries a fix.** Severity plus evidence plus the exact change. A finding
without a fix is a complaint.

**Demote what the reader cannot act on.** On `yourapp.vercel.app` the DNS tree, the
certificate and the mail records belong to Vercel. Reporting "no DMARC" there at medium
severity is asking for work that cannot be done, and a report full of impossible items is
a report that gets closed. Detect the delegated platform zones — `vercel.app`,
`pages.dev`, `netlify.app`, `github.io`, `workers.dev`, and the rest — demote those
findings to context, and say why. On the reader's own apex domain they stay at full
severity.

The general principle, worth more than the specific list: **the cost of a false positive
in security tooling is not one wasted minute, it is the operator's future attention.**
Precision beats coverage.

## 3. Where this sits

This is the *external* half of an audit — what the internet can already see. It composes
with, and does not replace:

- the STRIDE-per-boundary threat model and the OWASP pass → `references/security-playbook.md`
- auditing third-party artifacts before adopting them → `references/supply-chain-and-ai-artifacts.md`
- the instrument per defensive job (SAST, SCA, secrets, DAST) → `references/security-toolkit.md`

Two adjacent surfaces belong to other layers. The *discoverability* reading of the same
scan — title, description, canonical, `og:image`, sitemap — is `fabius-mercatus`. Deciding
how an agent is reached, and building a channel for it, is `fabius-cohors`; this layer
reviews the threat model of one when asked.

## 4. Reviewing a private transport, when you are handed one

A recurring request, and one where the honesty bar is the deliverable. What to establish,
in order:

- **What the encryption covers, and what it does not.** Content is the easy part. The
  interesting question is always metadata: who talked to whom, when, and how often. An
  envelope that hides the sender behind an ephemeral key still tells a relay that
  *someone* messaged *this* recipient at *this* time.
- **Where forward secrecy is absent.** Live sessions usually have it; stored-and-forwarded
  messages usually do not, because something has to be decryptable later. That is a
  legitimate design choice and an illegitimate thing to leave unstated.
- **What identifier persists.** "No accounts, no phone numbers" is compatible with a
  stable per-device key that links every session you ever had. Say so plainly.
- **Whether authenticity survives without signature verification.** It can: authenticated
  encryption means a payload that decrypts under a key derived from the claimed sender
  proves that sender held the private key. But then the *inner* author must be checked
  against the *outer* one, or anyone can wrap a message claiming any author. That check is
  the difference between a working design and an impersonation hole.
- **What the panic path is.** If the threat model includes device seizure, there must be a
  wipe that is immediate, unconfirmed, and reachable without unlocking anything.

Judge such a system by whether its own documentation states these limits. A protocol that
publishes its metadata leakage is more trustworthy than one that claims none.
