// Where fabius keeps its state on YOUR machine, and how it finds a key.
//
// Nothing here ever leaves the disk. Keys are read from the environment first, then
// from ~/.fabius/config.json (chmod 0600, enforced on write). The config file is
// NEVER printed, logged, or included in a transcript — `redact()` is the only path
// by which a key-shaped string reaches stdout.

import { homedir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFileSync, writeFileSync, mkdirSync, existsSync, chmodSync, statSync } from 'node:fs';

export const HOME = process.env.FABIUS_HOME || join(homedir(), '.fabius');
export const CONFIG_PATH = join(HOME, 'config.json');
export const MEMORY_DIR = join(HOME, 'memory');
export const RUNS_DIR = join(HOME, 'runs');
export const ARTIFACTS_DIR = join(HOME, 'artifacts');

// The brain: the sealed skill contracts, resolved relative to THIS file so the
// runtime works from any cwd and from a copied install.
export const REPO_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
export const SKILLS_DIR = process.env.FABIUS_SKILLS_DIR || join(REPO_ROOT, 'skills');

export function ensureDirs() {
  for (const d of [HOME, MEMORY_DIR, RUNS_DIR, ARTIFACTS_DIR]) {
    if (!existsSync(d)) mkdirSync(d, { recursive: true, mode: 0o700 });
  }
}

const DEFAULTS = {
  provider: 'anthropic',
  tier: null,             // null = let the router decide (R11)
  model: null,            // a custom model id overrides the tier default
  approve: 'ask',         // ask | auto | never  — governs write/exec, never read
  maxSteps: 12,
  maxCodeRuns: 6,
  budgetUsd: 2.0,         // per-run wall; the run stops rather than overspending
  workdir: null,          // null = cwd at launch
  keys: {},               // provider → key (env wins over this)
};

let cached = null;

export function loadConfig() {
  if (cached) return cached;
  let file = {};
  if (existsSync(CONFIG_PATH)) {
    try {
      const st = statSync(CONFIG_PATH);
      // 0o077 = any permission bit for group/other. A key file the whole machine can
      // read is a finding, not a preference — say so once, loudly, and continue.
      if (st.mode & 0o077) process.stderr.write(`[fabius] warning: ${CONFIG_PATH} is group/world-readable — run: chmod 600 ${CONFIG_PATH}\n`);
      file = JSON.parse(readFileSync(CONFIG_PATH, 'utf8'));
    } catch (e) {
      process.stderr.write(`[fabius] warning: could not read ${CONFIG_PATH} (${e.message}) — using defaults\n`);
    }
  }
  cached = { ...DEFAULTS, ...file, keys: { ...(file.keys || {}) } };
  return cached;
}

export function saveConfig(patch) {
  ensureDirs();
  const cur = existsSync(CONFIG_PATH) ? JSON.parse(readFileSync(CONFIG_PATH, 'utf8')) : {};
  const next = { ...cur, ...patch, keys: { ...(cur.keys || {}), ...(patch.keys || {}) } };
  writeFileSync(CONFIG_PATH, JSON.stringify(next, null, 2) + '\n', { mode: 0o600 });
  chmodSync(CONFIG_PATH, 0o600);
  cached = null;
  return next;
}

// Env var per provider — the conventional names each vendor's SDK reads, so one export
// works for the runner and for whatever harness you already use.
export const ENV_KEY = {
  anthropic: 'ANTHROPIC_API_KEY',
  openai: 'OPENAI_API_KEY',
  google: 'GOOGLE_API_KEY',
  mistral: 'MISTRAL_API_KEY',
  groq: 'GROQ_API_KEY',
  huggingface: 'HF_TOKEN',
  openrouter: 'OPENROUTER_API_KEY',
  ollama: 'OLLAMA_HOST',   // not a secret — a base URL; presence means "available"
};

export function providerKey(provider, cfg = loadConfig()) {
  const env = process.env[ENV_KEY[provider] || ''];
  if (typeof env === 'string' && env.trim()) return env.trim();
  const k = cfg.keys && cfg.keys[provider];
  return typeof k === 'string' && k.trim() ? k.trim() : '';
}

// Replace every configured key with •••• before anything is written to a transcript,
// an artifact, or the terminal. Called on EVERY observation — a tool that reads a
// dotfile must not be able to echo a key back into the model's context.
export function redact(text, cfg = loadConfig()) {
  let t = typeof text === 'string' ? text : String(text ?? '');
  const secrets = new Set();
  for (const p of Object.keys(ENV_KEY)) {
    if (p === 'ollama') continue;              // a base URL, not a secret
    const k = providerKey(p, cfg);
    if (k && k.length >= 12) secrets.add(k);
  }
  for (const extra of [process.env.TAVILY_API_KEY, process.env.SYNAPSE_TOKEN, process.env.NOSTR_NSEC]) {
    if (typeof extra === 'string' && extra.length >= 12) secrets.add(extra.trim());
  }
  // The DM-channel identity is stored as RAW HEX, which no vendor-prefix pattern
  // below will ever match — it must be in the literal set.
  if (typeof cfg?.nostr?.sk === 'string' && cfg.nostr.sk.length >= 12) secrets.add(cfg.nostr.sk.trim());
  for (const s of secrets) t = t.split(s).join('••••redacted••••');
  // Catch key-shaped strings we were never told about (a stray sk-… in a file the
  // agent read). Deliberately narrow: known vendor prefixes only, so ordinary text
  // and base64 payloads survive intact.
  t = t.replace(/\b(sk-ant-[A-Za-z0-9_-]{16,}|sk-[A-Za-z0-9]{20,}|hf_[A-Za-z0-9]{16,}|gsk_[A-Za-z0-9]{20,}|nsec1[a-z0-9]{20,})\b/g, '••••redacted••••');
  return t;
}
