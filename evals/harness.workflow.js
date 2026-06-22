export const meta = {
  name: 'fabius-eval',
  description: 'Real multi-model eval: opus/sonnet/haiku × baseline/terse/fabius × 6 tasks, objective length + blind-judge quality',
  phases: [
    { title: 'Generate', detail: '3 models × 3 arms × 6 tasks = 54 real model outputs' },
    { title: 'Judge', detail: 'blind rubric scoring, 1 judge per task over all 9 outputs' },
  ],
}

const MODELS = ['opus', 'sonnet', 'haiku']

const FABIUS = `Operate under the Fabius stance:
(1) LEAN OUTPUT — drop articles, filler, hedging, pleasantries; terse; fragments ok; keep ALL technical substance and correctness.
(2) LEAN CODE (YAGNI ladder) — does it need to exist at all? stdlib? native platform feature? already-installed dep? one line? only then minimal code. No speculative abstraction, no config for a constant, no unrequested flexibility/options.
(3) SURGICAL — minimum change; do not improve adjacent code; match existing style.
(4) THINK FIRST — if ambiguous, state the key assumption in one line; push back on over-specification.
(5) NEVER trim away: input validation at trust boundaries, error handling that prevents data loss, security, accessibility, or anything explicitly asked. Minimal, not flimsy. Non-trivial logic leaves one runnable check.
(6) UI: exactly one accent color, design tokens not inline hex, hierarchy from type not boxes, mobile-first.
(7) Agents: precise description + tight tool allowlist + explicit output contract + least privilege.`

const TERSE = `Be concise. Write minimal code. Skip unnecessary explanation.`

const TASKS = [
  { id: 'cache', kind: 'code', prompt: `Add caching to this Python function so repeated calls with the same args are fast:\n\ndef get_user(user_id):\n    return db.query("SELECT * FROM users WHERE id=?", user_id)` },
  { id: 'debug', kind: 'code', prompt: `This function should return true only if the token is still valid. Users report being logged out one second early. Fix it:\n\nfunction isValid(token){ return token.expiresAt > Date.now() + 1000; }` },
  { id: 'button', kind: 'design', prompt: `Give the CSS for a primary button and a content card for a modern SaaS landing page. Production quality.` },
  { id: 'agent', kind: 'agent', prompt: `Define a subagent (frontmatter + system prompt) that reviews pull requests for security issues. It must not be able to push or edit code.` },
  { id: 'pool', kind: 'explain', prompt: `Explain database connection pooling.` },
  { id: 'flag', kind: 'code', prompt: `We need a configuration system to control whether dark mode is on. Build it.` },
]

const ARMS = [
  { id: 'baseline', pre: '' },
  { id: 'terse', pre: TERSE },
  { id: 'fabius', pre: FABIUS },
]

phase('Generate')
// each cell: real model output, no schema => returns raw answer text
const cells = []
for (const model of MODELS) for (const arm of ARMS) for (const task of TASKS) {
  cells.push({ model, arm: arm.id, task: task.id, kind: task.kind, prompt: task.prompt, pre: arm.pre })
}

const gen = await parallel(cells.map(c => () =>
  agent(
    (c.pre ? c.pre + '\n\n---\n\n' : '') +
    `Task:\n${c.prompt}\n\nAnswer the task directly. Return only your answer (code + any essential note).`,
    { label: `${c.model}/${c.arm}/${c.task}`, phase: 'Generate', model: c.model }
  ).then(text => ({ ...c, output: text || '', outLen: (text || '').length, locLines: (text || '').split('\n').filter(l => l.trim()).length }))
))

const ok = gen.filter(Boolean)

// build judge batches: one per task, 9 outputs (3 models x 3 arms) anonymized as A..I
const JUDGE_SCHEMA = {
  type: 'object',
  properties: {
    scores: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          label: { type: 'string' },
          correctness: { type: 'number', description: '0-5: does it correctly solve the task' },
          minimality: { type: 'number', description: '0-5: lean, no bloat, no over-engineering, appropriately concise' },
          bestpractice: { type: 'number', description: '0-5: keeps validation/security/accessibility/design-or-agent discipline where relevant' },
        },
        required: ['label', 'correctness', 'minimality', 'bestpractice'],
      },
    },
  },
  required: ['scores'],
}

