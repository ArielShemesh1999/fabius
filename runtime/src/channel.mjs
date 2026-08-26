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

import { appendFileSync, existsSync, readFileSync, chmodSync } from 'node:fs';
import { join } from 'node:path';
import { run } from './loop.mjs';
import { loadConfig, saveConfig, HOME, ensureDirs, atomicWriteFile, redact } from './config.mjs';
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
  const stamped = `${new Date().toISOString()} ${redact(String(line))}\n`;
  try {
    appendFileSync(LOG(), stamped, { mode: 0o600 });
    chmodSync(LOG(), 0o600);
  } catch { /* logging must never break the listener */ }
  return stamped.trimEnd();
}

// A message the listener has already handled must never run twice — a relay replays, and
// two relays will hand you the same wrapper.
function seenStore() {
  ensureDirs();
  const path = join(HOME, 'channel-seen.json');
  let ids = [];
  try { ids = JSON.parse(readFileSync(path, 'utf8')); } catch { ids = []; }
  if (!Array.isArray(ids)) ids = [];
  ids = ids.filter((id) => typeof id === 'string' && id.length <= 128).slice(-500);
  if (existsSync(path)) { try { chmodSync(path, 0o600); } catch { /* repaired on next write */ } }
  const set = new Set(ids);
  return {
    has: (id) => set.has(id),
    add(id) {
      set.add(id);
      if (set.size > 500) set.delete(set.values().next().value);
      const trimmed = [...set].slice(-500);
      try { atomicWriteFile(path, JSON.stringify(trimmed)); } catch { /* best effort */ }
    },
  };
}

export const MAX_CHANNEL_PENDING = 8;

// Relay callbacks are concurrent, but runs are not: provider calls and memory compounding
// are serialised in-process so two completed tasks cannot race a read→rewrite of the
// memory index. The pending ceiling makes a relay flood fail closed instead of building
// an unbounded promise/LLM queue in RAM.
export function createSerialWorkQueue(maxPending = MAX_CHANNEL_PENDING) {
  if (!Number.isSafeInteger(maxPending) || maxPending < 1) throw new Error('queue limit must be a positive integer');
  let tail = Promise.resolve();
  let pending = 0;
  return {
    get pending() { return pending; },
    submit(work) {
      if (pending >= maxPending) return null;
      pending++;
      const result = tail.then(() => work());
      const settled = result.finally(() => { pending--; });
      tail = settled.catch(() => {});
      return settled;
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
  const outerInFlight = new Set();
  const messageInFlight = new Set();
  const workQueue = createSerialWorkQueue();
  let lastBusyLog = 0;

  const handleWrap = async (wrap) => {
    let replayId = '';
    try {
      let msg;
      try { msg = unwrapDirectMessage(wrap, me.sk); }
      catch (e) { onLine(note(`rejected a wrapper: ${e.message}`)); return; }

      if (!allow.has(msg.from)) {
        onLine(note(`ignored a message from ${npubEncode(msg.from)} — not on the allow-list`));
        return;
      }
      replayId = messageReplayKey(msg);
      if (seen.has(replayId) || messageInFlight.has(replayId)) return;
      messageInFlight.add(replayId);
      // Persist before execution: a crash after the tool acts must not make the relay's
      // retry execute the same authenticated task again.
      seen.add(replayId);
      // A relay replays history on connect. Without this, restarting the listener would
      // re-execute yesterday's instructions.
      const freshness = messageFreshness(msg.at, { maxAgeSec });
      if (!freshness.ok && freshness.age > maxAgeSec) {
        const age = freshness.age;
        onLine(note(`skipped a replayed message (${Math.round(age / 60)} minutes old)`));
        return;
      }
      if (!freshness.ok) {
        onLine(note(`skipped a message dated ${Math.round(-freshness.age / 60)} minutes in the future`));
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
      for (const part of chunk(reply, MAX_DM_CHUNK_BYTES)) {
        const ev = wrapDirectMessage(part, me.sk, msg.from);
        const sent = await publish(ev, relays);
        if (!sent.ok) onLine(note('reply was not accepted by any relay'));
      }
      onLine(note(`replied (${reply.length} chars, reviewed ${res.verdict?.score ?? '—'})`));
    } catch (e) {
      onLine(note(`listener error: ${String(e.message).slice(0, 200)}`));
    } finally {
      outerInFlight.delete(wrap.id);
      if (replayId) messageInFlight.delete(replayId);
    }
  };

  const stop = subscribe({ kinds: [1059], '#p': [me.pub], since }, (wrap) => {
    if (seen.has(wrap.id) || outerInFlight.has(wrap.id)) return; // includes pre-upgrade wrapper ids
    outerInFlight.add(wrap.id);
    const job = workQueue.submit(() => handleWrap(wrap));
    if (!job) {
      outerInFlight.delete(wrap.id);
      // A flood should not turn the diagnostic log into a second denial-of-service.
      if (Date.now() - lastBusyLog > 5000) {
        lastBusyLog = Date.now();
        onLine(note(`listener at capacity — dropped a relay wrapper (max pending ${MAX_CHANNEL_PENDING})`));
      }
      return;
    }
    job.catch((e) => onLine(note(`listener queue error: ${String(e.message).slice(0, 200)}`)));
  }, relays);

  return { stop, identity: me };
}

export const MAX_DM_CHUNK_BYTES = 30000;

export function messageFreshness(at, {
  nowSec = Math.floor(Date.now() / 1000), maxAgeSec = 900, maxFutureSec = 300,
} = {}) {
  const age = nowSec - at;
  return { ok: Number.isSafeInteger(at) && age <= maxAgeSec && age >= -maxFutureSec, age };
}

export function messageReplayKey(message) {
  const id = String(message?.id || '');
  if (!/^[0-9a-f]{64}$/.test(id)) throw new Error('an authenticated rumor id is required for replay protection');
  return id;
}

export function chunk(text, maxBytes) {
  const s = String(text || '');
  if (!Number.isSafeInteger(maxBytes) || maxBytes < 4) throw new Error('chunk size must be an integer of at least 4 UTF-8 bytes');
  if (Buffer.byteLength(s) <= maxBytes) return [s];
  const out = [];
  let part = '', bytes = 0;
  for (const codePoint of s) {
    const n = Buffer.byteLength(codePoint);
    if (bytes + n > maxBytes) { out.push(part); part = ''; bytes = 0; }
    part += codePoint; bytes += n;
  }
  if (part) out.push(part);
  return out;
}

export async function send(text, toNpub, { relays = DEFAULT_RELAYS } = {}) {
  const me = identity();
  const to = toHexKey(toNpub, 'npub');
  const results = [];
  let ok = true;
  const parts = chunk(text, MAX_DM_CHUNK_BYTES);
  for (const part of parts) {
    const sent = await publish(wrapDirectMessage(part, me.sk, to), relays);
    ok = ok && sent.ok;
    results.push(...sent.results);
  }
  return { ok, results, parts: parts.length };
}
