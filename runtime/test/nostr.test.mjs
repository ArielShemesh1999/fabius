// Hand-rolled cryptography is only worth trusting against the specification's own
// vectors, so that is what this file is: the official BIP-340 signature vectors and the
// official NIP-44 v2 vectors, run against our implementation. Nothing here touches the
// network.
//
// Vectors are fetched once into the scratch directory by tools/fetch-vectors.sh. When
// they are absent the suite SKIPS rather than silently passing — a crypto test that
// quietly does nothing is worse than no test.
import { test, skip } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  schnorrSign, getPublicKey, conversationKey, messageKeys, calcPaddedLen,
  nip44Encrypt, nip44Decrypt, eventId, finalizeEvent, wrapDirectMessage, unwrapDirectMessage,
  bech32Encode, bech32Decode, npubEncode, toHexKey, generateSecretKey, hex, unhex, publish,
  MAX_NIP44_PAYLOAD_CHARS,
} from '../src/nostr.mjs';
import { chunk, messageFreshness, messageReplayKey, createSerialWorkQueue } from '../src/channel.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const VECTORS = process.env.FABIUS_VECTORS || join(HERE, 'vectors');

test('BIP-340: every official signing vector reproduces byte for byte', (t) => {
  const path = join(VECTORS, 'bip340.csv');
  if (!existsSync(path)) return t.skip(`no vectors at ${path} — run tools/fetch-vectors.sh`);
  const rows = readFileSync(path, 'utf8').trim().split('\n').slice(1).map((l) => l.split(','));
  let checked = 0;
  for (const [index, sk, pk, aux, msg, sig, , comment] of rows) {
    if (!sk) continue;                       // verification-only vectors carry no secret key
    if (unhex(msg).length !== 32) continue;  // variable-length message vectors are out of scope
    assert.equal(hex(getPublicKey(sk)).toUpperCase(), pk.toUpperCase(), `vector ${index} pubkey`);
    assert.equal(hex(schnorrSign(msg, sk, unhex(aux))).toUpperCase(), sig.toUpperCase(),
      `vector ${index} signature ${comment || ''}`);
    checked++;
  }
  assert.ok(checked >= 4, `expected several signing vectors, ran ${checked}`);
});

test('BIP-340: a signature is deterministic in the aux and fresh without it', () => {
  const sk = generateSecretKey();
  const msg = unhex('11'.repeat(32));
  const aux = unhex('22'.repeat(32));
  assert.equal(hex(schnorrSign(msg, sk, aux)), hex(schnorrSign(msg, sk, aux)));
  assert.notEqual(hex(schnorrSign(msg, sk)), hex(schnorrSign(msg, sk)));
});

const nip44 = (() => {
  const p = join(VECTORS, 'nip44.json');
  return existsSync(p) ? JSON.parse(readFileSync(p, 'utf8')).v2 : null;
})();

test('NIP-44: conversation keys match the official vectors', (t) => {
  if (!nip44) return t.skip('no NIP-44 vectors — run tools/fetch-vectors.sh');
  for (const v of nip44.valid.get_conversation_key) {
    assert.equal(hex(conversationKey(v.sec1, v.pub2)), v.conversation_key);
  }
});

test('NIP-44: message keys match the official vectors', (t) => {
  if (!nip44) return t.skip('no NIP-44 vectors');
  const set = nip44.valid.get_message_keys;
  const conv = set.conversation_key;
  for (const v of set.keys) {
    const k = messageKeys(unhex(conv), v.nonce);
    assert.equal(hex(k.chachaKey), v.chacha_key);
    assert.equal(hex(k.chachaNonce), v.chacha_nonce);
    assert.equal(hex(k.hmacKey), v.hmac_key);
  }
});

test('NIP-44: the padding schedule matches the official vectors', (t) => {
  if (!nip44) return t.skip('no NIP-44 vectors');
  for (const [len, padded] of nip44.valid.calc_padded_len) {
    assert.equal(calcPaddedLen(len), padded, `length ${len}`);
  }
});

