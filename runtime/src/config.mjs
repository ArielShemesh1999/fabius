// Where fabius keeps its state on YOUR machine, and how it finds a key.
//
// Nothing here ever leaves the disk. Keys are read from the environment first, then
// from ~/.fabius/config.json (chmod 0600, enforced on write). The config file is
// NEVER printed, logged, or included in a transcript — `redact()` is the only path
// by which a key-shaped string reaches stdout.

import { homedir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, URL } from 'node:url';
import {
  readFileSync, writeFileSync, mkdirSync, existsSync, chmodSync, statSync,
  openSync, closeSync, fsyncSync, renameSync, unlinkSync, lstatSync,
} from 'node:fs';

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
    // A pre-existing state directory may have come from an older release or a permissive
    // umask. The files below are 0600, but a traversable state root still exposes names and
    // any legacy file that did not set its own mode, so repair the directory every time.
    chmodSync(d, 0o700);
  }
}

// Same-directory temp + fsync + rename: a crash may leave the old file or the new file,
// never a half-written JSON document containing keys or replay state.
export function atomicWriteFile(path, data, { mode = 0o600 } = {}) {
  const tmp = `${path}.${process.pid}.${Date.now().toString(36)}.${Math.random().toString(16).slice(2)}.tmp`;
  let fd;
  try {
    fd = openSync(tmp, 'wx', mode);
    writeFileSync(fd, data);
    fsyncSync(fd);
    closeSync(fd); fd = undefined;
    chmodSync(tmp, mode);
    renameSync(tmp, path);
    chmodSync(path, mode);
  } catch (e) {
    if (fd !== undefined) { try { closeSync(fd); } catch { /* already closed */ } }
    try { unlinkSync(tmp); } catch { /* no temp to remove */ }
    throw e;
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

function readConfigState() {
  if (!existsSync(CONFIG_PATH)) return {};
  if (lstatSync(CONFIG_PATH).isSymbolicLink()) throw new Error('refusing a symbolic-link config file');
  const st = statSync(CONFIG_PATH);
  if (st.mode & 0o077) {
    chmodSync(CONFIG_PATH, 0o600);
    process.stderr.write(`[fabius] warning: repaired group/world-readable permissions on ${CONFIG_PATH}\n`);
  }
  return JSON.parse(readFileSync(CONFIG_PATH, 'utf8'));
}

export function loadConfig() {
  if (cached) return cached;
  let file = {};
  if (existsSync(CONFIG_PATH)) {
    try {
      file = readConfigState();
    } catch (e) {
      process.stderr.write(`[fabius] warning: could not read ${CONFIG_PATH} (${e.message}) — using defaults\n`);
    }
  }
  cached = { ...DEFAULTS, ...file, keys: { ...(file.keys || {}) } };
  return cached;
}

export function saveConfig(patch) {
  ensureDirs();
  // Do not let setup/update follow a symlink and import arbitrary local JSON into the
  // credential store. The final atomic rename is safe; the read side must be as well.
  const cur = readConfigState();
  const next = { ...cur, ...patch, keys: { ...(cur.keys || {}), ...(patch.keys || {}) } };
  atomicWriteFile(CONFIG_PATH, JSON.stringify(next, null, 2) + '\n');
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

// Used twice: to remove credential-bearing variables from model-initiated child
// processes, and to redact their values if another path still surfaces them.
export const SECRET_ENV_NAME = /(KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|SESSION|COOKIE|AUTH|PRIVATE)/i;
export const CHILD_ENV_CONTROL_NAME = /^(BASH_ENV|ENV|CDPATH|GLOBIGNORE|SHELLOPTS|BASHOPTS|NODE_OPTIONS|NODE_PATH|PYTHONPATH|PYTHONHOME|RUBYOPT|RUBYLIB|PERL5OPT|PERL5LIB|LD_PRELOAD|LD_LIBRARY_PATH|DYLD_.+|GIT_CONFIG(?:_GLOBAL|_SYSTEM|_COUNT|_KEY_\d+|_VALUE_\d+)?|GIT_ASKPASS|SSH_ASKPASS|SSH_AUTH_SOCK|AWS_SHARED_CREDENTIALS_FILE|AWS_CONFIG_FILE|NPM_CONFIG_USERCONFIG|YARN_RC_FILENAME|DOCKER_CONFIG|KUBECONFIG)$/i;
const KNOWN_CONNECTION_SECRET_NAME = /^(DATABASE_URL|REDIS_URL|SENTRY_DSN)$/i;
const URLISH_ENV_NAME = /(?:^|_)(?:URL|URI|DSN)$/i;

function hasUrlUserinfo(value) {
  if (typeof value !== 'string' || !value.trim()) return false;
  try {
    const u = new URL(value.trim());
    return Boolean(u.username || u.password);
  } catch {
    return false;
  }
}

// Connection strings are credentials even when their variable name does not contain
// KEY/TOKEN/SECRET. Generic *_URL/*_URI/*_DSN values stay available when they are plain
// public endpoints, but any URL userinfo is private; the conventional database/cache/
// telemetry names fail closed even when a non-URL driver syntax hides the credentials.
export function isSensitiveEnvironmentEntry(name, value) {
  return SECRET_ENV_NAME.test(String(name || ''))
    || KNOWN_CONNECTION_SECRET_NAME.test(String(name || ''))
    || (URLISH_ENV_NAME.test(String(name || '')) && hasUrlUserinfo(value));
}

export function scrubEnvironment(env = process.env) {
  const out = {};
  for (const [name, value] of Object.entries(env || {})) {
    if (!isSensitiveEnvironmentEntry(name, value) && !CHILD_ENV_CONTROL_NAME.test(name)) out[name] = value;
  }
  return out;
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
  for (const [name, value] of Object.entries(process.env)) {
    if (!isSensitiveEnvironmentEntry(name, value) || typeof value !== 'string') continue;
    const s = value.trim();
    if (s.length >= 8) secrets.add(s);
  }
  // The DM-channel identity is stored as RAW HEX, which no vendor-prefix pattern
  // below will ever match — it must be in the literal set.
  if (typeof cfg?.nostr?.sk === 'string') {
    const s = cfg.nostr.sk.trim();
    if (s.length >= 12) secrets.add(s);
  }
  for (const s of [...secrets].sort((a, b) => b.length - a.length)) {
    t = t.split(s).join('••••redacted••••');
  }
  // Catch key-shaped strings we were never told about (a stray sk-… in a file the
  // agent read). Deliberately narrow: known vendor prefixes only, so ordinary text
  // and base64 payloads survive intact.
  t = t.replace(/\b(sk-(?:ant-|proj-|or-v1-)?[A-Za-z0-9_-]{16,}|hf_[A-Za-z0-9]{16,}|gsk_[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{30,}|nsec1[a-z0-9]{20,})\b/g, '••••redacted••••');
  // Defense in depth for a connection string surfaced from somewhere other than the
  // current environment (for example command output). Keep the scheme and host useful
  // for diagnosis while removing the complete userinfo field. A public URL has no `@`
  // in its authority and is left byte-for-byte unchanged.
  t = t.replace(/\b([a-z][a-z0-9+.-]*:\/\/)([^@\s/]+)@([^\s"'<>]+)/gi,
    '$1••••redacted••••@$3');
  t = t.replace(/\b(DATABASE_URL|REDIS_URL|SENTRY_DSN)\s*=\s*(?:"[^"\r\n]*"|'[^'\r\n]*'|[^\s\r\n]+)/gi,
    '$1=••••redacted••••');
  return t;
}
