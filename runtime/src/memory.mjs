// LOCAL MEMORY — the archivum layout, on your disk, in plain markdown.
//
// A harness may compound memory into a vector database. Locally there is no database and
// there should not be one: a knowledge base you cannot read in a text editor is a
// knowledge base you cannot correct. So memory here is exactly what archivum specifies —
// one page per fact, an index, and an append-only log — stored as files you own.
//
// Two properties come straight from the archivum rules, because both were measured, not assumed:
//
//   AUTHORITY- AND VERIFY-GATED WRITES. Only an explicit per-run opt-in plus a
//   deliverable that passed review at score ≥ 70 may compound.
//
//   RECALL STANDS DOWN ON FRESH-EYES WORK. Recalled context measurably helps design and
//   product work and measurably HURTS security and incident work, where a stale prior is
//   exactly the wrong witness. Security routes read no memory; recalled memory elsewhere
//   is candidate evidence, never authority.

import {
  readFileSync, appendFileSync, existsSync, readdirSync, mkdirSync, unlinkSync,
  chmodSync, lstatSync, openSync, closeSync, writeFileSync,
} from 'node:fs';
import { createHash } from 'node:crypto';
import { join, basename } from 'node:path';
import { MEMORY_DIR, ensureDirs, atomicWriteFile } from './config.mjs';

const INDEX = () => join(MEMORY_DIR, 'MEMORY.md');
const LOG = () => join(MEMORY_DIR, 'log.md');
const HISTORY = () => join(MEMORY_DIR, '.history');
const LOCK = () => join(MEMORY_DIR, '.write.lock');
let historySequence = 0;

export const slug = (s) => String(s || '').toLowerCase()
  .replace(/[^a-z0-9֐-׿]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60) || 'note';

export function initMemory() {
  ensureMemoryDir();
  return withMemoryLock(ensureMemoryControlFiles);
}

function ensureMemoryDir() {
  ensureDirs();
  if (!existsSync(MEMORY_DIR)) mkdirSync(MEMORY_DIR, { recursive: true, mode: 0o700 });
  chmodSync(MEMORY_DIR, 0o700);
}

function ensureMemoryControlFiles() {
  ensureMemoryFile(INDEX(), '# fabius memory\n\nOne line per page. This file is what a run reads first.\n\n');
  ensureMemoryFile(LOG(), '# log\n\nAppend-only. Newest at the bottom.\n\n');
}

function ensureMemoryFile(path, initial) {
  if (!existsSync(path)) atomicWriteFile(path, initial);
  const st = lstatSync(path);
  if (!st.isFile() || st.isSymbolicLink()) throw new Error(`refusing non-regular memory state file: ${path}`);
  chmodSync(path, 0o600);
}

export function listMemory() {
  if (!existsSync(MEMORY_DIR)) return [];
  let names;
  try { names = readdirSync(MEMORY_DIR); } catch { return []; }
  return names
    .filter((f) => f.endsWith('.md') && f !== 'MEMORY.md' && f !== 'log.md')
    .flatMap((f) => {
      const path = join(MEMORY_DIR, f);
      // Recalled pages are evidence supplied to the model. Never follow a dropped-in
      // symlink and mislabel unrelated local bytes as prior memory.
      let raw;
      try {
        const st = lstatSync(path);
        if (!st.isFile() || st.isSymbolicLink()) return [];
        raw = readFileSync(path, 'utf8');
      } catch { return []; }
      const fm = raw.match(/^---\n([\s\S]*?)\n---\n?/);
      const meta = {};
      for (const line of (fm?.[1] || '').split('\n')) {
        const m = line.match(/^(\w+):\s*(.*)$/);
        if (m) meta[m[1]] = m[2].trim();
      }
      const score = Math.max(0, Math.min(100, Number(meta.score) || 0));
      return [{ file: f, path, title: meta.title || f.replace(/\.md$/, ''),
               kind: meta.kind || 'note', scope: meta.scope || 'fabius', score,
               created: meta.created || '', body: fm ? raw.slice(fm[0].length) : raw }];
    });
}

