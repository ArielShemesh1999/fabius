// The BYOK gateway — one call shape over every provider fabius runs on.
//
// Same roster and same tier map as the cloud console, so a task routed locally picks
// the model it would have picked in the console. `frontier` is the strongest widely
// released tier per provider; R11 reserves it for ambiguity, architecture, security
// and irreversible work, and takes the cheap tier for mechanical work.

import { ENV_KEY, providerKey, loadConfig } from './config.mjs';

export const PROVIDERS = {
  anthropic: { label: 'Anthropic', tiers: { frontier: 'claude-fable-5', mid: 'claude-sonnet-5', fast: 'claude-haiku-4-5' } },
  openai: { label: 'OpenAI', tiers: { frontier: 'gpt-5', mid: 'gpt-5-mini', fast: 'gpt-5-nano' } },
  google: { label: 'Google Gemini', tiers: { frontier: 'gemini-2.5-pro', mid: 'gemini-2.5-flash', fast: 'gemini-2.5-flash-lite' } },
  mistral: { label: 'Mistral', tiers: { frontier: 'mistral-large-latest', mid: 'mistral-medium-latest', fast: 'mistral-small-latest' } },
  groq: { label: 'Groq', tiers: { frontier: 'llama-3.3-70b-versatile', mid: 'llama-3.3-70b-versatile', fast: 'llama-3.1-8b-instant' } },
  // One token, hundreds of open models across every partner. Any `org/name` repo id
  // passed as a custom model overrides the tier default — that is the "run any open
  // model" path.
  huggingface: { label: 'HuggingFace', router: true, tiers: { frontier: 'openai/gpt-oss-120b', mid: 'meta-llama/Llama-3.3-70B-Instruct', fast: 'meta-llama/Llama-3.1-8B-Instruct' } },
  openrouter: { label: 'OpenRouter', router: true, tiers: { frontier: 'anthropic/claude-sonnet-4.5', mid: 'openai/gpt-4.1-mini', fast: 'meta-llama/llama-3.3-70b-instruct' } },
  // Local inference. No key, no network, no cost — and no frontier tier: an 8–14B
  // local model is a `fast` model wherever it is pointed. Honest by construction.
  ollama: { label: 'Ollama (local)', local: true, tiers: { frontier: 'qwen2.5-coder:14b', mid: 'qwen2.5-coder:7b', fast: 'llama3.2:3b' } },
};

export const PROVIDER_ORDER = ['anthropic', 'openai', 'google', 'mistral', 'groq', 'huggingface', 'openrouter', 'ollama'];
export const TIERS = ['frontier', 'mid', 'fast'];

// [usd_in, usd_out] per 1M tokens ≡ micro-USD per token, so the ledger stays integer.
const PRICES = {
  anthropic: { 'claude-fable-5': [10, 50], 'claude-sonnet-5': [3, 15], 'claude-haiku-4-5': [1, 5] },
  openai: { 'gpt-5': [1.25, 10], 'gpt-5-mini': [0.25, 2], 'gpt-5-nano': [0.05, 0.4] },
  google: { 'gemini-2.5-pro': [1.25, 10], 'gemini-2.5-flash': [0.3, 2.5], 'gemini-2.5-flash-lite': [0.1, 0.4] },
  mistral: { 'mistral-large-latest': [2, 6], 'mistral-medium-latest': [0.4, 2], 'mistral-small-latest': [0.1, 0.3] },
  groq: { 'llama-3.3-70b-versatile': [0.59, 0.79], 'llama-3.1-8b-instant': [0.05, 0.08] },
  huggingface: { 'openai/gpt-oss-120b': [0.15, 0.6], 'meta-llama/Llama-3.3-70B-Instruct': [0.6, 0.7], 'meta-llama/Llama-3.1-8B-Instruct': [0.05, 0.08] },
  openrouter: { 'anthropic/claude-sonnet-4.5': [3, 15], 'openai/gpt-4.1-mini': [0.4, 1.6], 'meta-llama/llama-3.3-70b-instruct': [0.12, 0.3] },
  ollama: {},   // local inference costs no money
};

// An UNKNOWN model bills at the provider's MAX published rate. Over-counting stops a
// run early; under-counting spends the owner's money. Errs toward stopping.
function maxRate(table) {
  let mi = 0, mo = 0;
  for (const k of Object.keys(table)) { mi = Math.max(mi, table[k][0]); mo = Math.max(mo, table[k][1]); }
  return (mi > 0 || mo > 0) ? [mi, mo] : null;
}
export function costMicro(provider, model, usage) {
  const table = PRICES[provider];
  if (!table) return 0;
  const rate = table[model] || maxRate(table);
  if (!rate) return 0;
  const tin = Math.max(0, Number(usage?.input_tokens) || 0);
  const tout = Math.max(0, Number(usage?.output_tokens) || 0);
  return Math.round(tin * rate[0] + tout * rate[1]);
}

export function availableProviders(cfg = loadConfig()) {
  return PROVIDER_ORDER.filter((p) => !!providerKey(p, cfg));
}

// Resolve {provider, model, tier} honouring what is actually keyed; fall back along
// PROVIDER_ORDER to the first keyed provider. null when NOTHING is keyed.
export function resolveModel(provider, tier, cfg = loadConfig()) {
  const t = TIERS.includes(tier) ? tier : 'mid';
  const tryP = (p) => (PROVIDERS[p] && providerKey(p, cfg)) ? { provider: p, model: PROVIDERS[p].tiers[t], tier: t } : null;
  const first = tryP(provider);
  if (first) return first;
  for (const p of PROVIDER_ORDER) { const r = tryP(p); if (r) return r; }
  return null;
}

