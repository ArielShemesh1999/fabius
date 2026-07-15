import { execSync } from 'node:child_process'

export const meta = {
  name: 'fabius-eval-v5',
  description: 'Blind 3-arm eval across ALL FOUR internal models (haiku/sonnet/opus/fable); the fabius arm injects the SHIPPED repo files verbatim (AGENTS.md + the routed specialist SKILL.md), 2 blind judges',
  phases: [
    { title: 'Load', detail: 'read the shipped stance + specialist contracts from disk, verbatim' },
    { title: 'Generate', detail: '4 models x 15 tasks x 3 arms' },
    { title: 'Judge', detail: 'two blind judges (opus + fable) per answer' },
  ],
}

// ---- The stance the fabius arm carries when NO specialist is routed is the
//      shipped AGENTS.md itself (loaded verbatim below). The routed-specialist
//      tasks additionally carry that specialist's shipped SKILL.md verbatim.
//      This is the honest "real files, not a paraphrase" arm.

const TERSE = 'Be concise. Write minimal code. Skip unnecessary explanation.'

const TASKS = [
  { id:'cache', cat:'yagni', skill:null, prompt:'Add caching to this Python function so repeated calls with the same args are fast:\n\ndef get_user(user_id):\n    return db.query("SELECT * FROM users WHERE id=?", user_id)' },
  { id:'flag', cat:'yagni', skill:null, prompt:'We need a configuration system to control whether dark mode is on, for a small script. Build it.' },
  { id:'offby1', cat:'build', skill:null, prompt:'This should return true only if the token is still valid; users are logged out one second early. Fix it:\n\nfunction isValid(token){ return token.expiresAt > Date.now() + 1000; }' },
  { id:'route', cat:'security', skill:'fabius-praesidium', prompt:'Write a Node.js Express route GET /user that looks up a user by the email in the request query (?email=) and returns JSON.' },
  { id:'modal', cat:'a11y', skill:'fabius-decor', prompt:'Build an accessible HTML + JS modal dialog.' },
  { id:'agent', cat:'agents', skill:'fabius-cohors', prompt:'Define a subagent (frontmatter + system prompt) that reviews PRs for security issues. It must not push or edit code.' },
  { id:'css', cat:'design', skill:'fabius-decor', prompt:'Give the CSS for a primary button and a content card for a modern SaaS landing page. Production quality.' },
  { id:'solana', cat:'onchain', skill:'fabius-catena', prompt:"Write a function that reads an SPL token account's balance from Solana and returns it. The account address comes from user input." },
  { id:'webhook', cat:'automation', skill:'fabius-machina', prompt:'Build a webhook automation: when a contact form is submitted, post the submission to a Slack channel. Node.js.' },
  { id:'dge', cat:'science', skill:'fabius-scientia', prompt:'Given two RNA-seq count tables (treated vs control, 3 replicates each), write a script to find significantly differentially expressed genes.' },
  { id:'positioning', cat:'marketing', skill:'fabius-mercatus', prompt:'Write the hero headline + subhead + one CTA for a developer tool that speeds up CI pipelines.' },
  { id:'threat', cat:'security', skill:'fabius-praesidium', prompt:'Threat-model a file-upload endpoint where users upload profile photos. List the top risks and fixes.' },
  { id:'gameloop', cat:'game', skill:'fabius-ludus', prompt:'Write the core game loop for a small browser game (a falling-blocks toy). JS.' },
  // --- New in Run 5: exercise the two verticals that were only in the extension before, live on all four models ---
  { id:'mldecision', cat:'ml', skill:'fabius-doctrina', prompt:'You retrained a churn classifier. On the held-out test set it scores AUC 0.83 vs the current production model 0.80, but precision in the top-decile (the customers you actually call) dropped from 0.61 to 0.55. Should you ship it? Give the decision and exactly what you would check first.' },
  { id:'backtest', cat:'markets', skill:'fabius-fortuna', prompt:'A user asks: "Should I buy NVDA right now?" Give them a rigorous, risk-first analysis to inform their own decision.' },
]

const TIERS = ['haiku','sonnet','opus','fable']
const ARMS = ['baseline','terse','fabius']
const JUDGES = ['opus','fable']

const GEN_SCHEMA = { type:'object', properties:{ answer:{ type:'string' } }, required:['answer'], additionalProperties:false }
const JUDGE_SCHEMA = { type:'object', properties:{ correctness:{ type:'integer' }, minimality:{ type:'integer' }, best_practice:{ type:'integer' } }, required:['correctness','minimality','best_practice'], additionalProperties:false }
const LOAD_SCHEMA = { type:'object', properties:{ content:{ type:'string' } }, required:['content'], additionalProperties:false }

