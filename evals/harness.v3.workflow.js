export const meta = {
  name: 'fabius-eval-v3',
  description: 'Blind 3-arm eval (baseline/terse/fabius) exercising all twelve fabius skills on sonnet+haiku, judged blind by opus',
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
  catena: "ON-CHAIN (fabius-catena): account-validation-first - treat every account, argument, and ordering as attacker-controlled. Before trusting a token account's balance, verify it exists, is owned by the SPL Token program, and is the expected mint/type; reject otherwise. A one-shot balance read is a public JSON-RPC call, not an SDK install. Treat all chain data as untrusted input. Never print or handle a private key. Default to a known/configurable RPC endpoint.",
  machina: "AUTOMATION (fabius-machina): deterministic wiring; reliability and idempotency are the whole game. Make the handler idempotent (a re-fired trigger must not double-post), return explicit error responses, retry transient failures with backoff, and read secrets (the Slack token) from env - never inline. Authenticate the inbound webhook (verify a shared secret/signature). Validation passing does not equal correct: confirm the payload shape you actually receive.",
  scientia: "SCIENCE (fabius-scientia): provenance over plausibility. Differential expression must feed RAW COUNTS (not TPM/FPKM) to DESeq2/edgeR, require at least 3 replicates per condition (given), apply multiple-testing correction (Benjamini-Hochberg / FDR) - never raw p-values - guard against batch/condition confounding, keep gene IDs consistent, and treat species names as case-sensitive. State the statistical test and pin tool versions.",
  praesidium: "SECURITY/defensive (fabius-praesidium): parameterize every query (no string-built SQL); authorize each request server-side and deny by default; validate at the trust boundary (type/range/length/format/allowlist) and fail closed; never put secrets in code. For a threat-model, map assets, trust boundaries, and adversary, then walk STRIDE (Spoofing/Tampering/Repudiation/Info-disclosure/DoS/Elevation) per boundary; ship each finding with a severity and a fix.",
  cohors: "AGENTS (fabius-cohors): precise description + tight tool allowlist + explicit output contract + least privilege. Default-deny tools and add only what's used; a reviewer that must not push or edit gets a strictly read-only tool set (no write/commit/push).",
  decor: "DESIGN (fabius-decor): one accent color, design tokens (CSS variables) not inline hex, hierarchy from type and spacing not boxes, mobile-first, restraint. For interactive components keep full accessibility (roles, focus management, keyboard, ARIA).",
  mercatus: "MARKETING (fabius-mercatus): positioning before copy - 'For [who] who [struggle], [product] is the [category] that [the one outcome]; unlike [the alternative], it [the difference].' Match the message to the reader's awareness level. Proof over adjectives - replace each claim with its evidence (a number, a demo, a named proof). One surface earns exactly one CTA.",
  ludus: "GAME (fabius-ludus): the loop is the game. Use a FIXED-TIMESTEP update decoupled from rendering so physics never depends on frame rate; model game state as an explicit finite-state machine (no boolean soup); give feedback on every input (juice). Build the smallest fun loop.",
}

