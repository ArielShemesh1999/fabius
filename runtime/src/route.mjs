// THE ROUTER — R1 (classify on layer · machinery · model-tier) · R2 (climb the ladder
// to the smallest sufficient rung) · R11 (cheapest tier that holds; the strong tier for
// ambiguity, architecture, security, money, irreversibility).
//
// Heuristic and inspectable on purpose: no model call, no network, fully deterministic,
// and it prints its reasoning. The same classification the fabius router rule (R1)
// specifies, so a task routed on this machine lands on the same specialist it would
// land on inside any harness that loads the plugin.

import { PROVIDERS, resolveModel, overrideModel, availableProviders } from './providers.mjs';
import { loadConfig } from './config.mjs';

export const LADDER = ['inline', 'tool', 'retrieval', 'plan', 'subagent', 'swarm'];

const SIG = {
  memory: ['remember', 'recall', 'history', 'decided', 'past', 'precedent', 'last time', 'what did we decide', 'save this for later',
    'זכור*', 'תזכור', 'זיכרון', 'היסטוריה', 'החלטנו', 'תקדים', 'ידע קודם', 'שמור להמשך', 'תעד*'],
  tools: ['fetch', 'search', 'api', 'query', 'compute', 'calculate', 'scrape', 'lookup', 'database', 'integrate', 'deploy', 'read the file', 'run the', 'install',
    'חפש*', 'בדוק*', 'קרא*', 'הרץ*', 'התקן*', 'פרוס*', 'משוך*', 'שאילת*', 'חשב*', 'סרוק*', 'מסד נתונים', 'קובץ'],
  discipline: ['build', 'implement', 'fix', 'refactor', 'debug', 'patch', 'run tests', 'write tests', 'test the code', 'review the code',
    'בנה', 'בנו', 'יישם*', 'ממש*', 'תקן*', 'רפקטור*', 'דבג*', 'כתוב בדיקות', 'הרץ בדיקות', 'בדוק את הקוד'],
  planning: ['plan', 'steps', 'roadmap', 'orchestrate*', 'pipeline', 'workflow', 'phase', 'milestone', 'sequence', 'then', 'first', 'multi-agent',
    'תכנן*', 'תכנית', 'תוכנית', 'שלבים', 'מפת דרכים', 'תזמר*', 'תהליך עבודה', 'זרימת עבודה', 'מקצה לקצה', 'אחר כך', 'ואז', 'במקביל'],
  strong: ['architecture', 'architect*', 'security', 'threat', 'vuln*', 'crypto', 'auth', 'oauth', 'design system', 'migration', 'irreversible', 'delete', 'production', 'strategy', 'ambiguous', 'trade-off', 'tradeoff', 'why', 'should we', 'decide', 'choose between', 'risk', 'legal', 'payment', 'money',
    'ארכיטקטור*', 'אבטחה', 'איום', 'חולשה', 'קריפטו', 'אימות', 'הרשאה', 'מערכת עיצוב', 'מיגרציה', 'בלתי הפיך', 'מחק*', 'פרודקשן', 'אסטרטגיה', 'פשרה', 'למה', 'החלט*', 'בחר*', 'סיכון', 'משפטי', 'תשלום', 'כסף'],
  fast: ['rename', 'format', 'reformat', 'list', 'extract', 'classify', 'translate', 'summarize', 'tag', 'lookup', 'convert', 'lint',
    'שנה שם', 'פרמט*', 'רשימה', 'חלץ*', 'סווג*', 'תרגם*', 'סכם*', 'המר*'],
};