test('NIP-44: encryption reproduces the official payloads exactly', (t) => {
  if (!nip44) return t.skip('no NIP-44 vectors');
  let checked = 0;
  for (const v of nip44.valid.encrypt_decrypt) {
    const conv = conversationKey(v.sec1, hex(getPublicKey(v.sec2)));
    assert.equal(hex(conv), v.conversation_key, 'conversation key');
    assert.equal(nip44Encrypt(v.plaintext, conv, unhex(v.nonce)), v.payload, 'ciphertext');
    assert.equal(nip44Decrypt(v.payload, conv), v.plaintext, 'roundtrip');
    checked++;
  }
  assert.ok(checked > 0);
});

test('NIP-44: a tampered payload is rejected, not silently decrypted', (t) => {
  if (!nip44) return t.skip('no NIP-44 vectors');
  const v = nip44.valid.encrypt_decrypt[0];
  const conv = conversationKey(v.sec1, hex(getPublicKey(v.sec2)));
  const raw = Buffer.from(v.payload, 'base64');
  raw[raw.length - 1] ^= 0x01;                       // flip one MAC bit
  assert.throws(() => nip44Decrypt(raw.toString('base64'), conv), /MAC mismatch/);
  const body = Buffer.from(v.payload, 'base64');
  body[40] ^= 0x01;                                  // flip one ciphertext bit
  assert.throws(() => nip44Decrypt(body.toString('base64'), conv), /MAC mismatch/);
});

test('NIP-44: the invalid vectors are all refused', (t) => {
  if (!nip44?.invalid) return t.skip('no NIP-44 vectors');
  for (const v of nip44.invalid.decrypt || []) {
    assert.throws(() => nip44Decrypt(v.payload, unhex(v.conversation_key)), undefined, v.note || 'should throw');
  }
});

test('NIP-44 rejects an oversized relay payload before base64 allocation', () => {
  const oversized = 'A'.repeat(MAX_NIP44_PAYLOAD_CHARS + 4);
  assert.throws(() => nip44Decrypt(oversized, Buffer.alloc(32)), /too large/);
});

test('an event id is the hash of the canonical serialisation', () => {
  const ev = { pubkey: 'a'.repeat(64), created_at: 1700000000, kind: 1, tags: [['p', 'b'.repeat(64)]], content: 'hello "world"\nsecond line' };
  const id = eventId(ev);
  assert.match(id, /^[0-9a-f]{64}$/);
  assert.equal(id, eventId({ ...ev }));
  assert.notEqual(id, eventId({ ...ev, content: ev.content + ' ' }));
});

test('a finalized event carries a well-formed id and signature', () => {
  const sk = generateSecretKey();
  const ev = finalizeEvent({ kind: 1, content: 'from fabius' }, sk);
  assert.equal(ev.pubkey, hex(getPublicKey(sk)));
  assert.equal(ev.id, eventId(ev));
  assert.match(ev.sig, /^[0-9a-f]{128}$/);
});

test('a gift-wrapped message survives the round trip and hides the sender', () => {
  const alice = generateSecretKey(), bob = generateSecretKey();
  const bobPub = hex(getPublicKey(bob));
  const alicePub = hex(getPublicKey(alice));
  const wrap = wrapDirectMessage('recon areta.co.il', alice, bobPub);

  assert.equal(wrap.kind, 1059);
  assert.notEqual(wrap.pubkey, alicePub, 'the wrapper must be an ephemeral key, never the sender');
  assert.deepEqual(wrap.tags, [['p', bobPub]]);
  assert.doesNotMatch(JSON.stringify(wrap), /recon areta/, 'the plaintext must not appear anywhere in the wrapper');

  const got = unwrapDirectMessage(wrap, bob);
  assert.equal(got.text, 'recon areta.co.il');
  assert.equal(got.from, alicePub);
});

