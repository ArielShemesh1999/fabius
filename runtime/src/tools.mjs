// THE TOOL REGISTRY — the local hands.
//
// A hosted harness can fetch, search and run code in someone else's sandbox. On this
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
import { redact, scrubEnvironment } from './config.mjs';
import { insideJail, isSecretPath, isProtectedWritePath } from './approve.mjs';
import { clamp } from './util.mjs';
import { memoryContext } from './memory.mjs';
import { route } from './route.mjs';
import { recon, formatReport, normalizeTarget } from './recon.mjs';

const MAX_OBS = 8000;      // an observation longer than this teaches nothing extra
const MAX_READ = 200000;

const rel = (p, jail) => {
  const base = insideJail('.', jail).resolved;
  const target = insideJail(p, jail);
  return relative(base, target.ok ? target.resolved : resolve(jail, p)) || '.';
};

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
  const words = ipv6Words(s);
  if (words) {
    const mapped = words.slice(0, 5).every((n) => n === 0) && (words[5] === 0 || words[5] === 0xffff);
    if (mapped) {
      const hi = words[6], lo = words[7];
      return isBlockedAddress(`${hi >>> 8}.${hi & 255}.${lo >>> 8}.${lo & 255}`);
    }
    if (words.slice(0, 7).every((n) => n === 0) && words[7] <= 1) return true;
  }
  return /^(f[cd]|fe[89ab]|ff)/.test(s);                                // ULA, link-local, multicast
}

function ipv6Words(input) {
  let s = String(input || '').toLowerCase();
  const dotted = s.match(/^(.*:)(\d+)\.(\d+)\.(\d+)\.(\d+)$/);
  if (dotted) {
    const octets = dotted.slice(2).map(Number);
    if (octets.some((n) => !Number.isInteger(n) || n < 0 || n > 255)) return null;
    s = `${dotted[1]}${((octets[0] << 8) | octets[1]).toString(16)}:${((octets[2] << 8) | octets[3]).toString(16)}`;
  }
  const halves = s.split('::');
  if (halves.length > 2) return null;
  const parse = (part) => part ? part.split(':').map((x) => /^[0-9a-f]{1,4}$/.test(x) ? Number.parseInt(x, 16) : NaN) : [];
  const left = parse(halves[0]), right = parse(halves[1] || '');
  if ([...left, ...right].some(Number.isNaN)) return null;
  if (halves.length === 1) return left.length === 8 ? left : null;
  const fill = 8 - left.length - right.length;
  if (fill < 1) return null;
  return [...left, ...Array(fill).fill(0), ...right];
}

const LOCAL_NAME = /(^|\.)(localhost|local|internal|intranet|home\.arpa)$/i;

// Resolve before fetching and refuse the whole answer set: a hostname that resolves to
// even one private address is refused, so a split-horizon name cannot smuggle a request in.
//
// Be honest about the residual: this resolves the name, and then the request resolves it
// again independently, so a hostile name on a short TTL can answer public here and
// 169.254.169.254 on the request itself. Closing that needs pinning the checked address
// into the connection (a custom agent/lookup), which node:fetch does not expose. What is
// here defeats a static private target and a redirect to one — treat it as one layer.
export async function assertPublicHostname(hostname) {
  const host = String(hostname || '').replace(/^\[|\]$/g, '');
  if (isIP(host)) return isBlockedAddress(host) ? `(refused: ${host} is a loopback, private or link-local address)` : null;
  if (LOCAL_NAME.test(host)) return `(refused: ${host} is a local name)`;
  let addrs;
  try { addrs = await lookup(host, { all: true }); } catch { return `(refused: ${host} does not resolve)`; }
  if (!addrs.length) return `(refused: ${host} does not resolve)`;
  for (const a of addrs) if (isBlockedAddress(a.address)) return `(refused: ${host} resolves to a loopback, private or link-local address)`;
  return null;
}

const assertPublicHost = (u) => assertPublicHostname(u.hostname);

