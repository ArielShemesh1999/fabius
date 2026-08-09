#!/usr/bin/env node
// fabius — the agent, running on your machine.
//
//   fabius run "<task>"        one run: route → sense → act → prove → compound
//   fabius chat                 a conversation that keeps the loop between turns
//   fabius recon <domain>       audit a domain you own — no API key needed
//   fabius route "<task>"       show the routing decision, spend nothing
//   fabius memory …             list · search · add · rm
//   fabius doctor               what is configured, what is missing, what is sealed
//   fabius keys …               store a provider key in ~/.fabius/config.json (0600)
//
// Nothing here phones home. The only outbound traffic is the model provider you chose
// and the URLs a task explicitly asks for.

import { createInterface } from 'node:readline/promises';
import { readFileSync } from 'node:fs';
import { run } from './src/loop.mjs';
import { route } from './src/route.mjs';
import { recon, formatReport, CHECKS } from './src/recon.mjs';
import { loadConfig, saveConfig, providerKey, ENV_KEY, HOME, ensureDirs, redact } from './src/config.mjs';
import { PROVIDERS, PROVIDER_ORDER, availableProviders } from './src/providers.mjs';
import { loadSkills, verifySeal, skillSummary } from './src/skills.mjs';
import { listMemory, recallMemory, writeMemory, deleteMemory, initMemory } from './src/memory.mjs';
import { listen, identity, send } from './src/channel.mjs';
import { DEFAULT_RELAYS } from './src/nostr.mjs';
import { say, paint, die, warn } from './src/util.mjs';

const VERSION = '1.0.0';

// ── argv ────────────────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const flags = {}; const positional = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const [k, inline] = a.slice(2).split('=');
      const next = argv[i + 1];
      let v;
      if (inline !== undefined) v = inline;
      else if (next && !next.startsWith('--')) { v = next; i++; }
      else v = true;
      // repeatable flags (--relay, --owner) accumulate; consumers already [].concat()
      flags[k] = k in flags ? [].concat(flags[k], v) : v;
    } else positional.push(a);
  }
  return { flags, positional };
}

const HELP = `
${paint('violet', 'fabius')} ${paint('dim', VERSION)} — the agent, on your machine

  ${paint('bold', 'fabius run')} "<task>"        run one task end to end
      --act                    let it write files and run commands (asks before each)
      --yes                    approve writes and commands automatically
                               (irreversible actions are still held for you)
      --dir <path>             the working directory it is confined to (default: cwd)
      --provider <name>        ${PROVIDER_ORDER.join(' · ')}
      --model <id>             a specific model, e.g. any HuggingFace repo
      --tier frontier|mid|fast  override the router's choice
      --budget <usd>           stop rather than spend more (default 2.00)
      --offline                no network tools
      --sealed-only            refuse any contract the seal does not cover
      --no-memory              do not compound anything from this run
      --json                   machine-readable result

  ${paint('bold', 'fabius chat')}                 keep talking; memory and directory persist
  ${paint('bold', 'fabius recon')} <domain>       audit DNS · TLS · headers · cookies · mail · exposed files
      --ports                  also probe common service ports (authorised targets only)
      --json                   full findings as JSON
  ${paint('bold', 'fabius route')} "<task>"       print the routing decision, call no model
  ${paint('bold', 'fabius memory')} list|search <q>|add <title>|rm <name>
  ${paint('bold', 'fabius listen')} --owner <npub>  reachable by encrypted DM, no server in between
      --act                    let a message make it write and run things
      --relay <wss://…>        repeatable; defaults to three public relays
  ${paint('bold', 'fabius send')} <npub> "<text>"  send one encrypted message
  ${paint('bold', 'fabius whoami')}                print this machine's agent address

  ${paint('bold', 'fabius doctor')}               providers, skills, seal, paths
  ${paint('bold', 'fabius keys')} set <provider> <key>   |   keys list

  state lives in ${paint('dim', HOME)}
`;

// ── commands ────────────────────────────────────────────────────────────────────