test('a third party cannot open the wrapper', () => {
  const alice = generateSecretKey(), bob = generateSecretKey(), eve = generateSecretKey();
  const wrap = wrapDirectMessage('secret', alice, hex(getPublicKey(bob)));
  assert.throws(() => unwrapDirectMessage(wrap, eve));
});

test('a forged rumor author is caught', () => {
  const alice = generateSecretKey(), bob = generateSecretKey(), mallory = generateSecretKey();
  const bobPub = hex(getPublicKey(bob));
  // Mallory seals a rumor that claims Alice wrote it.
  const { conversationKey: ck, nip44Encrypt: enc, finalizeEvent: fin, eventId: eid } = { conversationKey, nip44Encrypt, finalizeEvent, eventId };
  const rumor = { pubkey: hex(getPublicKey(alice)), created_at: 1, kind: 14, tags: [['p', bobPub]], content: 'transfer the money' };
  rumor.id = eid(rumor);
  const seal = fin({ kind: 13, tags: [], content: enc(JSON.stringify(rumor), ck(mallory, bobPub)) }, mallory);
  const eph = generateSecretKey();
  const wrap = fin({ kind: 1059, tags: [['p', bobPub]], content: enc(JSON.stringify(seal), ck(eph, bobPub)) }, eph);
  assert.throws(() => unwrapDirectMessage(wrap, bob), /forged/);
});

test('an authenticated rumor id must match its decrypted content', () => {
  const alice = generateSecretKey(), bob = generateSecretKey();
  const bobPub = hex(getPublicKey(bob));
  const rumor = {
    pubkey: hex(getPublicKey(alice)), created_at: Math.floor(Date.now() / 1000),
    kind: 14, tags: [['p', bobPub]], content: 'same authenticated task', id: '0'.repeat(64),
  };
  const seal = finalizeEvent({ kind: 13, tags: [],
    content: nip44Encrypt(JSON.stringify(rumor), conversationKey(alice, bobPub)) }, alice);
  const eph = generateSecretKey();
  const wrap = finalizeEvent({ kind: 1059, tags: [['p', bobPub]],
    content: nip44Encrypt(JSON.stringify(seal), conversationKey(eph, bobPub)) }, eph);
  assert.throws(() => unwrapDirectMessage(wrap, bob), /rumor id/);
});

test('replay identity comes from the authenticated rumor, not mutable wrapper metadata', () => {
  const alice = generateSecretKey(), bob = generateSecretKey();
  const wrap = wrapDirectMessage('run once', alice, hex(getPublicKey(bob)));
  const a = unwrapDirectMessage(wrap, bob);
  const b = unwrapDirectMessage({ ...wrap, id: 'f'.repeat(64), sig: '0'.repeat(128) }, bob);
  assert.equal(messageReplayKey(a), messageReplayKey(b));
  assert.equal(a.id, b.id);
});

test('bech32 round-trips and rejects a corrupted checksum', () => {
  const sk = generateSecretKey();
  const pub = hex(getPublicKey(sk));
  const npub = npubEncode(pub);
  assert.match(npub, /^npub1[a-z0-9]+$/);
  assert.equal(hex(bech32Decode(npub).bytes), pub);
  assert.equal(toHexKey(npub, 'npub'), pub);
  assert.equal(toHexKey(pub), pub);
  const broken = npub.slice(0, -1) + (npub.endsWith('q') ? 'p' : 'q');
  assert.throws(() => bech32Decode(broken), /checksum/);
  assert.throws(() => toHexKey(npub, 'nsec'), /expected nsec/);
  const mixed = npub.slice(0, 5).toUpperCase() + npub.slice(5);
  assert.throws(() => bech32Decode(mixed), /mixed-case/);
});

