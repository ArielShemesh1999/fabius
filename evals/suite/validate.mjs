#!/usr/bin/env node
// FBS v1.0 deterministic suite validator — no model, no key, no network.
// Validates every task line against schema.json semantics + suite-level invariants.
// Usage: node evals/suite/validate.mjs
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const DIR = dirname(fileURLToPath(import.meta.url))
const CATS = {
  A: 'coding', B: 'debugging', C: 'tool_discipline', D: 'instruction_obedience', E: 'scope_control',
  F: 'design_product', G: 'memory_retrieval', H: 'agent_workflows', I: 'security_guardrails', J: 'error_recovery',
}
const SKILLS = ['fabius', 'fabius-parcus', 'fabius-disciplina', 'fabius-decor', 'fabius-cohors', 'fabius-archivum',
  'fabius-mercatus', 'fabius-praesidium', 'fabius-ludus', 'fabius-catena', 'fabius-machina', 'fabius-scientia',
  'fabius-doctrina', 'fabius-fortuna']
const STRESS = ['long_context', 'instruction_conflict', 'agent_loop', 'tool_trap', 'security_trap', 'memory_overload',
  'prompt_injection', 'false_assumption', 'competing_objectives', 'context_pollution', 'resource_constraint', 'multi_agent_failure']
const TIERS = [
  { file: 'tier1.smoke.jsonl', tier: 1, count: 20, letters: ['A', 'B', 'D', 'E', 'I'] },
  { file: 'tier2.core.jsonl', tier: 2, count: 50, letters: Object.keys(CATS) },
  { file: 'tier3.stress.jsonl', tier: 3, count: 30, letters: Object.keys(CATS) },
]

let pass = 0, fail = 0, warn = 0
const ok = (cond, label, detail = '') => {
  if (cond) { pass++; console.log(`  PASS  ${label}${detail ? '  — ' + detail : ''}`) }
  else { fail++; console.log(`  FAIL  ${label}${detail ? '  — ' + detail : ''}`) }
}
const warnIf = (cond, label) => { if (cond) { warn++; console.log(`  WARN  ${label}`) } }

const all = []
for (const t of TIERS) {
  let lines
  try { lines = readFileSync(join(DIR, t.file), 'utf8').trim().split('\n') }
  catch { ok(false, `${t.file} readable`); continue }
  ok(lines.length === t.count, `${t.file}: exactly ${t.count} tasks`, `found ${lines.length}`)
  for (const [i, line] of lines.entries()) {
    let task
    try { task = JSON.parse(line) } catch { ok(false, `${t.file}:${i + 1} valid JSON`); continue }
    const errs = []
    if (!/^FAB-\d{3}$/.test(task.id || '')) errs.push('id pattern')
    if (task.tier !== t.tier) errs.push(`tier must be ${t.tier}`)
    if (!t.letters.includes(task.category_letter)) errs.push(`category_letter ${task.category_letter} not allowed in tier ${t.tier}`)
    if (CATS[task.category_letter] !== task.category) errs.push(`category "${task.category}" mismatches letter ${task.category_letter}`)
    if (!['low', 'medium', 'high'].includes(task.difficulty)) errs.push('difficulty')
    if (typeof task.prompt !== 'string' || task.prompt.length < 120) errs.push('prompt ≥120 chars')
    if (typeof task.expected_behavior !== 'string' || task.expected_behavior.length < 40) errs.push('expected_behavior ≥40 chars')
    for (const f of ['failure_modes', 'automatic_checks'])
      if (!Array.isArray(task[f]) || task[f].length < 3 || task[f].length > 6 || task[f].some(x => typeof x !== 'string')) errs.push(`${f} 3–6 strings`)
    if (typeof task.human_review_notes !== 'string' || task.human_review_notes.length < 10) errs.push('human_review_notes')
    if (!SKILLS.includes(task.routed_skill)) errs.push(`routed_skill "${task.routed_skill}"`)
    if (task.category === 'memory_retrieval' && (typeof task.memory_snapshot !== 'string' || task.memory_snapshot.length < 40)) errs.push('category G requires memory_snapshot')
    if (t.tier === 3 && !STRESS.includes(task.stress_kind)) errs.push('tier 3 requires a valid stress_kind')
    if (t.tier !== 3 && 'stress_kind' in task) errs.push('stress_kind only on tier 3')
    const known = ['id', 'tier', 'category_letter', 'category', 'difficulty', 'prompt', 'expected_behavior', 'failure_modes', 'automatic_checks', 'human_review_notes', 'routed_skill', 'memory_snapshot', 'stress_kind']
    for (const k of Object.keys(task)) if (!known.includes(k)) errs.push(`unknown field ${k}`)
    // Neutrality: the prompt (what the generating model sees) must never name the layer or its vocabulary.
    if (/fabius|yagni/i.test(task.prompt)) errs.push('neutrality: prompt names the stance')
    if (task.memory_snapshot && (/fabius|FAB_MEMORY/i.test(task.memory_snapshot) || /\bBASE\b/.test(task.memory_snapshot))) errs.push('memory_snapshot leaks eval modes')
    if (errs.length) ok(false, `${task.id || t.file + ':' + (i + 1)} valid`, errs.join('; '))
    all.push(task)
  }
}

const ids = all.map(t => t.id)
ok(new Set(ids).size === ids.length, 'all task IDs unique', `${new Set(ids).size}/${ids.length}`)
ok(all.length === 100, 'suite total = 100 tasks', `found ${all.length}`)

const t2 = all.filter(t => t.tier === 2)
const t2counts = Object.fromEntries(Object.keys(CATS).map(L => [L, t2.filter(t => t.category_letter === L).length]))
ok(Object.values(t2counts).every(n => n === 5), 'tier 2 balanced: 5 tasks per category A–J', JSON.stringify(t2counts))
const t1 = all.filter(t => t.tier === 1)
ok(TIERS[0].letters.every(L => t1.filter(t => t.category_letter === L).length === 4), 'tier 1 balanced: 4 tasks per category A/B/D/E/I')
const kinds = new Set(all.filter(t => t.tier === 3).map(t => t.stress_kind))
ok(kinds.size >= 10, 'tier 3 covers ≥10 of the 12 stress kinds', `${kinds.size}/12: ${[...kinds].join(', ')}`)
const gWithMem = all.filter(t => t.category === 'memory_retrieval' && t.memory_snapshot).length
ok(gWithMem === all.filter(t => t.category === 'memory_retrieval').length, 'every category-G task carries a memory snapshot', `${gWithMem}`)
warnIf(all.some(t => /\bconcise\b|\bminimal\b/i.test(t.prompt) && !/minimal (change|diff|downtime|dependencies)/i.test(t.prompt)), 'some prompts use "concise"/"minimal" — review neutrality manually')

console.log(`\n  ${pass}/${pass + fail} passed${warn ? ` · ${warn} warnings` : ''}`)
process.exit(fail ? 1 : 0)
