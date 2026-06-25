export const meta = {
  name: 'fabius-eval-v3-ext',
  description: 'Extend Run 4: blind 3-arm eval of the two new verticals (doctrina = ML engineering, fortuna = markets) on sonnet+haiku, judged blind by opus',
  phases: [{ title: 'Generate' }, { title: 'Judge' }],
}

const STANCE = `Operate under the Fabius stance:
(1) LEAN OUTPUT - drop articles, filler, hedging, pleasantries; terse; fragments ok; keep ALL technical substance and correctness.
(2) LEAN CODE (YAGNI ladder) - need it at all? stdlib? native feature? installed dep? one line? only then minimal code. No speculative abstraction, no config for a constant, no unrequested options.
(3) SURGICAL - minimum change; don't improve adjacent code; match existing style.
(4) THINK FIRST - if ambiguous, state the key assumption in one line; push back on over-spec.
(5) NEVER trim away: input validation at trust boundaries, error handling that prevents data loss, security, accessibility, or anything explicitly asked. Minimal, not flimsy. Non-trivial logic leaves one runnable check.
(6) UI: one accent color, design tokens not inline hex, hierarchy from type not boxes, mobile-first.
(7) Agents: precise description + tight tool allowlist + explicit output contract + least privilege.`

const TERSE = "Be concise. Write minimal code. Skip unnecessary explanation."

const SPEC = {
  doctrina: "AI/ML ENGINEERING (fabius-doctrina): the model lifecycle, and EVALUATION is the hinge. Use a held-out, representative, LEAKAGE-FREE test set (check for train/eval overlap explicitly). Pick the metric that matches the job - precision/recall/F1 at the operating threshold, NOT accuracy (which lies under class imbalance). Compare against a CONTROL (the base / incumbent model), not nothing, and report the delta. Gate it: ship only if it clears the bar, ideally as a CI regression gate. Climb the rung ladder (prompt -> RAG -> fine-tune) - don't train when a cheaper rung passes the eval. Serve the smallest model that passes; track runs (params, metric, data version, code commit) reproducibly; secrets in env, never in a notebook.",
  fortuna: "MARKETS & FINANCE (fabius-fortuna): RISK before return - size to survivable loss not imagined gain, model the drawdown, and compute everything NET of transaction costs, slippage, and liquidity. BACKTEST HONESTLY - guard against lookahead / data-snooping bias, survivorship bias, in-sample vs out-of-sample (validate on a held-out window or walk-forward), and multiple-testing / overfitting; a backtest predicts the past, not the future. Evidence over narrative; state and stress-test the assumptions. The BRIGHT LINE: this is ANALYSIS, NOT personalized financial advice - surface the assumptions and the risk, the decision is the user's; never market manipulation. Charts route to the design layer.",
}

const TASKS = [
  { id:'mleval', cat:'ml', spec:'doctrina', prompt:'Write a Python script to decide whether a newly fine-tuned model is better than the base model on a support-ticket classification task (8 categories), and whether it is good enough to ship to production.' },
  { id:'backtest', cat:'markets', spec:'fortuna', prompt:'Backtest a simple moving-average crossover trading strategy on a stock (e.g. AAPL) in Python, and tell me whether I should trade it.' },
]

const TIERS = ['sonnet','haiku']
const ARMS = ['baseline','terse','fabius']
const UNITS = []
for (const tier of TIERS) for (const t of TASKS) UNITS.push({ tier, task: t })

const GEN_SCHEMA = { type:'object', properties:{ answer:{ type:'string' } }, required:['answer'], additionalProperties:false }
const JUDGE_SCHEMA = { type:'object', properties:{ correctness:{ type:'integer' }, minimality:{ type:'integer' }, best_practice:{ type:'integer' } }, required:['correctness','minimality','best_practice'], additionalProperties:false }

const NO_TOOLS = "Do NOT use any tools. Do NOT read files or explore the repository. Produce your complete answer directly as text in the 'answer' field."

function armText(arm, task){
  if (arm === 'baseline') return ''
  if (arm === 'terse') return TERSE
  return STANCE + (task.spec ? "\n\n" + SPEC[task.spec] : "")
}
function genPrompt(arm, task){
  const a = armText(arm, task)
  return NO_TOOLS + "\n\n" + (a ? a + "\n\n---\n\n" : "") + "Task:\n" + task.prompt
}

const JUDGE_SYS = "You are a strict, BLIND code/answer-quality judge. You are NOT told which system produced the answer; judge only the text. Give three integer scores 0-5:\n correctness - does it correctly and completely solve the stated task?\n minimality - is it free of over-engineering, speculative abstraction, and bloat?\n best_practice - does it keep what matters FOR THIS TASK? For an ML-evaluation task: a held-out leakage-free test set, the right metric (precision/recall/F1 at threshold, NOT bare accuracy on imbalance), comparison against a control/baseline model, a ship/no-ship gate. For a finance/backtest task: out-of-sample / walk-forward validation (not in-sample only), net of transaction costs + slippage, survivorship/lookahead guards, risk/position sizing, and 'analysis not personalized advice' (penalize a flat 'yes, trade it'). Reward keeping these, penalize dropping them.\nReturn only the three integers."

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
      const v = await agent(`${JUDGE_SYS}\n\nTASK:\n${unit.task.prompt}\n\nANSWER:\n${a.answer || '(empty)'}`, { label:`judge:${unit.tier}:${unit.task.id}:${a.arm}`, phase:'Judge', model:'opus', effort:'low', schema:JUDGE_SCHEMA })
      const sc = v || { correctness:0, minimality:0, best_practice:0 }
      const clamp = (n) => Math.max(0, Math.min(5, Number(n) || 0))
      const c = clamp(sc.correctness), m = clamp(sc.minimality), b = clamp(sc.best_practice)
      return { arm:a.arm, cat:unit.task.cat, tier:unit.tier, task:unit.task.id, correctness:c, minimality:m, best_practice:b, total:c+m+b, chars:(a.answer||'').length }
    }))
    return judged
  }
)

const flat = results.flat().filter(Boolean)
function agg(rows){ const n=rows.length||1; const s=(f)=>rows.reduce((a,r)=>a+f(r),0); return { n:rows.length, total:+(s(r=>r.total)/n).toFixed(2), chars:Math.round(s(r=>r.chars)/n) } }
const out = { byCat:{}, byTaskArm:{}, perTask:flat }
for (const c of [...new Set(TASKS.map(t=>t.cat))]){
  const b=agg(flat.filter(r=>r.cat===c&&r.arm==='baseline')), t=agg(flat.filter(r=>r.cat===c&&r.arm==='terse')), f=agg(flat.filter(r=>r.cat===c&&r.arm==='fabius'))
  out.byCat[c] = { baseline:b.total, terse:t.total, fabius:f.total, fab_minus_terse:+(f.total-t.total).toFixed(2), fab_minus_base:+(f.total-b.total).toFixed(2), chars_base:b.chars, chars_fabius:f.chars }
}
// per task x tier x arm detail
for (const t of TASKS) for (const tier of TIERS){
  for (const arm of ARMS){ const r=flat.find(x=>x.task===t.id&&x.tier===tier&&x.arm===arm); out.byTaskArm[`${t.id}/${tier}/${arm}`] = r? r.total : null }
}
return out