function withMemoryLock(work) {
  let fd;
  const sleeper = new Int32Array(new SharedArrayBuffer(4));
  for (let attempt = 0; attempt < 200; attempt++) {
    try {
      fd = openSync(LOCK(), 'wx', 0o600);
      try { writeFileSync(fd, `${process.pid}\n`); }
      catch (e) {
        try { closeSync(fd); } catch { /* already closed */ }
        fd = undefined;
        try { unlinkSync(LOCK()); } catch { /* best effort */ }
        throw e;
      }
      break;
    } catch (e) {
      if (e.code !== 'EEXIST') throw e;
      try {
        const st = lstatSync(LOCK());
        if (Date.now() - st.mtimeMs > 30000) { unlinkSync(LOCK()); continue; }
      } catch { continue; }
      Atomics.wait(sleeper, 0, 0, 10);
    }
  }
  if (fd === undefined) throw new Error('memory store is busy — could not acquire the write lock');
  try { return work(); }
  finally {
    try { closeSync(fd); } catch { /* already closed */ }
    try { unlinkSync(LOCK()); } catch { /* another cleanup already removed it */ }
  }
}

function archiveMemoryPage(path, reason, at) {
  let raw;
  try {
    const st = lstatSync(path);
    if (!st.isFile() || st.isSymbolicLink()) return '';
    raw = readFileSync(path, 'utf8');
  } catch { return ''; }
  if (!existsSync(HISTORY())) mkdirSync(HISTORY(), { recursive: true, mode: 0o700 });
  chmodSync(HISTORY(), 0o700);
  const stamp = at.replace(/[:.]/g, '-');
  const name = `${stamp}-${process.pid}-${historySequence++}-${reason}-${basename(path)}`;
  atomicWriteFile(join(HISTORY(), name), raw);
  return `.history/${name}`;
}

export function writeMemory(input) {
  ensureMemoryDir();
  return withMemoryLock(() => {
    ensureMemoryControlFiles();
    return writeMemoryUnlocked(input);
  });
}

function writeMemoryUnlocked({ title, body, kind = 'note', scope = 'fabius', score = 100, tags = [] }) {
  const cleanTitle = String(title || '').replace(/\s+/g, ' ').trim() || 'Untitled memory';
  const cleanBody = String(body || '');
  const cleanKind = String(kind || 'note').replace(/\s+/g, ' ').trim() || 'note';
  const cleanScope = String(scope || 'fabius').replace(/\s+/g, ' ').trim() || 'fabius';
  const cleanScore = Math.max(0, Math.min(100, Number(score) || 0));
  const base = slug(cleanTitle);
  let name = base;
  const basePath = join(MEMORY_DIR, `${base}.md`);
  if (existsSync(basePath)) {
    const current = memoryTitleAt(basePath);
    if (current !== cleanTitle) {
      const digest = createHash('sha256').update(cleanTitle).digest('hex');
      name = '';
      // Preserve a stable filename across restarts, extending the suffix rather than
      // overwriting another page if the shortened hash itself ever collides.
      for (const width of [8, 12, 16, 24, 32, 48]) {
        const candidate = `${base.slice(0, 59 - width)}-${digest.slice(0, width)}`;
        const candidatePath = join(MEMORY_DIR, `${candidate}.md`);
        if (!existsSync(candidatePath) || memoryTitleAt(candidatePath) === cleanTitle) {
          name = candidate;
          break;
        }
      }
      if (!name) throw new Error('could not allocate a collision-safe memory filename');
    }
  }
  const path = join(MEMORY_DIR, `${name}.md`);
  const at = new Date().toISOString();
  const previousRaw = regularFileText(path);
  const created = previousRaw?.match(/^created:\s*(.*)$/m)?.[1]?.trim() || at;
  const history = previousRaw ? archiveMemoryPage(path, 'update', at) : '';
  const fm = ['---', `title: ${cleanTitle}`, `kind: ${cleanKind}`, `scope: ${cleanScope}`, `score: ${cleanScore}`,
              `created: ${created}`, `updated: ${at}`, tags.length ? `tags: ${tags.join(', ')}` : null, '---', ''].filter((x) => x !== null).join('\n');
  atomicWriteFile(path, fm + cleanBody.trim() + '\n');
  // Index: one line per page, replaced in place if the page already existed.
  const indexTitle = cleanTitle.replace(/([\\\[\]])/g, '\\$1');
  const line = `- [${indexTitle}](${name}.md) <!-- fabius-memory kind=${encodeURIComponent(cleanKind)} scope=${encodeURIComponent(cleanScope)} score=${cleanScore} created=${encodeURIComponent(created)} --> — ${firstSentence(cleanBody)}`;
  const idx = readFileSync(INDEX(), 'utf8');
  const re = new RegExp(`^.*\\(${escapeRegex(`${name}.md`)}\\).*$`, 'm');
  atomicWriteFile(INDEX(), re.test(idx) ? idx.replace(re, line) : idx.trimEnd() + '\n' + line + '\n');
  appendFileSync(LOG(), `## [${at.slice(0, 10)}] ${history ? 'update' : 'write'} | ${cleanTitle}\n- kind ${cleanKind} · scope ${cleanScope} · score ${cleanScore}${history ? `\n- previous version: ${history}` : ''}\n\n`, { mode: 0o600 });
  chmodSync(LOG(), 0o600);
  return { path, name };
}

