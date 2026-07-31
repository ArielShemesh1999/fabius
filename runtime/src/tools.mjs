// THE TOOL REGISTRY — the local hands.
//
// The cloud console can fetch, search and run code in someone else's sandbox. On this
// machine the agent gets the things that only a local process can do: read your files,
// write your files, and run your commands. Which is precisely why every one of them is
// declared with a capability and passed through the gate in approve.mjs before it runs.
//
// One entry per capability. The system prompt's tool menu, the action whitelist and the
// executor all derive from this object — add a tool here and it appears everywhere.
//
// Every observation is redacted before it is handed back to the model: a tool that reads
// a dotfile must not be able to echo an API key into the transcript.

import { readFileSync, writeFileSync, existsSync, readdirSync, statSync, mkdirSync } from 'node:fs';
import { join, resolve, relative, dirname } from 'node:path';
import { spawn } from 'node:child_process';
import { lookup } from 'node:dns/promises';
import { isIP } from 'node:net';
import { redact } from './config.mjs';
import { isSecretPath } from './approve.mjs';
import { clamp } from './util.mjs';
import { memoryContext } from './memory.mjs';
import { route } from './route.mjs';
import { recon, formatReport } from './recon.mjs';

const MAX_OBS = 8000;      // an observation longer than this teaches nothing extra
const MAX_READ = 200000;

const rel = (p, jail) => relative(jail, resolve(jail, p)) || '.';

// The network the agent may reach is the PUBLIC internet. Loopback, RFC1918, link-local
// (which is where cloud instance metadata lives), CGNAT and multicast are not "a URL" —
// they are the inside of the machine and of the network it sits on, and a fetch tool that
// can reach them is a hole in every firewall the operator owns.
export function isBlockedAddress(ip) {
  const v = isIP(String(ip || ''));
  if (!v) return false;
  if (v === 4) {
    const [a, b] = String(ip).split('.').map(Number);
    if (a === 0 || a === 127 || a === 10 || a >= 224) return true;      // this-host, loopback, private, multicast/reserved
    if (a === 172 && b >= 16 && b <= 31) return true;                   // 172.16/12
    if (a === 192 && b === 168) return true;                            // 192.168/16
    if (a === 169 && b === 254) return true;                            // link-local — cloud IMDS
    if (a === 100 && b >= 64 && b <= 127) return true;                  // CGNAT 100.64/10
    if (a === 192 && b === 0) return true;                              // 192.0.0/24, 192.0.2/24
    if (a === 198 && (b === 18 || b === 19)) return true;               // benchmarking 198.18/15
    return false;
  }
  const s = String(ip).toLowerCase().split('%')[0];
  const m4 = s.match(/^::ffff:(\d+\.\d+\.\d+\.\d+)$/);
  if (m4) return isBlockedAddress(m4[1]);
  if (s === '::' || s === '::1') return true;
  return /^(f[cd]|fe[89ab]|ff)/.test(s);                                // ULA, link-local, multicast
}

const LOCAL_NAME = /(^|\.)(localhost|local|internal|intranet|home\.arpa)$/i;

// Resolve before fetching and refuse the whole answer set: a hostname that resolves to
// even one private address is refused, so a split-horizon name cannot smuggle a request in.
async function assertPublicHost(u) {
  const host = u.hostname.replace(/^\[|\]$/g, '');
  if (isIP(host)) return isBlockedAddress(host) ? `(refused: ${host} is a loopback, private or link-local address)` : null;
  if (LOCAL_NAME.test(host)) return `(refused: ${host} is a local name)`;
  let addrs;
  try { addrs = await lookup(host, { all: true }); } catch { return `(refused: ${host} does not resolve)`; }
  if (!addrs.length) return `(refused: ${host} does not resolve)`;
  for (const a of addrs) if (isBlockedAddress(a.address)) return `(refused: ${host} resolves to a loopback, private or link-local address)`;
  return null;
}