// A custom model id overrides the tier default ONLY when the caller explicitly named
// the provider it belongs to — never paste an HF repo id onto a fallback call.
export function overrideModel(resolved, wantProvider, model) {
  const m = typeof model === 'string' ? model.trim() : '';
  if (!resolved || !m || !wantProvider || !PROVIDERS[wantProvider]) return resolved;
  if (resolved.provider !== wantProvider) return resolved;
  return { provider: resolved.provider, model: m.slice(0, 200), tier: resolved.tier };
}

const ZERO = { input_tokens: 0, output_tokens: 0 };

// ── the single call. { provider, model, system, messages, maxTokens } → { ok, output, usage, status }
export async function callLLM({ provider, model, system, messages, maxTokens = 2048, timeoutMs = 120000 }, cfg = loadConfig()) {
  const key = providerKey(provider, cfg);
  if (!key && provider !== 'ollama') return { ok: false, output: '', usage: ZERO, status: 'no-key' };
  const ac = new AbortController();
  const timer = setTimeout(() => ac.abort(), timeoutMs);
  try {
    const r = await CALLERS[provider]({ key, model, system, messages, maxTokens, signal: ac.signal });
    return r;
  } catch (e) {
    // Never surface a provider's raw error body — it can echo the key back.
    const msg = e?.name === 'AbortError' ? `timed out after ${Math.round(timeoutMs / 1000)}s` : (e?.message || 'unknown error');
    return { ok: false, output: '', usage: ZERO, status: 'error: ' + String(msg).slice(0, 200) };
  } finally { clearTimeout(timer); }
}

async function readJson(res) {
  const text = await res.text();
  try { return JSON.parse(text); } catch { return { __raw: text.slice(0, 400) }; }
}

// OpenAI-compatible chat/completions — used verbatim by five of the eight providers.
function openaiCompatible(url, extraHeaders = {}) {
  return async ({ key, model, system, messages, maxTokens, signal }) => {
    const res = await fetch(url, {
      method: 'POST', signal,
      headers: { 'content-type': 'application/json', authorization: `Bearer ${key}`, ...extraHeaders },
      body: JSON.stringify({
        model,
        max_tokens: maxTokens,
        messages: [{ role: 'system', content: system }, ...messages],
      }),
    });
    const d = await readJson(res);
    if (!res.ok) return { ok: false, output: '', usage: ZERO, status: `http ${res.status}` };
    const out = d.choices?.[0]?.message?.content ?? '';
    return {
      ok: true, output: String(out), status: 'done',
      usage: { input_tokens: d.usage?.prompt_tokens || 0, output_tokens: d.usage?.completion_tokens || 0 },
    };
  };
}

const CALLERS = {
  anthropic: async ({ key, model, system, messages, maxTokens, signal }) => {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST', signal,
      headers: { 'content-type': 'application/json', 'x-api-key': key, 'anthropic-version': '2023-06-01' },
      body: JSON.stringify({ model, max_tokens: maxTokens, system, messages }),
    });
    const d = await readJson(res);
    if (!res.ok) return { ok: false, output: '', usage: ZERO, status: `http ${res.status}` };
    const out = (d.content || []).filter((b) => b.type === 'text').map((b) => b.text).join('');
    return { ok: true, output: out, status: 'done', usage: { input_tokens: d.usage?.input_tokens || 0, output_tokens: d.usage?.output_tokens || 0 } };
  },

  google: async ({ model, key, system, messages, maxTokens, signal }) => {
    const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:generateContent?key=${encodeURIComponent(key)}`, {
      method: 'POST', signal,
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: system }] },
        contents: messages.map((m) => ({ role: m.role === 'assistant' ? 'model' : 'user', parts: [{ text: m.content }] })),
        generationConfig: { maxOutputTokens: maxTokens },
      }),
    });
    const d = await readJson(res);
    if (!res.ok) return { ok: false, output: '', usage: ZERO, status: `http ${res.status}` };
    const out = (d.candidates?.[0]?.content?.parts || []).map((p) => p.text || '').join('');
    return { ok: true, output: out, status: 'done', usage: { input_tokens: d.usageMetadata?.promptTokenCount || 0, output_tokens: d.usageMetadata?.candidatesTokenCount || 0 } };
  },

  openai: openaiCompatible('https://api.openai.com/v1/chat/completions'),
  mistral: openaiCompatible('https://api.mistral.ai/v1/chat/completions'),
  groq: openaiCompatible('https://api.groq.com/openai/v1/chat/completions'),
  huggingface: openaiCompatible('https://router.huggingface.co/v1/chat/completions'),
  openrouter: openaiCompatible('https://openrouter.ai/api/v1/chat/completions', {
    'http-referer': 'https://fabius-landing.vercel.app', 'x-title': 'fabius',
  }),

  // Local. The "key" is the host URL; absence of a key means the caller never chose it.
  ollama: async ({ key, model, system, messages, maxTokens, signal }) => {
    const host = (key && key.startsWith('http')) ? key.replace(/\/$/, '') : 'http://127.0.0.1:11434';
    const res = await fetch(`${host}/api/chat`, {
      method: 'POST', signal,
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ model, stream: false, options: { num_predict: maxTokens }, messages: [{ role: 'system', content: system }, ...messages] }),
    });
    const d = await readJson(res);
    if (!res.ok) return { ok: false, output: '', usage: ZERO, status: `http ${res.status}` };
    return {
      ok: true, output: String(d.message?.content || ''), status: 'done',
      usage: { input_tokens: d.prompt_eval_count || 0, output_tokens: d.eval_count || 0 },
    };
  },
};

export { ENV_KEY };
