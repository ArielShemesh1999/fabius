// A CHANNEL WITH NO SERVER.
//
// A bot hosted by a messaging platform can be taken away by that platform; a bridge into a
// closed network needs a host and carries a ban risk — an account suspension, a banned
// number, a VPS that stops paying for itself.
//
// This channel is the option with no owner: a keypair is the identity, public relays are
// interchangeable and disposable, there is no account to suspend and no phone number to
// ban. Messages are end-to-end encrypted and metadata-wrapped, so a
// relay sees only that *someone* sent *something* to an ephemeral key.
//
// WHAT IS IMPLEMENTED, EXACTLY
//   BIP-340 Schnorr signing        — verified against the official BIP-340 vectors
//   NIP-44 v2 encryption           — verified against the official NIP-44 vectors
//   NIP-01 event id + relay socket — publish, subscribe, EOSE
//   NIP-17/59 sealed + gift-wrapped direct messages
//   NIP-19 npub/nsec              — so you can paste the identifiers people actually use
//
// WHAT IS NOT
//   No signature VERIFICATION of inbound events (that needs point addition, which this
//   module deliberately does not carry). Inbound authenticity rests on two other things
//   instead, and they are strong ones: NIP-44 is authenticated encryption, so a seal that
//   decrypts under conversation_key(our key, the seal's author) proves its author held
//   that private key; and the rumor's author must equal the seal's author, which is what
//   blocks the classic impersonation. On top of that, only an allow-listed key may
//   command the agent at all.
//
// Scalar multiplication is borrowed from node's ECDH rather than hand-rolled: deriving
// k·G is exactly what `setPrivateKey().getPublicKey()` does, which keeps the only
// bespoke arithmetic here to scalars modulo the curve order.

import { createHash, createHmac, createECDH, createCipheriv, createDecipheriv, randomBytes } from 'node:crypto';

// ── secp256k1 constants ─────────────────────────────────────────────────────────
const N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141n;

const hex = (b) => Buffer.from(b).toString('hex');
// Accepts a hex string OR raw bytes. Coercing bytes through String() would silently
// reinterpret them as UTF-8 and produce a different key — so the byte path comes first.
const unhex = (h) => {
  if (Buffer.isBuffer(h)) return h;
  if (h instanceof Uint8Array) return Buffer.from(h);
  const s = String(h).replace(/^0x/, '');
  if (!/^[0-9a-fA-F]*$/.test(s) || s.length % 2) throw new Error('expected hex or bytes');
  return Buffer.from(s, 'hex');
};
const sha256 = (b) => createHash('sha256').update(b).digest();
const be32 = (n) => { const b = Buffer.alloc(32); let x = n; for (let i = 31; i >= 0; i--) { b[i] = Number(x & 0xffn); x >>= 8n; } return b; };
const toBig = (b) => BigInt('0x' + hex(b));
const mod = (a, m) => ((a % m) + m) % m;

// SHA256(SHA256(tag) ‖ SHA256(tag) ‖ msg) — the BIP-340 domain separator.
const tagCache = new Map();
function taggedHash(tag, ...parts) {
  let t = tagCache.get(tag);
  if (!t) { t = sha256(Buffer.from(tag, 'utf8')); tagCache.set(tag, t); }
  // `.map(Buffer.from)` would hand the array index to Buffer.from as a byte offset.
  return sha256(Buffer.concat([t, t, ...parts.map((p) => Buffer.from(p))]));
}

// k·G, via node's own curve implementation. Returns { x (32B), odd (bool) }.
function pointFromScalar(scalar32) {
  const ecdh = createECDH('secp256k1');
  ecdh.setPrivateKey(Buffer.from(scalar32));
  const p = ecdh.getPublicKey(null, 'uncompressed');   // 0x04 ‖ X ‖ Y
  return { x: p.subarray(1, 33), odd: (p[64] & 1) === 1 };
}

export function getPublicKey(secretKey) {
  return pointFromScalar(unhex(secretKey)).x;
}

export function generateSecretKey() {
  for (;;) {
    const k = randomBytes(32);
    const d = toBig(k);
    if (d > 0n && d < N) return k;
  }
}

