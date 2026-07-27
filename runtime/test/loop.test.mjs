// The loop, end to end, with a scripted model. No key, no network, no spend — every
// rule seam (R8 rework, R14 repeat-probe nudge, M11 stub gate, M12 recall stand-down),
// the tool executor, the permission gate and the memory decision all fire for real.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync, writeFileSync, existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const home = mkdtempSync(join(tmpdir(), 'fabius-home-'));
process.env.FABIUS_HOME = home;

const { run } = await import('../src/loop.mjs');
const { listMemory } = await import('../src/memory.mjs');

const CFG = { keys: { anthropic: 'sk-ant-test-000000000000000000' }, provider: 'anthropic',
              approve: 'never', budgetUsd: 5, maxSteps: 8, maxCodeRuns: 2, workdir: null };

// A model that replays a script. Anything past the end delivers, so a loop that runs
// long fails loudly instead of hanging.
function scripted(turns) {
  let i = 0;
  const seen = [];
  const fn = async ({ system, messages }) => {
    seen.push({ system, last: messages[messages.length - 1].content });
    const out = i < turns.length ? turns[i++] : 'done.';
    return { ok: true, output: typeof out === 'function' ? out(messages) : out, status: 'done',
             usage: { input_tokens: 100, output_tokens: 50 } };
  };
  fn.seen = seen;
  fn.calls = () => i;
  return fn;
}
const verdictOf = (score) => JSON.stringify({ pass: score >= 70, score, issues: score >= 70 ? [] : ['thin'], fix: score >= 70 ? '' : 'add the missing section' });
const ART = 'x'.repeat(600);

test('a run routes, delivers, and reviews', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-jail-'));
  const llm = scripted([
    JSON.stringify({ think: 'straight to it', tool: 'deliver', input: ART }),
    verdictOf(90),
  ]);
  const res = await run('write a haiku about lean code', { cfg: CFG, jail, callLLM: llm, remember: false });
  assert.equal(res.output, ART);
  assert.equal(res.verdict.score, 90);
  assert.ok(res.fired.includes('R1'));
  rmSync(jail, { recursive: true, force: true });
});

test('the routed contracts are actually handed to the model', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-jail-'));
  const llm = scripted([JSON.stringify({ tool: 'deliver', input: ART }), verdictOf(90)]);
  const res = await run('design a landing page hero', { cfg: CFG, jail, callLLM: llm, remember: false });
  const prompt = llm.seen[0].last;
  assert.match(prompt, /<<<CONTRACT fabius-parcus>>>/);
  assert.match(prompt, /<<<CONTRACT fabius-decor>>>/);
  assert.ok(res.route.layers.includes('fabius-decor'));
  rmSync(jail, { recursive: true, force: true });
});

test('a tool call executes for real and its observation feeds back', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-jail-'));
  writeFileSync(join(jail, 'note.txt'), 'the secret ingredient is salt');
  const llm = scripted([
    JSON.stringify({ think: 'read it', tool: 'read', input: 'note.txt' }),
    JSON.stringify({ tool: 'deliver', input: ART }),
    verdictOf(85),
  ]);
  await run('read note.txt and summarise', { cfg: CFG, jail, callLLM: llm, remember: false });
  const fedBack = llm.seen[1].last;
  assert.match(fedBack, /the secret ingredient is salt/);
  rmSync(jail, { recursive: true, force: true });
});

test('read-only mode refuses a write, and the run continues', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-jail-'));
  const llm = scripted([
    JSON.stringify({ tool: 'write', input: 'out.txt\n---\nhello' }),
    JSON.stringify({ tool: 'deliver', input: ART }),
    verdictOf(80),
  ]);
  const res = await run('create out.txt', { cfg: CFG, jail, callLLM: llm, act: false, remember: false });
  // `write` is not even offered when acting is off, so the action degrades to deliver.
  assert.equal(existsSync(join(jail, 'out.txt')), false);
  assert.ok(res.output.length > 0);
  rmSync(jail, { recursive: true, force: true });
});

test('acting mode writes the file when the gate approves', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-jail-'));
  const llm = scripted([
    JSON.stringify({ tool: 'write', input: 'out.txt\n---\nhello from fabius' }),
    JSON.stringify({ tool: 'deliver', input: ART }),
    verdictOf(80),
  ]);
  const res = await run('create out.txt', { cfg: CFG, jail, callLLM: llm, act: true, approve: 'auto', remember: false });
  assert.equal(readFileSync(join(jail, 'out.txt'), 'utf8'), 'hello from fabius');
  assert.deepEqual(res.changed, ['out.txt']);
  rmSync(jail, { recursive: true, force: true });
});

test('a write outside the working directory is refused even in autonomous mode', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-jail-'));
  const outside = join(tmpdir(), 'fabius-should-not-exist.txt');
  const llm = scripted([
    JSON.stringify({ tool: 'write', input: `../fabius-should-not-exist.txt\n---\nescaped` }),
    JSON.stringify({ tool: 'deliver', input: ART }),
    verdictOf(80),
  ]);
  const res = await run('write outside', { cfg: CFG, jail, callLLM: llm, act: true, approve: 'auto', remember: false });
  assert.equal(existsSync(outside), false);
  assert.match(llm.seen[1].last, /denied/);
  assert.deepEqual(res.changed, []);
  rmSync(jail, { recursive: true, force: true });
});