// The DOMAIN axis — which specialist the task's WHAT pulls. One owner per capability, so
// these keyword sets are deliberately disjoint — enforced by the matcher below, not by
// hoping: word boundaries keep a key from firing inside a longer WORD, and longest-match-wins
// keeps it from firing inside a longer PHRASE another layer owns.
const DOMAIN = {
  'fabius-decor': ['ui', 'design', 'landing page', 'hero', 'component', 'css', 'brand', 'layout', 'chart', 'graph', 'diagram', 'visuali*', 'dashboard', 'figure', 'data-ink', 'svg',
    'עיצוב', 'עצב*', 'ממשק', 'דף נחיתה', 'רכיב', 'מותג', 'פריסה', 'תרשים', 'גרף', 'דשבורד', 'ויזואל*'],
  'fabius-cohors': ['build an agent', 'agent system', 'agent architecture', 'agent workflow', 'agent orchestration', 'orchestrate agents', 'subagent', 'swarm', 'multi-agent',
    'בנה סוכן', 'מערכת סוכנים', 'ארכיטקטורת סוכנים', 'זרימת סוכנים', 'תת סוכן', 'תתי סוכנים', 'נחיל סוכנים', 'תזמור סוכנים'],
  'fabius-archivum': ['knowledge base', 'wiki', 'memory', 'מאגר ידע', 'ויקי', 'זיכרון'],
  'fabius-mercatus': ['copy', 'positioning', 'launch', 'campaign', 'funnel', 'market*', 'headline', 'go-to-market', 'seo', 'advertising', 'landing copy',
    'קופי', 'מיצוב', 'השקה', 'קמפיין', 'משפך', 'שיווק', 'כותרת שיווקית', 'פרסום'],
  'fabius-praesidium': ['secure*', 'security', 'threat', 'vuln*', 'security audit', 'harden*', 'owasp', 'stride', 'xss', 'injection', 'pentest', 'recon', 'attack surface', 'security headers', 'tls', 'certificate', 'dmarc', 'spf', 'dnssec', 'signature verification',
    'אבטחה', 'אבטח*', 'איום', 'חולשה', 'ביקורת אבטחה', 'הקשח*', 'בדיקת חדירות', 'שטח תקיפה', 'כותרות אבטחה', 'תעודה', 'אימות חתימה'],
  'fabius-ludus': ['game', 'gameplay', 'playable', 'sprite', 'level design', 'platformer', 'משחק', 'משחקיות', 'ספרייט', 'עיצוב שלב'],
  'fabius-catena': ['smart contract', 'on-chain', 'onchain', 'crypto wallet', 'solidity', 'solana', 'evm', 'token mint', 'blockchain transaction', 'transaction signing', 'blockchain seal', 'provenance anchor', 'blockchain', 'foundry', 'eip-712',
    'חוזה חכם', 'בלוקציין', 'בלוקצ׳יין', 'ארנק קריפטו', 'עסקה בשרשרת', 'חתימת עסקה', 'הטבעת טוקן'],
  'fabius-machina': ['automate*', 'automation', 'webhook workflow', 'n8n', 'zapier', 'make.com', 'cron', 'workflow integration', 'no-code', 'low-code',
    'אוטומציה', 'הפוך לאוטומטי', 'זרימת webhook', 'וובהוק לאוטומציה', 'ללא קוד'],
  'fabius-scientia': ['biology', 'genom*', 'rna-seq', 'protein', 'molecule', 'chemistry', 'clinical trial', 'omics', 'scientific hypothesis', 'gene', 'genetic variant', 'scientific experiment', 'experimental design', 'bioinformatic*', 'cheminformatic*',
    'ביולוגיה', 'גנומ*', 'חלבון', 'מולקולה', 'כימיה', 'ניסוי קליני', 'אומיקס', 'השערה מדעית', 'גן', 'וריאנט גנטי', 'ניסוי מדעי', 'ביואינפורמט*'],
  'fabius-doctrina': ['train a model', 'train the model', 'train a classifier', 'model training', 'fine-tune', 'finetune', 'serve a model', 'model inference', 'vllm', 'mlflow', 'mlops', 'eval harness', 'model registry', 'quantiz*', 'fine tune', 'experiment track*', 'inference endpoint', 'gpu serving',
    'אמן מודל', 'אימון מודל', 'כוונון מודל', 'שרת מודל', 'הסקת מודל', 'רישום מודלים', 'קוונטיז*'],
  'fabius-fortuna': ['stock', 'equity', 'ticker', 'stock market', 'the market', 'index fund', 'backtest', 'investment portfolio', 'portfolio risk', 'valuation', 'dcf', 'economic indicator', 'gdp', 'cpi', 'interest rate', 'volatility', 'sharpe', 'trading strateg*', 'investment', 'is this a buy',
    'מניה', 'מניות', 'שוק ההון', 'קרן מחקה', 'בדיקה לאחור', 'תיק השקעות', 'תיק ההשקעות', 'סיכון בתיק', 'הערכת שווי', 'אינדיקטור כלכלי', 'ריבית', 'תנודתיות', 'אסטרטגיית מסחר', 'השקעה'],
  'fabius-concilium': ['model council', 'council of models', 'several models', 'panel of models', 'ask multiple models', 'ask three models', 'compare model answers', 'multiple providers',
    'מועצת מודלים', 'כמה מודלים', 'מספר מודלים', 'שאל כמה מודלים', 'השווה תשובות של מודלים', 'כמה ספקי מודל'],
};

// Domains whose stakes — money, irreversibility, security — warrant the strong tier.
const DOMAIN_STRONG = ['fabius-catena', 'fabius-praesidium', 'fabius-fortuna'];

