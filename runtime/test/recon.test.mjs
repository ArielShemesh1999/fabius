// Recon is graded on precision, not coverage: a security tool that cries wolf gets
// muted, and a muted tool protects nothing. These tests pin the parsers that decide
// whether a finding is real. Every assertion here is offline.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  normalizeTarget, parseCsp, auditCsp, checkSecurityHeaders,
  grade, delegatedPlatform, recon, CHECKS, SEVERITY,
} from '../src/recon.mjs';

test('a target is reduced to a bare hostname', () => {
  for (const [input, want] of [
    ['https://example.com/path?q=1', 'example.com'],
    ['http://Example.COM', 'example.com'],
    ['example.com:8443', 'example.com'],
    ['example.com.', 'example.com'],
    ['  sub.example.co.il/x  ', 'sub.example.co.il'],
  ]) assert.equal(normalizeTarget(input), want);
});

test('a non-hostname is refused rather than scanned', () => {
  for (const bad of ['', 'localhost', 'not a domain', 'http://', '1234']) {
    assert.throws(() => normalizeTarget(bad), undefined, `${bad} should throw`);
  }
});

test('a CSP is parsed per directive, not as one flat string', () => {
  const csp = parseCsp("default-src 'self'; script-src 'self' https://cdn.example.com; object-src 'none'");
  assert.deepEqual(csp['script-src'], ["'self'", 'https://cdn.example.com']);
  assert.deepEqual(csp['object-src'], ["'none'"]);
});

test("'unsafe-inline' in style-src is not reported as a script finding", () => {
  // The exact policy the fabius landing page serves: strict scripts, inline styles.
  const csp = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'";
  assert.deepEqual(auditCsp(csp), []);
});

test("'unsafe-inline' in script-src is reported", () => {
  const titles = auditCsp("script-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'none'").map((f) => f.title);
  assert.ok(titles.some((t) => /unsafe-inline/.test(t)));
});

test('a nonce plus strict-dynamic is treated as the strict policy it is', () => {
  // Browsers ignore 'unsafe-inline' and host sources when a nonce and strict-dynamic
  // are present; flagging them would be a false positive.
  assert.deepEqual(auditCsp("script-src 'nonce-r4nd0m' 'strict-dynamic' 'unsafe-inline' https:; object-src 'none'; base-uri 'none'"), []);
});

test('invalid or empty CSP trust roots cannot suppress real script findings', () => {
  for (const trust of ["'nonce-'", "'sha999-'", "'sha256-'"]) {
    const titles = auditCsp(`script-src ${trust} 'strict-dynamic' 'unsafe-inline' https:; object-src 'none'; base-uri 'none'`)
      .map((f) => f.title);
    assert.ok(titles.some((t) => /unsafe-inline/.test(t)), trust);
    assert.ok(titles.some((t) => /anywhere/.test(t)), trust);
  }
});

test('duplicate CSP directives preserve the browser-effective first occurrence', () => {
  const csp = parseCsp("script-src * 'unsafe-inline'; script-src 'self'; object-src 'none'; base-uri 'none'");
  assert.deepEqual(csp['script-src'], ['*', "'unsafe-inline'"]);
  const titles = auditCsp("script-src * 'unsafe-inline'; script-src 'self'; object-src 'none'; base-uri 'none'")
    .map((f) => f.title);
  assert.ok(titles.some((t) => /unsafe-inline/.test(t)));
  assert.ok(titles.some((t) => /anywhere/.test(t)));
});

test('a wide-open policy is caught on every axis', () => {
  const titles = auditCsp("default-src *; script-src * 'unsafe-inline' 'unsafe-eval'").map((f) => f.title);
  assert.ok(titles.some((t) => /unsafe-inline/.test(t)));
  assert.ok(titles.some((t) => /unsafe-eval/.test(t)));
  assert.ok(titles.some((t) => /anywhere/.test(t)));
  assert.ok(titles.some((t) => /object-src/.test(t)));
  assert.ok(titles.some((t) => /base-uri/.test(t)));
});

