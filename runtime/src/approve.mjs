// THE PERMISSION GATE — the difference between an agent in a sandbox and an agent on
// your laptop.
//
// In the cloud console the blast radius is a worker with no filesystem. Locally the
// blast radius is the owner's machine, so capability is not a preference: every tool
// declares a `cap`, every cap has a standing decision, and the decisions that cannot
// be undone are held back even in autonomous mode.
//
//   read   — inside the working directory, minus the secret deny-list. Never prompts.
//   net    — outbound HTTP GET. Never prompts (it reads; it does not change the world).
//   write  — create/modify a file inside the working directory. Prompts by default.
//   exec   — run a command on this machine. Prompts by default.
//
// Three postures: `ask` (default — a human decides each new class of action), `auto`
// (approve write/exec, still hold irreversible actions), `never` (read-only; the agent
// can look and reason but cannot touch anything).
//
// The gate is a PURE decision function (`classify`) plus a thin prompting shell, so the
// whole policy is testable with no TTY and no model.

import { realpathSync, existsSync, lstatSync } from 'node:fs';
import { resolve, relative, isAbsolute, sep } from 'node:path';
import { createInterface } from 'node:readline/promises';
import { homedir } from 'node:os';

export const CAPS = ['read', 'net', 'write', 'exec'];

// Files an agent has no business reading, whatever the task says. Matched against the
// resolved path, so `../../.ssh/id_rsa` and a symlink pointing there both trip it.
const SECRET_PATTERNS = [
  /(^|\/)\.ssh(\/|$)/, /(^|\/)\.aws(\/|$)/, /(^|\/)\.gnupg(\/|$)/, /(^|\/)\.kube(\/|$)/,
  /(^|\/)\.env(\.[\w-]+)?$/, /(^|\/)\.netrc$/, /(^|\/)\.npmrc$/, /(^|\/)\.pypirc$/,
  /(^|\/)id_(rsa|ed25519|ecdsa)(\.pub)?$/, /(^|\/)\.git-credentials$/,
  /(^|\/)credentials(\.json)?$/, /\.(pem|key|p12|pfx|keystore)$/,
  /(^|\/)\.fabius\/config\.json$/, /Library\/Keychains(\/|$)/,
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
  const s = String(p || '').replace(new RegExp('\\' + sep, 'g'), '/');
  const home = homedir().replace(/\\/g, '/');
  const candidates = [s, s.startsWith(home) ? s.slice(home.length) : s];
  return SECRET_PATTERNS.some((re) => candidates.some((c) => re.test(c)));
}

// The pure decision. Returns { decision: 'allow' | 'ask' | 'deny', reason }.
//   posture   'ask' | 'auto' | 'never'
//   cap       'read' | 'net' | 'write' | 'exec'
//   target    a path (write/read) or a command line (exec)
export function classify({ posture = 'ask', cap, target, jail, dangerous = false }) {
  if (!CAPS.includes(cap)) return { decision: 'deny', reason: `unknown capability "${cap}"` };

  if (cap === 'read' || cap === 'write') {
    if (isSecretPath(target)) return { decision: 'deny', reason: 'secret-bearing path — the deny-list is not negotiable' };
    if (jail) {
      const j = insideJail(target, jail);
      if (!j.ok) return { decision: 'deny', reason: `outside the working directory (${j.resolved})` };
    }
  }

  if (cap === 'read' || cap === 'net') return { decision: 'allow', reason: 'read-only capability' };

  if (posture === 'never') return { decision: 'deny', reason: 'read-only run (--approve never)' };

  if (cap === 'exec') {
    const why = isIrreversible(target);
    if (why) {
      if (dangerous) return { decision: 'allow', reason: `irreversible (${why}) — released by --dangerously-approve-everything` };
      return { decision: 'ask', reason: `irreversible: ${why}` };
    }
  }

  if (posture === 'auto') return { decision: 'allow', reason: 'autonomous mode (--yes)' };
  return { decision: 'ask', reason: 'default posture is to ask before acting' };
}

// The prompting shell. Non-interactive runs (no TTY, e.g. cron) must never hang waiting
// for a human — an `ask` there resolves to DENY, and the run continues without the tool.
export async function requestApproval({ cap, target, reason, autoNo = false }) {
  const interactive = !!(process.stdin.isTTY && process.stdout.isTTY);
  if (autoNo || !interactive) {
    return { approved: false, why: interactive ? 'declined' : 'no terminal to ask (non-interactive run) — denied' };
  }
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  try {
    const head = cap === 'exec' ? 'run this command' : `write ${target}`;
    process.stdout.write(`\n  \x1b[33m⚠ fabius wants to ${head}\x1b[0m\n`);
    if (cap === 'exec') process.stdout.write(`    \x1b[2m$\x1b[0m ${String(target).slice(0, 600)}\n`);
    process.stdout.write(`    \x1b[2m${reason}\x1b[0m\n`);
    const a = (await rl.question('    approve? [y/N/a=approve all this run] ')).trim().toLowerCase();
    if (a === 'a' || a === 'all') return { approved: true, why: 'approved (all, this run)', all: true };
    return { approved: a === 'y' || a === 'yes', why: a === 'y' || a === 'yes' ? 'approved' : 'declined' };
  } finally { rl.close(); }
}

// A live gate bound to one run: holds the posture, the jail, and the "approve all"
// escalation, and records every decision for the run's audit trail.
export function makeGate({ posture = 'ask', jail = process.cwd(), dangerous = false, autoNo = false } = {}) {
  const log = [];
  let approveAll = false;
  return {
    log,
    get posture() { return approveAll ? 'auto' : posture; },
    async check(cap, target) {
      const d = classify({ posture: approveAll ? 'auto' : posture, cap, target, jail, dangerous });
      let approved = d.decision === 'allow';
      let why = d.reason;
      if (d.decision === 'ask') {
        const r = await requestApproval({ cap, target, reason: d.reason, autoNo });
        approved = r.approved; why = r.why;
        if (r.all) approveAll = true;
      }
      log.push({ at: new Date().toISOString(), cap, target: String(target).slice(0, 300), decision: d.decision, approved, why });
      return { approved, why, decision: d.decision };
    },
  };
}

export function isSymlink(p) {
  try { return lstatSync(p).isSymbolicLink(); } catch { return false; }
}