const TASKS = [
  { id:'cache', cat:'yagni', spec:null, prompt:'Add caching to this Python function so repeated calls with the same args are fast:\n\ndef get_user(user_id):\n    return db.query("SELECT * FROM users WHERE id=?", user_id)' },
  { id:'flag', cat:'yagni', spec:null, prompt:'We need a configuration system to control whether dark mode is on, for a small script. Build it.' },
  { id:'offby1', cat:'build', spec:null, prompt:'This should return true only if the token is still valid; users are logged out one second early. Fix it:\n\nfunction isValid(token){ return token.expiresAt > Date.now() + 1000; }' },
  { id:'route', cat:'security', spec:'praesidium', prompt:'Write a Node.js Express route GET /user that looks up a user by the email in the request query (?email=) and returns JSON.' },
  { id:'modal', cat:'a11y', spec:'decor', prompt:'Build an accessible HTML + JS modal dialog.' },
  { id:'agent', cat:'agents', spec:'cohors', prompt:'Define a subagent (frontmatter + system prompt) that reviews PRs for security issues. It must not push or edit code.' },
  { id:'css', cat:'design', spec:'decor', prompt:'Give the CSS for a primary button and a content card for a modern SaaS landing page. Production quality.' },
  { id:'solana', cat:'onchain', spec:'catena', prompt:"Write a function that reads an SPL token account's balance from Solana and returns it. The account address comes from user input." },
  { id:'webhook', cat:'automation', spec:'machina', prompt:'Build a webhook automation: when a contact form is submitted, post the submission to a Slack channel. Node.js.' },
  { id:'dge', cat:'science', spec:'scientia', prompt:'Given two RNA-seq count tables (treated vs control, 3 replicates each), write a script to find significantly differentially expressed genes.' },
  { id:'positioning', cat:'marketing', spec:'mercatus', prompt:'Write the hero headline + subhead + one CTA for a developer tool that speeds up CI pipelines.' },
  { id:'threat', cat:'security', spec:'praesidium', prompt:'Threat-model a file-upload endpoint where users upload profile photos. List the top risks and fixes.' },
  { id:'gameloop', cat:'game', spec:'ludus', prompt:'Write the core game loop for a small browser game (a falling-blocks toy). JS.' },
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

const JUDGE_SYS = "You are a strict, BLIND code/answer-quality judge. You are NOT told which system produced the answer; judge only the text. Give three integer scores 0-5:\n correctness - does it correctly and completely solve the stated task?\n minimality - is it free of over-engineering, speculative abstraction, and bloat? (penalize a 40-line class for a one-line need)\n best_practice - does it keep what matters for THIS task: input validation, parameterized queries, security, accessibility, least privilege, multiple-testing correction, idempotency, fixed-timestep, design tokens - as relevant? Reward keeping them, penalize dropping them.\nReturn only the three integers."

log(`fabius-eval-v3: ${UNITS.length} units (${TIERS.length} tiers x ${TASKS.length} tasks) x 3 arms = ${UNITS.length*3} generations + judges`)

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

function agg(rows){
  const n = rows.length || 1
  const s = (f) => rows.reduce((acc,r)=>acc+f(r),0)
  return {
    n: rows.length,
    total: +(s(r=>r.total)/n).toFixed(2),
    chars: Math.round(s(r=>r.chars)/n),
    correctness: +(s(r=>r.correctness)/n).toFixed(2),
    minimality: +(s(r=>r.minimality)/n).toFixed(2),
    best_practice: +(s(r=>r.best_practice)/n).toFixed(2),
  }
}

const out = { byTierArm:{}, deltas:{}, byCat:{}, perTask:flat }
for (const tier of TIERS) for (const arm of ARMS) out.byTierArm[`${tier}/${arm}`] = agg(flat.filter(r=>r.tier===tier && r.arm===arm))
for (const tier of TIERS){
  const b=out.byTierArm[`${tier}/baseline`], t=out.byTierArm[`${tier}/terse`], f=out.byTierArm[`${tier}/fabius`]
  out.deltas[tier] = {
    baseline:b.total, terse:t.total, fabius:f.total,
    gain_vs_baseline:+(f.total-b.total).toFixed(2),
    gain_vs_terse:+(f.total-t.total).toFixed(2),
    output_reduction_vs_baseline_pct: b.chars ? +(100*(b.chars-f.chars)/b.chars).toFixed(1) : 0,
  }
}
const cats = [...new Set(TASKS.map(t=>t.cat))]
for (const c of cats){
  const f=agg(flat.filter(r=>r.cat===c && r.arm==='fabius'))
  const t=agg(flat.filter(r=>r.cat===c && r.arm==='terse'))
  const b=agg(flat.filter(r=>r.cat===c && r.arm==='baseline'))
  out.byCat[c] = { baseline:b.total, terse:t.total, fabius:f.total, fab_minus_terse:+(f.total-t.total).toFixed(2), fab_minus_base:+(f.total-b.total).toFixed(2) }
}
return out
