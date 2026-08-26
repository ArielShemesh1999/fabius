// Security-boundary regressions use synthetic inputs and disposable directories only.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  mkdtempSync, rmSync, writeFileSync, readFileSync, existsSync, mkdirSync,
  symlinkSync, readdirSync, copyFileSync, statSync,
} from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { spawn } from 'node:child_process';

const home = mkdtempSync(join(tmpdir(), 'fabius-security-home-'));
process.env.FABIUS_HOME = home;

const { makeGate } = await import('../src/approve.mjs');
const { runTool, runCommand, httpGetText, isBlockedAddress, activeTools } = await import('../src/tools.mjs');
const { verifySeal, contractsFor } = await import('../src/skills.mjs');
const { writeMemory, listMemory, deleteMemory, memoryContext } = await import('../src/memory.mjs');
const {
  SKILLS_DIR, MEMORY_DIR, redact, scrubEnvironment,
} = await import('../src/config.mjs');

const context = (jail, options = {}) => ({
  jail, task: 'synthetic security test', scope: 'test', opts: options,
  gate: makeGate({ posture: 'auto', jail, autoNo: true }),
  budget: { execRuns: 0, maxExecRuns: 4 }, changed: new Set(), ranCommands: [],
});

test('memory reads and absent deletes do not create a store', () => {
  assert.equal(existsSync(MEMORY_DIR), false);
  assert.deepEqual(listMemory(), []);
  assert.equal(memoryContext('anything', { mode: 'normal' }), '');
  assert.equal(memoryContext('anything', { mode: 'dampened' }), '');
  assert.equal(deleteMemory('not-there'), false);
  assert.equal(existsSync(MEMORY_DIR), false);
});

test('built-in file tools re-check each canonical file and skip a jail-escaping symlink', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-files-'));
  const outside = mkdtempSync(join(tmpdir(), 'fabius-outside-'));
  writeFileSync(join(outside, 'private.txt'), 'needle-from-outside');
  try { symlinkSync(join(outside, 'private.txt'), join(jail, 'ordinary.txt')); }
  catch { rmSync(jail, { recursive: true, force: true }); rmSync(outside, { recursive: true, force: true }); return; }

  const ctx = context(jail);
  assert.doesNotMatch(await runTool('grep', 'needle-from-outside', ctx), /needle-from-outside/);
  assert.doesNotMatch(await runTool('list', '.', ctx), /ordinary\.txt/);
  rmSync(jail, { recursive: true, force: true });
  rmSync(outside, { recursive: true, force: true });
});

test('dev secret files are denied by direct read, listing, grep, case variants, and aliases', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-dev-secrets-'));
  const devVars = join(jail, '.dev.vars');
  const envrc = join(jail, '.envrc');
  const upper = join(jail, '.DEV.VARS.production');
  writeFileSync(devVars, 'DEV_VARS_SYNTHETIC_NEEDLE=private');
  writeFileSync(envrc, 'export ENVRC_SYNTHETIC_NEEDLE=private');
  writeFileSync(upper, 'UPPER_SYNTHETIC_NEEDLE=private');
  try { symlinkSync(devVars, join(jail, 'ordinary.txt')); }
  catch { rmSync(jail, { recursive: true, force: true }); return; }

  const ctx = context(jail);
  for (const name of ['.dev.vars', '.envrc', '.DEV.VARS.production', 'ordinary.txt']) {
    assert.match(await runTool('read', name, ctx), /denied/, name);
  }
  const listed = await runTool('list', '.', ctx);
  assert.doesNotMatch(listed, /dev\.vars|envrc|ordinary\.txt/i);
  for (const needle of ['DEV_VARS_SYNTHETIC_NEEDLE', 'ENVRC_SYNTHETIC_NEEDLE', 'UPPER_SYNTHETIC_NEEDLE']) {
    assert.doesNotMatch(await runTool('grep', needle, ctx), /private|SYNTHETIC_NEEDLE/);
  }
  rmSync(jail, { recursive: true, force: true });
});