// ── BIP-340 Schnorr signature ───────────────────────────────────────────────────
export function schnorrSign(message32, secretKey, auxRand = randomBytes(32)) {
  const m = unhex(message32), sk = unhex(secretKey);
  if (m.length !== 32) throw new Error('BIP-340 signs a 32-byte message');
  const d0 = toBig(sk);
  if (d0 <= 0n || d0 >= N) throw new Error('secret key out of range');
  const P = pointFromScalar(sk);
  const d = P.odd ? N - d0 : d0;                                  // force even-y

  const t = Buffer.alloc(32);
  const aux = taggedHash('BIP0340/aux', auxRand);
  const dBytes = be32(d);
  for (let i = 0; i < 32; i++) t[i] = dBytes[i] ^ aux[i];

  const rand = taggedHash('BIP0340/nonce', t, P.x, m);
  const k0 = mod(toBig(rand), N);
  if (k0 === 0n) throw new Error('nonce is zero — retry with fresh aux');
  const R = pointFromScalar(be32(k0));
  const k = R.odd ? N - k0 : k0;                                  // force even-y

  const e = mod(toBig(taggedHash('BIP0340/challenge', R.x, P.x, m)), N);
  return Buffer.concat([R.x, be32(mod(k + e * d, N))]);
}

// ── NIP-44 v2 ───────────────────────────────────────────────────────────────────
// conversation_key = hkdf_extract(IKM = ECDH x-coordinate, salt = "nip44-v2")
export function conversationKey(secretKey, peerPubkeyXOnly) {
  const ecdh = createECDH('secp256k1');
  ecdh.setPrivateKey(unhex(secretKey));
  // Nostr publishes x-only keys; NIP-44 reads them as the even-y point.
  const shared = ecdh.computeSecret(Buffer.concat([Buffer.from([0x02]), unhex(peerPubkeyXOnly)]));
  return createHmac('sha256', Buffer.from('nip44-v2', 'utf8')).update(shared).digest();
}

// hkdf_expand, isolated: node's hkdfSync always extracts first, and here the PRK is
// already the conversation key.
function hkdfExpand(prk, info, length) {
  const out = [];
  let t = Buffer.alloc(0);
  for (let i = 1; out.reduce((n, b) => n + b.length, 0) < length; i++) {
    t = createHmac('sha256', prk).update(Buffer.concat([t, info, Buffer.from([i])])).digest();
    out.push(t);
  }
  return Buffer.concat(out).subarray(0, length);
}

export function messageKeys(convKey, nonce32) {
  const k = hkdfExpand(convKey, unhex(nonce32), 76);
  return { chachaKey: k.subarray(0, 32), chachaNonce: k.subarray(32, 44), hmacKey: k.subarray(44, 76) };
}

// Padding hides the length of short messages: everything under 32 bytes looks identical,
// and longer messages round up to a power-of-two-derived chunk.
export function calcPaddedLen(len) {
  if (len <= 32) return 32;
  const nextPower = 1 << (Math.floor(Math.log2(len - 1)) + 1);
  const chunk = nextPower <= 256 ? 32 : nextPower / 8;
  return chunk * (Math.floor((len - 1) / chunk) + 1);
}

export const MAX_NIP44_PLAINTEXT_BYTES = 65535;
export const MAX_NIP44_PAYLOAD_BYTES = 1 + 32 + 2 + calcPaddedLen(MAX_NIP44_PLAINTEXT_BYTES) + 32;
export const MAX_NIP44_PAYLOAD_CHARS = Math.ceil(MAX_NIP44_PAYLOAD_BYTES / 3) * 4;

function pad(plaintext) {
  const b = Buffer.from(plaintext, 'utf8');
  if (b.length < 1 || b.length > MAX_NIP44_PLAINTEXT_BYTES) throw new Error('NIP-44 plaintext must be 1..65535 bytes');
  const prefix = Buffer.alloc(2);
  prefix.writeUInt16BE(b.length);
  return Buffer.concat([prefix, b, Buffer.alloc(calcPaddedLen(b.length) - b.length)]);
}
function unpad(padded) {
  const len = padded.readUInt16BE(0);
  const text = padded.subarray(2, 2 + len);
  if (len < 1 || text.length !== len || padded.length !== 2 + calcPaddedLen(len)) throw new Error('invalid padding');
  return text.toString('utf8');
}

