// THE BRAIN, LOADED FROM DISK.
//
// The console injects the fabius stance; a harness like Claude Code injects the whole
// contract. Locally there is no harness — so the runtime reads the sealed SKILL.md
// contracts itself and hands the routed one to the model. That is what makes a local
// run *fabius* and not a generic ReAct loop: the same words, byte-for-byte, that the
// seal covers.

import { readFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { SKILLS_DIR, REPO_ROOT } from './config.mjs';

let cache = null;

export function loadSkills(dir = SKILLS_DIR) {
  if (cache && cache.dir === dir) return cache;
  const skills = new Map();
  if (existsSync(dir)) {
    for (const d of readdirSync(dir)) {
      const p = join(dir, d, 'SKILL.md');
      if (!existsSync(p)) continue;
      const raw = readFileSync(p, 'utf8');
      const fm = raw.match(/^---\n([\s\S]*?)\n---\n?/);
      const body = fm ? raw.slice(fm[0].length) : raw;
      skills.set(d, {
        name: d,
        path: p,
        bytes: Buffer.byteLength(raw),
        sha256: createHash('sha256').update(raw).digest('hex'),
        description: flatten(fm?.[1] || '', 'description'),
        whenToUse: flatten(fm?.[1] || '', 'when_to_use'),
        body,
      });
    }
  }
  cache = { dir, skills };
  return cache;
}

function flatten(fmText, key) {
  const lines = fmText.split('\n');
  const i = lines.findIndex((l) => new RegExp(`^${key}:`).test(l));
  if (i === -1) return '';
  const first = lines[i].replace(new RegExp(`^${key}:\\s*`), '');
  const parts = [];
  if (first && !/^[|>][-+]?\s*$/.test(first)) parts.push(first);
  for (let j = i + 1; j < lines.length; j++) {
    if (/^\S/.test(lines[j])) break;
    parts.push(lines[j].trim());
  }
  return parts.join(' ').replace(/\s+/g, ' ').trim();
}

// Verify the loaded contracts against the repo's content-bound seal. A local run that
// silently used a TAMPERED contract would be the whole provenance story undone, so the
// runtime can say, on demand, exactly which files match the sealed manifest.
export function verifySeal(dir = SKILLS_DIR) {
  const manifestPath = join(REPO_ROOT, 'provenance', 'seal-manifest.json');
  if (!existsSync(manifestPath)) return { available: false, reason: 'no seal-manifest.json' };
  let manifest;
  try { manifest = JSON.parse(readFileSync(manifestPath, 'utf8')); }
  catch (e) { return { available: false, reason: 'unreadable manifest: ' + e.message }; }
  const results = [];
  for (const [rel, want] of Object.entries(manifest.files || {})) {
    const abs = join(REPO_ROOT, rel);
    const got = existsSync(abs) ? createHash('sha256').update(readFileSync(abs)).digest('hex') : 'MISSING';
    results.push({ file: rel, ok: got === want });
  }
  // Hashing only what the manifest LISTS proves nothing listed changed — it cannot
  // notice a contract that was ADDED after sealing, because the loop never visits it.
  // A dropped-in skill is exactly what this runtime would otherwise load and hand to
  // the model, so membership is checked separately from content.
  const listed = new Set(Object.keys(manifest.files || {}));
  const unsealed = [...loadSkills(dir).skills.values()]
    .map((s) => `skills/${s.name}/SKILL.md`)
    .filter((rel) => !listed.has(rel));
  return {
    available: true,
    total: results.length,
    matched: results.filter((r) => r.ok).length,
    drift: results.filter((r) => !r.ok).map((r) => r.file),
    unsealed,
    ok: results.every((r) => r.ok) && unsealed.length === 0,
    merkleRoot: manifest.merkle_root,
  };
}

// The contract(s) the router chose, trimmed to a budget. The always-on lean core rides
// every run; the routed specialist comes next; a second domain is included only if it
// still fits. Contracts are ≤12KB each by construction (progressive disclosure) — the
// budget here bounds the WORST case, it is not expected to bite on a normal route.
export function contractsFor(routeResult, { budget = 24000, dir = SKILLS_DIR, sealedOnly = false } = {}) {
  const { skills } = loadSkills(dir);
  // `--sealed-only` turns the seal from a report into a gate: a contract that is not in
  // the manifest, or whose bytes drifted from it, is refused rather than handed to the
  // model. Off by default, because a working copy mid-edit is a normal state and
  // refusing to run in it would be theatre; on when the provenance claim has to hold.
  let refused = [];
  if (sealedOnly) {
    const seal = verifySeal(dir);
    if (!seal.available) throw new Error(`--sealed-only: no seal manifest to check against (${seal.reason})`);
    refused = [...new Set([...(seal.unsealed || []), ...(seal.drift || [])])]
      .map((rel) => rel.split('/')[1]).filter(Boolean);
  }
  const wanted = [];
  const push = (n) => { if (skills.has(n) && !wanted.includes(n)) wanted.push(n); };
  push('fabius-parcus');
  for (const d of routeResult.domains || []) push(d);
  for (const l of routeResult.layers || []) push(l);

  const parts = [];
  let used = 0;
  const included = [];
  const excluded = [];
  for (const n of wanted) {
    if (refused.includes(n)) { excluded.push(n); continue; }
    const s = skills.get(n);
    const block = `<<<CONTRACT ${s.name}>>>\n${s.body.trim()}\n<<<END CONTRACT ${s.name}>>>`;
    if (used + block.length > budget && parts.length) break;
    parts.push(block); used += block.length; included.push(s.name);
  }
  return { text: parts.join('\n\n'), included, excluded, bytes: used };
}

// A one-line inventory for `fabius doctor`.
export function skillSummary(dir = SKILLS_DIR) {
  const { skills } = loadSkills(dir);
  return [...skills.values()].map((s) => ({ name: s.name, bytes: s.bytes, sha: s.sha256.slice(0, 12) }));
}

export function skillsDirExists(dir = SKILLS_DIR) {
  try { return statSync(dir).isDirectory(); } catch { return false; }
}
