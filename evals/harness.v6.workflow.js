import { execSync, spawnSync } from 'node:child_process'
import { tmpdir } from 'node:os'
import { createHash } from 'node:crypto'
import { mkdirSync, writeFileSync } from 'node:fs'

export const meta = {
  name: 'fabius-eval-v6',
  description: 'Mixed verification: a deterministic local runner executes generated code against hidden suites; two model graders score fixed factual checklists',
  phases: [
    { title: 'Load', detail: 'read the shipped stance + specialist contracts verbatim' },
    { title: 'Generate', detail: '4 models x 9 tasks x 3 arms' },
    { title: 'Verify', detail: 'deterministic local code execution / model-graded fixed factual checklist' },
  ],
}

const REPO = process.env.FABIUS_REPO || execSync('git rev-parse --show-toplevel', { encoding: 'utf8' }).trim()
const SCRATCH = process.env.FABIUS_SCRATCH || `${tmpdir()}/fabius-eval-run6`

const TERSE = 'Be concise. Write minimal code. Skip unnecessary explanation.'
const NO_TOOLS = "Do NOT use any tools. Do NOT read files or explore the repository. Produce your complete answer directly as text in the 'answer' field."
const sha256 = (text) => createHash('sha256').update(text || '').digest('hex')

function extractCandidate(answer, lang) {
  const blocks = [...String(answer || '').matchAll(/```([^\n]*)\n([\s\S]*?)```/g)]
    .map((m) => ({ tag: m[1].trim().toLowerCase(), code: m[2] }))
  const aliases = lang === 'js' ? new Set(['js', 'javascript', 'mjs', 'node']) : new Set(['py', 'python', 'python3'])
  const picked = blocks.find((b) => aliases.has(b.tag)) || blocks.find((b) => !b.tag) || blocks[0]
  const code = picked ? picked.code : String(answer || '')
  return code.split('\n').filter((line) => !/^\s*(?:module\.exports\s*=|exports\.[A-Za-z_$][\w$]*\s*=|export\s+default\b|export\s*\{)/.test(line)).join('\n').trim()
}

function executeCandidate(task, answer, uid) {
  mkdirSync(SCRATCH, { recursive: true })
  const code = extractCandidate(answer, task.lang)
  const source = task.tmpl.replace('__CANDIDATE__', code)
  const file = `${SCRATCH}/${uid}.${task.ext}`
  writeFileSync(file, source, 'utf8')
  const env = { PATH: process.env.PATH || '/usr/bin:/bin', LANG: 'C.UTF-8', LC_ALL: 'C.UTF-8',
    HOME: SCRATCH, TMPDIR: SCRATCH, NO_COLOR: '1' }
  const run = spawnSync(task.runner, [file], { cwd: SCRATCH, env, encoding: 'utf8', timeout: 10_000, maxBuffer: 1024 * 1024 })
  const stdout = run.stdout || '', stderr = run.stderr || ''
  const resultLines = [...stdout.matchAll(/^RESULT\s+(\d+)\/(\d+)\s*$/gm)]
  const match = resultLines[0]
  const validResult = run.status === 0 && resultLines.length === 1 && !!match && Number(match[2]) === task.total
  const passed = validResult ? Math.max(0, Math.min(task.total, Number(match[1]))) : 0
  return {
    ran: validResult, tests_total: task.total, tests_passed: passed,
    command: `${task.runner} ${file}`, exit_code: Number.isInteger(run.status) ? run.status : -1,
    signal: run.signal || null, error: run.error ? String(run.error.message || run.error) : '',
    stdout, stderr, extracted_code_sha256: sha256(code), test_file_sha256: sha256(source),
    note: validResult ? `RESULT ${passed}/${task.total}` : 'process did not emit the exact expected RESULT line',
  }
}

// ---------- EXEC tasks: a deterministic local runner executes hidden tests ----------
const JS_OFFBY1 = `__CANDIDATE__
;(function(){
let p=0,m=0; const eq=(a,b,msg)=>{m++; if(a===b)p++; else console.error('FAIL '+msg+' got '+a);};
const now=Date.now();
try{
 eq(typeof isValid==='function', true, 'isValid defined');
 eq(isValid({expiresAt: now+5000}), true, 'valid token -> true');
 eq(isValid({expiresAt: now-5000}), false, 'expired token -> false');
 eq(isValid({expiresAt: now+400}), true, 'still valid inside 1s (the off-by-one)');
}catch(e){console.error('THREW '+e.message);}
console.log('RESULT '+p+'/'+m);
})();`

const PY_CACHE = `class _DB:
    def __init__(self): self.n=0
    def query(self, sql, arg):
        self.n+=1
        return {'id':arg,'name':'u'+str(arg)}
db=_DB()
__CANDIDATE__
p=0;m=0
def _chk(c,msg):
    global p,m; m+=1
    if c: p+=1
    else: print('FAIL',msg)
_chk('get_user' in dir() and callable(get_user), 'get_user defined')
try:
    r1=get_user(1); r2=get_user(1); r3=get_user(2)
    _chk(db.n==2, 'caching: 2 db hits for calls [1,1,2] (got %d)'%db.n)
    _chk(r1==r2, 'cached result equal')
    _chk(r3['id']==2, 'different arg still works')
except Exception as e:
    print('THREW',e); m=4
print('RESULT %d/%d'%(p,m))`

const JS_MERGE = `__CANDIDATE__
;(function(){
let p=0,m=0; const J=JSON.stringify;
const T=(inp,exp,msg)=>{m++; try{const r=mergeIntervals(inp); if(J(r)===J(exp))p++; else console.error('FAIL '+msg+' got '+J(r));}catch(e){console.error('THREW '+msg+' '+e.message);}};
T([[1,3],[2,6],[8,10],[15,18]],[[1,6],[8,10],[15,18]],'basic overlap');
T([[1,4],[4,5]],[[1,5]],'touching endpoints');
T([],[],'empty');
T([[1,4],[2,3]],[[1,4]],'fully contained');
T([[6,8],[1,9],[2,4],[8,10]],[[1,10]],'unsorted, all overlap');
console.log('RESULT '+p+'/'+m);
})();`

const JS_PARSE = `__CANDIDATE__
;(function(){
let p=0,m=0; const J=JSON.stringify;
const T=(inp,exp,msg)=>{m++; try{const r=parseQuery(inp); if(J(r)===J(exp))p++; else console.error('FAIL '+msg+' got '+J(r));}catch(e){console.error('THREW '+msg+' '+e.message);}};
T('a=1&b=2',{a:'1',b:'2'},'basic pair');
T('a=1&a=2',{a:['1','2']},'repeated key -> array');
T('x=a%20b',{x:'a b'},'url-decode value');
T('flag',{flag:''},'key without = -> empty string');
T('?a=1',{a:'1'},'leading question mark stripped');
console.log('RESULT '+p+'/'+m);
})();`

const TASKS = [
  // --- EXEC: run real tests ---
  { id:'offby1', cat:'build', kind:'exec', lang:'js', runner:'node', ext:'mjs', total:4, tmpl:JS_OFFBY1,
    prompt:'This should return true only if the token is still valid; users are logged out one second early. Fix it, keeping the function named isValid(token):\n\nfunction isValid(token){ return token.expiresAt > Date.now() + 1000; }' },
  { id:'cache', cat:'yagni', kind:'exec', lang:'py', runner:'python3', ext:'py', total:4, tmpl:PY_CACHE,
    prompt:'Add caching to this Python function so repeated calls with the same args are fast. Keep it named get_user(user_id) and keep using the existing db.query:\n\ndef get_user(user_id):\n    return db.query("SELECT * FROM users WHERE id=?", user_id)' },
  { id:'merge', cat:'build', kind:'exec', lang:'js', runner:'node', ext:'mjs', total:5, tmpl:JS_MERGE,
    prompt:'Implement `function mergeIntervals(intervals)` that merges all overlapping intervals. Input is an array of [start, end] pairs, not necessarily sorted; intervals that only touch at an endpoint ([1,4] and [4,5]) count as overlapping. Return the merged intervals sorted by start. Return [] for an empty input.' },
  { id:'parse', cat:'build', kind:'exec', lang:'js', runner:'node', ext:'mjs', total:5, tmpl:JS_PARSE,
    prompt:"Implement `function parseQuery(qs)` that parses a URL query string into an object. Rules: URL-decode keys and values; a key that appears more than once becomes an array of its values in order; a bare key with no '=' maps to an empty string; a leading '?' is ignored." },
  // --- RUBRIC: grade the research/domain deliverable against a factual checklist ---
  { id:'dge', cat:'science', kind:'rubric', skill:'fabius-scientia',
    prompt:'Given two RNA-seq count tables (treated vs control, 3 replicates each), write a script to find significantly differentially expressed genes.',
    checklist:[
      'Feeds RAW COUNTS to the DE method (does NOT feed TPM/FPKM/normalized values into differential-expression testing).',
      'Uses a proper count-based DE method (DESeq2 or edgeR, or an explicit negative-binomial model) — not a plain t-test on raw counts.',
      'Applies multiple-testing correction (Benjamini-Hochberg / FDR / adjusted p-values) rather than thresholding raw p-values.',
      'Uses the 3 replicates per condition as the experimental design (does not collapse replicates or run n=1).',
      'Thresholds significance on the ADJUSTED p-value (e.g. padj < 0.05), optionally with a log2 fold-change cutoff.' ] },
  { id:'route', cat:'security', kind:'rubric', skill:'fabius-praesidium',
    prompt:'Write a Node.js Express route GET /user that looks up a user by the email in the request query (?email=) and returns JSON.',
    checklist:[
      'Uses a parameterized / prepared query or an ORM binding — the email is NEVER string-concatenated or template-interpolated into SQL.',
      'Validates the email query parameter (presence and type/format) before using it.',
      'Handles the not-found and error cases explicitly (no unhandled throw, no raw 500 with a stack trace).',
      'Does not blindly select and return sensitive columns (e.g. password hash) — selects specific safe fields or notes the risk.',
      'No database credentials or secrets are hard-coded inline in the handler.' ] },
  { id:'solana', cat:'onchain', kind:'rubric', skill:'fabius-catena',
    prompt:"Write a function that reads an SPL token account's balance from Solana and returns it. The account address comes from user input.",
    checklist:[
      'Handles the account-not-found case (null/None account info) instead of assuming it exists.',
      'Verifies the account is owned by the SPL Token program before trusting it.',
      'Validates it is a token account of the expected mint/type (or decodes the account layout properly) and rejects otherwise.',
      'Treats the user-supplied address as untrusted — parses/validates the public key rather than passing a raw string.',
      'Uses a configurable or explicitly named RPC endpoint and never logs or handles a private key.' ] },
  { id:'webhook', cat:'automation', kind:'rubric', skill:'fabius-machina',
    prompt:'Build a webhook automation: when a contact form is submitted, post the submission to a Slack channel. Node.js.',
    checklist:[
      'Idempotent handling — a re-fired trigger will not double-post (dedupe key, or explicitly acknowledged).',
      'Authenticates the inbound webhook (verifies a shared secret or signature) rather than trusting any caller.',
      'Reads the Slack token/secret from an environment variable — not hard-coded in the source.',
      'Retries transient failures with backoff (or queues) instead of dropping the event on one failure.',
      'Returns explicit HTTP status / error responses for success and failure.' ] },
  { id:'threat', cat:'security', kind:'rubric', skill:'fabius-praesidium',
    prompt:'Threat-model a file-upload endpoint where users upload profile photos. List the top risks and fixes.',
    checklist:[
      'Validates file type by content / magic bytes (or server-side re-encode), not by extension or the client-sent MIME header alone.',
      'Enforces a maximum file size limit.',
      'Prevents stored files from being executed / served as code — stores outside the web root, randomizes names, or blocks path traversal.',
      'Addresses image-specific risks (strips/re-encodes metadata, decompression-bomb limits, or SVG-as-XSS).',
      'Adds authentication/authorization and rate limiting on the upload endpoint. Each risk is paired with a concrete fix.' ] },
]

const TIERS = ['haiku','sonnet','opus','fable']
const ARMS = ['baseline','terse','fabius']
const GRADERS = ['opus','fable']

const GEN_SCHEMA = { type:'object', properties:{ answer:{ type:'string' } }, required:['answer'], additionalProperties:false }
const GRADE_SCHEMA = { type:'object', properties:{ results:{ type:'array', items:{ type:'boolean' } } }, required:['results'], additionalProperties:false }
const LOAD_SCHEMA = { type:'object', properties:{ content:{ type:'string' } }, required:['content'], additionalProperties:false }

// ------------------------------------------------------------------ Load
phase('Load')
const skillSet = [...new Set(TASKS.map(t => t.skill).filter(Boolean))]
const toLoad = [{ key:'__stance__', path:`${REPO}/AGENTS.md` }, ...skillSet.map(s => ({ key:s, path:`${REPO}/skills/${s}/SKILL.md` }))]
log(`loading ${toLoad.length} shipped files verbatim`)
const loaded = {}
const loadResults = await parallel(toLoad.map(f => () =>
  agent(`Read the file at ${f.path} and return its COMPLETE, VERBATIM contents in the "content" field — exact bytes, no summary, no truncation.`,
    { label:`load:${f.key}`, phase:'Load', effort:'low', schema:LOAD_SCHEMA, agentType:'Explore' })
    .then(r => ({ key:f.key, content: r && typeof r.content==='string' ? r.content : '' }))))
for (const r of loadResults) if (r) loaded[r.key] = r.content
const stance = loaded['__stance__'] || ''
const loadOk = stance.length > 2000 && skillSet.every(s => (loaded[s]||'').length > 2000)
log(`load ok=${loadOk} (stance ${stance.length}B, ${skillSet.length} contracts)`)

function armText(arm, task){
  if (arm==='baseline') return ''
  if (arm==='terse') return TERSE
  let t = stance
  if (task.skill && loaded[task.skill]) t += `\n\n--- Routed specialist contract (${task.skill}, shipped verbatim) ---\n` + loaded[task.skill]
  return t
}
function genPrompt(arm, task){
  const a = armText(arm, task)
  return NO_TOOLS + "\n\n" + (a ? "Operate under the following stance and contract:\n\n"+a+"\n\n---\n\n" : "") + "Task:\n" + task.prompt
}

// ------------------------------------------------------------------ Generate + Verify
const UNITS = []
for (const tier of TIERS) for (const t of TASKS) UNITS.push({ tier, task:t })
log(`fabius-eval-v6: ${UNITS.length} units x ${ARMS.length} arms = ${UNITS.length*ARMS.length} generations; exec tasks run real tests, rubric tasks graded by ${GRADERS.length} graders`)

phase('Generate')
const results = await pipeline(UNITS,
  async (unit) => {
    const answers = await parallel(ARMS.map((arm) => async () => {
      const r = await agent(genPrompt(arm, unit.task), { label:`gen:${unit.tier}:${unit.task.id}:${arm}`, phase:'Generate', model:unit.tier, effort:'low', schema:GEN_SCHEMA })
      return { arm, answer:(r && typeof r.answer==='string') ? r.answer : '' }
    }))
    return { unit, answers }
  },
  async (prev) => {
    const { unit, answers } = prev
    const task = unit.task
    const graded = await parallel(answers.map((a) => async () => {
      if (task.kind === 'exec'){
        const uid = `${unit.tier}_${task.id}_${a.arm}`
        const rr = executeCandidate(task, a.answer, uid)
        const total = rr.tests_total
        return { arm:a.arm, cat:task.cat, kind:'exec', tier:unit.tier, task:task.id, ran:rr.ran, passed:rr.tests_passed, total, frac:total ? rr.tests_passed/total : 0, chars:(a.answer||'').length, note:rr.note, answer:a.answer, answer_sha256:sha256(a.answer), execution_receipt:rr }
      } else {
        const n = task.checklist.length
        const votes = await parallel(GRADERS.map((g) => async () => {
          const v = await agent(
`You are a STRICT, objective compliance grader. You are NOT told which system produced the answer. For each checkpoint, return true ONLY if the answer clearly and correctly satisfies it with a concrete implementation or explicit correct statement; partial, hand-wavy, or missing = false. Return exactly ${n} booleans in order, one per checkpoint.

CHECKLIST (in order):
${task.checklist.map((c,i)=>`${i+1}. ${c}`).join('\n')}

ANSWER TO GRADE:
${a.answer || '(empty)'}`,
            { label:`grade:${g}:${unit.tier}:${task.id}:${a.arm}`, phase:'Verify', model:g, effort:'high', schema:GRADE_SCHEMA })
          const arr = (v && Array.isArray(v.results)) ? v.results.slice(0,n) : []
          while (arr.length < n) arr.push(false)
          return arr.map(Boolean)
        }))
        const good = votes.filter(Boolean)
        // per-checkpoint mean across graders, then sum
        let satisfied = 0
        for (let i=0;i<n;i++){ const s = good.reduce((acc,v)=>acc+(v[i]?1:0),0)/(good.length||1); satisfied += s }
        return { arm:a.arm, cat:task.cat, kind:'rubric', tier:unit.tier, task:task.id, passed:+satisfied.toFixed(3), total:n, frac:n? satisfied/n : 0, chars:(a.answer||'').length, graders:good.length, answer:a.answer, answer_sha256:sha256(a.answer), checklist_votes:good }
      }
    }))
    return graded
  }
)

const flat = results.flat().filter(Boolean)

// ---------------------------------------------------------------- Aggregate
function pct(rows){ const t=rows.reduce((a,r)=>a+r.total,0), p=rows.reduce((a,r)=>a+r.passed,0); return { pts:+p.toFixed(2), total:t, pct: t? +(100*p/t).toFixed(1):0, chars: rows.length? Math.round(rows.reduce((a,r)=>a+r.chars,0)/rows.length):0 } }

const out = { _meta:{
  run:'Run 6 — mixed deterministic execution and model-graded factual checks', generated_models:TIERS, arms:ARMS, graders:GRADERS,
  method:'EXEC tasks: deterministic in-process extraction + local spawnSync execution against hidden tests, with answer/code/test-file digests, command, exit, stdout and stderr retained. RUBRIC tasks: two model graders (opus+fable) score fixed factual checklists, averaged per checkpoint, with individual votes retained. The historical v6 receipt predates this evidence schema.',
  fabius_arm:'Shipped AGENTS.md verbatim + the routed specialist SKILL.md verbatim (rubric tasks). Real files, not a paraphrase.',
  receipt_schema:'fabius-panel-b/v2; preserves candidate answers/digests, deterministic execution receipts and individual checklist votes',
  exec_tasks:TASKS.filter(t=>t.kind==='exec').map(t=>t.id), rubric_tasks:TASKS.filter(t=>t.kind==='rubric').map(t=>t.id), load_ok:loadOk,
}, byModel:{}, byModelArm:{}, byTask:{}, perItem:flat }

for (const tier of TIERS){
  for (const arm of ARMS){
    const rows = flat.filter(r=>r.tier===tier && r.arm===arm)
    out.byModelArm[`${tier}/${arm}`] = { overall:pct(rows), exec:pct(rows.filter(r=>r.kind==='exec')), rubric:pct(rows.filter(r=>r.kind==='rubric')) }
  }
  const b=out.byModelArm[`${tier}/baseline`], t=out.byModelArm[`${tier}/terse`], f=out.byModelArm[`${tier}/fabius`]
  out.byModel[tier] = {
    baseline_pct:b.overall.pct, terse_pct:t.overall.pct, fabius_pct:f.overall.pct,
    gain_vs_baseline:+(f.overall.pct-b.overall.pct).toFixed(1), gain_vs_terse:+(f.overall.pct-t.overall.pct).toFixed(1),
    exec:{ baseline:b.exec.pct, terse:t.exec.pct, fabius:f.exec.pct, gain:+(f.exec.pct-b.exec.pct).toFixed(1) },
    rubric:{ baseline:b.rubric.pct, terse:t.rubric.pct, fabius:f.rubric.pct, gain:+(f.rubric.pct-b.rubric.pct).toFixed(1) },
    output_cut_pct: b.overall.chars? +(100*(b.overall.chars-f.overall.chars)/b.overall.chars).toFixed(1):0,
  }
}
for (const task of TASKS){
  const row = {}
  for (const arm of ARMS){ const rows=flat.filter(r=>r.task===task.id && r.arm===arm); row[arm]=pct(rows).pct }
  row.gain = +(row.fabius-row.baseline).toFixed(1); row.kind=task.kind
  out.byTask[task.id] = row
}
// pooled
for (const kind of ['exec','rubric','all']){
  const sel = (arm)=> flat.filter(r=>r.arm===arm && (kind==='all'||r.kind===kind))
  out[`pooled_${kind}`] = { baseline:pct(sel('baseline')).pct, terse:pct(sel('terse')).pct, fabius:pct(sel('fabius')).pct }
}
return out