async function httpGetText(url, { timeoutMs = 15000, maxBytes = 120000, userAgent = 'fabius/1.0', maxHops = 5 } = {}) {
  let u;
  try { u = new URL(String(url).trim()); } catch { return '(not a URL)'; }
  if (!['http:', 'https:'].includes(u.protocol)) return '(only http and https are fetchable)';
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(), timeoutMs);
  try {
    let target = u, hops = 0, res;
    // Redirects are followed by hand so every hop is re-validated: an allowlist that is
    // only checked on the first URL is bypassed by a 302 to 169.254.169.254.
    for (;;) {
      const bad = await assertPublicHost(target);
      if (bad) return bad;
      res = await fetch(target, { signal: ac.signal, redirect: 'manual', headers: { 'user-agent': userAgent, accept: 'text/html,text/plain,application/json;q=0.9,*/*;q=0.8' } });
      if (![301, 302, 303, 307, 308].includes(res.status)) break;
      const loc = res.headers.get('location');
      if (!loc) break;
      if (++hops > maxHops) return '(too many redirects)';
      let next;
      try { next = new URL(loc, target); } catch { return '(bad redirect target)'; }
      if (!['http:', 'https:'].includes(next.protocol)) return '(only http and https are fetchable)';
      target = next;
    }
    const ct = res.headers.get('content-type') || '';
    if (!/text|json|xml|javascript/.test(ct)) return `(${res.status} ${ct || 'unknown type'} — not text, nothing to read)`;
    const body = (await res.text()).slice(0, maxBytes);
    return `[${res.status}] ${stripHtml(body)}`;
  } catch (e) {
    return `(fetch failed: ${e.name === 'AbortError' ? 'timed out' : e.message})`;
  } finally { clearTimeout(t); }
}

// Enough to make a page readable to a model; not a parser. Script and style bodies go
// first because they are pure noise and eat the whole budget.
export function stripHtml(html) {
  return String(html)
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<\/(p|div|li|h[1-6]|tr|section|article)>/gi, '\n')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'")
    .replace(/[ \t]+/g, ' ').replace(/\n{3,}/g, '\n\n').trim();
}