// ChaCha20 as a raw stream cipher: node takes a 16-byte IV = 4-byte LE counter ‖ nonce.
const chacha = (fn, key, nonce12, data) => {
  const iv = Buffer.concat([Buffer.alloc(4), nonce12]);
  const c = fn('chacha20', key, iv);
  return Buffer.concat([c.update(data), c.final()]);
};

export function nip44Encrypt(plaintext, convKey, nonce = randomBytes(32)) {
  const { chachaKey, chachaNonce, hmacKey } = messageKeys(convKey, nonce);
  const ciphertext = chacha(createCipheriv, chachaKey, chachaNonce, pad(plaintext));
  const mac = createHmac('sha256', hmacKey).update(Buffer.concat([nonce, ciphertext])).digest();
  return Buffer.concat([Buffer.from([2]), nonce, ciphertext, mac]).toString('base64');
}

export function nip44Decrypt(payload, convKey) {
  if (typeof payload !== 'string' || payload.startsWith('#')) throw new Error('unsupported NIP-44 version');
  // Buffer.from(base64) allocates from the encoded length. A relay controls this string,
  // so enforce the protocol's maximum before decoding rather than after an attacker has
  // already bought the allocation. NIP-44 plaintext tops out at 65,535 bytes.
  if (payload.length > MAX_NIP44_PAYLOAD_CHARS) throw new Error('NIP-44 payload is too large');
  if (payload.length % 4 !== 0 || !/^[A-Za-z0-9+/]*={0,2}$/.test(payload)) throw new Error('malformed NIP-44 base64');
  const raw = Buffer.from(payload, 'base64');
  if (raw.length > MAX_NIP44_PAYLOAD_BYTES) throw new Error('NIP-44 payload is too large');
  if (raw.length < 99 || raw[0] !== 2) throw new Error('malformed NIP-44 payload');
  const nonce = raw.subarray(1, 33);
  const ciphertext = raw.subarray(33, raw.length - 32);
  const mac = raw.subarray(raw.length - 32);
  const { chachaKey, chachaNonce, hmacKey } = messageKeys(convKey, nonce);
  const want = createHmac('sha256', hmacKey).update(Buffer.concat([nonce, ciphertext])).digest();
  // Constant-time compare: a MAC oracle is exactly the bug this whole layer exists to avoid.
  if (want.length !== mac.length || !timingSafeEqualBuf(want, mac)) throw new Error('MAC mismatch — the message is not authentic');
  return unpad(chacha(createDecipheriv, chachaKey, chachaNonce, ciphertext));
}

function timingSafeEqualBuf(a, b) {
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a[i] ^ b[i];
  return diff === 0;
}

// ── NIP-01 events ───────────────────────────────────────────────────────────────
export function eventId(ev) {
  const serial = JSON.stringify([0, ev.pubkey, ev.created_at, ev.kind, ev.tags, ev.content]);
  return hex(sha256(Buffer.from(serial, 'utf8')));
}

export function finalizeEvent(draft, secretKey) {
  const ev = {
    pubkey: hex(getPublicKey(secretKey)),
    created_at: draft.created_at ?? Math.floor(Date.now() / 1000),
    kind: draft.kind,
    tags: draft.tags || [],
    content: draft.content || '',
  };
  ev.id = eventId(ev);
  ev.sig = hex(schnorrSign(unhex(ev.id), secretKey));
  return ev;
}

