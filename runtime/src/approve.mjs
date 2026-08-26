// THE PERMISSION GATE — the difference between an agent in a sandbox and an agent on
// your laptop.
//
// In a hosted sandbox the blast radius is a container with no filesystem. Locally the
// blast radius is the owner's machine, so capability is not a preference: every tool
// declares a `cap`, every cap has a standing decision, and the decisions that cannot
// be undone are held back even in autonomous mode.
//
//   read   — inside the working directory, minus the secret deny-list. Never prompts.
//   net    — outbound HTTP GET. Exact-origin authority; first contact prompts or denies.
//   write  — create/modify a file inside the working directory. Prompts by default.
//   exec   — run a command on this machine. Prompts by default.
//
// Three postures: `ask` (default — a human decides each new class of action), `auto`
// (approve bounded in-jail writes plus a tiny read-only command set; ask for everything
// else and still hold irreversible actions), `never` (read-only; the agent can look and
// reason but cannot touch anything).
//
// The gate is a PURE decision function (`classify`) plus a thin prompting shell, so the
// whole policy is testable with no TTY and no model.

import { realpathSync, existsSync, lstatSync } from 'node:fs';
import { resolve, relative, isAbsolute } from 'node:path';
import { createInterface } from 'node:readline/promises';
import { homedir } from 'node:os';
import { createHash } from 'node:crypto';
import { CONFIG_PATH, redact } from './config.mjs';

export const CAPS = ['read', 'net', 'write', 'exec'];

// Files an agent has no business reading, whatever the task says. Matched against the
// resolved path, so `../../.ssh/id_rsa` and a symlink pointing there both trip it.
const SECRET_PATTERNS = [
  /(^|\/)\.ssh(\/|$)/i, /(^|\/)\.aws(\/|$)/i, /(^|\/)\.gnupg(\/|$)/i, /(^|\/)\.kube(\/|$)/i,
  /(^|\/)\.docker\/config\.json$/i, /(^|\/)\.config\/gcloud\/application_default_credentials\.json$/i,
  /(^|\/)\.env(?:\.[\w-]+)*$/i, /(^|\/)\.dev\.vars(?:\.[\w-]+)*$/i, /(^|\/)\.envrc$/i,
  /(^|\/)\.netrc$/i, /(^|\/)\.npmrc$/i, /(^|\/)\.pypirc$/i,
  /(^|\/)id_(rsa|dsa|ed25519|ecdsa)(\.pub)?$/i, /(^|\/)\.git-credentials$/i,
  /(^|\/)\.git\/(config|hooks)(\/|$)/i,
  /(^|\/)(credentials?|secrets?)(\.[\w-]+)?$/i, /(^|\/)terraform\.tfstate(?:\.backup)?$/i,
  /\.(pem|key|p12|pfx|keystore)$/i,
  /(^|\/)\.fabius\/config\.json$/i, /Library\/Keychains(\/|$)/i,
  // The RESOLVED config path — FABIUS_HOME can move the key file out from under the
  // literal .fabius/config.json pattern above, so the actual location is always denied.
  new RegExp(CONFIG_PATH.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '$', 'i'),
];

// Commands whose effect cannot be walked back by re-running the agent. These are held
// for a human even under `--yes`; only the explicit `--dangerously-approve-everything`
// releases them, and that flag is recorded in the run's audit log.
const IRREVERSIBLE = [
  { re: /\brm\s+(-[a-z]*[rf][a-z]*\s+)+/i, why: 'recursive/forced delete' },
  { re: /\b(mkfs|dd\s+if=|shred|diskutil\s+erase)\b/i, why: 'destroys a filesystem or device' },
  { re: /\bgit\s+push\b/i, why: 'publishes to a remote' },
  { re: /\bgit\s+(reset\s+--hard|clean\s+-[a-z]*f|checkout\s+--\s)/i, why: 'discards uncommitted work' },
  { re: /\b(npm|yarn|pnpm)\s+publish\b/i, why: 'publishes a package' },
  // `--prod` cannot take a leading \b: the character before the dash is a space, and a
  // space→dash transition is not a word boundary, so the alternation must be bare.
  { re: /\b(vercel|wrangler|netlify|fly|gh)\b[^|]*(?:\bdeploy\b|--prod\b|\bpublish\b|\brelease\s+create\b)/i, why: 'deploys or publishes to production' },
  { re: /\bdrop\s+(table|database)\b/i, why: 'destroys stored data' },
  { re: /\bsudo\b/i, why: 'escalates privilege' },
  { re: /\bcurl\b[^|]*\|\s*(ba)?sh\b/i, why: 'executes code fetched from the network' },
  { re: /\b(shutdown|reboot|halt|killall)\b/i, why: 'takes the machine down' },
  { re: /\bchmod\s+(-R\s+)?777\b/i, why: 'makes files world-writable' },
];