async function cmdRun(positional, flags) {
  const task = positional.join(' ').trim();
  if (!task) die('  give it something to do:  fabius run "write a README for this project"');
  const opts = runOptions(flags);
  const started = Date.now();
  if (!flags.json) printRouteHeader(route(task, opts));

  const res = await run(task, { ...opts, onEvent: flags.json ? () => {} : liveEvent });
  if (res.error) die('  ' + res.error);

  if (flags.json) {
    say(JSON.stringify({ output: res.output, verdict: res.verdict, route: { layers: res.route.layers, tier: res.route.tier, model: res.route.model },
      cost: res.cost, usage: res.usage, changed: res.changed, fired: res.fired }, null, 2));
    return;
  }
  say('');
  say(paint('violet', '  ── deliverable ──'));
  say('');
  say(res.output.split('\n').map((l) => '  ' + l).join('\n'));
  say('');
  const v = res.verdict || {};
  const mark = v.pass && v.score >= 70 ? paint('green', '✓') : paint('yellow', '~');
  say(`  ${mark} reviewed ${v.score ?? '—'}/100${v.execVerified === true ? paint('green', ' · code ran clean') : v.execVerified === false ? paint('red', ' · code failed to run') : ''}`);
  if (v.issues?.length && v.score < 90) for (const i of v.issues.slice(0, 3)) say(paint('dim', `    · ${i}`));
  if (res.changed.length) say(`  ${paint('cyan', 'changed')} ${res.changed.join(', ')}`);
  if (res.proposal?.write) say(`  ${paint('cyan', 'remembered')} ${res.proposal.title}`);
  say(paint('dim', `  ${((Date.now() - started) / 1000).toFixed(1)}s · $${res.cost.toFixed(4)} · ${res.usage.input_tokens + res.usage.output_tokens} tokens · rules ${res.fired.join(' ')}`));
  say('');
}

function runOptions(flags) {
  const cfg = loadConfig();
  return {
    cfg,
    act: !!flags.act,
    approve: flags.yes ? 'auto' : (flags['read-only'] ? 'never' : cfg.approve),
    dangerous: !!flags['dangerously-approve-everything'],
    jail: flags.dir ? String(flags.dir) : (cfg.workdir || process.cwd()),
    provider: flags.provider ? String(flags.provider) : undefined,
    model: flags.model ? String(flags.model) : undefined,
    tier: flags.tier ? String(flags.tier) : undefined,
    budgetUsd: flags.budget ? Number(flags.budget) : undefined,
    offline: !!flags.offline,
    remember: !flags['no-memory'],
    sealedOnly: !!flags['sealed-only'],
    maxSteps: flags.steps ? Number(flags.steps) : undefined,
  };
}

function printRouteHeader(r) {
  say('');
  say(paint('dim', `  ${r.rationale.classify}`));
  say(paint('dim', `  ${r.rationale.ladder}`));
  say(paint('dim', `  ${r.rationale.tier}`));
  say(paint('dim', `  → ${r.rationale.select}`));
  say('');
}

function liveEvent(kind, body) {
  if (kind === 'contracts') say(paint('dim', `  contracts: ${body.included.join(' · ')}`));
  else if (kind === 'sense') say(paint('dim', `  sense: ${body.note}`));
  else if (kind === 'think') say(paint('dim', `  · ${String(body.text).slice(0, 160)}`));
  else if (kind === 'act') say(`  ${paint('cyan', body.tool)} ${paint('dim', String(body.input).replace(/\n/g, ' ').slice(0, 100))}`);
  else if (kind === 'rule') say(paint('yellow', `  ${body.rule} — ${body.note}`));
  else if (kind === 'oracle') say(paint(body.ok ? 'green' : 'red', `  oracle: ran the ${body.lang} artifact → exit ${body.exit}`));
  else if (kind === 'stop') say(paint('yellow', `  stopped: ${body.reason}`));
}

async function cmdChat(flags) {
  const opts = runOptions(flags);
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  say('');
  say(paint('violet', '  fabius') + paint('dim', ` — ${opts.act ? 'acting' : 'read-only'} in ${opts.jail}. Ctrl-C to leave.`));
  say('');
  for (;;) {
    let line;
    try { line = (await rl.question(paint('violet', '  › '))).trim(); }
    catch { break; }
    if (!line) continue;
    if (['exit', 'quit', ':q'].includes(line)) break;
    const res = await run(line, { ...opts, onEvent: liveEvent });
    if (res.error) { warn('  ' + res.error); continue; }
    say('');
    say(res.output.split('\n').map((l) => '  ' + l).join('\n'));
    say(paint('dim', `  $${res.cost.toFixed(4)} · reviewed ${res.verdict?.score ?? '—'}/100`));
    say('');
  }
  rl.close();
}