test('bech32 matches the reference checksum on the BIP-173 vectors', () => {
  // Independent vectors, so this proves the checksum polynomial rather than merely that
  // our encoder and decoder agree with each other.
  for (const valid of ['A12UEL5L', 'a12uel5l', 'abcdef1qpzry9x8gf2tvdw0s3jn54khce6mua7lmqqqxw',
                       'split1checkupstagehandshakeupstreamerranterredcaperred2y9e3w']) {
    assert.ok(bech32Decode(valid), valid);
  }
  for (const bad of ['A12UEL5X', 'pzry9x0s0muk', '1pzry9x0s0muk', 'x1b4n0q5v', 'li1dgmt3']) {
    assert.throws(() => bech32Decode(bad), undefined, `${bad} must be rejected`);
  }
  // 20 bytes in → the canonical BIP-173 string back out.
  const { bytes } = bech32Decode('abcdef1qpzry9x8gf2tvdw0s3jn54khce6mua7lmqqqxw');
  assert.equal(bech32Encode('abcdef', bytes), 'abcdef1qpzry9x8gf2tvdw0s3jn54khce6mua7lmqqqxw');
});

test('DM chunking is byte-bounded and never splits a Unicode code point', () => {
  const source = 'שלום🙂עולם🙂'.repeat(20);
  const parts = chunk(source, 17);
  assert.equal(parts.join(''), source);
  assert.ok(parts.length > 1);
  for (const part of parts) {
    assert.ok(Buffer.byteLength(part) <= 17);
    assert.doesNotMatch(part, /[\uD800-\uDBFF]$|^[\uDC00-\uDFFF]/);
  }
});

test('channel freshness rejects stale and future-dated authenticated rumors', () => {
  const nowSec = 2_000_000_000;
  assert.equal(messageFreshness(nowSec - 30, { nowSec }).ok, true);
  assert.equal(messageFreshness(nowSec - 901, { nowSec }).ok, false);
  assert.equal(messageFreshness(nowSec + 301, { nowSec }).ok, false);
});

test('channel work is serial and refuses an unbounded pending flood', async () => {
  const queue = createSerialWorkQueue(2);
  let releaseFirst;
  const blocker = new Promise((resolve) => { releaseFirst = resolve; });
  const order = [];
  const first = queue.submit(async () => { order.push('first:start'); await blocker; order.push('first:end'); });
  const second = queue.submit(async () => { order.push('second'); });
  assert.equal(queue.submit(async () => { order.push('overflow'); }), null);
  await new Promise((resolve) => setImmediate(resolve));
  assert.deepEqual(order, ['first:start']);
  releaseFirst();
  await Promise.all([first, second]);
  assert.deepEqual(order, ['first:start', 'first:end', 'second']);
  assert.equal(queue.pending, 0);
});

test('relay publish closes every socket after first success and after timeout', async () => {
  const original = globalThis.WebSocket;
  const sockets = [];
  class FakeWebSocket {
    constructor(url) { this.url = url; this.closed = 0; sockets.push(this); queueMicrotask(() => this.onopen?.()); }
    send(payload) {
      const msg = JSON.parse(payload);
      if (this.url.endsWith('/ok') && msg[0] === 'EVENT') {
        queueMicrotask(() => this.onmessage?.({ data: JSON.stringify(['OK', msg[1].id, true, 'accepted']) }));
      }
    }
    close() { this.closed++; queueMicrotask(() => this.onclose?.()); }
  }
  globalThis.WebSocket = FakeWebSocket;
  try {
    const event = { id: 'a'.repeat(64) };
    const success = await publish(event, ['wss://relay.test/ok', 'wss://relay.test/pending'], { timeoutMs: 100 });
    assert.equal(success.ok, true);
    assert.ok(sockets.slice(0, 2).every((ws) => ws.closed > 0));

    const start = sockets.length;
    const timeout = await publish(event, ['wss://relay.test/one', 'wss://relay.test/two'], { timeoutMs: 10 });
    assert.equal(timeout.ok, false);
    assert.ok(sockets.slice(start).every((ws) => ws.closed > 0));
  } finally { globalThis.WebSocket = original; }
});