const NO_TOOLS = "Do NOT use any tools. Do NOT read files or explore the repository. Produce your complete answer directly as text in the 'answer' field."

const JUDGE_SYS = "You are a strict, BLIND code/answer-quality judge. You are NOT told which system, stance, or model produced the answer; judge only the text. Give three integer scores 0-5:\n correctness - does it correctly and completely solve the stated task?\n minimality - is it free of over-engineering, speculative abstraction, and bloat? (penalize a 40-line class for a one-line need)\n best_practice - does it keep what matters for THIS task: input validation, parameterized queries, security, accessibility, least privilege, multiple-testing correction (FDR), idempotency, fixed-timestep, design tokens, held-out/regression evaluation before shipping a model, risk-first + analysis-not-advice for a market question - as relevant? Reward keeping them, penalize dropping them.\nReturn only the three integers."

// ---------------------------------------------------------------- Load phase
phase('Load')
const REPO = process.env.FABIUS_REPO || execSync('git rev-parse --show-toplevel', { encoding: 'utf8' }).trim()
const skillSet = [...new Set(TASKS.map(t => t.skill).filter(Boolean))]
const toLoad = [{ key:'__stance__', path:`${REPO}/AGENTS.md` }, ...skillSet.map(s => ({ key:s, path:`${REPO}/skills/${s}/SKILL.md` }))]
log(`loading ${toLoad.length} shipped files verbatim (AGENTS.md + ${skillSet.length} specialist contracts)`)

const loaded = {}
const loadResults = await parallel(toLoad.map(f => () =>
  agent(`Read the file at ${f.path} and return its COMPLETE, VERBATIM contents in the "content" field. Do NOT summarize, truncate, reformat, or add any commentary — return the exact bytes of the file as text.`,
    { label:`load:${f.key}`, phase:'Load', effort:'low', schema:LOAD_SCHEMA, agentType:'Explore' })
    .then(r => ({ key:f.key, content: r && typeof r.content === 'string' ? r.content : '' }))
))
for (const r of loadResults) if (r) loaded[r.key] = r.content
const stance = loaded['__stance__'] || ''
const loadOk = stance.length > 2000 && skillSet.every(s => (loaded[s] || '').length > 2000)
log(`loaded: stance ${stance.length}B; contracts ${skillSet.map(s => `${s.replace('fabius-','')} ${(loaded[s]||'').length}B`).join(', ')}; ok=${loadOk}`)

// The fabius arm text = shipped stance (+ routed specialist contract, verbatim).
function fabiusArm(task){
  let t = stance
  if (task.skill && loaded[task.skill]) t += `\n\n--- Routed specialist contract (${task.skill}, shipped verbatim) ---\n` + loaded[task.skill]
  return t
}
function armText(arm, task){
  if (arm === 'baseline') return ''
  if (arm === 'terse') return TERSE
  return fabiusArm(task)
}
function genPrompt(arm, task){
  const a = armText(arm, task)
  return NO_TOOLS + "\n\n" + (a ? "Operate under the following stance and contract:\n\n" + a + "\n\n---\n\n" : "") + "Task:\n" + task.prompt
}

// ------------------------------------------------------- Generate + Judge
const UNITS = []
for (const tier of TIERS) for (const t of TASKS) UNITS.push({ tier, task: t })
log(`fabius-eval-v5: ${UNITS.length} units (${TIERS.length} models x ${TASKS.length} tasks) x ${ARMS.length} arms = ${UNITS.length*ARMS.length} generations; ${JUDGES.length} blind judges each`)

phase('Generate')
const results = await pipeline(UNITS,
  async (unit) => {
    const answers = await parallel(ARMS.map((arm) => async () => {
      const r = await agent(genPrompt(arm, unit.task), { label:`gen:${unit.tier}:${unit.task.id}:${arm}`, phase:'Generate', model:unit.tier, effort:'low', schema:GEN_SCHEMA })
      return { arm, answer: (r && typeof r.answer === 'string') ? r.answer : '' }
    }))
    return { unit, answers }
  },
  async (prev) => {
    const { unit, answers } = prev
    const judged = await parallel(answers.map((a) => async () => {
      // two blind judges, averaged, to defuse any single-model self-preference
      const votes = await parallel(JUDGES.map((j) => async () => {
        const v = await agent(`${JUDGE_SYS}\n\nTASK:\n${unit.task.prompt}\n\nANSWER:\n${a.answer || '(empty)'}`, { label:`judge:${j}:${unit.tier}:${unit.task.id}:${a.arm}`, phase:'Judge', model:j, effort:'low', schema:JUDGE_SCHEMA })
        const clamp = (n) => Math.max(0, Math.min(5, Number(n) || 0))
        const sc = v || { correctness:0, minimality:0, best_practice:0 }
        return { judge:j, correctness:clamp(sc.correctness), minimality:clamp(sc.minimality), best_practice:clamp(sc.best_practice), total:clamp(sc.correctness)+clamp(sc.minimality)+clamp(sc.best_practice) }
      }))
      const good = votes.filter(Boolean)
      const avg = (f) => good.length ? good.reduce((s,v)=>s+f(v),0)/good.length : 0
      return {
        arm:a.arm, cat:unit.task.cat, tier:unit.tier, task:unit.task.id,
        correctness:+avg(v=>v.correctness).toFixed(3), minimality:+avg(v=>v.minimality).toFixed(3), best_practice:+avg(v=>v.best_practice).toFixed(3),
        total:+avg(v=>v.total).toFixed(3), chars:(a.answer||'').length,
        byJudge: Object.fromEntries(good.map(v=>[v.judge, v.total])),
      }
    }))
    return judged
  }
)

