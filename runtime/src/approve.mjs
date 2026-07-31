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

// Metacharacters that let one command line become several, or that hide what will really
// run (`$(…)`, backticks, a pipe, a redirect, an escaped quote). A string carrying them
// cannot be inspected honestly — the shell re-reads it after we have looked — so it is
// never auto-approved; it goes to a human.
const SHELL_META = /[|;&`$><\n\\]/;

// Interpreter flags that smuggle a program in as an argument: `node -e`, `python -c`,
// `perl -e`. Inspecting the command name tells you nothing about what these run.
const INLINE_CODE = /(^|\s)-{1,2}(e|c|p|eval|exec|command|print)(\s|=|$)/;

// What autonomous mode may run WITHOUT asking. This is deliberately an allowlist: the old
// policy — "auto-approve anything that does not match the irreversible denylist" — is
// fail-open, because a regex denylist over a raw shell string is trivially evaded
// (`rm --recursive --force`, `find . -delete`, `s''udo`, base64 | sh). The denylist is
// kept below as a warn-layer, not as the boundary.
const AUTO_EXEC_ALLOW = [
  /^(npm|pnpm|yarn|bun)\s+(test|run\s+[\w:.-]+|ls|list|why|outdated|audit)\b/,
  /^(npx\s+)?(jest|vitest|mocha|ava|pytest|tsc|eslint|prettier|ruff|black|mypy|go\s+test|cargo\s+(test|check|build|clippy))\b/,
  // Each argument group must start with whitespace and its body may not contain any, so
  // a run of spaces has exactly one valid split. The earlier `(\s+[…]*)*` — a nestable
  // quantifier over a body that can match empty — had 2^(n-1) of them, and a command of
  // the form `node x` + 30 spaces + `#` froze this gate for minutes on the way in.
  /^(node|python3?|deno|bun)(\s+[\w./@=:+-]+)+$/,
  /^git\s+(status|diff|log|show|branch|remote|rev-parse|describe|ls-files|blame)\b/,
  /^(ls|pwd|whoami|date|echo|which|uname|wc|head|tail|cat|file|stat|du|df|tree|sort|uniq|cut|basename|dirname|realpath)\b/,
  /^(grep|rg|jq|diff|md5|shasum|sha256sum)\b/,
  /^(make)\s+(test|check|lint|build)\b/,
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
  const s = String(p || '').replace(new RegExp('\\' + sep, 'g'), '/');
  const home = homedir().replace(/\\/g, '/');
  const candidates = [s, s.startsWith(home) ? s.slice(home.length) : s];
  return SECRET_PATTERNS.some((re) => candidates.some((c) => re.test(c)));
}

// The pure decision. Returns { decision: 'allow' | 'ask' | 'deny', reason }.
//   posture   'ask' | 'auto' | 'never'
//   cap       'read' | 'net' | 'write' | 'exec'
//   target    a path (write/read) or a command line (exec)
//   oracle    true when the target is the delivered artifact the verification oracle wants
//             to run, rather than a command the model composed
export function classify({ posture = 'ask', cap, target, jail, dangerous = false, oracle = false }) {
  if (!CAPS.includes(cap)) return { decision: 'deny', reason: `unknown capability "${cap}"` };

  if (cap === 'read' || cap === 'write') {
    if (isSecretPath(target)) return { decision: 'deny', reason: 'secret-bearing path — the deny-list is not negotiable' };
    if (jail) {
      const j = insideJail(target, jail);
      if (!j.ok) return { decision: 'deny', reason: `outside the working directory (${j.resolved})` };
    }
  }

  // The deny-list is documented as absolute, so it screens commands too — not only the
  // read and write tools. A command may not name a secret-bearing path.
  if (cap === 'exec') {
    for (const p of commandPaths(target)) {
      if (isSecretPath(p)) return { decision: 'deny', reason: `secret-bearing path in the command (${p}) — the deny-list is not negotiable` };
    }
  }

  if (cap === 'read') return { decision: 'allow', reason: 'read-only capability' };

  // `net` observes rather than changes, so it never prompts — but a read-only run means
  // read-only: no outbound request either.
  if (cap === 'net') {
    if (posture === 'never') return { decision: 'deny', reason: 'read-only run (--approve never) — no outbound request' };
    return { decision: 'allow', reason: 'read-only capability' };
  }

  if (posture === 'never') return { decision: 'deny', reason: 'read-only run (--approve never)' };

  if (cap === 'exec') {
    const why = isIrreversible(target);
    if (why) {
      if (dangerous) return { decision: 'allow', reason: `irreversible (${why}) — released by --dangerously-approve-everything` };
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
    async check(cap, target, { oracle = false } = {}) {
      const d = classify({ posture: approveAll ? 'auto' : posture, cap, target, jail, dangerous, oracle });
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