async function cancelBody(res) {
  try { await res?.body?.cancel(); } catch { /* already consumed, locked, or closed */ }
}

// Read at most `maxBytes` from a WHATWG response stream, then cancel it. `res.text()`
// cannot enforce a memory bound because it buffers the entire hostile response before a
// caller can slice the string. Copy only the retained prefix of each chunk so one
// over-sized chunk is not kept alive by a view into its backing buffer.
async function readTextBounded(res, maxBytes) {
  const limit = Number.isSafeInteger(maxBytes) && maxBytes >= 0 ? maxBytes : 0;
  if (!res.body) return '';
  const reader = res.body.getReader();
  const chunks = [];
  let total = 0;
  try {
    while (total < limit) {
      const { done, value } = await reader.read();
      if (done) return Buffer.concat(chunks, total).toString('utf8');
      const bytes = value instanceof Uint8Array ? value : new Uint8Array(value);
      const take = Math.min(bytes.byteLength, limit - total);
      if (take) {
        chunks.push(Buffer.from(bytes.subarray(0, take)));
        total += take;
      }
      if (take < bytes.byteLength || total === limit) {
        try { await reader.cancel(); } catch { /* stream already closed */ }
        return Buffer.concat(chunks, total).toString('utf8');
      }
    }
    try { await reader.cancel(); } catch { /* zero-byte limit or already closed */ }
    return '';
  } catch (e) {
    try { await reader.cancel(); } catch { /* preserve the original read error */ }
    throw e;
  } finally {
    try { reader.releaseLock(); } catch { /* an errored reader may already be detached */ }
  }
}

