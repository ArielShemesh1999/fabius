import { test } from 'node:test';
import assert from 'node:assert/strict';
import { route } from '../src/route.mjs';
import { availableProviders, resolveModel } from '../src/providers.mjs';

const CFG = { keys: { anthropic: 'sk-ant-test-000000000000000000' }, provider: 'anthropic' };

test('Hebrew routing exercises the same axes and owners as English', () => {
  const cases = [
    ['עצב דף נחיתה למוצר חדש ובנה תוכנית עבודה', 'fabius-decor', 'plan'],
    ['בדוק את האבטחה של זרימת ההתחברות', 'fabius-praesidium', 'tool'],
    ['נתח את תיק ההשקעות והסיכון', 'fabius-fortuna', 'inline'],
    ['תזכור את ההחלטה הזאת וכתוב אותה לוויקי', 'fabius-archivum', 'retrieval'],
  ];
  for (const [task, owner, rung] of cases) {
    const r = route(task, { cfg: CFG });
    assert.ok(r.domains.includes(owner), `${task} should route to ${owner}`);
    assert.equal(r.rung, rung, task);
  }
  const broad = route('הרץ בדיקות על הריפו ותכנן שיפור מקצה לקצה', { cfg: CFG });
  assert.equal(broad.rung, 'subagent');
  assert.ok(!broad.layers.includes('fabius-cohors'), 'using tools is machinery, not agent-engineering ownership');
  assert.ok(broad.layers.includes('fabius-disciplina'));
});

test('build, fix, and test work loads Disciplina without inventing Cohors ownership', () => {
  const build = route('build a landing page', { cfg: CFG });
  assert.equal(build.rung, 'tool');
  assert.ok(build.layers.includes('fabius-disciplina'));
  assert.ok(build.layers.includes('fabius-decor'));
  assert.ok(!build.layers.includes('fabius-cohors'));

  const testRun = route('run tests for this repository', { cfg: CFG });
  assert.equal(testRun.rung, 'tool');
  assert.ok(testRun.layers.includes('fabius-disciplina'));
  assert.ok(!testRun.layers.includes('fabius-cohors'));

  const agents = route('orchestrate a multi-agent code review', { cfg: CFG });
  assert.ok(agents.layers.includes('fabius-cohors'), 'explicit agent engineering belongs to Cohors');

  for (const ordinary of ['have the agent run tests', 'orchestrate a webhook workflow']) {
    assert.ok(!route(ordinary, { cfg: CFG }).layers.includes('fabius-cohors'), ordinary);
  }
});

test('fresh-eyes work explicitly suppresses recall in both languages', () => {
  for (const task of [
    'remember the last security decision and audit this incident',
    'תזכור את ההחלטה הקודמת ובדוק את אירוע האבטחה',
  ]) {
    const r = route(task, { cfg: CFG });
    assert.equal(r.recall, 'off');
    assert.equal(r.recallReason, 'fresh-eyes');
    assert.equal(r.axes.memory, false);
    assert.ok(!r.layers.includes('fabius-archivum'));
  }
  assert.equal(route('recall our design decision', { cfg: CFG }).recall, 'normal');
  const ordinary = route('summarize this paragraph', { cfg: CFG });
  assert.equal(ordinary.recall, 'off');
  assert.equal(ordinary.recallReason, 'no-signal');
  for (const currentArtifact of ['write a short note', 'read the error log', 'migrate this wiki']) {
    assert.equal(route(currentArtifact, { cfg: CFG }).axes.memory, false, currentArtifact);
  }
});

test('contrastive intent pairs do not route on broad homonyms', () => {
  const none = [
    'explain database transaction isolation',
    'review my employment contract',
    'write a sales training plan',
    'run an A/B experiment for the landing page',
    'please deliberate carefully before answering',
  ];
  for (const task of none) {
    const d = route(task, { cfg: CFG }).domains;
    assert.ok(!d.includes('fabius-catena'), task);
    assert.ok(!d.includes('fabius-doctrina'), task);
    assert.ok(!d.includes('fabius-scientia'), task);
    assert.ok(!d.includes('fabius-concilium'), task);
  }
  assert.deepEqual(route('security audit this Solidity smart contract', { cfg: CFG }).domains.sort(), ['fabius-catena', 'fabius-praesidium']);
  assert.ok(route('train a classifier and deploy model inference', { cfg: CFG }).domains.includes('fabius-doctrina'));
  assert.ok(route('design a scientific experiment for this protein', { cfg: CFG }).domains.includes('fabius-scientia'));
  assert.deepEqual(route('fix webhook signature verification', { cfg: CFG }).domains, ['fabius-praesidium']);
  assert.deepEqual(route('ask three providers to compare model answers', { cfg: CFG }).domains, ['fabius-concilium']);
});

test('an explicit or configured Ollama choice is keyless but never an implicit fallback', () => {
  const empty = { keys: {}, provider: 'anthropic' };
  assert.equal(resolveModel('anthropic', 'mid', empty), null);
  assert.deepEqual(availableProviders(empty), []);

  const explicit = route('summarize this', { cfg: empty, provider: 'ollama' });
  assert.equal(explicit.fireable, true);
  assert.equal(explicit.provider, 'ollama');
  assert.ok(explicit.available.includes('ollama'));

  const configured = { keys: {}, provider: 'ollama' };
  assert.equal(resolveModel('ollama', 'fast', configured)?.provider, 'ollama');
  assert.ok(availableProviders(configured).includes('ollama'));
});