test('write performs a final canonical secret check before opening the file', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-write-'));
  const secret = join(jail, '.env');
  writeFileSync(secret, 'TOKEN=original');
  try { symlinkSync(secret, join(jail, 'notes.txt')); }
  catch { rmSync(jail, { recursive: true, force: true }); return; }

  const out = await runTool('write', 'notes.txt\n---\nTOKEN=overwritten', context(jail));
  assert.match(out, /denied/);
  assert.equal(readFileSync(secret, 'utf8'), 'TOKEN=original');
  rmSync(jail, { recursive: true, force: true });
});

test('write and edit cannot mutate git control data directly or through an alias', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-git-write-'));
  const git = join(jail, '.git');
  const head = join(git, 'HEAD');
  mkdirSync(git);
  writeFileSync(head, 'ref: refs/heads/main\n');
  try { symlinkSync(head, join(jail, 'ordinary.txt')); }
  catch { rmSync(jail, { recursive: true, force: true }); return; }

  const ctx = context(jail);
  assert.match(await runTool('write', '.git/HEAD\n---\nref: refs/heads/attacker', ctx), /denied/);
  assert.match(await runTool('write', 'ordinary.txt\n---\nref: refs/heads/attacker', ctx), /denied/);
  assert.match(await runTool('edit', '.git/HEAD\n<<<OLD\nmain\nOLD>>>\n<<<NEW\nattacker\nNEW>>>', ctx), /denied/);
  assert.equal(readFileSync(head, 'utf8'), 'ref: refs/heads/main\n');
  assert.deepEqual([...ctx.changed], []);
  rmSync(jail, { recursive: true, force: true });
});

test('model shell commands inherit no credential-shaped env and redact output again', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-env-'));
  const value = 'synthetic-secret-material-12345';
  const script = join(jail, 'probe.mjs');
  process.env.FABIUS_TEST_SECRET = value;
  process.env.NODE_OPTIONS = '--require=/definitely/not/a/real/module.cjs';
  process.env.BASH_ENV = join(jail, 'model-controlled-shell-startup');
  writeFileSync(script, `process.stdout.write([process.env.FABIUS_TEST_SECRET || 'absent', process.env.NODE_OPTIONS || 'no-node-options', process.env.BASH_ENV || 'no-bash-env'].join('|'));\nprocess.stderr.write(${JSON.stringify(value)});\n`);
  const result = await runCommand(`node ${JSON.stringify(script)}`, { cwd: jail });
  delete process.env.FABIUS_TEST_SECRET;
  delete process.env.NODE_OPTIONS;
  delete process.env.BASH_ENV;

  assert.equal(result.out, 'absent|no-node-options|no-bash-env');
  assert.doesNotMatch(result.err, /synthetic-secret-material/);
  assert.match(result.err, /redacted/);
  rmSync(jail, { recursive: true, force: true });
});

