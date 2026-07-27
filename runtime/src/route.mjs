// THE ROUTER — R1 (classify on layer · machinery · model-tier) · R2 (climb the ladder
// to the smallest sufficient rung) · R11 (cheapest tier that holds; the strong tier for
// ambiguity, architecture, security, money, irreversibility).
//
// Heuristic and inspectable on purpose: no model call, no network, fully deterministic,
// and it prints its reasoning. The same classification the console runs, so a task
// routed on this machine lands on the same specialist it would land on in the cloud.

import { PROVIDERS, resolveModel, overrideModel, availableProviders } from './providers.mjs';
import { loadConfig } from './config.mjs';

export const LADDER = ['inline', 'tool', 'retrieval', 'plan', 'subagent', 'swarm'];

const SIG = {
  memory: ['remember', 'recall', 'history', 'decided', 'past', 'precedent', 'knowledge', 'wiki', 'note', 'log'],
  tools: ['fetch', 'search', 'api', 'query', 'compute', 'calculate', 'scrape', 'lookup', 'database', 'integrate', 'deploy', 'read the file', 'run the', 'install'],
  planning: ['plan', 'steps', 'roadmap', 'orchestrate', 'pipeline', 'workflow', 'phase', 'milestone', 'sequence', 'then', 'first', 'multi'],
  strong: ['architecture', 'architect', 'security', 'threat', 'vuln', 'crypto', 'auth', 'design system', 'migration', 'irreversible', 'delete', 'production', 'strategy', 'ambiguous', 'trade-off', 'tradeoff', 'why', 'should we', 'decide', 'choose between', 'risk', 'legal', 'payment', 'money'],
  fast: ['rename', 'format', 'reformat', 'list', 'extract', 'classify', 'translate', 'summarize', 'tag', 'lookup', 'convert', 'lint'],
};

// The DOMAIN axis — which specialist the task's WHAT pulls. One owner per capability,
// so these keyword sets are deliberately disjoint.
const DOMAIN = {
  'fabius-decor': ['ui', 'design', 'landing page', 'component', 'css', 'brand', 'layout', 'chart', 'graph', 'diagram', 'visuali', 'dashboard', 'figure', 'data-ink', 'svg'],
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

function countHits(text, words) {
  const t = String(text || '').toLowerCase();
  const matched = [];
  for (const w of words) if (t.includes(w)) matched.push(w);
  return { n: matched.length, matched };
}

export function route(task, opts = {}) {
  const cfg = opts.cfg || loadConfig();
  const text = String(task || '');
  const words = text.split(/\s+/).filter(Boolean).length;
  const mem = countHits(text, SIG.memory), tool = countHits(text, SIG.tools), plan = countHits(text, SIG.planning);
  const longText = words > 60;
  const axes = { memory: mem.n > 0, tools: tool.n > 0, planning: plan.n > 0 || longText };

  const domains = Object.keys(DOMAIN).filter((layer) => countHits(text, DOMAIN[layer]).n > 0);
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
  const ambiguous = (words < 6 && /\?/.test(text)) || /\b(should|which|whether|or)\b/i.test(text);
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