// ── NIP-19 bech32 (npub / nsec) ─────────────────────────────────────────────────
const CHARSET = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l';
const polymod = (values) => {
  const GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3];
  let chk = 1;
  for (const v of values) {
    const b = chk >> 25;
    chk = ((chk & 0x1ffffff) << 5) ^ v;
    for (let i = 0; i < 5; i++) if ((b >> i) & 1) chk ^= GEN[i];
  }
  return chk;
};
const hrpExpand = (hrp) => [...[...hrp].map((c) => c.charCodeAt(0) >> 5), 0, ...[...hrp].map((c) => c.charCodeAt(0) & 31)];
function convertBits(data, from, to, padding) {
  let acc = 0, bits = 0;
  const out = [], maxv = (1 << to) - 1;
  for (const value of data) {
    acc = (acc << from) | value;
    bits += from;
    while (bits >= to) { bits -= to; out.push((acc >> bits) & maxv); }
  }
  if (padding) { if (bits) out.push((acc << (to - bits)) & maxv); }
  else if (bits >= from || ((acc << (to - bits)) & maxv)) throw new Error('bad bech32 padding');
  return out;
}
export function bech32Encode(hrp, dataBytes) {
  const data = convertBits([...Buffer.from(dataBytes)], 8, 5, true);
  const values = [...hrpExpand(hrp), ...data];
  const chk = polymod([...values, 0, 0, 0, 0, 0, 0]) ^ 1;
  const checksum = [];
  for (let i = 0; i < 6; i++) checksum.push((chk >> (5 * (5 - i))) & 31);
  return hrp + '1' + [...data, ...checksum].map((d) => CHARSET[d]).join('');
}
export function bech32Decode(str) {
  const raw = String(str);
  if (raw !== raw.toLowerCase() && raw !== raw.toUpperCase()) throw new Error('mixed-case bech32 string');
  const s = raw.toLowerCase();
  const pos = s.lastIndexOf('1');
  if (pos < 1 || pos + 7 > s.length) throw new Error('not a bech32 string');
  const hrp = s.slice(0, pos);
  const data = [...s.slice(pos + 1)].map((c) => {
    const i = CHARSET.indexOf(c);
    if (i < 0) throw new Error(`invalid bech32 character "${c}"`);
    return i;
  });
  if (polymod([...hrpExpand(hrp), ...data]) !== 1) throw new Error('bech32 checksum failed');
  return { hrp, bytes: Buffer.from(convertBits(data.slice(0, -6), 5, 8, false)) };
}
export const npubEncode = (pubkeyHex) => bech32Encode('npub', unhex(pubkeyHex));
export const nsecEncode = (secretHex) => bech32Encode('nsec', unhex(secretHex));
// Accepts hex or bech32 and returns hex — the owner should never have to care which.
export function toHexKey(input, expect) {
  const s = String(input || '').trim();
  if (/^[0-9a-f]{64}$/i.test(s)) return s.toLowerCase();
  const { hrp, bytes } = bech32Decode(s);
  if (expect && hrp !== expect) throw new Error(`expected ${expect}…, got ${hrp}…`);
  return hex(bytes);
}

// ── NIP-17 / NIP-59 sealed, gift-wrapped direct messages ────────────────────────
// Timestamps are fuzzed backwards by up to two days so a relay cannot correlate a seal
// and its wrapper by the clock.
const fuzzedNow = () => Math.floor(Date.now() / 1000) - Math.floor(Math.random() * 172800);

export function wrapDirectMessage(text, senderSecretKey, recipientPubkey) {
  const senderPub = hex(getPublicKey(senderSecretKey));
  // The rumor is deliberately UNSIGNED: an unsigned event cannot be replayed by a relay
  // as proof that you said anything.
  const rumor = {
    pubkey: senderPub,
    created_at: Math.floor(Date.now() / 1000),
    kind: 14,
    tags: [['p', recipientPubkey]],
    content: text,
  };
  rumor.id = eventId(rumor);

  const seal = finalizeEvent({
    kind: 13,
    created_at: fuzzedNow(),
    tags: [],
    content: nip44Encrypt(JSON.stringify(rumor), conversationKey(senderSecretKey, recipientPubkey)),
  }, senderSecretKey);

  const ephemeral = generateSecretKey();
  return finalizeEvent({
    kind: 1059,
    created_at: fuzzedNow(),
    tags: [['p', recipientPubkey]],
    content: nip44Encrypt(JSON.stringify(seal), conversationKey(ephemeral, recipientPubkey)),
  }, ephemeral);
}