// Recursive listing that skips the directories nobody wants in a model's context.
const SKIP_DIRS = new Set(['node_modules', '.git', 'dist', 'build', '.next', '.venv', '__pycache__', '.cache', 'coverage', '.wrangler', 'vendor']);
export function walk(dir, { maxFiles = 400, maxDepth = 6 } = {}) {
  const out = [];
  const visit = (d, depth) => {
    if (depth > maxDepth || out.length >= maxFiles) return;
    let entries;
    try { entries = readdirSync(d, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      if (out.length >= maxFiles) return;
      if (e.name.startsWith('.') && e.name !== '.well-known') continue;
      if (e.isDirectory()) { if (!SKIP_DIRS.has(e.name)) visit(join(d, e.name), depth + 1); }
      else out.push(join(d, e.name));
    }
  };
  visit(dir, 0);
  return out;
}

function runCommand(cmd, { cwd, timeoutMs = 120000, maxBytes = 40000, env = process.env }) {
  return new Promise((res) => {
    const child = spawn(cmd, { cwd, shell: true, env: { ...env, FABIUS_RUNTIME: '1' } });
    let out = '', err = '', killed = false;
    const t = setTimeout(() => { killed = true; child.kill('SIGKILL'); }, timeoutMs);
    child.stdout.on('data', (d) => { if (out.length < maxBytes) out += d.toString(); });
    child.stderr.on('data', (d) => { if (err.length < maxBytes) err += d.toString(); });
    child.on('error', (e) => { clearTimeout(t); res({ code: -1, out, err: String(e.message), killed }); });
    child.on('close', (code) => { clearTimeout(t); res({ code, out, err, killed }); });
  });
}

export const TOOLS = {
  list: {
    cap: 'read',
    desc: 'list files under a directory (input = a relative path, "." for the working directory)',
    run: async (input, ctx) => {
      const target = resolve(ctx.jail, input?.trim() || '.');
      const gate = await ctx.gate.check('read', target);
      if (!gate.approved) return `(denied: ${gate.why})`;
      if (!existsSync(target)) return `(no such path: ${rel(target, ctx.jail)})`;
      if (!statSync(target).isDirectory()) return `(${rel(target, ctx.jail)} is a file, not a directory)`;
      // The directory-level approval is not a licence to enumerate deny-listed files: a
      // name like `deploy.key` or `credentials.json` is itself a finding for an attacker.
      const files = walk(target).filter((f) => !isSecretPath(f)).map((f) => rel(f, ctx.jail));
      return files.length ? files.join('\n') : '(empty)';
    },
  },

  read: {
    cap: 'read',
    desc: 'read a text file (input = a relative path)',
    run: async (input, ctx) => {
      const target = resolve(ctx.jail, String(input || '').trim());
      const gate = await ctx.gate.check('read', target);
      if (!gate.approved) return `(denied: ${gate.why})`;
      if (!existsSync(target)) return `(no such file: ${rel(target, ctx.jail)})`;
      const st = statSync(target);
      if (st.isDirectory()) return `(${rel(target, ctx.jail)} is a directory — use list)`;
      if (st.size > MAX_READ) return `(${rel(target, ctx.jail)} is ${Math.round(st.size / 1024)}KB — too large to read whole; grep it instead)`;
      return readFileSync(target, 'utf8');
    },
  },

  grep: {
    cap: 'read',
    desc: 'search the working directory for a pattern (input = the regular expression)',
    run: async (input, ctx) => {
      const pattern = String(input || '').trim();
      if (!pattern) return '(no pattern given)';
      let re;
      try { re = new RegExp(pattern, 'i'); } catch (e) { return `(bad regular expression: ${e.message})`; }
      const gate = await ctx.gate.check('read', ctx.jail);
      if (!gate.approved) return `(denied: ${gate.why})`;
      const hits = [];
      for (const f of walk(ctx.jail, { maxFiles: 1500 })) {
        if (hits.length >= 80) break;
        // One gate on the directory is not enough: grep opens every file, so the same
        // per-file deny-list `read` enforces has to be applied here or `grep "PRIVATE
        // KEY"` becomes the way around it.
        if (isSecretPath(f)) continue;
        let text;
        try { if (statSync(f).size > MAX_READ) continue; text = readFileSync(f, 'utf8'); } catch { continue; }
        text.split('\n').forEach((line, i) => {
          if (hits.length < 80 && re.test(line)) hits.push(`${rel(f, ctx.jail)}:${i + 1}: ${line.trim().slice(0, 200)}`);
        });
      }
      return hits.length ? hits.join('\n') : '(no matches)';
    },
  },

  write: {
    cap: 'write',
    desc: 'create or replace a file — input = "<relative path>\\n---\\n<full file contents>"',
    run: async (input, ctx) => {
      const i = String(input || '').indexOf('\n---\n');
      if (i < 0) return '(write expects "<path>\\n---\\n<contents>")';
      const path = String(input).slice(0, i).trim();
      const body = String(input).slice(i + 5);
      const target = resolve(ctx.jail, path);
      const gate = await ctx.gate.check('write', target);
      if (!gate.approved) return `(denied: ${gate.why})`;
      mkdirSync(dirname(target), { recursive: true });
      const existed = existsSync(target);
      writeFileSync(target, body);
      ctx.changed?.add(rel(target, ctx.jail));
      return `${existed ? 'replaced' : 'created'} ${rel(target, ctx.jail)} (${Buffer.byteLength(body)} bytes)`;
    },
  },

  edit: {
    cap: 'write',
    desc: 'replace exact text in a file — input = "<relative path>\\n<<<OLD\\n…\\nOLD>>>\\n<<<NEW\\n…\\nNEW>>>"',
    run: async (input, ctx) => {
      const s = String(input || '');
      const m = s.match(/^(.+?)\n<<<OLD\n([\s\S]*?)\nOLD>>>\n<<<NEW\n([\s\S]*?)\nNEW>>>\s*$/);
      if (!m) return '(edit expects "<path>\\n<<<OLD\\n…\\nOLD>>>\\n<<<NEW\\n…\\nNEW>>>")';
      const target = resolve(ctx.jail, m[1].trim());
      const gate = await ctx.gate.check('write', target);
      if (!gate.approved) return `(denied: ${gate.why})`;
      if (!existsSync(target)) return `(no such file: ${rel(target, ctx.jail)})`;
      const cur = readFileSync(target, 'utf8');
      const count = cur.split(m[2]).length - 1;
      if (count === 0) return '(the OLD text does not appear in the file — read it first)';
      if (count > 1) return `(the OLD text appears ${count} times — make it unique)`;
      writeFileSync(target, cur.replace(m[2], m[3]));
      ctx.changed?.add(rel(target, ctx.jail));
      return `edited ${rel(target, ctx.jail)}`;
    },
  },

  shell: {
    cap: 'exec',
    desc: 'run a shell command in the working directory (input = the command line)',
    run: async (input, ctx) => {
      const cmd = String(input || '').trim();
      if (!cmd) return '(no command given)';
      if (ctx.budget.execRuns >= ctx.budget.maxExecRuns) return '(command budget exhausted for this run)';
      const gate = await ctx.gate.check('exec', cmd);
      if (!gate.approved) return `(denied: ${gate.why})`;
      ctx.budget.execRuns++;
      const r = await runCommand(cmd, { cwd: ctx.jail });
      ctx.ranCommands?.push({ cmd, code: r.code });
      return `[exit ${r.code}${r.killed ? ' — killed on timeout' : ''}]\n` +
        `stdout:\n${r.out.trim() || '(none)'}\n` +
        `stderr:\n${r.err.trim() || '(none)'}`;
    },
  },

  fetch: {
    cap: 'net',
    desc: 'GET a URL and read it as text (input = the full http(s) URL)',
    run: async (input, ctx) => {
      const gate = await ctx.gate.check('net', input);
      if (!gate.approved) return `(denied: ${gate.why})`;
      return httpGetText(String(input || '').trim());
    },
  },

  recon: {
    cap: 'net',
    desc: 'audit a domain you own: DNS, TLS, security headers, cookies, mail authentication, exposed files (input = the hostname)',
    run: async (input, ctx) => {
      const gate = await ctx.gate.check('net', input);
      if (!gate.approved) return `(denied: ${gate.why})`;
      try {
        const r = await recon(String(input || '').trim());
        return formatReport(r, { color: false });
      } catch (e) { return `(recon failed: ${e.message})`; }
    },
  },

  recall: {
    cap: 'read',
    desc: 'search your own memory for prior decisions and facts (input = the query)',
    run: async (input, ctx) => memoryContext(input || ctx.task, { scope: ctx.scope }) || '(no matching memory)',
  },

  route: {
    cap: 'read',
    desc: 'classify a sub-task by layer, machinery and model tier (input = the sub-task)',
    run: async (input, ctx) => {
      const r = route(input || ctx.task, ctx.opts);
      return `layers: ${r.layers.join(', ')} · rung: ${r.rung} · tier: ${r.tier}` +
        (r.domains.length ? ` · domains: ${r.domains.join(', ')}` : '');
    },
  },
};

export const TOOL_NAMES = Object.keys(TOOLS);

// Which tools may fire this run. `read` is always on. `net` unless the caller asks for
// an offline run. `write`/`exec` only when the caller opted into acting — a default run
// can look at the machine and reason about it, and change nothing.
export function activeTools({ act = false, offline = false } = {}) {
  const caps = new Set(['read']);
  if (!offline) caps.add('net');
  if (act) { caps.add('write'); caps.add('exec'); }
  return TOOL_NAMES.filter((n) => caps.has(TOOLS[n].cap));
}

export async function runTool(name, input, ctx) {
  const tool = TOOLS[name];
  if (!tool) return `(unknown tool "${name}")`;
  try {
    const out = await tool.run(input, ctx);
    return clamp(redact(String(out ?? '')), MAX_OBS);
  } catch (e) {
    return `(the ${name} tool errored: ${String(e.message).slice(0, 200)})`;
  }
}

export { httpGetText, runCommand };