// Full words are bounded on BOTH sides, in every script. A trailing `*` marks the handful
// of intentional stems. The old left-only matcher made `contract`, `train`, `experiment`
// and Hebrew substrings fire inside unrelated words — cheap routing needs precision more
// than an ever-growing bag of fragments.
const RX = new Map();
function kwRx(w) {
  let rx = RX.get(w);
  if (!rx) {
    const stem = w.endsWith('*');
    const literal = stem ? w.slice(0, -1) : w;
    const esc = literal.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const left = /^[\p{L}\p{N}]/u.test(literal) ? '(?<![\\p{L}\\p{N}_])' : '';
    const right = !stem && /[\p{L}\p{N}]$/u.test(literal) ? '(?![\\p{L}\\p{N}_])' : '';
    rx = new RegExp(left + esc + right, 'u');
    RX.set(w, rx);
  }
  return rx;
}

function countHits(text, words) {
  const t = String(text || '').toLowerCase();
  const matched = [];
  for (const w of words) if (kwRx(w).test(t)) matched.push(w);
  return { n: matched.length, matched };
}

// Every place a keyword lands, not just whether it landed. Containment has to be judged on
// SPANS: "improve the design; also fix the level design" contains 'design' standing on its own
// AND inside ludus's 'level design', and a string-only comparison drops decor for a phrase that
// matched somewhere else entirely.
function hitSpans(text, words) {
  const t = String(text || '').toLowerCase();
  const out = [];
  for (const w of words) {
    const rx = new RegExp(kwRx(w).source, 'g');
    for (let m = rx.exec(t); m; m = rx.exec(t)) {
      out.push({ w, start: m.index, end: m.index + m[0].length });
      if (m.index === rx.lastIndex) rx.lastIndex++;   // zero-width guard
    }
  }
  return out;
}