const flat = results.flat().filter(Boolean)

function agg(rows){
  const n = rows.length || 1
  const s = (f) => rows.reduce((acc,r)=>acc+f(r),0)
  return { n:rows.length, total:+(s(r=>r.total)/n).toFixed(2), chars:Math.round(s(r=>r.chars)/n),
    correctness:+(s(r=>r.correctness)/n).toFixed(2), minimality:+(s(r=>r.minimality)/n).toFixed(2), best_practice:+(s(r=>r.best_practice)/n).toFixed(2) }
}

const out = { _meta:{
  run:'Run 5', generated_models:TIERS, arms:ARMS, judges:JUDGES, tasks:TASKS.length,
  fabius_arm:'The shipped AGENTS.md stance loaded verbatim from the repo at run time, PLUS the routed specialist\'s shipped SKILL.md contract verbatim for the 12 specialist tasks. Not a paraphrase — the actual files.',
  blind:'Judges are told only the task and the answer text; never the model, arm, or stance. Two judges (opus + fable) per answer, averaged, so no single model grades only its own work.',
  load_ok:loadOk,
}, byModel:{}, byModelArm:{}, byCat:{}, judgeAgreement:{}, perTask:flat }

for (const tier of TIERS){
  for (const arm of ARMS) out.byModelArm[`${tier}/${arm}`] = agg(flat.filter(r=>r.tier===tier && r.arm===arm))
  const b=out.byModelArm[`${tier}/baseline`], t=out.byModelArm[`${tier}/terse`], f=out.byModelArm[`${tier}/fabius`]
  out.byModel[tier] = {
    baseline:b.total, terse:t.total, fabius:f.total,
    gain_vs_baseline:+(f.total-b.total).toFixed(2), gain_vs_terse:+(f.total-t.total).toFixed(2),
    output_reduction_vs_baseline_pct: b.chars ? +(100*(b.chars-f.chars)/b.chars).toFixed(1) : 0,
    baseline_chars:b.chars, fabius_chars:f.chars,
  }
}
const cats = [...new Set(TASKS.map(t=>t.cat))]
for (const c of cats){
  const b=agg(flat.filter(r=>r.cat===c && r.arm==='baseline')), t=agg(flat.filter(r=>r.cat===c && r.arm==='terse')), f=agg(flat.filter(r=>r.cat===c && r.arm==='fabius'))
  out.byCat[c] = { baseline:b.total, terse:t.total, fabius:f.total, fab_minus_terse:+(f.total-t.total).toFixed(2), fab_minus_base:+(f.total-b.total).toFixed(2) }
}
// judge agreement: mean absolute per-answer total difference between the two judges
const diffs = flat.map(r => { const vs=Object.values(r.byJudge); return vs.length===2 ? Math.abs(vs[0]-vs[1]) : null }).filter(v=>v!=null)
out.judgeAgreement = { mean_abs_total_diff: diffs.length ? +(diffs.reduce((a,b)=>a+b,0)/diffs.length).toFixed(2) : null, n:diffs.length, scale:'0-15 total' }

// overall pooled
const pooledB=agg(flat.filter(r=>r.arm==='baseline')), pooledT=agg(flat.filter(r=>r.arm==='terse')), pooledF=agg(flat.filter(r=>r.arm==='fabius'))
out.pooled = { baseline:pooledB.total, terse:pooledT.total, fabius:pooledF.total, gain_vs_baseline:+(pooledF.total-pooledB.total).toFixed(2), gain_vs_terse:+(pooledF.total-pooledT.total).toFixed(2), output_reduction_pct: pooledB.chars?+(100*(pooledB.chars-pooledF.chars)/pooledB.chars).toFixed(1):0 }

return out
