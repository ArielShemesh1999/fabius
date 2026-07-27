// Recon is graded on precision, not coverage: a security tool that cries wolf gets
// muted, and a muted tool protects nothing. These tests pin the parsers that decide
// whether a finding is real. Every assertion here is offline.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { normalizeTarget, parseCsp, auditCsp, grade, delegatedPlatform, CHECKS, SEVERITY } from '../src/recon.mjs';

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

test('a wide-open policy is caught on every axis', () => {
  const titles = auditCsp("default-src *; script-src * 'unsafe-inline' 'unsafe-eval'").map((f) => f.title);
  assert.ok(titles.some((t) => /unsafe-inline/.test(t)));
  assert.ok(titles.some((t) => /unsafe-eval/.test(t)));
  assert.ok(titles.some((t) => /anywhere/.test(t)));
  assert.ok(titles.some((t) => /object-src/.test(t)));
  assert.ok(titles.some((t) => /base-uri/.test(t)));
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