async function httpGetText(url, {
  timeoutMs = 15000, maxBytes = 120000, userAgent = 'fabius/1.0', maxHops = 5,
  gate = null, allowedOrigins = [],
} = {}) {
  let u;
  try { u = new URL(String(url).trim()); } catch { return '(not a URL)'; }
  if (!['http:', 'https:'].includes(u.protocol) || u.username || u.password) return '(only http and https URLs without embedded credentials are fetchable)';
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(), timeoutMs);
  try {
    let target = u, hops = 0, res;
    // Redirects are followed by hand so every hop is re-validated: an allowlist that is
    // only checked on the first URL is bypassed by a 302 to 169.254.169.254.
    for (;;) {
      // Authorise BEFORE DNS resolution: even a lookup discloses the destination. The
      // gate remembers an approved origin for this run, while every new redirect origin
      // parks here again and is denied automatically when no terminal is present.
      if (gate) {
        const decision = await gate.check('net', target.href, { allowedOrigins });
        if (!decision.approved) return `(denied: ${decision.why})`;
      }
      const bad = await assertPublicHost(target);
      if (bad) return bad;
      res = await fetch(target, { signal: ac.signal, redirect: 'manual', headers: { 'user-agent': userAgent, accept: 'text/html,text/plain,application/json;q=0.9,*/*;q=0.8' } });
      if (![301, 302, 303, 307, 308].includes(res.status)) break;
      const loc = res.headers.get('location');
      // Nothing reads a redirect's body, and the socket stays held until it is consumed
      // or cancelled — release it before moving to the next hop.
      await cancelBody(res);
      if (!loc) return `(${res.status} redirect with no location)`;
      if (++hops > maxHops) return '(too many redirects)';
      let next;
      try { next = new URL(loc, target); } catch { return '(bad redirect target)'; }
      if (!['http:', 'https:'].includes(next.protocol) || next.username || next.password) return '(only http and https URLs without embedded credentials are fetchable)';
      target = next;
    }
    const ct = res.headers.get('content-type') || '';
    if (!/text|json|xml|javascript/i.test(ct)) {
      await cancelBody(res);
      return `(${res.status} ${ct || 'unknown type'} — not text, nothing to read)`;
    }
    const body = await readTextBounded(res, maxBytes);
    return `[${res.status}] ${stripHtml(body)}`;
  } catch (e) {
    return redact(`(fetch failed: ${e.name === 'AbortError' ? 'timed out' : e.message})`);
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

function safeOperationalPath(path, jail, { write = false } = {}) {
  const checked = insideJail(path, jail);
  if (!checked.ok || isSecretPath(path) || isSecretPath(checked.resolved)
      || (write && (isProtectedWritePath(path) || isProtectedWritePath(checked.resolved)))) return null;
  return checked.resolved;
}

function runCommand(cmd, { cwd, timeoutMs = 120000, maxBytes = 40000, env = scrubEnvironment(process.env) }) {
  return new Promise((res) => {
    const grouped = process.platform !== 'win32';
    let out = '', err = '', killed = false;
    let settled = false;
    let t;
    let child;
    const limit = Number.isSafeInteger(maxBytes) && maxBytes >= 0 ? maxBytes : 40000;
    const appendBounded = (current, data) => {
      const remaining = limit - Buffer.byteLength(current);
      return remaining > 0 ? current + Buffer.from(data).subarray(0, remaining).toString('utf8') : current;
    };
    const finish = (result) => {
      if (settled) return;
      settled = true; clearTimeout(t);
      res({ ...result, out: redact(out), err: redact(result.err ?? err) });
    };
    try {
      child = spawn(cmd, {
        cwd, shell: true, detached: grouped, stdio: ['ignore', 'pipe', 'pipe'],
        env: { ...scrubEnvironment(env), FABIUS_RUNTIME: '1' },
      });
    } catch (e) {
      finish({ code: -1, err: String(e.message), killed });
      return;
    }
    t = setTimeout(() => {
      killed = true;
      try {
        if (grouped && child.pid) process.kill(-child.pid, 'SIGKILL');
        else child.kill('SIGKILL');
      } catch { try { child.kill('SIGKILL'); } catch { /* already gone */ } }
    }, timeoutMs);
    child.stdout.on('data', (d) => { out = appendBounded(out, d); });
    child.stderr.on('data', (d) => { err = appendBounded(err, d); });
    child.on('error', (e) => finish({ code: -1, err: String(e.message), killed }));
    child.on('close', (code) => finish({ code, err, killed }));
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
      const files = walk(target)
        .map((f) => safeOperationalPath(f, ctx.jail))
        .filter(Boolean)
        .map((f) => rel(f, ctx.jail));
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
      const safe = safeOperationalPath(target, ctx.jail);
      if (!safe) return '(denied: path changed or resolves outside the safe working tree)';
      if (!existsSync(safe)) return `(no such file: ${rel(target, ctx.jail)})`;
      const st = statSync(safe);
      if (st.isDirectory()) return `(${rel(target, ctx.jail)} is a directory — use list)`;
      if (st.size > MAX_READ) return `(${rel(target, ctx.jail)} is ${Math.round(st.size / 1024)}KB — too large to read whole; grep it instead)`;
      return readFileSync(safe, 'utf8');
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
        const safe = safeOperationalPath(f, ctx.jail);
        if (!safe) continue;
        let text;
        try {
          const st = statSync(safe);
          if (!st.isFile() || st.size > MAX_READ) continue;
          text = readFileSync(safe, 'utf8');
        } catch { continue; }
        text.split('\n').forEach((line, i) => {
          if (hits.length < 80 && re.test(line)) hits.push(`${rel(safe, ctx.jail)}:${i + 1}: ${line.trim().slice(0, 200)}`);
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
      const gate = await ctx.gate.check('write', target, { payload: body });
      if (!gate.approved) return `(denied: ${gate.why})`;
      const safe = safeOperationalPath(target, ctx.jail, { write: true });
      if (!safe) return '(denied: path changed or resolves outside the safe working tree)';
      mkdirSync(dirname(safe), { recursive: true });
      const existed = existsSync(safe);
      writeFileSync(safe, body);
      ctx.changed?.add(rel(safe, ctx.jail));
      return `${existed ? 'replaced' : 'created'} ${rel(safe, ctx.jail)} (${Buffer.byteLength(body)} bytes)`;
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
      const gate = await ctx.gate.check('write', target, { payload: `<<<OLD\n${m[2]}\nOLD>>>\n<<<NEW\n${m[3]}\nNEW>>>` });
      if (!gate.approved) return `(denied: ${gate.why})`;
      const safe = safeOperationalPath(target, ctx.jail, { write: true });
      if (!safe) return '(denied: path changed or resolves outside the safe working tree)';
      if (!existsSync(safe)) return `(no such file: ${rel(target, ctx.jail)})`;
      const cur = readFileSync(safe, 'utf8');
      const count = cur.split(m[2]).length - 1;
      if (count === 0) return '(the OLD text does not appear in the file — read it first)';
      if (count > 1) return `(the OLD text appears ${count} times — make it unique)`;
      writeFileSync(safe, cur.replace(m[2], m[3]));
      ctx.changed?.add(rel(safe, ctx.jail));
      return `edited ${rel(safe, ctx.jail)}`;
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
      return httpGetText(String(input || '').trim(), {
        gate: ctx.gate,
        allowedOrigins: ctx.opts?.allowedOrigins || [],
      });
    },
  },

  recon: {
    cap: 'net',
    operatorOnly: true,
    desc: 'audit a domain you own: DNS, TLS, security headers, cookies, mail authentication, exposed files (input = the hostname)',
    run: async (input, ctx) => {
      const gate = await ctx.gate.check('net', input);
      if (!gate.approved) return `(denied: ${gate.why})`;
      // recon opens TLS, HTTP and (with ports) TCP connections to whatever host it is
      // handed, so it needs the same public-internet check `fetch` applies: `127.0.0.1`,
      // `169.254.169.254`, `192.168.1.1` and `router.local` all satisfy its hostname
      // syntax, and "audit a domain you own" would otherwise scan the operator's LAN.
      let host;
      try { host = normalizeTarget(String(input || '').trim()); } catch (e) { return `(recon failed: ${e.message})`; }
      const bad = await assertPublicHostname(host);
      if (bad) return bad;
      try {
        const r = await recon(host);
        return formatReport(r, { color: false });
      } catch (e) { return `(recon failed: ${e.message})`; }
    },
  },

  recall: {
    cap: 'read',
    desc: 'search your own memory for prior decisions and facts (input = the query)',
    run: async (input, ctx) => {
      const mode = ctx?.route?.recall;
      // The tool executor is a second boundary behind the menu. A stale/model-forged
      // action cannot turn an operator no-memory run or a fresh-eyes route back on.
      if (ctx?.opts?.noMemory || !['normal', 'dampened'].includes(mode)) {
        return '(denied: memory recall is disabled for this run)';
      }
      return memoryContext(input || ctx.task, { scope: ctx.scope, mode }) || '(no matching memory)';
    },
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
export function activeTools({ act = false, offline = false, recall = false } = {}) {
  const caps = new Set(['read']);
  if (!offline) caps.add('net');
  if (act) { caps.add('write'); caps.add('exec'); }
  return TOOL_NAMES.filter((n) => !TOOLS[n].operatorOnly
    && caps.has(TOOLS[n].cap)
    && (n !== 'recall' || recall === true));
}

export async function runTool(name, input, ctx) {
  const tool = TOOLS[name];
  if (!tool) return `(unknown tool "${name}")`;
  if (tool.operatorOnly && !ctx?.operator) return `(${name} is operator-only and is not exposed to the model)`;
  try {
    const out = await tool.run(input, ctx);
    return clamp(redact(String(out ?? '')), MAX_OBS);
  } catch (e) {
    return redact(`(the ${name} tool errored: ${String(e.message).slice(0, 200)})`);
  }
}

export { httpGetText, runCommand };