export function isIrreversible(command) {
  const c = String(command || '');
  for (const r of IRREVERSIBLE) if (r.re.test(c)) return r.why;
  return null;
}

// Metacharacters that let one command line become several, or that hide what will really
// run (`$(…)`, backticks, a pipe, a redirect, an escaped quote). A string carrying them
// cannot be inspected honestly — the shell re-reads it after we have looked — so it is
// never auto-approved; it goes to a human.
const SHELL_META = /[|;&`$><\n\\*?\[\]{}()~]/;

// Interpreter flags that smuggle a program in as an argument: `node -e`, `python -c`,
// `perl -e`. Inspecting the command name tells you nothing about what these run.
const INLINE_CODE = /(^|\s)-{1,2}(e|c|p|eval|exec|command|print)(\s|=|$)/;

// What autonomous mode may run WITHOUT asking. A shell, interpreter, package runner,
// linter config and repository task are all executable programs, even when their command
// line looks familiar. They therefore do not belong here. File reads use the built-in
// jailed tools; this tiny list contains only commands whose arguments cannot name code or
// recursively expand into a secret after the gate has inspected them.
const AUTO_EXEC_ALLOW = [
  /^pwd(?:\s+-[LP])?$/,
  /^whoami$/,
  /^uname(?:\s+-[amnrsvpio]+)?$/,
  /^date$/,
];

export function autoApprovable(command) {
  const c = String(command || '').trim();
  if (!c || SHELL_META.test(c)) return false;
  if (INLINE_CODE.test(c)) return false;
  return AUTO_EXEC_ALLOW.some((re) => re.test(c));
}

// Path-looking tokens inside a command line, `~`/`$HOME`-expanded and unquoted, so the
// secret deny-list can be applied to `exec` and not only to `read`/`write`. Arbitrary
// shell is not statically decidable — `c""at $H""OME/.ssh/id_rsa` defeats this — so treat
// it as defense in depth that raises the bar, never as a boundary.
export function commandPaths(command) {
  const c = String(command || '');
  const home = homedir();
  const out = [];
  const re = /"([^"]*)"|'([^']*)'|([^\s"'=]+)/g;
  let m;
  while ((m = re.exec(c))) {
    let t = (m[1] ?? m[2] ?? m[3] ?? '').replace(/^[@<>]+/, '');
    if (!t) continue;
    if (t === '~' || t.startsWith('~/')) t = home + t.slice(1);
    // `~root/...` and `~someone/...` are ANOTHER account's home. Resolving them needs the
    // password database, which is not worth reaching for — but the one thing that matters
    // is already known: the answer is absolute, and it is not inside the working
    // directory. Left as-is the token looks relative and `~root/Documents/x.txt` resolves
    // *inside* the jail, so the gate auto-approves it under --yes while the shell reads
    // root's home. Mark it absolute so the jail check refuses and a human is asked.
    else if (t.startsWith('~')) t = '/' + t;
    else if (t.startsWith('$HOME')) t = home + t.slice(5);
    else if (t.startsWith('${HOME}')) t = home + t.slice(7);
    if (/[/\\.]/.test(t)) out.push(t);
  }
  return out;
}

// Is `p` inside the jail, after symlinks are resolved? A symlink that points out of the
// working directory is the classic escape, so the check runs on the REAL path — and on
// the nearest existing ancestor when the file itself does not exist yet (a create).
export function insideJail(p, jail) {
  const abs = isAbsolute(p) ? p : resolve(jail, p);
  let probe = abs;
  // Walk up to the first path that exists, so realpath can resolve it.
  while (!existsSync(probe)) {
    const parent = resolve(probe, '..');
    if (parent === probe) break;
    probe = parent;
  }
  let real;
  try { real = realpathSync(probe); } catch { real = probe; }
  // Re-attach the not-yet-existing tail so `jail/new/deep/file.txt` still resolves.
  const tail = relative(probe, abs);
  const full = tail && tail !== '' ? resolve(real, tail) : real;
  let realJail;
  try { realJail = realpathSync(jail); } catch { realJail = resolve(jail); }
  const rel = relative(realJail, full);
  return { ok: rel === '' || (!rel.startsWith('..') && !isAbsolute(rel)), resolved: full };
}

export function isSecretPath(p) {
  const s = String(p || '').replace(/\\/g, '/');
  const home = homedir().replace(/\\/g, '/');
  const candidates = [s, s.startsWith(home) ? s.slice(home.length) : s];
  return SECRET_PATTERNS.some((re) => candidates.some((c) => re.test(c)));
}

// Repository control data is not an ordinary artifact. Allowing an autonomous write to
// `.git/HEAD`, refs, the index or objects can rewrite history or corrupt the repository
// without ever spelling an irreversible shell command.
export function isProtectedWritePath(p) {
  return /(^|\/)\.git(\/|$)/i.test(String(p || '').replace(/\\/g, '/'));
}

export function networkOrigin(target) {
  try {
    const u = new URL(String(target || '').trim());
    if (!['http:', 'https:'].includes(u.protocol) || u.username || u.password) return null;
    return u.origin;
  } catch { return null; }
}

// Approval text is model-controlled. Render terminal controls and bidi overrides as
// visible escapes so a payload cannot clear/reorder the screen or counterfeit the prompt
// the operator is being asked to approve. Newlines remain newlines for full visibility.
export function visibleForApproval(value) {
  return [...String(value ?? '')].map((ch) => {
    if (ch === '\n') return ch;
    const cp = ch.codePointAt(0);
    if (ch === '\t') return '\\t';
    if (cp < 0x20 || (cp >= 0x7f && cp <= 0x9f)
        || cp === 0x061c || cp === 0x200e || cp === 0x200f
        || (cp >= 0x202a && cp <= 0x202e) || (cp >= 0x2066 && cp <= 0x2069)) {
      return `\\u{${cp.toString(16).padStart(4, '0')}}`;
    }
    return ch;
  }).join('');
}

const allowedOriginSet = (origins) => {
  const values = typeof origins === 'string' ? [origins] : [...(origins || [])];
  return new Set(values.map(networkOrigin).filter(Boolean));
};

// The pure decision. Returns { decision: 'allow' | 'ask' | 'deny', reason }.
//   posture   'ask' | 'auto' | 'never'
//   cap       'read' | 'net' | 'write' | 'exec'
//   target    a path (write/read) or a command line (exec)
//   oracle    true when the target is the delivered artifact the verification oracle wants
//             to run, rather than a command the model composed
export function classify({ posture = 'ask', cap, target, jail, dangerous = false, oracle = false, allowedOrigins = [] }) {
  if (!CAPS.includes(cap)) return { decision: 'deny', reason: `unknown capability "${cap}"` };

  if (cap === 'read' || cap === 'write') {
    if (isSecretPath(target)) return { decision: 'deny', reason: 'secret-bearing path — the deny-list is not negotiable' };
    if (cap === 'write' && isProtectedWritePath(target)) return { decision: 'deny', reason: 'repository control data under .git is not writable by an agent tool' };
    if (jail) {
      const j = insideJail(target, jail);
      if (!j.ok) return { decision: 'deny', reason: `outside the working directory (${j.resolved})` };
      if (isSecretPath(j.resolved)) return { decision: 'deny', reason: 'path resolves to a secret-bearing file — aliases do not bypass the deny-list' };
      if (cap === 'write' && isProtectedWritePath(j.resolved)) return { decision: 'deny', reason: 'path resolves to repository control data under .git' };
    }
  }

  // The deny-list is documented as absolute, so it screens commands too — not only the
  // read and write tools. A command may not name a secret-bearing path.
  if (cap === 'exec') {
    for (const p of commandPaths(target)) {
      if (isSecretPath(p)) return { decision: 'deny', reason: `secret-bearing path in the command (${p}) — the deny-list is not negotiable` };
      if (jail) {
        const j = insideJail(p, jail);
        if (j.ok && isSecretPath(j.resolved)) {
          return { decision: 'deny', reason: `command path resolves to a secret-bearing file (${j.resolved}) — aliases do not bypass the deny-list` };
        }
      }
    }
  }

  if (cap === 'read') return { decision: 'allow', reason: 'read-only capability' };

  // Outbound GET is still egress: it can carry workspace data in a path/query, and many
  // servers violate GET's "safe" semantics. Authority is exact-origin and session-scoped.
  if (cap === 'net') {
    if (posture === 'never') return { decision: 'deny', reason: 'read-only run (--approve never) — no outbound request' };
    const origin = networkOrigin(target);
    if (!origin) return { decision: 'deny', reason: 'network target is not an http(s) origin without embedded credentials' };
    if (allowedOriginSet(allowedOrigins).has(origin)) return { decision: 'allow', reason: `origin allowed for this run (${origin})` };
    return { decision: 'ask', reason: `first contact with network origin ${origin} — a human or explicit allow-list decides` };
  }

  if (posture === 'never') return { decision: 'deny', reason: 'read-only run (--approve never)' };

  if (cap === 'exec') {
    const why = isIrreversible(target);
    if (why) {
      // Unprompted release needs autonomous mode too: under the default ask posture a
      // human is approving each action, so the flag only downgrades the hold to the
      // same prompt everything else gets — never below it.
      if (dangerous) {
        if (posture === 'auto') return { decision: 'allow', reason: `irreversible (${why}) — released by --dangerously-approve-everything` };
        return { decision: 'ask', reason: `irreversible (${why}) — --dangerously-approve-everything lowers the hold to this prompt, not past it` };
      }
      return { decision: 'ask', reason: `irreversible: ${why}` };
    }
    // The verification oracle runs a whole program the model wrote. No allowlist can
    // vouch for a program the way it can vouch for `npm test`, so `--yes` does not get
    // to skip the human here: autonomous mode approves recognised commands, not
    // authored code. A run with no terminal simply skips the oracle and falls back to
    // the reviewer's verdict — the deliverable still ships, unverified by execution.
    if (oracle && posture !== 'ask') {
      if (dangerous) return { decision: 'allow', reason: 'model-authored code — released by --dangerously-approve-everything' };
      return { decision: 'ask', reason: 'model-authored code — a human reads the body before it runs on this machine' };
    }
    // The jail applies to commands too, not only to the read and write tools: under
    // `--yes` a bare `cat /etc/passwd` or `node /tmp/x.js` is on the allowlist above and
    // would otherwise run unprompted. A command naming a path outside the working
    // directory goes to a human instead. Same caveat as the secret screen — arbitrary
    // shell can spell a path other ways, so this raises the bar, it is not a seal.
    if (jail && posture === 'auto' && !dangerous) {
      for (const p of commandPaths(target)) {
        const j = insideJail(p, jail);
        if (!j.ok) return { decision: 'ask', reason: `the command reaches outside the working directory (${j.resolved}) — a human decides` };
      }
    }
    // Autonomous mode approves what it recognises and can inspect; anything else — an
    // unknown binary, a pipeline, a substitution, an interpreter given inline code —
    // is held for a human, and a non-interactive run refuses it rather than guessing.
    if (posture === 'auto' && !dangerous && !autoApprovable(target)) {
      return { decision: 'ask', reason: 'autonomous mode approves only recognised, inspectable commands — this one is not on that list' };
    }
  }

  if (posture === 'auto') return { decision: 'allow', reason: 'autonomous mode (--yes)' };
  return { decision: 'ask', reason: 'default posture is to ask before acting' };
}

// The prompting shell. Non-interactive runs (no TTY, e.g. cron) must never hang waiting
// for a human — an `ask` there resolves to DENY, and the run continues without the tool.
export async function requestApproval({ cap, target, payload = '', reason, autoNo = false }) {
  const interactive = !!(process.stdin.isTTY && process.stdout.isTTY);
  if (autoNo || !interactive) {
    return { approved: false, why: interactive ? 'declined' : 'no terminal to ask (non-interactive run) — denied' };
  }
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  try {
    const head = cap === 'exec' ? 'run this command' : cap === 'net' ? `contact ${networkOrigin(target) || target}` : `write ${target}`;
    process.stdout.write(`\n  \x1b[33m⚠ fabius wants to ${head}\x1b[0m\n`);
    if (cap === 'exec') {
      const t = visibleForApproval(target);
      process.stdout.write(t.split('\n').map((l, i) => `    \x1b[2m${i ? '|' : '$'}\x1b[0m ${l}`).join('\n') + '\n');
    } else if (cap === 'write') {
      const body = visibleForApproval(payload);
      process.stdout.write(body.split('\n').map(l => `    \x1b[2m|\x1b[0m ${l}`).join('\n') + '\n');
    } else if (cap === 'net') {
      process.stdout.write(`    ${visibleForApproval(target)}\n`);
    }
    process.stdout.write(`    \x1b[2m${visibleForApproval(reason)}\x1b[0m\n`);
    const choices = cap === 'net' ? 'y/N/a=allow this origin this run' : 'y/N/a=approve all this run';
    const a = (await rl.question(`    approve? [${choices}] `)).trim().toLowerCase();
    if (a === 'a' || a === 'all') return { approved: true, why: 'approved (all, this run)', all: true };
    return { approved: a === 'y' || a === 'yes', why: a === 'y' || a === 'yes' ? 'approved' : 'declined' };
  } finally { rl.close(); }
}

// A live gate bound to one run: holds the posture, the jail, and the "approve all"
// escalation, and records every decision for the run's audit trail.
export function makeGate({ posture = 'ask', jail = process.cwd(), dangerous = false, autoNo = false, allowedOrigins = [] } = {}) {
  const log = [];
  let approveAll = false;
  const origins = allowedOriginSet(allowedOrigins);
  return {
    log,
    get posture() { return approveAll ? 'auto' : posture; },
    get allowedOrigins() { return [...origins]; },
    async check(cap, target, { oracle = false, payload = '', allowedOrigins: suppliedOrigins = [] } = {}) {
      for (const origin of allowedOriginSet(suppliedOrigins)) origins.add(origin);
      const d = classify({ posture: approveAll ? 'auto' : posture, cap, target, jail, dangerous, oracle, allowedOrigins: origins });
      let approved = d.decision === 'allow';
      let why = d.reason;
      if (d.decision === 'ask') {
        const r = await requestApproval({ cap, target, payload, reason: d.reason, autoNo });
        approved = r.approved; why = r.why;
        if (r.all && cap !== 'net') approveAll = true;
      }
      const targetText = String(target);
      const payloadText = String(payload || '');
      const digest = (s) => createHash('sha256').update(s).digest('hex');
      if (approved && cap === 'net') {
        const origin = networkOrigin(target);
        if (origin) origins.add(origin);
      }
      log.push({
        at: new Date().toISOString(), cap, target: redact(targetText.slice(0, 300)),
        targetSha256: digest(targetText), payloadSha256: digest(payloadText),
        payloadBytes: Buffer.byteLength(payloadText), actionSha256: digest(`${cap}\0${targetText}\0${payloadText}`),
        decision: d.decision, approved, why: redact(why), dangerous,
      });
      return { approved, why, decision: d.decision };
    },
  };
}

export function isSymlink(p) {
  try { return lstatSync(p).isSymbolicLink(); } catch { return false; }
}