export function unwrapDirectMessage(giftWrap, recipientSecretKey) {
  const seal = JSON.parse(nip44Decrypt(giftWrap.content, conversationKey(recipientSecretKey, giftWrap.pubkey)));
  if (seal.kind !== 13) throw new Error(`expected a seal (kind 13), got kind ${seal.kind}`);
  const rumor = JSON.parse(nip44Decrypt(seal.content, conversationKey(recipientSecretKey, seal.pubkey)));
  // THE impersonation check. Without it, anyone could seal a rumor claiming any author.
  if (rumor.pubkey !== seal.pubkey) throw new Error('rumor author does not match the seal author — forged');
  if (rumor.kind !== 14) throw new Error(`expected a chat rumor (kind 14), got kind ${rumor.kind}`);
  if (!/^[0-9a-f]{64}$/.test(String(rumor.pubkey || ''))) throw new Error('rumor author is malformed');
  if (!Number.isSafeInteger(rumor.created_at)) throw new Error('rumor timestamp is malformed');
  // The outer wrapper id is not authenticated here and relays may present the same
  // authenticated rumor under modified wrapper metadata. Bind replay identity to the
  // decrypted rumor bytes, and reject a sender-supplied id that does not name them.
  if (!/^[0-9a-f]{64}$/.test(String(rumor.id || '')) || rumor.id !== eventId(rumor)) {
    throw new Error('rumor id does not match its authenticated content');
  }
  return { from: rumor.pubkey, text: rumor.content, at: rumor.created_at, id: rumor.id };
}

// ── relays ──────────────────────────────────────────────────────────────────────
export const DEFAULT_RELAYS = ['wss://relay.damus.io', 'wss://nos.lol', 'wss://relay.primal.net'];

// Publish to several relays and resolve as soon as ONE accepts. Relays are interchangeable
// and individually unreliable; treating any single one as required would recreate exactly
// the dependency this channel exists to remove.
export function publish(event, relays = DEFAULT_RELAYS, { timeoutMs = 10000 } = {}) {
  return new Promise((resolve) => {
    const results = [];
    const sockets = new Set();
    let settled = false;
    let timer;
    const done = () => {
      if (settled) return;
      settled = true; clearTimeout(timer);
      for (const ws of sockets) { try { ws.close(); } catch { /* already closing */ } }
      resolve({ ok: results.some((r) => r.ok), results });
    };
    timer = setTimeout(done, timeoutMs);
    let open = relays.length;
    for (const url of relays) {
      let ws;
      try { ws = new WebSocket(url); } catch (e) { results.push({ url, ok: false, error: e.message }); if (--open === 0) { clearTimeout(timer); done(); } continue; }
      sockets.add(ws);
      let finished = false;
      const finish = (r) => {
        if (finished || settled) return;
        finished = true;
        results.push({ url, ...r });
        try { ws.close(); } catch { /* already closing */ }
        if (r.ok) done();
        else if (--open === 0) done();
      };
      ws.onopen = () => {
        try { ws.send(JSON.stringify(['EVENT', event])); }
        catch (e) { finish({ ok: false, error: `send failed: ${e.message}` }); }
      };
      ws.onmessage = (m) => {
        try {
          const msg = JSON.parse(m.data);
          if (msg[0] === 'OK' && msg[1] === event.id) finish({ ok: !!msg[2], reason: msg[3] || '' });
        } catch { /* a relay may send noise */ }
      };
      ws.onerror = () => finish({ ok: false, error: 'socket error' });
      ws.onclose = () => finish({ ok: false, error: 'socket closed before acknowledgement' });
    }
    if (!relays.length) done();
  });
}

// Subscribe across relays, de-duplicating by event id. Returns a stop() handle.
export function subscribe(filter, onEvent, relays = DEFAULT_RELAYS) {
  const seen = new Set();
  const sockets = [];
  const subId = 'fab' + randomBytes(4).toString('hex');
  for (const url of relays) {
    let ws;
    try { ws = new WebSocket(url); } catch { continue; }
    sockets.push(ws);
    ws.onopen = () => ws.send(JSON.stringify(['REQ', subId, filter]));
    ws.onmessage = (m) => {
      try {
        const msg = JSON.parse(m.data);
        if (msg[0] === 'EVENT' && msg[1] === subId) {
          const ev = msg[2];
          if (!seen.has(ev.id)) {
            seen.add(ev.id);
            if (seen.size > 5000) seen.delete(seen.values().next().value);
            onEvent(ev, url);
          }
        }
      } catch { /* ignore malformed relay traffic */ }
    };
    ws.onerror = () => { /* one relay dropping is normal */ };
  }
  return () => { for (const ws of sockets) { try { ws.send(JSON.stringify(['CLOSE', subId])); ws.close(); } catch { /* already gone */ } } };
}

export { hex, unhex };
