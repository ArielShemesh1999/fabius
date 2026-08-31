import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { existsSync, mkdtempSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';
import { parseArgs, validateCommandFlags, positiveNumber } from '../src/cli-args.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const CLI = join(HERE, '..', 'fabius.mjs');

test('boolean flags never consume the task or domain that follows', () => {
  assert.deepEqual(parseArgs(['run', '--act', 'synthetic task']), {
    flags: { act: true }, positional: ['run', 'synthetic task'],
  });
  assert.deepEqual(parseArgs(['route', '--json', 'synthetic task']), {
    flags: { json: true }, positional: ['route', 'synthetic task'],
  });
  assert.deepEqual(parseArgs(['recon', '--ports', 'example.com']), {
    flags: { ports: true }, positional: ['recon', 'example.com'],
  });
  assert.deepEqual(parseArgs(['run', '--remember', 'synthetic task']), {
    flags: { remember: true }, positional: ['run', 'synthetic task'],
  });
});

test('CLI flags are typed, scoped, repeatable only when declared, and support --', () => {
  assert.deepEqual(parseArgs(['run', '--allow-origin=https://a.example', '--allow-origin', 'https://b.example', '--', '--literal-task']), {
    flags: { 'allow-origin': ['https://a.example', 'https://b.example'] },
    positional: ['run', '--literal-task'],
  });
  assert.throws(() => parseArgs(['run', '--mystery']), /unknown flag/);
  assert.throws(() => parseArgs(['run', '--budget']), /requires a value/);
  assert.throws(() => parseArgs(['run', '--act=yes']), /boolean flag/);
  assert.throws(() => parseArgs(['run', '--budget', '1', '--budget', '2']), /only once/);
  assert.throws(() => validateCommandFlags('route', { act: true }), /not valid for route/);
});

test('--read-only rejects every flag that grants mutation, approval, or egress authority', () => {
  for (const conflicting of ['act', 'yes', 'dangerously-approve-everything', 'remember', 'allow-origin']) {
    const value = conflicting === 'allow-origin' ? 'https://example.com' : true;
    assert.throws(
      () => validateCommandFlags('run', { 'read-only': true, [conflicting]: value }),
      new RegExp(`--read-only cannot be combined with --${conflicting}`),
    );
  }

  const cli = spawnSync(
    process.execPath,
    [CLI, 'run', '--act', '--read-only', '--yes', 'synthetic task'],
    { encoding: 'utf8' },
  );
  assert.notEqual(cli.status, 0);
  assert.match(cli.stderr + cli.stdout, /--read-only cannot be combined with --act, --yes/);
});

test('numeric walls reject NaN, infinity, zero, negatives, and fractional step counts', () => {
  for (const bad of ['NaN', 'Infinity', '0', '-1']) assert.throws(() => positiveNumber(bad, 'budget'), /finite positive/);
  assert.throws(() => positiveNumber('1.5', 'steps', { integer: true }), /positive integer/);
  assert.equal(positiveNumber('0.25', 'budget'), 0.25);
  assert.equal(positiveNumber('3', 'steps', { integer: true }), 3);
});

test('--version is a real global flag and unknown flags fail nonzero', () => {
  const version = spawnSync(process.execPath, [CLI, '--version'], { encoding: 'utf8' });
  assert.equal(version.status, 0);
  assert.equal(version.stdout.trim(), '2.6.5');
  const bad = spawnSync(process.execPath, [CLI, 'route', '--unknown', 'task'], { encoding: 'utf8' });
  assert.notEqual(bad.status, 0);
  assert.match(bad.stderr + bad.stdout, /unknown flag/);
  assert.doesNotMatch(bad.stderr + bad.stdout, /at parseArgs|fabius\.mjs:\d+/);
});

test('memory writes require opt-in and cannot be combined with no-memory', () => {
  const conflict = spawnSync(process.execPath, [CLI, 'run', '--remember', '--no-memory', 'task'], { encoding: 'utf8' });
  assert.notEqual(conflict.status, 0);
  assert.match(conflict.stderr + conflict.stdout, /cannot be combined/);
});

test('doctor and read-only memory commands do not scaffold state', () => {
  for (const args of [['doctor'], ['memory', 'list'], ['memory', 'search', 'absent']]) {
    const home = mkdtempSync(join(tmpdir(), 'fabius-cli-readonly-'));
    const env = { ...process.env, FABIUS_HOME: home };
    const r = spawnSync(process.execPath, [CLI, ...args], { encoding: 'utf8', env });
    assert.equal(r.status, 0, `${args.join(' ')}: ${r.stderr}`);
    assert.equal(existsSync(join(home, 'memory')), false, `${args.join(' ')} created memory state`);
    rmSync(home, { recursive: true, force: true });
  }
});

test('positional secrets are rejected before they can be stored', () => {
  const r = spawnSync(process.execPath, [CLI, 'keys', 'set', 'anthropic', 'synthetic-secret'], { encoding: 'utf8' });
  assert.notEqual(r.status, 0);
  assert.match(r.stderr + r.stdout, /never accepted in argv/);
  assert.doesNotMatch(r.stderr + r.stdout, /synthetic-secret/);
});