export function deleteMemory(name) {
  // A read-like remove probe against an absent store must stay side-effect free.
  if (!existsSync(MEMORY_DIR)) return false;
  ensureMemoryDir();
  return withMemoryLock(() => {
    ensureMemoryControlFiles();
    return deleteMemoryUnlocked(name);
  });
}

function deleteMemoryUnlocked(name) {
  const requested = String(name || '').trim();
  const pages = listMemory();
  const page = pages.find((m) => m.file === requested || m.file === `${requested}.md`)
    || pages.find((m) => m.title === requested)
    || pages.find((m) => m.file === `${slug(requested)}.md`);
  if (!page) return false;
  const at = new Date().toISOString();
  const history = archiveMemoryPage(page.path, 'delete', at);
  if (!history) throw new Error('refusing to delete a memory page without a recoverable history snapshot');
  unlinkSync(page.path);
  const idx = readFileSync(INDEX(), 'utf8');
  const file = escapeRegex(page.file);
  atomicWriteFile(INDEX(), idx.replace(new RegExp(`^.*\\(${file}\\).*$\n?`, 'm'), ''));
  appendFileSync(LOG(), `## [${at.slice(0, 10)}] delete | ${page.title}\n- recoverable version: ${history}\n\n`, { mode: 0o600 });
  chmodSync(LOG(), 0o600);
  return true;
}

function memoryTitleAt(path) {
  return regularFileText(path)?.match(/^title:\s*(.*)$/m)?.[1]?.trim() || null;
}

function regularFileText(path) {
  try {
    const st = lstatSync(path);
    if (!st.isFile() || st.isSymbolicLink()) return null;
    return readFileSync(path, 'utf8');
  } catch { return null; }
}

const escapeRegex = (s) => String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

function listMemoryIndex() {
  if (!existsSync(INDEX())) return [];
  try {
    const st = lstatSync(INDEX());
    if (!st.isFile() || st.isSymbolicLink()) return [];
    return readFileSync(INDEX(), 'utf8').split('\n').flatMap((line) => {
      const m = line.match(/^- \[(.*?)\]\(([^)]+\.md)\) <!-- fabius-memory kind=(\S+) scope=(\S+) score=(\d+(?:\.\d+)?) created=(\S+) --> — (.*)$/);
      if (!m) return [];
      const score = Math.max(0, Math.min(100, Number(m[5]) || 0));
      return [{
        file: m[2], path: join(MEMORY_DIR, m[2]),
        title: m[1].replace(/\\([\\\[\]])/g, '$1'),
        kind: decodeURIComponent(m[3]), scope: decodeURIComponent(m[4]), score,
        created: decodeURIComponent(m[6]), body: m[7], indexOnly: true,
      }];
    });
  } catch { return []; }
}

const STOP = new Set(['the', 'a', 'an', 'and', 'or', 'to', 'of', 'in', 'for', 'is', 'it', 'this', 'that', 'with', 'on', 'at', 'as', 'by', 'be', 'are', 'was', 'from', 'how', 'what', 'why', 'do', 'does', 'my', 'i', 'you', 'we']);
const tokens = (s) => new Set(String(s || '').toLowerCase().match(/[a-z0-9֐-׿]{2,}/g)?.filter((t) => !STOP.has(t)) || []);

