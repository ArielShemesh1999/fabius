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
  memory: ['remember', 'recall', 'history', 'decided', 'past', 'precedent', 'knowledge', 'wiki', 'note', 'log'],
  tools: ['fetch', 'search', 'api', 'query', 'compute', 'calculate', 'scrape', 'lookup', 'database', 'integrate', 'deploy', 'read the file', 'run the', 'install'],
  planning: ['plan', 'steps', 'roadmap', 'orchestrate', 'pipeline', 'workflow', 'phase', 'milestone', 'sequence', 'then', 'first', 'multi'],
  strong: ['architecture', 'architect', 'security', 'threat', 'vuln', 'crypto', 'auth', 'oauth', 'design system', 'migration', 'irreversible', 'delete', 'production', 'strategy', 'ambiguous', 'trade-off', 'tradeoff', 'why', 'should we', 'decide', 'choose between', 'risk', 'legal', 'payment', 'money'],
  fast: ['rename', 'format', 'reformat', 'list', 'extract', 'classify', 'translate', 'summarize', 'tag', 'lookup', 'convert', 'lint'],
};

// The DOMAIN axis — which specialist the task's WHAT pulls. One owner per capability, so
// these keyword sets are deliberately disjoint — enforced by the matcher below, not by
// hoping: word boundaries keep a key from firing inside a longer WORD, and longest-match-wins
// keeps it from firing inside a longer PHRASE another layer owns.
const DOMAIN = {
  'fabius-decor': ['ui', 'design', 'landing page', 'hero', 'component', 'css', 'brand', 'layout', 'chart', 'graph', 'diagram', 'visuali', 'dashboard', 'figure', 'data-ink', 'svg'],
  'fabius-cohors': ['agent', 'subagent', 'swarm', 'orchestrat', 'multi-agent'],
  'fabius-archivum': ['knowledge base', 'wiki', 'memory'],
  'fabius-mercatus': ['copy', 'positioning', 'launch', 'campaign', 'funnel', 'market', 'headline', 'go-to-market', 'seo', 'ad ', 'ads', 'landing copy'],
  'fabius-praesidium': ['secure', 'security', 'threat', 'vuln', 'audit', 'harden', 'owasp', 'stride', 'xss', 'injection', 'pentest', 'recon', 'attack surface', 'headers', 'tls', 'certificate', 'dmarc', 'spf', 'dnssec'],
  'fabius-ludus': ['game', 'gameplay', 'playable', 'juice', 'sprite', 'level design', 'platformer'],
  'fabius-catena': ['contract', 'on-chain', 'onchain', 'wallet', 'solidity', 'solana', 'evm', 'mint', 'transaction', 'seal', 'provenance', 'anchor', 'blockchain', 'foundry', 'eip-712', 'sign this', 'sign the'],
  'fabius-machina': ['automate', 'automation', 'webhook', 'n8n', 'zapier', 'make.com', 'cron', 'integration', 'connect ', 'when x', 'no-code', 'low-code'],
  'fabius-scientia': ['biology', 'genom', 'rna-seq', 'protein', 'molecule', 'chemistry', 'clinical', 'omics', 'hypothesis', 'gene ', 'variant', 'experiment', 'bioinformatic', 'cheminformatic'],
  'fabius-doctrina': ['train', 'fine-tune', 'finetune', 'serve a model', 'inference', 'vllm', 'mlflow', 'mlops', 'eval harness', 'model registry', 'quantiz', 'fine tune', 'experiment track', 'inference endpoint', 'gpu serving'],
  'fabius-fortuna': ['stock', 'equity', 'ticker', 'the market', 'index fund', 'backtest', 'portfolio', 'valuation', 'dcf', 'economic indicator', 'gdp', 'cpi', 'interest rate', 'volatility', 'sharpe', 'trading strateg', 'investment', 'is this a buy'],
  'fabius-concilium': ['council', 'several models', 'panel of models', 'ask multiple models', 'deliberate'],
};

// Domains whose stakes — money, irreversibility, security — warrant the strong tier.
const DOMAIN_STRONG = ['fabius-catena', 'fabius-praesidium', 'fabius-fortuna'];

// A keyword is anchored on its LEFT word boundary and left open on the right, so stems keep
// earning their keep — 'quantiz' still catches quantized, 'visuali' visualisation — while
// 'train' stops firing inside "constraint" and "restraint", and 'ad ' inside "read the file".
// Keys that start with punctuation take no anchor. Compiled once per keyword, because route()
// runs on every step of every loop.
const RX = new Map();
function kwRx(w) {
  let rx = RX.get(w);
  if (!rx) { rx = new RegExp((/^[a-z0-9]/.test(w) ? '\\b' : '') + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')); RX.set(w, rx); }
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
  const longText = words > 60;
  const axes = { memory: mem.n > 0, tools: tool.n > 0, planning: plan.n > 0 || longText };

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
  if (axes.tools) layers.push('fabius-cohors');
  if (axes.planning) layers.push('fabius-disciplina');
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
  const available = availableProviders(cfg);

  return {
    axes, layers, domains, rung, rungIndex, ladder: LADDER, tier,
    requestedProvider: wantProvider,
    provider: resolved ? resolved.provider : wantProvider,
    model: resolved ? resolved.model : PROVIDERS[wantProvider].tiers[tier],
    available, fireable: !!resolved,
    rationale: {
      classify: `Memory=${axes.memory} · Tools=${axes.tools} · Planning=${axes.planning} · Domain=${axes.domain}` +
        ` (mem:${mem.n} tool:${tool.n} plan:${plan.n}${longText ? ' +long' : ''}${domains.length ? ' → ' + domains.map((d) => d.replace('fabius-', '')).join(', ') : ''})`,
      ladder: `R2 → smallest sufficient rung: ${rung} (stopped before ${LADDER[Math.min(rungIndex + 1, LADDER.length - 1)]})`,
      tier: `R11 → ${tier}: ${tierWhy}`,
      select: resolved
        ? `${PROVIDERS[resolved.provider].label} ${resolved.model}` + (resolved.provider !== wantProvider ? ` (fell back from ${wantProvider} — no key)` : '')
        : 'no provider keyed — nothing will fire',
    },
  };
}