test("'none' must be exclusive and broad base/frame sources are not protective", () => {
  for (const policy of [
    "script-src 'self'; object-src 'none' https:; base-uri 'none'",
    "script-src 'self'; object-src 'none' 'self'; base-uri 'none'",
  ]) {
    assert.ok(auditCsp(policy).some((f) => /object-src/.test(f.title)), policy);
  }
  for (const source of ['*', 'https:', 'http:', "'none' https:"]) {
    const findings = auditCsp(`script-src 'self'; object-src 'none'; base-uri ${source}`);
    assert.ok(findings.some((f) => /base-uri is not restrictive/.test(f.title)), source);
  }
  for (const source of ['*', 'https:', 'http:', "'none' https:"]) {
    const findings = auditCsp(`script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors ${source}`);
    assert.ok(findings.some((f) => /frame-ancestors is not restrictive/.test(f.title)), source);
  }
  assert.deepEqual(auditCsp("script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'self' https://embed.example.com"), []);
});

test('clickjacking protection requires an effective directive or valid legacy header', async () => {
  const surface = (csp, xfo = null) => ({
    headers: {
      'strict-transport-security': 'max-age=31536000; includeSubDomains',
      'content-security-policy': csp,
      'x-content-type-options': 'nosniff',
      'referrer-policy': 'strict-origin-when-cross-origin',
      'permissions-policy': 'camera=()',
      ...(xfo ? { 'x-frame-options': xfo } : {}),
    },
  });
  const titles = async (csp, xfo) => (await checkSecurityHeaders('example.com', {}, surface(csp, xfo)))
    .findings.map((f) => f.title);

  assert.ok((await titles("default-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors *", 'DENY'))
    .some((t) => /frame-ancestors is not restrictive/.test(t)), 'broad CSP overrides protective XFO');
  assert.ok((await titles("default-src 'self'; object-src 'none'; base-uri 'none'", 'ALLOWALL'))
    .some((t) => /nothing prevents framing/.test(t)), 'an arbitrary XFO value is not protection');
  assert.ok(!(await titles("default-src 'self'; object-src 'none'; base-uri 'none'", 'DENY'))
    .some((t) => /framing|frame-ancestors/.test(t)), 'valid XFO covers a missing CSP directive');
  assert.ok(!(await titles("default-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"))
    .some((t) => /framing|frame-ancestors/.test(t)), 'restrictive CSP is sufficient');
});

test('script-src falls back to default-src, as the spec says', () => {
  assert.ok(auditCsp("default-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'none'")
    .some((f) => /unsafe-inline/.test(f.title)));
});

test('platform subdomains are recognised so unfixable findings can be demoted', () => {
  assert.equal(delegatedPlatform('myapp.vercel.app'), 'vercel.app');
  assert.equal(delegatedPlatform('x.pages.dev'), 'pages.dev');
  assert.equal(delegatedPlatform('areta.co.il'), null);
  assert.equal(delegatedPlatform('notvercel.app.example.com'), null);
});

test('the grade tracks severity, and the floor holds', () => {
  assert.equal(grade({ critical: 0, high: 0, medium: 0, low: 0, info: 0 }).letter, 'A');
  assert.equal(grade({ critical: 0, high: 0, medium: 1, low: 2, info: 9 }).letter, 'B');
  assert.equal(grade({ critical: 1, high: 0, medium: 0, low: 0, info: 0 }).letter, 'C');
  assert.equal(grade({ critical: 4, high: 4, medium: 4, low: 4, info: 0 }).score, 0);
});

test('the check list is stable and ports stay out of the default scan', () => {
  assert.ok(CHECKS.includes('ports'));
  assert.deepEqual(SEVERITY, ['critical', 'high', 'medium', 'low', 'info']);
});

test('unknown, empty, and implicitly authorised active check selections fail closed', async () => {
  await assert.rejects(() => recon('example.com', { checks: ['bogus'] }), /unknown check/);
  await assert.rejects(() => recon('example.com', { checks: [] }), /at least one/);
  await assert.rejects(() => recon('example.com', { checks: ['ports'] }), /explicit.*ports/i);
});
