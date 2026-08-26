import { test } from 'node:test';
import assert from 'node:assert/strict';
import { callLLM } from '../src/providers.mjs';

test('Google API credentials travel in a header, never in the URL', async () => {
  const original = globalThis.fetch;
  let seen;
  globalThis.fetch = async (url, options) => {
    seen = { url: String(url), options };
    return new Response(JSON.stringify({ candidates: [{ content: { parts: [{ text: 'ok' }] } }], usageMetadata: {} }), {
      status: 200, headers: { 'content-type': 'application/json' },
    });
  };
  try {
    const key = 'AIzaSyntheticCredentialForHeaderOnly123456';
    const r = await callLLM({ provider: 'google', model: 'gemini-test', system: 's', messages: [], maxTokens: 1 }, { keys: { google: key } });
    assert.equal(r.ok, true);
    assert.doesNotMatch(seen.url, /AIza|[?&]key=/);
    assert.equal(seen.options.headers['x-goog-api-key'], key);
  } finally { globalThis.fetch = original; }
});

test('provider exceptions are redacted before entering status text', async () => {
  const original = globalThis.fetch;
  const key = 'sk-proj-SyntheticCredentialMaterial123456789';
  globalThis.fetch = async () => { throw new Error(`transport repeated ${key}`); };
  try {
    const r = await callLLM({ provider: 'openai', model: 'gpt-test', system: 's', messages: [], maxTokens: 1 }, { keys: { openai: key } });
    assert.equal(r.ok, false);
    assert.doesNotMatch(r.status, /SyntheticCredentialMaterial/);
    assert.match(r.status, /redacted/);
  } finally { globalThis.fetch = original; }
});