export function route(task, opts = {}) {
  const cfg = opts.cfg || loadConfig();
  const text = String(task || '');
  const words = text.split(/\s+/).filter(Boolean).length;
  const mem = countHits(text, SIG.memory), tool = countHits(text, SIG.tools), plan = countHits(text, SIG.planning);
  const discipline = countHits(text, SIG.discipline);
  const longText = words > 60;
  const freshEyes = /\b(incident|breach|outage|vulnerab\w*|exploit|threat.?model|security|forensic|data.?loss|rollback|postmortem|recon|error recovery)\b/i.test(text)
    || /(אירוע אבטחה|אבטחה|פריצה|השבתה|חולש\w*|ניצול חולשה|מודל איומים|חקירה פורנזית|אובדן מידע|שחזור מתקלה|פוסט.?מורטם)/u.test(text);
  // Recall is authority-bearing context even when it is labelled suspect. Ordinary
  // work therefore starts off; an explicit memory signal enables normal recall, while
  // fresh-eyes routes override even that request and stay off.
  const recall = freshEyes ? 'off' : (mem.n > 0 ? 'normal' : 'off');
  const recallReason = freshEyes ? 'fresh-eyes' : (mem.n > 0 ? 'explicit-signal' : 'no-signal');
  const axes = { memory: mem.n > 0 && recall !== 'off', tools: tool.n > 0 || discipline.n > 0, planning: plan.n > 0 || longText };

  // Longest-match-wins, judged POSITIONALLY. A word boundary cannot stop a key firing inside a
  // longer phrase another layer owns — 'market' sits inside fortuna's 'the market', 'design'
  // inside ludus's 'level design'. But a hit is only swallowed when a longer hit covers THAT
  // OCCURRENCE: a layer that also fires somewhere else keeps its own evidence and stays. Drop
  // a layer only when every one of its occurrences sits inside a longer one (R13).
  const spans = {};
  for (const layer of Object.keys(DOMAIN)) {
    const s = hitSpans(text, DOMAIN[layer]);
    if (s.length) spans[layer] = s;
  }
  const allSpans = Object.values(spans).flat();
  const swallowed = (h) => allSpans.some((o) =>
    (o.end - o.start) > (h.end - h.start) && o.start <= h.start && o.end >= h.end);
  const domains = Object.keys(spans).filter((layer) => spans[layer].some((h) => !swallowed(h)));
  axes.domain = domains.length > 0;

  const layers = ['fabius-parcus'];
  if (axes.memory) layers.push('fabius-archivum');
  // Tool use chooses machinery; it does not make the task agent-engineering. Cohors
  // owns explicit agent/subagent/swarm design, while Disciplina owns build/fix/test
  // process even when the user did not ask for a written plan.
  if (axes.planning || discipline.n > 0) layers.push('fabius-disciplina');
  for (const d of domains) if (!layers.includes(d)) layers.push(d);   // R13 — the domain leads the vertical

  // R2 — climb to the SMALLEST sufficient rung: take the highest rung any signal
  // demands, and stop there. Each signal names its own floor, so `tool` is reachable on
  // its own rather than being skipped whenever a task needs a tool but no plan.
  let rung = 'inline';
  const climb = (to) => { if (LADDER.indexOf(to) > LADDER.indexOf(rung)) rung = to; };
  if (axes.tools) climb('tool');
  if (axes.memory) climb('retrieval');
  if (axes.planning) climb('plan');
  if (axes.planning && axes.tools) climb('subagent');
  const rungIndex = LADDER.indexOf(rung);

  const strong = countHits(text, SIG.strong), fast = countHits(text, SIG.fast);
  // Ambiguity, not conjunctions. A bare `or` is one of the commonest words in English, and it
  // was buying the frontier tier for "rename the button label to Save or Cancel" — an
  // alternation is only a fork when it sits inside a question or under a modal.
  // `should` and `which` had to keep earning the tier, though: dropping them bare took
  // "should the API be versioned" and "which caching layer do we pick" down with the noise, so
  // they return as MODAL phrasings rather than as bare words. `either way` is not here: it
  // states indifference, which is the opposite of a fork worth paying for.
  const modal = /\bshould\s+(we|i|you|the|it|they|this)\b/i.test(text)
    || /\bwhich\b[^.?!]{0,40}\b(should|do we|to use|pick|choose|prefer)\b/i.test(text);
  const ambiguous = (words < 6 && /\?/.test(text))
    || /\b(whether|unclear|unsure|not sure|which one)\b/i.test(text)
    || modal
    || (/\bor\b/i.test(text) && (/\?/.test(text) || modal));
  const domainStrong = domains.some((d) => DOMAIN_STRONG.includes(d));

  let tier = 'mid', tierWhy;
  if (strong.n > 0 || ambiguous || rung === 'subagent' || domainStrong) {
    tier = 'frontier';
    tierWhy = strong.n > 0 ? `strong-tier signal (${strong.matched.slice(0, 3).join(', ')}) — R11 reserves frontier for ambiguity/architecture/security/irreversible`
      : domainStrong ? `high-stakes domain (${domains.filter((d) => DOMAIN_STRONG.includes(d)).join(', ')}) — R11 reserves frontier for money/security calls`
      : rung === 'subagent' ? 'work splits across agents — lead reasoning needs the strong tier'
      : 'ambiguous request — resolve with the strong tier';
  } else if (fast.n > 0 && !axes.planning && !axes.tools && !axes.domain) {
    tier = 'fast'; tierWhy = `mechanical/contracted work (${fast.matched.slice(0, 3).join(', ')}) — R11 cheap tier`;
  } else {
    tierWhy = 'default workhorse tier — no strong-tier or fast-tier signal';
  }
  if (opts.tier) { tier = opts.tier; tierWhy = `tier forced by the caller (--tier ${opts.tier})`; }

  const wantProvider = PROVIDERS[opts.provider] ? opts.provider : (PROVIDERS[cfg.provider] ? cfg.provider : 'anthropic');
  const resolved = overrideModel(resolveModel(wantProvider, tier, cfg), PROVIDERS[opts.provider] ? opts.provider : null, opts.model || cfg.model);
  const available = availableProviders(cfg, wantProvider);

  return {
    axes, recall, recallReason, layers, domains, rung, rungIndex, ladder: LADDER, tier,
    requestedProvider: wantProvider,
    provider: resolved ? resolved.provider : wantProvider,
    model: resolved ? resolved.model : PROVIDERS[wantProvider].tiers[tier],
    available, fireable: !!resolved,
    rationale: {
      classify: `Memory=${axes.memory} · Tools=${axes.tools} · Planning=${axes.planning} · Domain=${axes.domain} · Recall=${recall}(${recallReason})` +
        ` (mem:${mem.n} tool:${tool.n} plan:${plan.n} process:${discipline.n}${longText ? ' +long' : ''}${domains.length ? ' → ' + domains.map((d) => d.replace('fabius-', '')).join(', ') : ''})`,
      ladder: `R2 → smallest sufficient rung: ${rung} (stopped before ${LADDER[Math.min(rungIndex + 1, LADDER.length - 1)]})`,
      tier: `R11 → ${tier}: ${tierWhy}`,
      select: resolved
        ? `${PROVIDERS[resolved.provider].label} ${resolved.model}` + (resolved.provider !== wantProvider ? ` (fell back from ${wantProvider} — no key)` : '')
        : 'no provider keyed — nothing will fire',
    },
  };
}