test('R8 — a failed review earns exactly one rework', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-jail-'));
  const llm = scripted([
    JSON.stringify({ tool: 'deliver', input: ART }),
    verdictOf(40),               // first review fails
    'y'.repeat(600),             // the rework
    verdictOf(95),               // second review passes
  ]);
  const res = await run('write the deployment checklist', { cfg: CFG, jail, callLLM: llm, remember: false });
  assert.ok(res.fired.includes('R8'));
  assert.equal(res.verdict.score, 95);
  assert.match(res.output, /^y+$/);
  assert.equal(llm.calls(), 4, 'exactly one rework, not a loop');
  rmSync(jail, { recursive: true, force: true });
});

test('M11 — a pointer-stub is sent back for a complete artifact', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-jail-'));
  const llm = scripted([
    JSON.stringify({ tool: 'deliver', input: 'See the plan above for the full details.' }),
    ART,                          // the forced complete-artifact turn
    verdictOf(88),
  ]);
  const res = await run('write the migration plan', { cfg: CFG, jail, callLLM: llm, remember: false });
  assert.ok(res.fired.includes('M11'));
  assert.equal(res.output, ART);
  rmSync(jail, { recursive: true, force: true });
});

test('R14 — a repeated probe earns one nudge', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-jail-'));
  const probe = JSON.stringify({ tool: 'route', input: 'the same thing' });
  const llm = scripted([probe, probe, JSON.stringify({ tool: 'deliver', input: ART }), verdictOf(80)]);
  const res = await run('plan and query the api', { cfg: CFG, jail, callLLM: llm, remember: false });
  assert.ok(res.fired.includes('R14'));
  assert.match(llm.seen[2].last, /R14/);
  rmSync(jail, { recursive: true, force: true });
});

test('M12 — security work reads no memory', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-jail-'));
  const llm = scripted([JSON.stringify({ tool: 'deliver', input: ART }), verdictOf(80)]);
  const res = await run('threat-model the payment flow', { cfg: CFG, jail, callLLM: llm, remember: false });
  assert.ok(res.fired.includes('M12'));
  assert.doesNotMatch(llm.seen[0].last, /binding precedent/);
  rmSync(jail, { recursive: true, force: true });
});

test('the memory gate compounds a verified decision and refuses an unverified one', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-jail-'));
  const decision = 'We decided to use Postgres instead of DynamoDB because the access patterns are relational and the join cost dominates. ' + 'x'.repeat(300);

  const pass = scripted([JSON.stringify({ tool: 'deliver', input: decision }), verdictOf(85)]);
  const a = await run('choose the datastore for the new service', { cfg: CFG, jail, callLLM: pass });
  assert.equal(a.proposal.write, true);
  assert.equal(listMemory().length, 1);

  const fail = scripted([JSON.stringify({ tool: 'deliver', input: decision }), verdictOf(55), decision, verdictOf(55)]);
  const b = await run('choose the cache layer for the new service', { cfg: CFG, jail, callLLM: fail });
  assert.equal(b.proposal.write, false);
  assert.match(b.proposal.reason, /unverified/);
  assert.equal(listMemory().length, 1, 'the unverified run must not compound');
  rmSync(jail, { recursive: true, force: true });
});

test('the budget wall stops the run instead of spending past it', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-jail-'));
  const probe = JSON.stringify({ tool: 'route', input: 'again' });
  const llm = scripted(Array(20).fill(probe));
  const res = await run('plan and query the api repeatedly', {
    cfg: { ...CFG, maxSteps: 20 }, jail, callLLM: llm, remember: false,
    budgetUsd: 0.002,   // a couple of calls at Fable rates
  });
  assert.ok(llm.calls() < 20, `stopped early (${llm.calls()} calls)`);
  assert.ok(res.cost <= 0.02);
  rmSync(jail, { recursive: true, force: true });
});

test('the local execution oracle overrules a generous reviewer', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-jail-'));
  const broken = '```python\nraise SystemExit(3)\n```\n' + 'x'.repeat(400);
  const llm = scripted([
    JSON.stringify({ tool: 'deliver', input: broken }),
    verdictOf(95),                     // the judge loves it
    '```python\nprint("ok")\n```\n' + 'x'.repeat(400),
    verdictOf(95),
  ]);
  const res = await run('write a python script', { cfg: CFG, jail, callLLM: llm, act: true, approve: 'auto', remember: false });
  // The first artifact exits 3 → the run must not have accepted it at 95.
  assert.ok(res.fired.includes('R8'), 'a failing oracle forces the rework');
  assert.equal(res.verdict.execVerified, true);
  rmSync(jail, { recursive: true, force: true });
});

test.after(() => rmSync(home, { recursive: true, force: true }));
