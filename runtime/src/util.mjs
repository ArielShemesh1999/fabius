// Small shared helpers. Zero dependencies, pure where possible.

export const clamp = (s, max) => {
  const t = typeof s === 'string' ? s : String(s ?? '');
  return t.length > max ? t.slice(0, max) + `\n[…truncated at ${max} chars]` : t;
};

export const isTTY = () => !!(process.stdout.isTTY && process.stdin.isTTY);

const C = {
  reset: '\x1b[0m', dim: '\x1b[2m', bold: '\x1b[1m',
  violet: '\x1b[38;5;99m', red: '\x1b[31m', green: '\x1b[32m', yellow: '\x1b[33m', cyan: '\x1b[36m',
};
// Colour only when a human is watching and NO_COLOR is unset — piped output stays clean.
const useColor = () => !!process.stdout.isTTY && !process.env.NO_COLOR;
export const paint = (key, s) => (useColor() && C[key] ? C[key] + s + C.reset : s);

export const say = (s = '') => process.stdout.write(s + '\n');
export const warn = (s) => process.stderr.write(paint('yellow', s) + '\n');
export const die = (s, code = 1) => { process.stderr.write(paint('red', s) + '\n'); process.exit(code); };

// A deliverable that POINTS AT content instead of containing it (M11). The measured
// failure mode is a short answer that says "as described above" while containing no
// above. Cheap, sync, no model call.
export function isStubDeliverable(text) {
  const t = String(text || '').trim();
  if (!t) return true;
  if (t.length < 400 && /\b(as (described|outlined|shown) (above|below)|see (above|below|the (plan|section))|the (plan|artifact|document) (above|below)|refer to)\b/i.test(t)) return true;
  return t.length < 120;
}

// Pull the first fenced ```lang block — the execution oracle's input.
export function extractCodeBlock(text) {
  const m = String(text || '').match(/```([a-zA-Z0-9_+-]*)\s*\n([\s\S]*?)```/);
  if (!m) return null;
  const lang = (m[1] || '').toLowerCase();
  const known = { py: 'python', python: 'python', js: 'node', javascript: 'node', node: 'node', mjs: 'node', sh: 'bash', bash: 'bash', shell: 'bash', zsh: 'bash' };
  return { lang: known[lang] || null, code: m[2] };
}

// Parse ONE agent turn → {think, tool, input}. Tolerant by design: pulls the first
// balanced {...}, coerces an unknown tool to `deliver`, and on any parse failure
// treats the whole text as a delivery — a non-JSON reply still finishes the run.
export function parseAgentAction(text, allowed) {
  const allow = Array.isArray(allowed) ? allowed : ['deliver'];
  const t = String(text || '');
  let jsonStr = '';
  const i = t.indexOf('{');
  if (i >= 0) {
    let depth = 0, inStr = false, esc = false;
    for (let j = i; j < t.length; j++) {
      const ch = t[j];
      if (inStr) { if (esc) esc = false; else if (ch === '\\') esc = true; else if (ch === '"') inStr = false; continue; }
      if (ch === '"') inStr = true;
      else if (ch === '{') depth++;
      else if (ch === '}') { depth--; if (depth === 0) { jsonStr = t.slice(i, j + 1); break; } }
    }
  }
  if (jsonStr) {
    try {
      const o = JSON.parse(jsonStr);
      const tool = String(o.tool || o.action || '').toLowerCase();
      const input = typeof o.input === 'string' ? o.input
        : (typeof o.artifact === 'string' ? o.artifact
        : (o.input != null ? JSON.stringify(o.input) : ''));
      return {
        think: typeof o.think === 'string' ? o.think : (typeof o.thought === 'string' ? o.thought : ''),
        tool: allow.includes(tool) ? tool : 'deliver',
        input,
      };
    } catch { /* fall through to a graceful deliver */ }
  }
  return { think: '', tool: 'deliver', input: t.trim() };
}

// {"pass":bool,"score":0-100,"issues":[…],"fix":"…"} out of a reviewer reply.
export function parseVerdict(text) {
  const t = String(text || '');
  const i = t.indexOf('{');
  if (i < 0) return null;
  const j = t.lastIndexOf('}');
  if (j <= i) return null;
  try {
    const o = JSON.parse(t.slice(i, j + 1));
    return {
      pass: !!o.pass,
      score: Math.max(0, Math.min(100, Number(o.score) || 0)),
      issues: Array.isArray(o.issues) ? o.issues.map((x) => String(x).slice(0, 400)).slice(0, 8) : [],
      fix: String(o.fix || '').slice(0, 600),
    };
  } catch { return null; }
}

// A stable, human-scannable id: 2026-07-27T14-03-51-a1b2.
export function stamp(now = new Date()) {
  const iso = now.toISOString().replace(/[:.]/g, '-').replace(/Z$/, '');
  return iso.slice(0, 19) + '-' + Math.random().toString(16).slice(2, 6);
}

export const nowIso = () => new Date().toISOString();