async function cmdRecon(positional, flags) {
  const target = positional[0];
  if (!target) die('  which domain?  fabius recon example.com');
  if (flags.ports && !flags.json) {
    warn('  port probing is an active check — run it only against hosts you are authorised to test.');
  }
  const checks = flags.checks ? String(flags.checks).split(',').map((s) => s.trim()).filter((c) => CHECKS.includes(c)) : null;
  const r = await recon(target, { ports: !!flags.ports, checks });
  if (flags.json) say(JSON.stringify(r, null, 2));
  else say(formatReport(r));
}

function cmdRoute(positional, flags) {
  const task = positional.join(' ').trim();
  if (!task) die('  fabius route "<task>"');
  const r = route(task, runOptions(flags));
  if (flags.json) return say(JSON.stringify(r, null, 2));
  printRouteHeader(r);
  say(`  layers   ${r.layers.join(' · ')}`);
  say(`  rung     ${r.rung}  ${paint('dim', '(' + r.ladder.join(' → ') + ')')}`);
  say(`  tier     ${r.tier}`);
  say(`  model    ${r.fireable ? r.model : paint('yellow', 'nothing keyed')}`);
  say('');
}

function cmdDoctor() {
  ensureDirs(); initMemory();
  const cfg = loadConfig();
  say('');
  say(paint('violet', `  fabius ${VERSION}`) + paint('dim', `  · node ${process.version} · ${process.platform}`));
  say('');
  say(paint('bold', '  providers'));
  for (const p of PROVIDER_ORDER) {
    const has = !!providerKey(p, cfg);
    const mark = has ? paint('green', '✓') : paint('dim', '·');
    say(`   ${mark} ${p.padEnd(13)} ${paint('dim', has ? `keyed (${ENV_KEY[p]})` : `set ${ENV_KEY[p]}`)}  ${paint('dim', Object.values(PROVIDERS[p].tiers).join(' / '))}`);
  }
  const avail = availableProviders(cfg);
  say('');
  say(avail.length ? paint('green', `   ${avail.length} provider(s) ready — default ${cfg.provider}`)
                   : paint('yellow', '   nothing is keyed — fabius can route and recon, but cannot think'));

  say('');
  say(paint('bold', '  brain'));
  const { skills } = loadSkills();
  say(`   ${skills.size} skill contract(s) loaded`);
  const seal = verifySeal();
  if (!seal.available) say(paint('dim', `   seal: ${seal.reason}`));
  else {
    if (seal.drift.length) say(paint('red', `   seal: ${seal.matched}/${seal.total} match — DRIFT in ${seal.drift.join(', ')}`));
    else say(paint('green', `   seal: ${seal.matched}/${seal.total} files match the sealed manifest`));
    // A contract the manifest never listed is invisible to a hash check — it has to be
    // looked for separately, or a dropped-in skill reaches the model unsealed.
    if (seal.unsealed.length) say(paint('red', `   seal: ${seal.unsealed.length} UNSEALED contract(s) present — ${seal.unsealed.join(', ')}  (run with --sealed-only to refuse them)`));
  }

  say('');
  say(paint('bold', '  state'));
  say(paint('dim', `   home      ${HOME}`));
  say(paint('dim', `   memory    ${listMemory().length} page(s)`));
  say(paint('dim', `   posture   ${cfg.approve}  ${paint('dim', '(ask · auto · never)')}`));
  say(paint('dim', `   budget    $${(cfg.budgetUsd ?? 2).toFixed(2)} per run`));
  say('');
}

function cmdMemory(positional, flags) {
  const [sub, ...rest] = positional;
  initMemory();
  if (!sub || sub === 'list') {
    const all = listMemory();
    if (!all.length) return say(paint('dim', '  memory is empty — it fills as verified runs compound.'));
    say('');
    for (const m of all) say(`  ${paint('bold', m.title)}  ${paint('dim', `[${m.kind} · ${m.score}]`)}\n    ${paint('dim', m.file)}`);
    say('');
    return;
  }
  if (sub === 'search') {
    const q = rest.join(' ');
    const hits = recallMemory(q, { k: 8 });
    if (!hits.length) return say(paint('dim', '  no matches'));
    for (const h of hits) say(`  ${(h.relevance * 100).toFixed(0)}%  ${paint('bold', h.title)}  ${paint('dim', h.file)}`);
    return;
  }
  if (sub === 'add') {
    const title = rest.join(' ');
    if (!title) die('  fabius memory add "<title>"  (body on stdin)');
    let body = '';
    try { body = readFileSync(0, 'utf8'); } catch { /* no stdin */ }
    if (!body.trim()) die('  pipe the body in:  echo "the fact" | fabius memory add "title"');
    const w = writeMemory({ title, body, kind: flags.kind || 'note', score: 100 });
    return say(`  wrote ${w.path}`);
  }
  if (sub === 'rm') {
    const name = rest.join(' ');
    return say(deleteMemory(name) ? `  removed ${name}` : paint('yellow', `  no such page: ${name}`));
  }
  die('  fabius memory list|search <q>|add <title>|rm <name>');
}

