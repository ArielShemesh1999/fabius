// THE LISTENER — fabius reachable from your phone, with nothing hosted in between.
//
// It subscribes to gift-wrapped direct messages addressed to its own key, unwraps them,
// runs the task, and sends the deliverable back the same way.
//
// Three rules make this safe enough to leave running:
//
//   AN ALLOW-LIST IS MANDATORY. The listener refuses to start without one. A public
//   inbox that executes what it is told is not a feature.
//   ACTING IS OPT-IN, exactly as it is on the command line. By default a message can
//   make fabius read and reason; it cannot make it write a file or run a command.
//   INBOUND TEXT IS A TASK, NEVER AN INSTRUCTION TO THE RUNTIME. It reaches the model as
//   the task string and nothing else — it cannot raise its own permissions, and the
//   approval gate is upstream of every tool regardless of what the message says.

import { writeFileSync, appendFileSync, existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { run } from './loop.mjs';
import { loadConfig, saveConfig, HOME, ensureDirs } from './config.mjs';
import {
  generateSecretKey, getPublicKey, npubEncode, toHexKey, hex,
  wrapDirectMessage, unwrapDirectMessage, publish, subscribe, DEFAULT_RELAYS,
} from './nostr.mjs';

// The identity lives in the same 0600 config as the provider keys. It is generated once;
// losing it means a new address, not lost data.
export function identity() {
  const cfg = loadConfig();
  let sk = cfg.nostr?.sk;
  if (!sk) {
    sk = hex(generateSecretKey());
    saveConfig({ nostr: { ...(cfg.nostr || {}), sk } });
  }
  const pub = hex(getPublicKey(sk));
  return { sk, pub, npub: npubEncode(pub) };
}

const LOG = () => join(HOME, 'channel.log');
function note(line) {
  ensureDirs();
  const stamped = `${new Date().toISOString()} ${line}\n`;
  try { appendFileSync(LOG(), stamped); } catch { /* logging must never break the listener */ }
  return stamped.trimEnd();
}

// A message the listener has already handled must never run twice — a relay replays, and
// two relays will hand you the same wrapper.
function seenStore() {
  const path = join(HOME, 'channel-seen.json');
  let ids = [];
  try { ids = JSON.parse(readFileSync(path, 'utf8')); } catch { ids = []; }
  const set = new Set(ids);
  return {
    has: (id) => set.has(id),
    add(id) {
      set.add(id);
      const trimmed = [...set].slice(-500);
      try { writeFileSync(path, JSON.stringify(trimmed), { mode: 0o600 }); } catch { /* best effort */ }
    },
  };
}

export async function listen({ owners, relays = DEFAULT_RELAYS, act = false, onLine = console.log, runOptions = {} } = {}) {
  const allow = new Set((owners || []).map((o) => toHexKey(o, 'npub')));
  if (!allow.size) throw new Error('a listener without an allow-list would execute anything it is sent — pass --owner <npub>');

  const me = identity();
  const seen = seenStore();
  const cfg = loadConfig();

  onLine(`  listening as ${me.npub}`);
  onLine(`  allowed senders: ${[...allow].map((k) => npubEncode(k)).join(', ')}`);
  onLine(`  relays: ${relays.join(' · ')}`);
  onLine(`  mode: ${act ? 'ACTING — it may write files and run commands' : 'read-only'}`);
  onLine('');
  note(`listener started as ${me.npub} (act=${act})`);

  // A gift wrapper's `created_at` is deliberately fuzzed BACKWARDS by up to two days, so
  // that a relay cannot correlate a wrapper with its seal by the clock. That makes the
  // wrapper's timestamp useless as a freshness filter: a `since` of "five minutes ago"
  // drops messages sent five seconds ago. So the relay filter is deliberately wide, and
  // freshness is judged on the RUMOR's timestamp after unwrapping — the one value in the
  // envelope that is not fuzzed.
  const FUZZ_WINDOW = 172800;                       // NIP-59's two days
  const since = Math.floor(Date.now() / 1000) - FUZZ_WINDOW - 600;
  const maxAgeSec = 900;                            // act on the last fifteen minutes only
  const inFlight = new Set();

  const stop = subscribe({ kinds: [1059], '#p': [me.pub], since }, async (wrap) => {
    if (seen.has(wrap.id) || inFlight.has(wrap.id)) return;
    inFlight.add(wrap.id);
    try {
      let msg;
      try { msg = unwrapDirectMessage(wrap, me.sk); }
      catch (e) { onLine(note(`rejected a wrapper: ${e.message}`)); return; }

      if (!allow.has(msg.from)) {
        onLine(note(`ignored a message from ${npubEncode(msg.from)} — not on the allow-list`));
        return;
      }
      seen.add(wrap.id);
      // A relay replays history on connect. Without this, restarting the listener would
      // re-execute yesterday's instructions.
      const age = Math.floor(Date.now() / 1000) - (msg.at || 0);
      if (age > maxAgeSec) {
        onLine(note(`skipped a replayed message (${Math.round(age / 60)} minutes old)`));
        return;
      }
      const task = String(msg.text || '').trim();
      if (!task) return;
      onLine(note(`task from ${npubEncode(msg.from).slice(0, 16)}…: ${task.slice(0, 120)}`));

      const res = await run(task, {
        ...runOptions,
        cfg,
        act,
        // No terminal is attached, so anything the gate would have asked about is denied
        // rather than left hanging.
        autoNo: true,
        approve: act ? 'auto' : 'never',
        onEvent: () => {},
      });

      const reply = res.error
        ? `fabius could not run that: ${res.error}`
        : `${res.output}\n\n— reviewed ${res.verdict?.score ?? '—'}/100 · $${res.cost.toFixed(4)}${res.changed?.length ? ` · changed ${res.changed.join(', ')}` : ''}`;

      // Nostr events are not chunk-aware; keep a reply inside what relays reliably accept.
      for (const part of chunk(reply, 60000)) {
        const ev = wrapDirectMessage(part, me.sk, msg.from);
        const sent = await publish(ev, relays);
        if (!sent.ok) onLine(note('reply was not accepted by any relay'));
      }
      onLine(note(`replied (${reply.length} chars, reviewed ${res.verdict?.score ?? '—'})`));
    } catch (e) {
      onLine(note(`listener error: ${String(e.message).slice(0, 200)}`));
    } finally {
      inFlight.delete(wrap.id);
    }
  }, relays);

  return { stop, identity: me };
}

export function chunk(text, size) {
  const s = String(text || '');
  if (s.length <= size) return [s];
  const out = [];
  for (let i = 0; i < s.length; i += size) out.push(s.slice(i, i + size));
  return out;
}

export async function send(text, toNpub, { relays = DEFAULT_RELAYS } = {}) {
  const me = identity();
  const to = toHexKey(toNpub, 'npub');
  const ev = wrapDirectMessage(text, me.sk, to);
  return publish(ev, relays);
}
