// Router, parsers, redaction, memory. All offline, all deterministic.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync, writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const FAKE = { keys: { anthropic: 'sk-ant-test-000000000000000000' }, provider: 'anthropic', approve: 'never', budgetUsd: 2, maxSteps: 6, maxCodeRuns: 2 };

const { route } = await import('../src/route.mjs');
const { parseAgentAction, parseVerdict, isStubDeliverable, extractCodeBlock } = await import('../src/util.mjs');
const { stripHtml, walk, activeTools } = await import('../src/tools.mjs');

test('the router sends security work to praesidium on the strong tier', () => {
  const r = route('audit the auth flow for injection vulnerabilities', { cfg: FAKE });
  assert.ok(r.domains.includes('fabius-praesidium'));
  assert.equal(r.tier, 'frontier');
});

test('the router sends mechanical work to the cheap tier', () => {
  const r = route('reformat this list', { cfg: FAKE });
  assert.equal(r.tier, 'fast');
});

test('the always-on lean core rides every route', () => {
  for (const t of ['reformat this list', 'design a landing page', 'backtest this strategy']) {
    assert.ok(route(t, { cfg: FAKE }).layers.includes('fabius-parcus'), t);
  }
});

test('the ladder climbs only as far as the task demands, and every rung is reachable', () => {
  assert.equal(route('rename this variable', { cfg: FAKE }).rung, 'inline');
  assert.equal(route('fetch the pricing page', { cfg: FAKE }).rung, 'tool');
  assert.equal(route('recall what we decided about the schema', { cfg: FAKE }).rung, 'retrieval');
  assert.equal(route('plan the migration in phases', { cfg: FAKE }).rung, 'plan');
  assert.equal(route('plan the migration then query the api for each table', { cfg: FAKE }).rung, 'subagent');
});

test('an explicit tier overrides the heuristic', () => {
  assert.equal(route('reformat this list', { cfg: FAKE, tier: 'frontier' }).tier, 'frontier');
});

test('a keyword does not fire inside a longer word, or inside a phrase another layer owns', () => {
  const d = (t) => route(t, { cfg: FAKE }).domains;
  assert.deepEqual(d('add a unique constraint to the users table'), []);      // not 'train'
  assert.deepEqual(d('hold the Apple restraint in the hero'), ['fabius-decor']);
  assert.deepEqual(d('read the file and summarize it'), []);                  // not 'ad '
  assert.deepEqual(d('what is the market doing for NVDA this quarter'), ['fabius-fortuna']);
  assert.deepEqual(d('write the launch copy for our new product'), ['fabius-mercatus']);
  assert.deepEqual(d('train a classifier on this data'), ['fabius-doctrina']); // no false negative
});

test('a conjunction does not buy the frontier tier, but a real fork still does', () => {
  assert.equal(route('rename the button label to Save or Cancel', { cfg: FAKE }).tier, 'fast');
  // Long enough that the short-question rule cannot carry it — this asserts the or-clause itself.
  assert.equal(route('do we ship the modal now or later for checkout?', { cfg: FAKE }).tier, 'frontier');
  // A modal decision keeps the tier without needing a question mark.
  assert.equal(route('should the public API be versioned before we ship it', { cfg: FAKE }).tier, 'frontier');
  assert.equal(route('which caching layer do we pick for the session store', { cfg: FAKE }).tier, 'frontier');
  // Indifference is not a fork — it must not reach the frontier tier.
  assert.equal(route('either way works for the button label', { cfg: FAKE }).tier, 'mid');
});

test('a layer keeps its own evidence when it also fires outside a longer phrase', () => {
  const d = (t) => route(t, { cfg: FAKE }).domains;
  assert.deepEqual(d('improve the design; also fix the level design').sort(), ['fabius-decor', 'fabius-ludus']);
  assert.deepEqual(d('market this product to the market we identified').sort(), ['fabius-fortuna', 'fabius-mercatus']);
  // ...but a lone occupant of a longer phrase still yields to its owner.
  assert.deepEqual(d('tune the level design pacing'), ['fabius-ludus']);
});

test('oauth still buys the strong tier', () => {
  assert.equal(route('add oauth to the login flow', { cfg: FAKE }).tier, 'frontier');
});

test('no key means nothing fires — and the router says so instead of pretending', () => {
  const r = route('anything', { cfg: { keys: {} } });
  assert.equal(r.fireable, false);
  assert.match(r.rationale.select, /no provider keyed/);
});

test('an agent turn is parsed out of surrounding prose', () => {
  const a = parseAgentAction('Sure!\n{"think":"look first","tool":"read","input":"src/a.js"}\nthanks', ['read', 'deliver']);
  assert.equal(a.tool, 'read');
  assert.equal(a.input, 'src/a.js');
});

test('a tool that is not enabled this run degrades to deliver, never to an error', () => {
  const a = parseAgentAction('{"tool":"shell","input":"rm -rf /"}', ['read', 'deliver']);
  assert.equal(a.tool, 'deliver');
});

