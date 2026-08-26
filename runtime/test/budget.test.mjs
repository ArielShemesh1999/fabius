import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { reserveCallBudget } from '../src/providers.mjs';
import { run } from '../src/loop.mjs';

test('a call is sized before dispatch so its worst case fits the remaining wall', () => {
  const fit = reserveCallBudget({
    provider: 'anthropic', model: 'claude-sonnet-5', system: 'system',
    messages: [{ role: 'user', content: 'x'.repeat(1000) }], maxTokens: 4096,
    remainingMicro: 25_000,
  });
  assert.ok(fit);
  assert.ok(fit.maxTokens > 0 && fit.maxTokens < 4096);
  assert.ok(fit.reserveMicro <= 25_000);
  assert.equal(reserveCallBudget({
    provider: 'anthropic', model: 'claude-sonnet-5', system: 'x'.repeat(2000),
    messages: [], maxTokens: 1, remainingMicro: 1,
  }), null);
});

test('missing provider usage is charged conservatively, never as a free call', async () => {
  const jail = mkdtempSync(join(tmpdir(), 'fabius-budget-'));
  let calls = 0;
  const llm = async () => {
    calls++;
    return {
      ok: true,
      output: JSON.stringify({ tool: 'deliver', input: 'x'.repeat(700) }),
      status: 'done', usage: { input_tokens: 0, output_tokens: 0 },
    };
  };
  const cfg = { keys: { anthropic: 'sk-ant-test-000000000000000000' }, provider: 'anthropic', approve: 'never', budgetUsd: 0.05, maxSteps: 2, maxCodeRuns: 0 };
  const res = await run('write a short note', { cfg, jail, callLLM: llm, remember: false, budgetUsd: 0.05 });
  assert.equal(calls, 1, 'the reserved first call should leave no room for an unreserved reviewer');
  assert.equal(res.budget.estimatedCalls, 1);
  assert.ok(res.cost > 0, 'missing usage cannot make the call free');
  assert.ok(res.budget.reservedUsd <= res.budget.limitUsd);
  rmSync(jail, { recursive: true, force: true });
});