const LABELS = 'ABCDEFGHI'.split('')
phase('Judge')
const judged = await parallel(TASKS.map(task => () => {
  const outs = ok.filter(c => c.task === task.id)
  const mapping = {}
  const block = outs.map((c, i) => { mapping[LABELS[i]] = `${c.model}/${c.arm}`; return `### Output ${LABELS[i]}\n${c.output.slice(0, 4000)}` }).join('\n\n')
  return agent(
    `You are a strict, blind judge. The task was:\n${task.prompt}\n\nBelow are ${outs.length} candidate answers labeled ${LABELS.slice(0, outs.length).join(',')}. You do NOT know who wrote each. Score each on three axes 0-5:\n` +
    `- correctness: solves the task correctly.\n- minimality: lean, no bloat, no speculative over-engineering, appropriately concise (an over-engineered or padded answer scores LOW even if correct).\n- bestpractice: preserves what must not be cut (input validation, security, accessibility, design tokens / one-accent for UI, least-privilege + output contract for agents) and follows the domain's good practice.\n\n` +
    `Answers:\n\n${block}\n\nReturn a score object per label. Be discriminating; do not give everything the same score.`,
    { label: `judge:${task.id}`, phase: 'Judge', model: 'opus', schema: JUDGE_SCHEMA }
  ).then(res => ({ task: task.id, mapping, scores: (res && res.scores) || [] }))
}))

// aggregate
const rows = {} // key model/arm -> arrays
function key(m, a) { return `${m}/${a}` }
for (const m of MODELS) for (const a of ARMS) rows[key(m, a.id)] = { lens: [], correct: [], minimal: [], best: [], total: [] }
for (const c of ok) rows[key(c.model, c.arm)].lens.push(c.outLen)
for (const j of judged.filter(Boolean)) {
  for (const s of j.scores) {
    const ma = j.mapping[s.label]
    if (!ma || !rows[ma]) continue
    rows[ma].correct.push(s.correctness)
    rows[ma].minimal.push(s.minimality)
    rows[ma].best.push(s.bestpractice)
    rows[ma].total.push((s.correctness || 0) + (s.minimality || 0) + (s.bestpractice || 0))
  }
}
const avg = arr => arr.length ? +(arr.reduce((x, y) => x + y, 0) / arr.length).toFixed(2) : null
const summary = {}
for (const k of Object.keys(rows)) {
  const r = rows[k]
  summary[k] = { n: r.total.length, avgOutChars: avg(r.lens), correctness: avg(r.correct), minimality: avg(r.minimal), bestpractice: avg(r.best), totalScore15: avg(r.total) }
}
// deltas fabius vs baseline + vs terse, per model
const deltas = {}
for (const m of MODELS) {
  const b = summary[key(m, 'baseline')], t = summary[key(m, 'terse')], f = summary[key(m, 'fabius')]
  deltas[m] = {
    score_baseline: b.totalScore15, score_terse: t.totalScore15, score_fabius: f.totalScore15,
    score_gain_vs_baseline: (b.totalScore15 != null && f.totalScore15 != null) ? +(f.totalScore15 - b.totalScore15).toFixed(2) : null,
    score_gain_vs_terse: (t.totalScore15 != null && f.totalScore15 != null) ? +(f.totalScore15 - t.totalScore15).toFixed(2) : null,
    chars_baseline: b.avgOutChars, chars_fabius: f.avgOutChars,
    output_reduction_vs_baseline_pct: (b.avgOutChars && f.avgOutChars) ? +(100 * (1 - f.avgOutChars / b.avgOutChars)).toFixed(1) : null,
  }
}

return { summary, deltas, perTaskJudged: judged.filter(Boolean).length, generated: ok.length }