test('a non-JSON reply still finishes the run as a delivery', () => {
  const a = parseAgentAction('here is the answer, plainly written', ['read', 'deliver']);
  assert.equal(a.tool, 'deliver');
  assert.match(a.input, /plainly written/);
});

test('nested braces in the action do not break the parser', () => {
  const a = parseAgentAction('{"think":"x","tool":"write","input":"a.json\\n---\\n{\\"k\\": {\\"n\\": 1}}"}', ['write', 'deliver']);
  assert.equal(a.tool, 'write');
  assert.match(a.input, /"n": 1/);
});

test('a verdict is clamped into range', () => {
  assert.deepEqual(parseVerdict('{"pass":true,"score":420,"issues":[],"fix":""}').score, 100);
  assert.equal(parseVerdict('nonsense'), null);
});

test('a pointer-stub is detected; a real artifact is not', () => {
  assert.equal(isStubDeliverable('See the plan above for details.'), true);
  assert.equal(isStubDeliverable(''), true);
  assert.equal(isStubDeliverable('x'.repeat(500)), false);
});

test('the execution oracle only claims languages it can actually run', () => {
  assert.equal(extractCodeBlock('```python\nprint(1)\n```').lang, 'python');
  assert.equal(extractCodeBlock('```js\nconsole.log(1)\n```').lang, 'node');
  assert.equal(extractCodeBlock('```rust\nfn main(){}\n```').lang, null);
  assert.equal(extractCodeBlock('no code here'), null);
});

test('html is reduced to readable text', () => {
  const t = stripHtml('<html><head><style>a{}</style><script>evil()</script></head><body><h1>Title</h1><p>One</p><p>Two</p></body></html>');
  assert.match(t, /Title/);
  assert.doesNotMatch(t, /evil|a\{\}/);
});

test('capability sets are least-privilege by default', () => {
  const readOnly = activeTools({});
  assert.ok(!readOnly.includes('shell') && !readOnly.includes('write'));
  assert.ok(readOnly.includes('read') && readOnly.includes('fetch'));
  const acting = activeTools({ act: true });
  assert.ok(acting.includes('shell') && acting.includes('write'));
  assert.ok(!activeTools({ offline: true }).includes('fetch'));
});

test('the tree walk skips the directories that are pure noise', () => {
  const dir = mkdtempSync(join(tmpdir(), 'fabius-walk-'));
  mkdirSync(join(dir, 'node_modules'), { recursive: true });
  mkdirSync(join(dir, 'src'), { recursive: true });
  writeFileSync(join(dir, 'node_modules', 'junk.js'), '');
  writeFileSync(join(dir, 'src', 'real.js'), '');
  const files = walk(dir);
  assert.ok(files.some((f) => f.endsWith('real.js')));
  assert.ok(!files.some((f) => f.includes('node_modules')));
  rmSync(dir, { recursive: true, force: true });
});

test('provider keys never survive into an observation', async () => {
  const home = mkdtempSync(join(tmpdir(), 'fabius-home-'));
  process.env.FABIUS_HOME = home;
  process.env.ANTHROPIC_API_KEY = 'sk-ant-api03-REALKEYMATERIAL0000000';
  const { redact } = await import('../src/config.mjs');
  const out = redact('the config says ANTHROPIC_API_KEY=sk-ant-api03-REALKEYMATERIAL0000000 ok');
  assert.doesNotMatch(out, /REALKEYMATERIAL/);
  assert.match(out, /redacted/);
  // …and a key-shaped string we were never told about is caught too.
  assert.doesNotMatch(redact('found hf_abcdefghijklmnopqrstuvwx in a file'), /abcdefghijklmnop/);
  delete process.env.ANTHROPIC_API_KEY;
  rmSync(home, { recursive: true, force: true });
});

test('the seal check notices an ADDED contract, not just a changed one', async () => {
  const { verifySeal, loadSkills } = await import('../src/skills.mjs');
  const { mkdtempSync, writeFileSync, mkdirSync, rmSync, cpSync, existsSync } = await import('node:fs');
  const { join } = await import('node:path');
  const { tmpdir } = await import('node:os');
  const { SKILLS_DIR } = await import('../src/config.mjs');

  const clean = verifySeal();
  if (!clean.available) return;                      // no manifest in this checkout
  assert.deepEqual(clean.unsealed, [], 'baseline must be clean');

  // Drop an intruder into a COPY of the tree — never mutate the real skills dir.
  const stage = mkdtempSync(join(tmpdir(), 'fabius-skills-'));
  cpSync(SKILLS_DIR, stage, { recursive: true });
  mkdirSync(join(stage, 'zz-probe'), { recursive: true });
  writeFileSync(join(stage, 'zz-probe', 'SKILL.md'), '---\nname: zz-probe\ndescription: intruder\n---\n<!-- provenance fab1-copied -->\n');
  const dirty = verifySeal(stage);
  assert.deepEqual(dirty.unsealed, ['skills/zz-probe/SKILL.md'], 'an added contract must be reported');
  assert.equal(dirty.ok, false);
  rmSync(stage, { recursive: true, force: true });
});
