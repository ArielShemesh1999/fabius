// LOCAL MEMORY — the archivum layout, on your disk, in plain markdown.
//
// A harness may compound memory into a vector database. Locally there is no database and
// there should not be one: a knowledge base you cannot read in a text editor is a
// knowledge base you cannot correct. So memory here is exactly what archivum specifies —
// one page per fact, an index, and an append-only log — stored as files you own.
//
// Two properties come straight from the archivum rules, because both were measured, not assumed:
//
//   VERIFY-GATED WRITES. Only a deliverable that passed review at score ≥ 70 may
//   compound. An unverified answer that becomes "precedent" poisons every later recall.
//
//   RECALL STANDS DOWN ON FRESH-EYES WORK. Recalled context measurably helps design and
//   product work and measurably HURTS security and incident work, where a stale
//   precedent is exactly the wrong prior. Security routes read no memory.

import { readFileSync, writeFileSync, appendFileSync, existsSync, readdirSync, mkdirSync, unlinkSync } from 'node:fs';
import { join } from 'node:path';
import { MEMORY_DIR, ensureDirs } from './config.mjs';

const INDEX = () => join(MEMORY_DIR, 'MEMORY.md');
const LOG = () => join(MEMORY_DIR, 'log.md');

export const slug = (s) => String(s || '').toLowerCase()
  .replace(/[^a-z0-9֐-׿]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60) || 'note';

export function initMemory() {
  ensureDirs();
  if (!existsSync(MEMORY_DIR)) mkdirSync(MEMORY_DIR, { recursive: true, mode: 0o700 });
  if (!existsSync(INDEX())) writeFileSync(INDEX(), '# fabius memory\n\nOne line per page. This file is what a run reads first.\n\n', { mode: 0o600 });
  if (!existsSync(LOG())) writeFileSync(LOG(), '# log\n\nAppend-only. Newest at the bottom.\n\n', { mode: 0o600 });
}

export function listMemory() {
  initMemory();
  return readdirSync(MEMORY_DIR)
    .filter((f) => f.endsWith('.md') && f !== 'MEMORY.md' && f !== 'log.md')
    .map((f) => {
      const raw = readFileSync(join(MEMORY_DIR, f), 'utf8');
      const fm = raw.match(/^---\n([\s\S]*?)\n---\n?/);
      const meta = {};
      for (const line of (fm?.[1] || '').split('\n')) {
        const m = line.match(/^(\w+):\s*(.*)$/);
        if (m) meta[m[1]] = m[2].trim();
      }
      return { file: f, path: join(MEMORY_DIR, f), title: meta.title || f.replace(/\.md$/, ''),
               kind: meta.kind || 'note', scope: meta.scope || 'fabius', score: Number(meta.score) || 0,
               created: meta.created || '', body: fm ? raw.slice(fm[0].length) : raw };
    });
}

export function writeMemory({ title, body, kind = 'note', scope = 'fabius', score = 100, tags = [] }) {
  initMemory();
  const name = slug(title);
  const path = join(MEMORY_DIR, `${name}.md`);
  const created = new Date().toISOString();
  const fm = ['---', `title: ${title}`, `kind: ${kind}`, `scope: ${scope}`, `score: ${score}`,
              `created: ${created}`, tags.length ? `tags: ${tags.join(', ')}` : null, '---', ''].filter((x) => x !== null).join('\n');
  writeFileSync(path, fm + body.trim() + '\n', { mode: 0o600 });
  // Index: one line per page, replaced in place if the page already existed.
  const line = `- [${title}](${name}.md) — ${firstSentence(body)}`;
  const idx = readFileSync(INDEX(), 'utf8');
  const re = new RegExp(`^- \\[[^\\]]*\\]\\(${name}\\.md\\).*$`, 'm');
  writeFileSync(INDEX(), re.test(idx) ? idx.replace(re, line) : idx.trimEnd() + '\n' + line + '\n', { mode: 0o600 });
  appendFileSync(LOG(), `## [${created.slice(0, 10)}] write | ${title}\n- kind ${kind} · scope ${scope} · score ${score}\n\n`);
  return { path, name };
}

export function deleteMemory(name) {
  const path = join(MEMORY_DIR, `${slug(name)}.md`);
  if (!existsSync(path)) return false;
  unlinkSync(path);
  const idx = readFileSync(INDEX(), 'utf8');
  writeFileSync(INDEX(), idx.replace(new RegExp(`^- \\[[^\\]]*\\]\\(${slug(name)}\\.md\\).*$\n?`, 'm'), ''), { mode: 0o600 });
  appendFileSync(LOG(), `## [${new Date().toISOString().slice(0, 10)}] delete | ${name}\n\n`);
  return true;
}

const STOP = new Set(['the', 'a', 'an', 'and', 'or', 'to', 'of', 'in', 'for', 'is', 'it', 'this', 'that', 'with', 'on', 'at', 'as', 'by', 'be', 'are', 'was', 'from', 'how', 'what', 'why', 'do', 'does', 'my', 'i', 'you', 'we']);
const tokens = (s) => new Set(String(s || '').toLowerCase().match(/[a-z0-9֐-׿]{2,}/g)?.filter((t) => !STOP.has(t)) || []);

// Keyword overlap, weighted by the verify score and decayed by age. No embedding model,
// no network, no index to rebuild — and on a memory of a few hundred pages it is both
// instant and inspectable, which matters more here than recall@k.
export function recallMemory(query, { scope = null, k = 5, minScore = 70 } = {}) {
  const q = tokens(query);
  if (!q.size) return [];
  const now = Date.now();
  return listMemory()
    .filter((m) => m.score >= minScore && (!scope || m.scope === scope || m.scope === 'fabius'))
    .map((m) => {
      const t = tokens(m.title + ' ' + m.body);
      let hits = 0;
      for (const w of q) if (t.has(w)) hits++;
      const overlap = hits / q.size;
      const ageDays = m.created ? (now - Date.parse(m.created)) / 86400000 : 999;
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
  const hits = recallMemory(task, opts);
  if (!hits.length) return '';
  return hits.map((h) => `- ${h.title} (${h.kind}, verified ${h.score}): ${firstSentence(h.body)}`).join('\n');
}

// THE GATE. A deliverable compounds only when an independent reviewer passed it at
// ≥ 70 and the task carried something worth keeping. Returns a proposal, never a write —
// the caller decides, so a dry run stays dry.
export function decideMemoryWrite({ task, output, verdict, route }) {
  const score = verdict?.score || 0;
  if (!verdict?.pass || score < 70) {
    return { write: false, reason: `unverified (score ${score} < 70) — an unverified answer must not become precedent` };
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