test('credential-bearing connection env is scrubbed and redacted while public URLs survive', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-connection-env-'));
  const script = join(jail, 'probe.mjs');
  const synthetic = {
    DATABASE_URL: 'postgresql://app_user:db-pass-123@db.example.invalid/app',
    REDIS_URL: 'redis://:redis-pass-456@cache.example.invalid/0',
    SENTRY_DSN: 'https://sentry-public:sentry-secret-789@sentry.example.invalid/42',
    PUBLIC_SITE_URL: 'https://www.example.invalid/catalog',
    PATH: '/synthetic/bin',
    HOME: '/synthetic/home',
    LANG: 'en_US.UTF-8',
  };
  writeFileSync(script,
    `process.stdout.write(JSON.stringify({database:process.env.DATABASE_URL||'absent',redis:process.env.REDIS_URL||'absent',sentry:process.env.SENTRY_DSN||'absent',publicUrl:process.env.PUBLIC_SITE_URL,path:process.env.PATH,home:process.env.HOME,lang:process.env.LANG}));`);

  const child = await runCommand(`${JSON.stringify(process.execPath)} ${JSON.stringify(script)}`, { cwd: jail, env: synthetic });
  assert.deepEqual(JSON.parse(child.out), {
    database: 'absent', redis: 'absent', sentry: 'absent',
    publicUrl: synthetic.PUBLIC_SITE_URL,
    path: synthetic.PATH, home: synthetic.HOME, lang: synthetic.LANG,
  });
  const scrubbed = scrubEnvironment(synthetic);
  for (const name of ['DATABASE_URL', 'REDIS_URL', 'SENTRY_DSN']) assert.equal(name in scrubbed, false, name);
  assert.equal(scrubbed.PUBLIC_SITE_URL, synthetic.PUBLIC_SITE_URL);

  const prior = Object.fromEntries(Object.keys(synthetic).map((name) => [name, process.env[name]]));
  try {
    for (const [name, value] of Object.entries(synthetic)) process.env[name] = value;
    const raw = `${synthetic.DATABASE_URL}\n${synthetic.REDIS_URL}\n${synthetic.SENTRY_DSN}\n${synthetic.PUBLIC_SITE_URL}`;
    const safe = redact(raw);
    for (const value of [synthetic.DATABASE_URL, synthetic.REDIS_URL, synthetic.SENTRY_DSN]) {
      assert.doesNotMatch(safe, new RegExp(value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
    }
    assert.match(safe, /redacted/);
    assert.match(safe, new RegExp(synthetic.PUBLIC_SITE_URL.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  } finally {
    for (const [name, value] of Object.entries(prior)) {
      if (value === undefined) delete process.env[name];
      else process.env[name] = value;
    }
  }
  rmSync(jail, { recursive: true, force: true });
});

test('recall is absent by default and its executor fails closed for disabled routes', async () => {
  assert.equal(activeTools({}).includes('recall'), false);
  assert.equal(activeTools({ recall: false }).includes('recall'), false);
  assert.equal(activeTools({ recall: true }).includes('recall'), true);

  const jail = mkdtempSync(join(tmpdir(), 'fabius-recall-boundary-'));
  const base = context(jail);
  assert.match(await runTool('recall', 'anything', { ...base, route: { recall: 'off' } }), /denied/);
  assert.match(await runTool('recall', 'anything', {
    ...base, opts: { noMemory: true }, route: { recall: 'normal' },
  }), /denied/);
  rmSync(jail, { recursive: true, force: true });
});

test('a timeout kills the whole spawned process group, not only its shell', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-timeout-'));
  const marker = join(jail, 'survived.txt');
  const writer = join(jail, 'writer.mjs');
  const blocker = join(jail, 'blocker.mjs');
  writeFileSync(writer, `import { writeFileSync } from 'node:fs'; setTimeout(() => writeFileSync(process.argv[2], 'survived'), 350);`);
  writeFileSync(blocker, 'setTimeout(() => {}, 5000);');
  const result = await runCommand(
    `node ${JSON.stringify(writer)} ${JSON.stringify(marker)} & node ${JSON.stringify(blocker)}`,
    { cwd: jail, timeoutMs: 80 },
  );
  await new Promise((resolve) => setTimeout(resolve, 550));
  assert.equal(result.killed, true);
  assert.equal(existsSync(marker), false, 'a grandchild must not outlive the timed-out shell');
  rmSync(jail, { recursive: true, force: true });
});

test('hexadecimal IPv4-mapped IPv6 cannot bypass private-address blocking', () => {
  for (const ip of ['::ffff:7f00:1', '0:0:0:0:0:ffff:7f00:1', '::ffff:127.0.0.1', '::ffff:a9fe:a9fe', '::ffff:0a00:1']) {
    assert.equal(isBlockedAddress(ip), true, ip);
  }
  assert.equal(isBlockedAddress('::ffff:5db8:d822'), false); // 93.184.216.34
});

test('each redirect origin is authorised before DNS or the next request', async () => {
  const first = 'http://93.184.216.34/start';
  const second = 'http://142.250.72.14/final';
  const originalFetch = globalThis.fetch;
  const calls = [];
  let redirectBodiesCancelled = 0;
  globalThis.fetch = async (url) => {
    calls.push(String(url));
    if (calls.length % 2 === 1) {
      const body = new ReadableStream({ cancel() { redirectBodiesCancelled++; } });
      return new Response(body, { status: 302, headers: { location: second } });
    }
    return new Response('safe body', { status: 200, headers: { 'content-type': 'text/plain' } });
  };
  try {
    const deniedGate = makeGate({ posture: 'auto', jail: process.cwd(), autoNo: true });
    const denied = await httpGetText(first, { gate: deniedGate, allowedOrigins: ['http://93.184.216.34'] });
    assert.match(denied, /denied/);
    assert.equal(calls.length, 1, 'the unknown redirect origin must not be contacted');
    assert.deepEqual(deniedGate.log.map((x) => x.approved), [true, false]);

    calls.length = 0;
    const allowedGate = makeGate({ posture: 'auto', jail: process.cwd(), autoNo: true });
    const allowed = await httpGetText(first, {
      gate: allowedGate,
      allowedOrigins: ['http://93.184.216.34', 'http://142.250.72.14'],
    });
    assert.match(allowed, /safe body/);
    assert.equal(calls.length, 2);
    assert.equal(redirectBodiesCancelled, 2, 'every redirect response body must release its socket');
  } finally { globalThis.fetch = originalFetch; }
});

test('fetch reads a byte-bounded prefix and cancels hostile or non-text bodies', async () => {
  const originalFetch = globalThis.fetch;
  let produced = 0, largeCancelled = 0, binaryCancelled = 0;
  try {
    globalThis.fetch = async () => new Response(new ReadableStream({
      pull(controller) {
        produced++;
        if (produced > 1000) controller.close();
        else controller.enqueue(new TextEncoder().encode('A'.repeat(64)));
      },
      cancel() { largeCancelled++; },
    }), { status: 200, headers: { 'content-type': 'text/plain' } });

    const bounded = await httpGetText('http://93.184.216.34/large', { maxBytes: 100 });
    assert.equal((bounded.match(/A/g) || []).length, 100);
    assert.ok(produced < 10, `stream should stop near the cap, not consume ${produced} chunks`);
    assert.equal(largeCancelled, 1);

    globalThis.fetch = async () => new Response(new ReadableStream({
      pull(controller) { controller.enqueue(new Uint8Array(64)); },
      cancel() { binaryCancelled++; },
    }), { status: 200, headers: { 'content-type': 'application/octet-stream' } });
    const binary = await httpGetText('http://93.184.216.34/binary');
    assert.match(binary, /not text/);
    assert.equal(binaryCancelled, 1);
  } finally { globalThis.fetch = originalFetch; }
});

test('deep recon stays operator-only and outside the model tool menu', () => {
  assert.equal(activeTools({}).includes('recon'), false);
  assert.equal(activeTools({ act: true }).includes('recon'), false);
});

test('a custom skills directory is bound to its own bytes under sealed-only mode', () => {
  const stage = mkdtempSync(join(tmpdir(), 'fabius-sealed-skills-'));
  for (const name of readdirSync(SKILLS_DIR)) {
    const source = join(SKILLS_DIR, name, 'SKILL.md');
    if (!existsSync(source)) continue;
    mkdirSync(join(stage, name), { recursive: true });
    copyFileSync(source, join(stage, name, 'SKILL.md'));
  }
  const rel = 'skills/fabius-parcus/SKILL.md';
  assert.equal(verifySeal(stage).drift.includes(rel), false, 'fixture starts with the sealed bytes');
  writeFileSync(join(stage, 'fabius-parcus', 'SKILL.md'), '\nTAMPERED\n', { flag: 'a' });
  assert.equal(verifySeal(stage).drift.includes(rel), true);
  assert.throws(
    () => contractsFor({ domains: [], layers: ['fabius-parcus'] }, { dir: stage, sealedOnly: true }),
    /seal mismatch/,
  );
  rmSync(stage, { recursive: true, force: true });
});

test('colliding memory slugs keep distinct pages and private atomic state files', () => {
  const first = writeMemory({ title: 'Collision!', body: 'First durable fact.' });
  const second = writeMemory({ title: 'Collision?', body: 'Second durable fact.' });
  assert.notEqual(first.name, second.name);
  assert.equal(listMemory().filter((m) => m.title.startsWith('Collision')).length, 2);
  assert.equal(writeMemory({ title: 'Collision!', body: 'Updated first fact.' }).name, first.name);
  for (const path of [first.path, second.path, join(MEMORY_DIR, 'MEMORY.md'), join(MEMORY_DIR, 'log.md')]) {
    assert.equal(statSync(path).mode & 0o077, 0, path);
  }
  assert.equal(deleteMemory('Collision?'), true, 'a colliding title deletes its own suffixed page');
  assert.deepEqual(listMemory().filter((m) => m.title.startsWith('Collision')).map((m) => m.title), ['Collision!']);
  const history = join(MEMORY_DIR, '.history');
  const snapshots = readdirSync(history).map((f) => readFileSync(join(history, f), 'utf8')).join('\n');
  assert.match(snapshots, /First durable fact/);
  assert.match(snapshots, /Second durable fact/);
});

test('concurrent processes serialize colliding memory pages and index updates', async () => {
  const raceHome = mkdtempSync(join(tmpdir(), 'fabius-memory-race-'));
  const moduleUrl = new URL('../src/memory.mjs', import.meta.url).href;
  const program = `const { writeMemory } = await import(${JSON.stringify(moduleUrl)}); writeMemory({ title: process.argv[1], body: 'Concurrent durable fact for ' + process.argv[1] });`;
  const marks = ['!', '?', '#', '@', '$', '%', '^', '&', '*', '+', '=', ','];
  const runChild = (mark) => new Promise((resolve, reject) => {
    const child = spawn(process.execPath, ['--input-type=module', '-e', program, `Concurrent collision${mark}`], {
      env: { ...process.env, FABIUS_HOME: raceHome }, stdio: ['ignore', 'ignore', 'pipe'],
    });
    let err = '';
    child.stderr.on('data', (d) => { err += d; });
    child.on('error', reject);
    child.on('close', (code) => code === 0 ? resolve() : reject(new Error(`memory child exited ${code}: ${err}`)));
  });
  await Promise.all(marks.map(runChild));

  const dir = join(raceHome, 'memory');
  const pages = readdirSync(dir).filter((f) => f.endsWith('.md') && !['MEMORY.md', 'log.md'].includes(f));
  const index = readFileSync(join(dir, 'MEMORY.md'), 'utf8');
  assert.equal(pages.length, marks.length);
  assert.equal((index.match(/<!-- fabius-memory/g) || []).length, marks.length);
  assert.equal(existsSync(join(dir, '.write.lock')), false);
  rmSync(raceHome, { recursive: true, force: true });
});

test('dampened recall is high-confidence and index-only; default context is off', () => {
  writeMemory({
    title: 'High-confidence index signal', score: 95,
    body: 'Visible index summary. deep-body-only-token must not be read in dampened mode.',
  });
  writeMemory({
    title: 'Tentative quasar marker', score: 80,
    body: 'Low-confidence summary.',
  });
  assert.equal(memoryContext('High-confidence index signal'), '', 'no recall signal fails closed');
  assert.match(memoryContext('High-confidence index signal', { mode: 'dampened' }), /High-confidence index signal/);
  assert.equal(memoryContext('deep-body-only-token', { mode: 'dampened' }), '');
  assert.match(memoryContext('deep-body-only-token', { mode: 'normal' }), /High-confidence index signal/);
  assert.equal(memoryContext('quasar', { mode: 'dampened' }), '');
  assert.match(memoryContext('quasar', { mode: 'normal' }), /Tentative quasar marker/);
});

test.after(() => rmSync(home, { recursive: true, force: true }));
