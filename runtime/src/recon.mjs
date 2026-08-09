// EXTERNAL RECON — what the internet can already see about a domain you own.
//
// Every check here runs from primitives Node already ships: node:dns for the record
// tree, node:tls for the certificate and the negotiated cipher, fetch for the response
// surface, node:net for a reachability probe. No API key, no third-party SaaS, no
// account — which matters, because a security check you cannot run without registering
// somewhere is a check you will not run.
//
// DEFENSIVE POSTURE. Everything below is passive: it reads what the target publishes to
// any client — DNS records, a TLS handshake, response headers, files the site serves on
// purpose (robots.txt, security.txt). It sends no payload, tries no credential, and
// probes no vulnerability. The one active check, a TCP connect on common service ports,
// is OFF unless the caller passes `ports: true` and asserts authorization.
//
// Findings carry a severity and a fix, never a raw dump: the deliverable is "here is
// what to change and why", not "here are 400 lines of JSON".

import { Resolver } from 'node:dns/promises';
import { connect as tlsConnect } from 'node:tls';
import { connect as netConnect } from 'node:net';
import { assertPublicHostname } from './tools.mjs';

export const SEVERITY = ['critical', 'high', 'medium', 'low', 'info'];
const sevRank = (s) => SEVERITY.indexOf(s);

const DEFAULT_TIMEOUT = 8000;

// The redirect set, written once. Two hand-kept copies drifted before — the plain-HTTP check
// was missing 303, so a host that legitimately answered `303 → https://…` was reported HIGH
// for "no redirect", which is the false positive that teaches an operator to stop reading.
const REDIRECT_STATUS = [301, 302, 303, 307, 308];

// ── tiny helpers ────────────────────────────────────────────────────────────────
const withTimeout = (p, ms, label) => Promise.race([
  p,
  new Promise((_, rej) => setTimeout(() => rej(new Error(`${label} timed out after ${ms}ms`)), ms).unref?.()),
]);