function cmdKeys(positional) {
  const [sub, provider, key] = positional;
  if (sub === 'list' || !sub) {
    const cfg = loadConfig();
    for (const p of PROVIDER_ORDER) {
      const k = providerKey(p, cfg);
      say(`  ${p.padEnd(13)} ${k ? paint('green', 'keyed  ') + paint('dim', k.slice(0, 6) + '…' + k.slice(-4)) : paint('dim', 'not set')}`);
    }
    return;
  }
  if (sub === 'set') {
    if (!PROVIDERS[provider]) die(`  unknown provider "${provider}" — one of ${PROVIDER_ORDER.join(', ')}`);
    if (!key) die(`  fabius keys set ${provider} <key>`);
    saveConfig({ keys: { [provider]: key } });
    return say(`  stored ${provider} in ${paint('dim', HOME + '/config.json')} ${paint('dim', '(0600)')}`);
  }
  die('  fabius keys set <provider> <key>   |   fabius keys list');
}

async function cmdListen(flags) {
  const owners = [].concat(flags.owner || []).filter((o) => typeof o === 'string');
  if (!owners.length) {
    say('');
    say(paint('yellow', '  a listener needs an allow-list — otherwise anyone who learns the address can task it.'));
    say(`  your own address is ${paint('bold', identity().npub)}`);
    say(paint('dim', '  fabius listen --owner npub1…      (the key you will message it FROM)'));
    say('');
    process.exit(1);
  }
  const relays = [].concat(flags.relay || []).filter((r) => typeof r === 'string' && r.startsWith('wss://'));
  const { stop } = await listen({
    owners,
    relays: relays.length ? relays : DEFAULT_RELAYS,
    act: !!flags.act,
    onLine: (l) => say(l ? '  ' + l.replace(/^\s+/, '') : ''),
    runOptions: runOptions(flags),
  });
  process.on('SIGINT', () => { stop(); say('\n  stopped.'); process.exit(0); });
  await new Promise(() => {});   // run until interrupted
}

async function cmdSend(positional) {
  const [to, ...rest] = positional;
  const text = rest.join(' ');
  if (!to || !text) die('  fabius send <npub> "<text>"');
  const r = await send(text, to);
  say(r.ok ? paint('green', '  delivered to at least one relay') : paint('yellow', '  no relay accepted it'));
}

function cmdWhoami() {
  const me = identity();
  say('');
  say(`  ${paint('bold', me.npub)}`);
  say(paint('dim', `  hex ${me.pub}`));
  say(paint('dim', '  message this address to reach the agent (it must be listening, and you must be on its allow-list)'));
  say('');
}

// ── entry ───────────────────────────────────────────────────────────────────────
const { flags, positional } = parseArgs(process.argv.slice(2));
const cmd = positional.shift();

try {
  switch (cmd) {
    case 'run': await cmdRun(positional, flags); break;
    case 'chat': await cmdChat(flags); break;
    case 'recon': await cmdRecon(positional, flags); break;
    case 'route': cmdRoute(positional, flags); break;
    case 'memory': cmdMemory(positional, flags); break;
    case 'listen': await cmdListen(flags); break;
    case 'send': await cmdSend(positional); break;
    case 'whoami': cmdWhoami(); break;
    case 'keys': cmdKeys(positional); break;
    case 'doctor': cmdDoctor(); break;
    case 'version': case '--version': say(VERSION); break;
    case undefined: case 'help': case '--help': case '-h': say(HELP); break;
    default: say(HELP); die(`  unknown command "${cmd}"`);
  }
} catch (e) {
  die('  ' + redact(String(e?.stack || e?.message || e)));
}