// Keyword overlap, weighted by the verify score and decayed by age. No embedding model,
// no network, no index to rebuild — and on a memory of a few hundred pages it is both
// instant and inspectable, which matters more here than recall@k.
export function recallMemory(query, { scope = null, k = 5, minScore = 70, mode = 'normal' } = {}) {
  const q = tokens(query);
  if (!q.size || !['normal', 'dampened'].includes(mode)) return [];
  const now = Date.now();
  const floor = mode === 'dampened' ? Math.max(90, minScore) : minScore;
  const pages = mode === 'dampened' ? listMemoryIndex() : listMemory();
  return pages
    .filter((m) => m.score >= floor && (!scope || m.scope === scope || m.scope === 'fabius'))
    .map((m) => {
      const t = tokens(m.title + ' ' + m.body);
      let hits = 0;
      for (const w of q) if (t.has(w)) hits++;
      const overlap = hits / q.size;
      const parsed = Date.parse(m.created);
      const ageDays = Number.isFinite(parsed) ? Math.max(0, (now - parsed) / 86400000) : 999;
      // ~0.5 at 90 days, floored at 0.3 — a fresh correction outranks a stale fact.
      const recency = Math.max(0.3, Math.pow(0.5, ageDays / 90));
      return { ...m, hits, relevance: overlap * (0.5 + 0.5 * m.score / 100) * recency };
    })
    .filter((m) => m.hits > 0)
    .sort((a, b) => b.relevance - a.relevance)
    .slice(0, k);
}

// What a run sees before it starts. Empty string when nothing is relevant — never a
// placeholder, so the model is not primed by the shape of an absent memory.
export function memoryContext(task, opts = {}) {
  const mode = opts.mode || 'off';
  if (!['normal', 'dampened'].includes(mode)) return '';
  const hits = recallMemory(task, { ...opts, mode });
  if (!hits.length) return '';
  return hits.map((h) => `- [suspect prior — verify against current evidence] ${h.title} (${h.kind}, verified ${h.score}): ${firstSentence(h.body)}`).join('\n');
}

// THE GATE. A deliverable compounds only when an independent reviewer passed it at
// ≥ 70 and the task carried something worth keeping. Returns a proposal, never a write —
// the caller decides, so a dry run stays dry.
export function decideMemoryWrite({ task, output, verdict, route, authorized = false }) {
  // Authority is a capability, not a truthy preference: only the literal boolean passed
  // by an explicit per-run opt-in may release the write. Strings from config/env/JSON and
  // omitted or false values all fail closed.
  if (authorized !== true) {
    return { write: false, reason: 'memory write requires explicit opt-in for this run' };
  }
  const score = verdict?.score || 0;
  if (!verdict?.pass || score < 70) {
    return { write: false, reason: `unverified (score ${score} < 70) — an unverified answer must not become durable memory` };
  }
  if (String(output || '').length < 200) {
    return { write: false, reason: 'deliverable too small to carry a durable fact' };
  }
  const isDecision = /\b(decided|chose|we will|going with|rejected|instead of|because)\b/i.test(output);
  const isDurable = isDecision || (route?.domains || []).length > 0;
  if (!isDurable) return { write: false, reason: 'no decision or domain fact worth keeping' };
  return {
    write: true,
    reason: `verified ${score} — a ${isDecision ? 'decision' : 'domain fact'} worth keeping`,
    title: titleFor(task),
    kind: isDecision ? 'decision' : 'fact',
    score,
  };
}

function titleFor(task) {
  const t = String(task || '').trim().replace(/\s+/g, ' ');
  return t.length > 70 ? t.slice(0, 67) + '…' : t;
}
function firstSentence(body) {
  const t = String(body || '').replace(/\s+/g, ' ').trim();
  const m = t.match(/^(.{0,160}?[.!?])(\s|$)/);
  return (m ? m[1] : t.slice(0, 160)).trim();
}

export { firstSentence };