export function normalizeTarget(input) {
  let s = String(input || '').trim();
  if (!s) throw new Error('no target given');
  s = s.replace(/^[a-z][a-z0-9+.-]*:\/\//i, '');   // strip any scheme
  s = s.split('/')[0].split('?')[0].split('#')[0]; // host only
  s = s.replace(/:\d+$/, '');                      // strip a port
  s = s.replace(/\.$/, '').toLowerCase();
  if (!/^[a-z0-9.-]+$/.test(s) || !s.includes('.')) throw new Error(`"${input}" is not a hostname`);
  return s;
}

const resolver = () => { const r = new Resolver({ timeout: 4000, tries: 2 }); return r; };
const safe = async (fn, dflt = null) => { try { return await fn(); } catch { return dflt; } };

// Hosting platforms that own the parent zone. On `myapp.vercel.app` the DNS tree, the
// certificate and the mail records belong to Vercel, not to you — so DNSSEC, CAA and
// SPF/DMARC findings there are not work you can do. A report full of items the reader
// cannot action is a report they stop reading, so those get demoted to `info` and told
// why. On your own apex domain they stay at full severity.
const PLATFORM_ZONES = ['vercel.app', 'pages.dev', 'netlify.app', 'github.io', 'workers.dev', 'herokuapp.com', 'web.app', 'firebaseapp.com', 'fly.dev', 'onrender.com', 'surge.sh', 'gitlab.io', 'azurewebsites.net', 'cloudfront.net'];
export function delegatedPlatform(host) {
  const h = String(host || '').toLowerCase();
  for (const z of PLATFORM_ZONES) if (h === z || h.endsWith('.' + z)) return z;
  return null;
}
// Findings whose fix lives in the parent zone's DNS, not in the deployment.
const ZONE_OWNED = new Set(['dns', 'dnssec', 'mail']);

// DNS-over-HTTPS — the only way to read the AD (authenticated data) bit that proves a
// validating resolver checked DNSSEC. node:dns cannot report it.
async function doh(name, type, { timeoutMs = DEFAULT_TIMEOUT } = {}) {
  const url = `https://cloudflare-dns.com/dns-query?name=${encodeURIComponent(name)}&type=${encodeURIComponent(type)}`;
  const res = await withTimeout(fetch(url, { headers: { accept: 'application/dns-json' } }), timeoutMs, 'DoH');
  if (!res.ok) throw new Error(`DoH http ${res.status}`);
  return res.json();
}

// ── the checks ──────────────────────────────────────────────────────────────────

async function checkDns(host, ctx) {
  const r = resolver();
  const [a, aaaa, mx, ns, txt, cname, soa, caa] = await Promise.all([
    safe(() => r.resolve4(host), []), safe(() => r.resolve6(host), []),
    safe(() => r.resolveMx(host), []), safe(() => r.resolveNs(host), []),
    safe(() => r.resolveTxt(host), []), safe(() => r.resolveCname(host), []),
    safe(() => r.resolveSoa(host), null), safe(() => r.resolveCaa(host), []),
  ]);
  const findings = [];
  if (!a.length && !aaaa.length && !cname.length) {
    findings.push({ severity: 'critical', title: 'the name does not resolve', detail: `${host} has no A, AAAA or CNAME record.`, fix: 'Publish an address record, or the site is unreachable for everyone.' });
  }
  if (!caa.length) {
    findings.push({ severity: 'low', title: 'no CAA record', detail: 'Any certificate authority may issue a certificate for this name.', fix: `Add a CAA record naming only the CAs you use, e.g. \`${host}. IN CAA 0 issue "letsencrypt.org"\`.` });
  }
  if (ns.length === 1) {
    findings.push({ severity: 'medium', title: 'a single nameserver', detail: `Only ${ns[0]} is authoritative — it is a single point of failure for the whole domain.`, fix: 'Run at least two nameservers, ideally on separate networks.' });
  }
  const flatTxt = txt.map((x) => x.join(''));
  return { id: 'dns', title: 'DNS records', data: { a, aaaa, mx, ns, txt: flatTxt, cname, soa, caa }, findings };
}

async function checkDnssec(host, ctx) {
  const findings = [];
  let ad = null, ds = [], dnskey = [];
  try {
    const res = await doh(host, 'A', ctx);
    ad = res.AD === true;
    const dsRes = await safe(() => doh(host, 'DS', ctx), null);
    ds = (dsRes?.Answer || []).filter((x) => x.type === 43);
    const kRes = await safe(() => doh(host, 'DNSKEY', ctx), null);
    dnskey = (kRes?.Answer || []).filter((x) => x.type === 48);
  } catch (e) {
    return { id: 'dnssec', title: 'DNSSEC', data: { error: e.message }, findings: [] };
  }
  if (!ad && !ds.length) {
    findings.push({ severity: 'low', title: 'DNSSEC is not enabled', detail: 'Responses for this zone are not cryptographically signed, so a resolver cannot detect a forged answer.', fix: 'Enable DNSSEC at the registrar and publish the DS record. Most managed DNS providers do both in one click.' });
  }
  return { id: 'dnssec', title: 'DNSSEC', data: { authenticated: ad, dsRecords: ds.length, dnskeys: dnskey.length }, findings };
}

// The certificate as a client sees it, plus the protocol and cipher actually negotiated.
function tlsHandshake(host, { port = 443, timeoutMs = DEFAULT_TIMEOUT, servername = host } = {}) {
  return new Promise((res, rej) => {
    const sock = tlsConnect({ host, port, servername, rejectUnauthorized: false, ALPNProtocols: ['h2', 'http/1.1'] }, () => {
      const cert = sock.getPeerCertificate(true);
      const cipher = sock.getCipher();
      const out = {
        authorized: sock.authorized,
        authorizationError: sock.authorizationError ? String(sock.authorizationError) : null,
        protocol: sock.getProtocol(),
        alpn: sock.alpnProtocol || null,
        cipher,
        subject: cert?.subject || null,
        issuer: cert?.issuer || null,
        valid_from: cert?.valid_from || null,
        valid_to: cert?.valid_to || null,
        san: cert?.subjectaltname || '',
        bits: cert?.bits || null,
        keyType: cert?.asn1Curve || cert?.nistCurve || (cert?.modulus ? 'RSA' : null),
        fingerprint256: cert?.fingerprint256 || null,
        chain: chainOf(cert),
      };
      sock.end(); res(out);
    });
    sock.setTimeout(timeoutMs, () => { sock.destroy(); rej(new Error(`TLS handshake timed out after ${timeoutMs}ms`)); });
    sock.on('error', (e) => rej(e));
  });
}
function chainOf(cert) {
  const out = [];
  let c = cert, guard = 0;
  while (c && guard++ < 10) {
    out.push({ subject: c.subject?.CN || '(none)', issuer: c.issuer?.CN || '(none)', valid_to: c.valid_to });
    if (!c.issuerCertificate || c.issuerCertificate === c) break;
    c = c.issuerCertificate;
  }
  return out;
}

async function checkTls(host, ctx) {
  const findings = [];
  let hs;
  try { hs = await tlsHandshake(host, ctx); }
  catch (e) {
    return { id: 'tls', title: 'TLS certificate', data: { error: e.message }, findings: [{ severity: 'critical', title: 'no TLS handshake', detail: `Could not complete a TLS handshake with ${host}:443 — ${e.message}`, fix: 'Serve HTTPS on port 443. Every modern browser treats plain HTTP as insecure.' }] };
  }
  if (!hs.authorized) {
    findings.push({ severity: 'critical', title: 'the certificate does not validate', detail: `Chain validation failed: ${hs.authorizationError}.`, fix: 'Install the full chain (leaf + intermediates) and make sure the name on the certificate covers this host.' });
  }
  const daysLeft = hs.valid_to ? Math.floor((Date.parse(hs.valid_to) - Date.now()) / 86400000) : null;
  if (daysLeft !== null) {
    if (daysLeft < 0) findings.push({ severity: 'critical', title: 'the certificate has expired', detail: `Expired ${Math.abs(daysLeft)} days ago (${hs.valid_to}).`, fix: 'Renew now — browsers are hard-failing this request.' });
    else if (daysLeft < 14) findings.push({ severity: 'high', title: `the certificate expires in ${daysLeft} days`, detail: `Valid until ${hs.valid_to}.`, fix: 'Renew, and make renewal automatic so the clock never matters again.' });
    else if (daysLeft < 30) findings.push({ severity: 'medium', title: `the certificate expires in ${daysLeft} days`, detail: `Valid until ${hs.valid_to}.`, fix: 'Confirm automated renewal is actually firing.' });
  }
  const proto = hs.protocol || '';
  if (/TLSv1(\.[01])?$/.test(proto)) {
    findings.push({ severity: 'high', title: `negotiated ${proto}`, detail: 'TLS 1.0/1.1 are deprecated and fail modern client policy.', fix: 'Require TLS 1.2 as a floor and prefer TLS 1.3.' });
  }
  if (hs.keyType === 'RSA' && hs.bits && hs.bits < 2048) {
    findings.push({ severity: 'high', title: `RSA key is only ${hs.bits} bits`, detail: 'Below the 2048-bit floor.', fix: 'Reissue with a 2048-bit RSA key or, better, a P-256 EC key.' });
  }
  if (!hs.alpn || hs.alpn === 'http/1.1') {
    findings.push({ severity: 'info', title: 'HTTP/2 is not offered', detail: `ALPN negotiated ${hs.alpn || 'nothing'}.`, fix: 'Enable HTTP/2 — it is free latency on every page load.' });
  }
  return { id: 'tls', title: 'TLS certificate', data: { ...hs, daysLeft }, findings };
}

// Redirects are followed BY HAND so every hop is re-checked, not just the entry host.
// Platform fetch follows a cross-host redirect itself, silently, so a public domain that
// answers `302 -> http://169.254.169.254/latest/meta-data/` would otherwise turn this
// passive audit into a request against cloud metadata — with the status, the headers and
// the final URL landing in the report. Same assertion `fetch` applies in tools.mjs,
// applied in the same place: inside the loop.
//
// A refusal stops the chain rather than failing the scan: what was already read from the
// public hops is still a real answer, and `refused` says plainly why it went no further.
async function fetchHops(url, ctx, maxHops = 10) {
  const headers = { 'user-agent': ctx.userAgent };
  const chain = [];
  let current = String(url), res = null, refused = null;
  for (let hop = 0; hop < maxHops; hop++) {
    const bad = await assertPublicHostname(new URL(current).hostname);
    if (bad) { refused = `${current} ${bad}`; break; }
    res = await withTimeout(fetch(current, { redirect: 'manual', headers }), ctx.timeoutMs, 'HTTP');
    const loc = res.headers.get('location');
    chain.push({ url: current, status: res.status, location: loc || null });
    if (!REDIRECT_STATUS.includes(res.status) || !loc) return { res, chain, finalUrl: current, refused: null };
    let next;
    try { next = new URL(loc, current); }
    catch { return { res, chain, finalUrl: current, refused: `(refused: ${loc} is not a URL)` }; }
    if (!['http:', 'https:'].includes(next.protocol)) { refused = `(refused: ${next.protocol}// is not http or https)`; break; }
    if (hop === maxHops - 1) { refused = '(refused: too many redirects)'; break; }
    // Nothing reads a redirect's body, and the socket stays held until it is consumed
    // or cancelled — release it before moving to the next hop. Only ever on the way to a
    // next hop: every `break` above hands this response back, and the caller still reads it.
    await res.body?.cancel().catch(() => {});
    current = next.toString();
  }
  if (!res) throw new Error(`refused to fetch ${refused}`);
  return { res, chain, finalUrl: chain[chain.length - 1].url, refused };
}

// One fetch, reused by every response-surface check.
async function fetchSurface(host, ctx) {
  const url = `https://${host}/`;
  const { res, chain, finalUrl, refused } = await fetchHops(url, ctx);
  const headers = {};
  for (const [k, v] of res.headers) headers[k.toLowerCase()] = v;
  const ct = headers['content-type'] || '';
  const body = /text|html|json|xml/.test(ct) ? (await res.text()).slice(0, 400000) : '';
  return { url, finalUrl, status: res.status, headers, body, chain, refused,
           setCookie: res.headers.getSetCookie ? res.headers.getSetCookie() : [] };
}

async function checkHttp(host, ctx, surface) {
  const findings = [];
  const h = surface.headers;
  // Plain HTTP must be redirected, not merely available.
  const plain = await safe(async () => {
    // Same rule as every hop above: never probe a host that is not on the public internet.
    const bad = await assertPublicHostname(host);
    if (bad) throw new Error(bad);
    const r = await withTimeout(fetch(`http://${host}/`, { redirect: 'manual', headers: { 'user-agent': ctx.userAgent } }), ctx.timeoutMs, 'HTTP');
    return { status: r.status, location: r.headers.get('location') };
  }, null);
  // Same test fetchHops applies to a hop: a redirect status AND a Location to go to.
  if (plain && (!REDIRECT_STATUS.includes(plain.status) || !plain.location)) {
    findings.push({ severity: 'high', title: 'plain HTTP is served without a redirect', detail: `http://${host}/ answered ${plain.status}${plain.location ? '' : ' with no Location header'} instead of redirecting to HTTPS.`, fix: 'Return a 301 to the https:// URL for every plain-HTTP request.' });
  } else if (plain?.location && !/^https:/i.test(plain.location)) {
    findings.push({ severity: 'medium', title: 'the HTTP redirect does not go to HTTPS', detail: `Redirects to ${plain.location}.`, fix: 'Point the redirect at the https:// origin directly — an extra hop is an extra chance to be intercepted.' });
  }
  if (surface.status >= 500) {
    findings.push({ severity: 'critical', title: `the origin answers ${surface.status}`, detail: 'The homepage is returning a server error.', fix: 'Fix the origin — nothing else on this report matters while the site is down.' });
  }
  if (h['server'] && /\d+\.\d+/.test(h['server'])) {
    findings.push({ severity: 'low', title: 'the server banner leaks a version', detail: `Server: ${h['server']}`, fix: 'Strip the version from the banner — it hands an attacker a CVE shortlist for free.' });
  }
  for (const leak of ['x-powered-by', 'x-aspnet-version', 'x-generator']) {
    if (h[leak]) findings.push({ severity: 'low', title: `${leak} leaks the stack`, detail: `${leak}: ${h[leak]}`, fix: `Remove the ${leak} header.` });
  }
  if (surface.refused) {
    findings.push({ severity: 'medium', title: 'the redirect chain leaves the public internet', detail: `The chain was not followed past ${surface.refused}`, fix: 'Redirect to a public address. A public hostname that hands clients an internal one is either a misconfiguration or an SSRF lure.' });
  }
  return { id: 'http', title: 'HTTP response', data: { status: surface.status, finalUrl: surface.finalUrl, redirects: surface.chain, refused: surface.refused || null, server: h['server'] || null, alt_svc: h['alt-svc'] || null, plainHttp: plain }, findings };
}

// The header set that actually changes an attacker's options, graded the way a reviewer
// grades it: missing → what breaks, and the exact value to ship.
const SECURITY_HEADERS = [
  { key: 'strict-transport-security', severity: 'high', title: 'HSTS', why: 'Without HSTS the first request of every session can be downgraded to plain HTTP and intercepted.', fix: 'Add `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`.' },
  { key: 'content-security-policy', severity: 'high', title: 'Content-Security-Policy', why: 'CSP is the one control that turns an injected <script> from a full account takeover into a blocked console error.', fix: "Start with `Content-Security-Policy: default-src 'self'; object-src 'none'; base-uri 'none'` and widen deliberately." },
  { key: 'x-content-type-options', severity: 'medium', title: 'X-Content-Type-Options', why: 'Browsers may sniff a response into a type you did not intend, turning an upload into a script.', fix: 'Add `X-Content-Type-Options: nosniff`.' },
  { key: 'referrer-policy', severity: 'low', title: 'Referrer-Policy', why: 'Full URLs — including tokens in query strings — leak to every third party you link to.', fix: 'Add `Referrer-Policy: strict-origin-when-cross-origin`.' },
  { key: 'permissions-policy', severity: 'low', title: 'Permissions-Policy', why: 'Embedded frames inherit access to camera, microphone and geolocation by default.', fix: 'Add `Permissions-Policy: camera=(), microphone=(), geolocation=()` and open only what you use.' },
];

// A CSP is a set of directives, and a keyword only matters in the directive it lands in.
// `style-src 'unsafe-inline'` is ordinary and low-risk; the same keyword in `script-src`
// is the whole attack. Grading the header as one flat string produces exactly the kind of
// false positive that teaches an operator to ignore the tool — so parse it properly.
export function parseCsp(header) {
  const out = {};
  for (const part of String(header || '').split(';')) {
    const toks = part.trim().split(/\s+/).filter(Boolean);
    if (!toks.length) continue;
    out[toks[0].toLowerCase()] = toks.slice(1);
  }
  return out;
}
// Which sources actually apply to a directive, following the default-src fallback.
const effective = (csp, name) => csp[name] || csp['default-src'] || null;

export function auditCsp(header) {
  const csp = parseCsp(header);
  const f = [];
  const script = effective(csp, 'script-src');
  const has = (list, kw) => Array.isArray(list) && list.some((s) => s.toLowerCase() === kw);
  const nonced = Array.isArray(script) && script.some((s) => /^'(nonce-|sha\d{3}-)/i.test(s));

  if (!script) {
    f.push({ severity: 'medium', title: 'the CSP does not restrict scripts', detail: 'Neither script-src nor default-src is set, so script sources are unrestricted.', fix: "Add `script-src 'self'`." });
  } else {
    // 'strict-dynamic' with a nonce is the modern strict policy; there, host-source
    // keywords are ignored by the browser and flagging them would be wrong.
    const strictDynamic = has(script, "'strict-dynamic'");
    if (has(script, "'unsafe-inline'") && !nonced) {
      f.push({ severity: 'medium', title: "script-src allows 'unsafe-inline'", detail: 'An injected inline <script> executes, which is most of what CSP exists to stop.', fix: 'Move inline scripts to files, or adopt a nonce/hash policy.' });
    }
    if (has(script, "'unsafe-eval'")) {
      f.push({ severity: 'medium', title: "script-src allows 'unsafe-eval'", detail: 'eval() and its relatives stay available to injected code.', fix: "Remove 'unsafe-eval' and the library that needs it." });
    }
    if (!strictDynamic && script.some((s) => s === '*' || s === 'http:' || s === 'https:' || s === 'data:')) {
      f.push({ severity: 'medium', title: 'script-src accepts scripts from anywhere', detail: `Sources: ${script.join(' ')}`, fix: "Name the origins you actually load from, starting from 'self'." });
    }
  }
  const obj = effective(csp, 'object-src');
  if (!obj || !has(obj, "'none'")) {
    f.push({ severity: 'low', title: "object-src is not 'none'", detail: 'Legacy plugin content (<object>, <embed>) can still be injected.', fix: "Add `object-src 'none'` — nothing modern needs it." });
  }
  if (!csp['base-uri']) {
    f.push({ severity: 'low', title: 'no base-uri directive', detail: "An injected <base> tag can silently repoint every relative URL on the page, including scripts.", fix: "Add `base-uri 'none'` (or 'self')." });
  }
  return f;
}

async function checkSecurityHeaders(host, ctx, surface) {
  const h = surface.headers;
  const findings = [];
  const present = {};
  for (const spec of SECURITY_HEADERS) {
    const v = h[spec.key];
    present[spec.key] = v || null;
    if (!v) findings.push({ severity: spec.severity, title: `no ${spec.title}`, detail: spec.why, fix: spec.fix });
  }
  // Clickjacking is covered by EITHER frame-ancestors or the legacy header.
  const csp = h['content-security-policy'] || '';
  if (!/frame-ancestors/i.test(csp) && !h['x-frame-options']) {
    findings.push({ severity: 'medium', title: 'nothing prevents framing', detail: 'Neither `frame-ancestors` in CSP nor X-Frame-Options is set, so the page can be embedded in an attacker\'s frame and clickjacked.', fix: "Add `frame-ancestors 'none'` to the CSP (and `X-Frame-Options: DENY` for old clients)." });
  }
  if (csp) findings.push(...auditCsp(csp));
  // HSTS quality, not just presence.
  const hsts = h['strict-transport-security'];
  if (hsts) {
    const maxAge = Number((hsts.match(/max-age\s*=\s*(\d+)/i) || [])[1] || 0);
    if (maxAge < 15552000) findings.push({ severity: 'low', title: `HSTS max-age is only ${maxAge}s`, detail: 'Below the 180-day floor the preload list requires.', fix: 'Raise max-age to 31536000 (one year).' });
    if (!/includeSubDomains/i.test(hsts)) findings.push({ severity: 'low', title: 'HSTS does not cover subdomains', detail: 'A subdomain can still be reached over plain HTTP and used to set cookies for the parent.', fix: 'Add `includeSubDomains`.' });
  }
  return { id: 'headers', title: 'security headers', data: { present, raw: h }, findings };
}

function parseCookie(line) {
  const [pair, ...attrs] = line.split(';').map((s) => s.trim());
  const name = pair.split('=')[0];
  const flags = new Set(attrs.map((a) => a.split('=')[0].toLowerCase()));
  const sameSite = (attrs.find((a) => /^samesite=/i.test(a)) || '').split('=')[1] || null;
  return { name, secure: flags.has('secure'), httpOnly: flags.has('httponly'), sameSite };
}

async function checkCookies(host, ctx, surface) {
  const findings = [];
  const cookies = (surface.setCookie || []).map(parseCookie);
  for (const c of cookies) {
    if (!c.secure) findings.push({ severity: 'medium', title: `cookie "${c.name}" is not Secure`, detail: 'It will be sent over plain HTTP if a request is ever downgraded.', fix: `Set the Secure attribute on ${c.name}.` });
    if (!c.httpOnly) findings.push({ severity: 'medium', title: `cookie "${c.name}" is readable by JavaScript`, detail: 'Any XSS on the page can exfiltrate it.', fix: `Set HttpOnly on ${c.name} unless the front end genuinely reads it.` });
    if (!c.sameSite) findings.push({ severity: 'low', title: `cookie "${c.name}" has no SameSite`, detail: 'Cross-site requests may carry it, which is the CSRF precondition.', fix: `Set SameSite=Lax (or Strict) on ${c.name}.` });
  }
  return { id: 'cookies', title: 'cookies', data: { cookies }, findings };
}

// SPF, DMARC, DKIM and BIMI decide whether anyone can send mail as this domain.
async function checkMail(host, ctx, dnsData) {
  const findings = [];
  const r = resolver();
  const txt = (dnsData?.txt || []);
  const spf = txt.find((t) => /^v=spf1/i.test(t)) || null;
  const dmarcTxt = await safe(async () => (await r.resolveTxt(`_dmarc.${host}`)).map((x) => x.join('')), []);
  const dmarc = dmarcTxt.find((t) => /^v=DMARC1/i.test(t)) || null;
  const bimi = await safe(async () => (await r.resolveTxt(`default._bimi.${host}`)).map((x) => x.join('')).find((t) => /^v=BIMI1/i.test(t)) || null, null);
  const mx = dnsData?.mx || [];
  // Common selectors, probed cheaply. Absence proves nothing (selectors are arbitrary).
  const selectors = ['default', 'google', 'selector1', 'selector2', 'k1', 'mail', 's1', 'dkim'];
  const dkim = [];
  await Promise.all(selectors.map(async (s) => {
    const v = await safe(async () => (await r.resolveTxt(`${s}._domainkey.${host}`)).map((x) => x.join('')).join(''), '');
    if (v && /v=DKIM1|p=/i.test(v)) dkim.push(s);
  }));

  const sendsMail = mx.length > 0;
  if (!spf) {
    findings.push({ severity: sendsMail ? 'high' : 'medium', title: 'no SPF record', detail: 'Nothing tells a receiving server which hosts may send mail as this domain, so anyone can.', fix: sendsMail ? 'Publish `v=spf1 include:<your provider> -all`.' : 'Even a non-sending domain should publish `v=spf1 -all` to stop spoofing.' });
  } else if (/[?~]all\s*$/.test(spf)) {
    findings.push({ severity: 'low', title: 'SPF ends in a soft fail', detail: `Policy: ${spf}`, fix: 'Once the sending hosts are confirmed, tighten `~all` to `-all`.' });
  } else if (!/[-~?]all/.test(spf)) {
    findings.push({ severity: 'medium', title: 'SPF has no `all` mechanism', detail: `Policy: ${spf}`, fix: 'End the record with `-all`, or it authorises nothing in particular.' });
  }
  if (!dmarc) {
    findings.push({ severity: sendsMail ? 'high' : 'medium', title: 'no DMARC record', detail: 'Without DMARC a receiver has no instruction about what to do with mail that fails SPF and DKIM — most will deliver it.', fix: 'Publish `_dmarc` as `v=DMARC1; p=none; rua=mailto:you@domain` first, read the reports, then move to `p=reject`.' });
  } else {
    const p = (dmarc.match(/p\s*=\s*(none|quarantine|reject)/i) || [])[1]?.toLowerCase();
    if (p === 'none') findings.push({ severity: 'medium', title: 'DMARC is in monitor-only mode', detail: `Policy: ${dmarc}`, fix: 'Once the reports look clean, move `p=none` to `p=quarantine`, then `p=reject`.' });
    if (!/rua=/i.test(dmarc)) findings.push({ severity: 'low', title: 'DMARC collects no reports', detail: 'No `rua=` address, so nobody sees who is sending as this domain.', fix: 'Add `rua=mailto:dmarc@yourdomain`.' });
  }
  if (sendsMail && !dkim.length) {
    findings.push({ severity: 'low', title: 'no DKIM key found on the common selectors', detail: `Probed: ${selectors.join(', ')}. Selectors are arbitrary, so this is a hint, not a verdict.`, fix: 'Confirm DKIM signing is enabled at your mail provider and that the selector is published.' });
  }
  return { id: 'mail', title: 'mail authentication', data: { spf, dmarc, bimi, dkimSelectors: dkim, mx: mx.map((m) => `${m.priority} ${m.exchange}`) }, findings };
}

// Through the same hop-checking loop: robots.txt and security.txt legitimately redirect
// (apex to www, http to https), and letting the platform follow those hops unchecked is
// the same SSRF as the one above — worse, in fact, because this one reads the body.
async function fetchText(url, ctx) {
  const { res } = await fetchHops(url, ctx, 5);
  if (!res.ok) return { ok: false, status: res.status, text: '' };
  const ct = res.headers.get('content-type') || '';
  return { ok: true, status: res.status, contentType: ct, text: (await res.text()).slice(0, 200000) };
}

async function checkWellKnown(host, ctx) {
  const findings = [];
  const [robots, secTxt, secTxtRoot, sitemapIdx] = await Promise.all([
    safe(() => fetchText(`https://${host}/robots.txt`, ctx), { ok: false }),
    safe(() => fetchText(`https://${host}/.well-known/security.txt`, ctx), { ok: false }),
    safe(() => fetchText(`https://${host}/security.txt`, ctx), { ok: false }),
    safe(() => fetchText(`https://${host}/sitemap.xml`, ctx), { ok: false }),
  ]);
  const sec = secTxt.ok ? secTxt : (secTxtRoot.ok ? secTxtRoot : null);
  if (!sec) {
    findings.push({ severity: 'low', title: 'no security.txt', detail: 'A researcher who finds a flaw has no documented way to report it, so they post it publicly instead.', fix: 'Publish /.well-known/security.txt with `Contact:` and `Expires:` (RFC 9116).' });
  } else {
    if (!/^Contact:/mi.test(sec.text)) findings.push({ severity: 'low', title: 'security.txt has no Contact field', detail: 'The one required field is missing.', fix: 'Add `Contact: mailto:security@yourdomain`.' });
    const exp = (sec.text.match(/^Expires:\s*(.+)$/mi) || [])[1];
    if (!exp) findings.push({ severity: 'info', title: 'security.txt has no Expires field', detail: 'RFC 9116 requires it.', fix: 'Add `Expires:` with an ISO date under a year out.' });
    else if (Date.parse(exp) < Date.now()) findings.push({ severity: 'low', title: 'security.txt has expired', detail: `Expires: ${exp}`, fix: 'Refresh the file and push the date forward.' });
  }
  // robots.txt that leaks the map of what you wanted hidden.
  if (robots.ok) {
    const juicy = (robots.text.match(/^Disallow:\s*(\/\S*)/gmi) || [])
      .map((l) => l.split(':')[1].trim())
      .filter((p) => /admin|private|secret|backup|\.git|internal|staging|test|config|dump|api\/key/i.test(p));
    if (juicy.length) {
      findings.push({ severity: 'low', title: 'robots.txt advertises sensitive paths', detail: `Disallow entries name: ${juicy.slice(0, 6).join(', ')}. robots.txt is a public file and is the first thing an attacker reads.`, fix: 'Protect these paths with authentication; do not rely on robots.txt to hide them.' });
    }
  }
  if (!sitemapIdx.ok && !(robots.ok && /sitemap:/i.test(robots.text))) {
    findings.push({ severity: 'info', title: 'no sitemap found', detail: 'Neither /sitemap.xml nor a Sitemap: line in robots.txt.', fix: 'Publish a sitemap so search engines index the pages you care about.' });
  }
  return { id: 'wellknown', title: 'well-known files', data: {
    robots: robots.ok, securityTxt: !!sec, sitemap: sitemapIdx.ok,
    robotsPreview: robots.ok ? robots.text.slice(0, 800) : null,
  }, findings };
}

// Fingerprint the edge and the stack from what the response already says. Deliberately
// evidence-based: every hit names the header or marker that produced it.
const WAF_SIGNS = [
  { name: 'Cloudflare', test: (h) => h['cf-ray'] || /cloudflare/i.test(h['server'] || '') },
  { name: 'Vercel', test: (h) => /vercel/i.test(h['server'] || '') || h['x-vercel-id'] },
  { name: 'Netlify', test: (h) => /netlify/i.test(h['server'] || '') || h['x-nf-request-id'] },
  { name: 'AWS CloudFront', test: (h) => /cloudfront/i.test(h['via'] || '') || h['x-amz-cf-id'] },
  { name: 'Fastly', test: (h) => /fastly/i.test(h['x-served-by'] || h['via'] || '') },
  { name: 'Akamai', test: (h) => h['x-akamai-transformed'] || /akamai/i.test(h['server'] || '') },
  { name: 'Sucuri', test: (h) => h['x-sucuri-id'] },
  { name: 'Imperva/Incapsula', test: (h) => h['x-iinfo'] || /incap/i.test(h['set-cookie'] || '') },
];
const TECH_SIGNS = [
  { name: 'Next.js', test: (h, b) => h['x-nextjs-prerender'] || h['x-powered-by'] === 'Next.js' || /\/_next\/static\//.test(b) },
  { name: 'Nuxt', test: (h, b) => /__NUXT__/.test(b) },
  { name: 'React', test: (h, b) => /data-reactroot|__REACT_DEVTOOLS/.test(b) },
  { name: 'Vue', test: (h, b) => /data-v-[0-9a-f]{8}|__VUE__/.test(b) },
  { name: 'Svelte', test: (h, b) => /svelte-[0-9a-z]{6}/.test(b) },
  { name: 'WordPress', test: (h, b) => /wp-content|wp-includes/.test(b) },
  { name: 'Shopify', test: (h, b) => /cdn\.shopify\.com/.test(b) },
  { name: 'Astro', test: (h, b) => /astro-island|data-astro-/.test(b) },
  { name: 'Google Analytics', test: (h, b) => /gtag\/js|googletagmanager/.test(b) },
  { name: 'Cloudflare Turnstile', test: (h, b) => /challenges\.cloudflare\.com\/turnstile/.test(b) },
];

async function checkFingerprint(host, ctx, surface) {
  const h = surface.headers, b = surface.body || '';
  const edge = WAF_SIGNS.filter((s) => { try { return !!s.test(h); } catch { return false; } }).map((s) => s.name);
  const tech = TECH_SIGNS.filter((s) => { try { return !!s.test(h, b); } catch { return false; } }).map((s) => s.name);
  const findings = [];
  if (!edge.length) {
    findings.push({ severity: 'info', title: 'no CDN or WAF detected in the response', detail: 'Requests appear to reach the origin directly, so the origin absorbs any flood on its own.', fix: 'Consider putting a CDN/WAF in front — it is the cheapest availability control there is.' });
  }
  return { id: 'fingerprint', title: 'edge and stack', data: { edge, tech }, findings };
}

// The page's own description of itself — the surface search engines and social cards read.
async function checkMeta(host, ctx, surface) {
  const b = surface.body || '';
  const pick = (re) => (b.match(re) || [])[1]?.trim() || null;
  const title = pick(/<title[^>]*>([\s\S]{0,300}?)<\/title>/i);
  const description = pick(/<meta[^>]+name=["']description["'][^>]+content=["']([^"']{0,400})["']/i);
  const ogTitle = pick(/<meta[^>]+property=["']og:title["'][^>]+content=["']([^"']{0,300})["']/i);
  const ogImage = pick(/<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']{0,500})["']/i);
  const canonical = pick(/<link[^>]+rel=["']canonical["'][^>]+href=["']([^"']{0,500})["']/i);
  const lang = pick(/<html[^>]+lang=["']([^"']{0,20})["']/i);
  const viewport = /<meta[^>]+name=["']viewport["']/i.test(b);
  const findings = [];
  if (!title) findings.push({ severity: 'medium', title: 'no <title>', detail: 'The tab, the bookmark and the search result all have nothing to show.', fix: 'Add a specific <title> under ~60 characters.' });
  if (!description) findings.push({ severity: 'low', title: 'no meta description', detail: 'Search engines will invent the snippet from page text.', fix: 'Add a 120–160 character description that states the offer.' });
  if (!ogImage) findings.push({ severity: 'low', title: 'no og:image', detail: 'Links shared to social or chat render as a bare grey card.', fix: 'Add a 1200×630 og:image.' });
  if (!canonical) findings.push({ severity: 'info', title: 'no canonical link', detail: 'Duplicate URLs (query strings, trailing slashes) can split ranking signals.', fix: 'Add <link rel="canonical">.' });
  if (!viewport) findings.push({ severity: 'medium', title: 'no viewport meta', detail: 'The page will render zoomed-out and unusable on a phone.', fix: 'Add <meta name="viewport" content="width=device-width, initial-scale=1">.' });
  if (!lang) findings.push({ severity: 'low', title: 'no lang attribute on <html>', detail: 'Screen readers cannot pick the right voice, and right-to-left text will not be handled correctly.', fix: 'Set lang (and dir="rtl" for Hebrew or Arabic).' });
  return { id: 'meta', title: 'page metadata', data: { title, description, ogTitle, ogImage, canonical, lang, viewport }, findings };
}

// Wayback: how long the name has been public. Keyless, public API.
async function checkArchive(host, ctx) {
  const j = await safe(async () => {
    const res = await withTimeout(fetch(`https://archive.org/wayback/available?url=${encodeURIComponent(host)}`), ctx.timeoutMs, 'archive');
    return res.ok ? res.json() : null;
  }, null);
  const snap = j?.archived_snapshots?.closest || null;
  return { id: 'archive', title: 'archive history', data: { archived: !!snap, timestamp: snap?.timestamp || null, url: snap?.url || null }, findings: [] };
}

// ACTIVE — off unless the caller asks and asserts authorization. A TCP connect on a
// short list of service ports; no banner grabbing, no payload, no vulnerability probe.
const COMMON_PORTS = [21, 22, 25, 80, 110, 143, 443, 445, 3000, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 9200, 27017];
const PORT_RISK = {
  21: ['high', 'FTP — credentials in the clear'], 22: ['info', 'SSH'], 23: ['critical', 'Telnet — credentials in the clear'],
  25: ['info', 'SMTP'], 445: ['high', 'SMB exposed to the internet'], 3306: ['high', 'MySQL reachable from the internet'],
  3389: ['high', 'RDP exposed to the internet'], 5432: ['high', 'PostgreSQL reachable from the internet'],
  5900: ['high', 'VNC exposed to the internet'], 6379: ['critical', 'Redis reachable from the internet — often unauthenticated'],
  9200: ['critical', 'Elasticsearch reachable from the internet — often unauthenticated'],
  27017: ['critical', 'MongoDB reachable from the internet — often unauthenticated'],
};
function probePort(host, port, timeoutMs = 2500) {
  return new Promise((res) => {
    const s = netConnect({ host, port });
    const done = (open) => { s.destroy(); res(open); };
    s.setTimeout(timeoutMs, () => done(false));
    s.on('connect', () => done(true));
    s.on('error', () => done(false));
  });
}
async function checkPorts(host, ctx) {
  const results = await Promise.all(COMMON_PORTS.map(async (p) => ({ port: p, open: await probePort(host, p, Math.min(ctx.timeoutMs, 3000)) })));
  const open = results.filter((r) => r.open).map((r) => r.port);
  const findings = [];
  for (const p of open) {
    const risk = PORT_RISK[p];
    if (risk && p !== 80 && p !== 443) {
      findings.push({ severity: risk[0], title: `port ${p} is open`, detail: risk[1], fix: `Close ${p} at the firewall or bind the service to localhost / a private network.` });
    }
  }
  return { id: 'ports', title: 'open service ports', data: { probed: COMMON_PORTS, open }, findings };
}

// ── the scan ────────────────────────────────────────────────────────────────────

export const CHECKS = ['dns', 'dnssec', 'tls', 'http', 'headers', 'cookies', 'mail', 'wellknown', 'fingerprint', 'meta', 'archive', 'ports'];

export async function recon(target, options = {}) {
  const host = normalizeTarget(target);
  const ctx = {
    timeoutMs: options.timeoutMs || DEFAULT_TIMEOUT,
    userAgent: options.userAgent || 'fabius-recon/1.0 (+https://fabius-landing.vercel.app)',
  };
  const want = new Set(options.checks?.length ? options.checks : CHECKS.filter((c) => c !== 'ports'));
  if (options.ports) want.add('ports');
  else want.delete('ports');

  const sections = [];
  const errors = [];
  const run = async (id, fn) => {
    if (!want.has(id)) return null;
    try { const r = await fn(); if (r) sections.push(r); return r; }
    catch (e) { errors.push({ check: id, error: e.message }); return null; }
  };

  // DNS first — mail reuses its records. The response surface is fetched once and
  // shared by every header-derived check.
  const dnsSec = await run('dns', () => checkDns(host, ctx));
  let surface = null;
  try { surface = await fetchSurface(host, ctx); }
  catch (e) { errors.push({ check: 'http', error: e.message }); }

  await Promise.all([
    run('dnssec', () => checkDnssec(host, ctx)),
    run('tls', () => checkTls(host, ctx)),
    run('mail', () => checkMail(host, ctx, dnsSec?.data)),
    run('wellknown', () => checkWellKnown(host, ctx)),
    run('archive', () => checkArchive(host, ctx)),
    run('ports', () => checkPorts(host, ctx)),
    ...(surface ? [
      run('http', () => checkHttp(host, ctx, surface)),
      run('headers', () => checkSecurityHeaders(host, ctx, surface)),
      run('cookies', () => checkCookies(host, ctx, surface)),
      run('fingerprint', () => checkFingerprint(host, ctx, surface)),
      run('meta', () => checkMeta(host, ctx, surface)),
    ] : []),
  ]);

  if (!surface) {
    sections.push({ id: 'http', title: 'HTTP response', data: {}, findings: [{ severity: 'critical', title: 'the site did not answer over HTTPS', detail: `No usable response from https://${host}/.`, fix: 'Confirm the origin is up and serving TLS on 443.' }] });
  }

  const platform = delegatedPlatform(host);
  const findings = sections.flatMap((s) => (s.findings || []).map((f) => {
    if (platform && ZONE_OWNED.has(s.id)) {
      return { ...f, check: s.id, severity: 'info', delegated: platform,
        detail: `${f.detail} (The ${platform} zone is not yours to change — this is context, not a task.)`, fix: '' };
    }
    return { ...f, check: s.id };
  }));
  findings.sort((a, b) => sevRank(a.severity) - sevRank(b.severity));
  const counts = Object.fromEntries(SEVERITY.map((s) => [s, findings.filter((f) => f.severity === s).length]));

  return {
    target: host,
    platform,
    scannedAt: new Date().toISOString(),
    grade: grade(counts),
    counts,
    findings,
    sections: Object.fromEntries(sections.map((s) => [s.id, { title: s.title, data: s.data }])),
    errors,
  };
}

// A single letter, so a scan can be compared to last week's without reading it.
export function grade(counts) {
  const score = 100 - (counts.critical * 30 + counts.high * 12 + counts.medium * 5 + counts.low * 2);
  const s = Math.max(0, score);
  return { score: s, letter: s >= 92 ? 'A' : s >= 80 ? 'B' : s >= 65 ? 'C' : s >= 45 ? 'D' : 'F' };
}

// The human report. Findings first, evidence after — an operator should be able to act
// from the top of the page without scrolling to a JSON dump.
export function formatReport(r, { color = true } = {}) {
  const c = (k, s) => color ? ({ critical: '\x1b[31m', high: '\x1b[31m', medium: '\x1b[33m', low: '\x1b[36m', info: '\x1b[2m', bold: '\x1b[1m', dim: '\x1b[2m', reset: '\x1b[0m' }[k] || '') + s + '\x1b[0m' : s;
  const L = [];
  L.push('');
  L.push(c('bold', `  ${r.target}`) + c('dim', `   scanned ${r.scannedAt}`));
  if (r.platform) L.push(c('dim', `  hosted on ${r.platform} — DNS, DNSSEC and mail records belong to that zone, so those findings are shown as context only`));
  const sevs = SEVERITY.filter((s) => r.counts[s]).map((s) => `${r.counts[s]} ${s}`).join(' · ');
  L.push(`  grade ${c(r.grade.letter === 'A' ? 'info' : r.grade.letter === 'F' ? 'critical' : 'medium', r.grade.letter)}  (${r.grade.score}/100)` +
    (sevs ? ` · ${sevs}` : c('dim', ' · no findings')));
  L.push('');
  if (!r.findings.length) L.push(c('dim', '  nothing to fix — every check passed.'));
  for (const f of r.findings) {
    L.push(`  ${c(f.severity, f.severity.toUpperCase().padEnd(8))} ${c('bold', f.title)}  ${c('dim', '[' + f.check + ']')}`);
    L.push(`           ${f.detail}`);
    if (f.fix) L.push(`           ${c('dim', '→ ' + f.fix)}`);
    L.push('');
  }
  const s = r.sections;
  L.push(c('dim', '  ── evidence ──'));
  if (s.dns) L.push(c('dim', `  A ${(s.dns.data.a || []).join(', ') || '—'} · MX ${(s.dns.data.mx || []).length} · NS ${(s.dns.data.ns || []).join(', ') || '—'}`));
  if (s.tls) L.push(c('dim', `  TLS ${s.tls.data.protocol || '—'} ${s.tls.data.cipher?.name || ''} · issuer ${s.tls.data.issuer?.O || '—'} · ${s.tls.data.daysLeft ?? '—'}d left`));
  if (s.fingerprint) L.push(c('dim', `  edge ${(s.fingerprint.data.edge || []).join(', ') || 'none detected'} · stack ${(s.fingerprint.data.tech || []).join(', ') || 'unidentified'}`));
  if (s.mail) L.push(c('dim', `  SPF ${s.mail.data.spf ? 'yes' : 'no'} · DMARC ${s.mail.data.dmarc ? 'yes' : 'no'} · DKIM selectors ${(s.mail.data.dkimSelectors || []).join(', ') || 'none found'}`));
  if (r.errors.length) L.push(c('dim', `  checks that errored: ${r.errors.map((e) => e.check).join(', ')}`));
  L.push('');
  return L.join('\n');
}
