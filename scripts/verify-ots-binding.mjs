#!/usr/bin/env node
// Dependency-free parser for the OpenTimestamps detached-proof envelope used
// by Fabius. This proves that the committed .ots bytes are structurally valid
// and embed the SHA-256 of the exact sealed record. It deliberately does not
// claim that any calendar or blockchain attestation is trusted.

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const MAGIC = Buffer.from("004f70656e54696d657374616d7073000050726f6f6600bf89e2e884e89294", "hex");
const MAX_PROOF_BYTES = 1024 * 1024;
const MAX_MESSAGE_BYTES = 4096;
const MAX_ATTESTATION_BYTES = 8192;
const MAX_OPERATION_DEPTH = 256;
const PENDING_TAG = "83dfe30d2ef90c8e";
const BLOCK_HEIGHT_TAGS = new Set([
  "0588960d73d71901", // Bitcoin
  "06869a0d73d71b45", // Litecoin
  "30fe8087b5c7ead7", // Ethereum (legacy/dubious OTS namespace)
]);
const PENDING_URI_BYTES = new Set(Buffer.from("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._/:", "ascii"));

class Reader {
  constructor(bytes, label = "proof") {
    this.bytes = bytes;
    this.offset = 0;
    this.label = label;
  }

  remaining() { return this.bytes.length - this.offset; }

  readByte(context) {
    if (this.offset >= this.bytes.length) throw new Error(`truncated ${this.label} while reading ${context}`);
    return this.bytes[this.offset++];
  }

  readBytes(length, context) {
    if (!Number.isSafeInteger(length) || length < 0 || this.remaining() < length) {
      throw new Error(`truncated ${this.label} while reading ${context}`);
    }
    const value = this.bytes.subarray(this.offset, this.offset + length);
    this.offset += length;
    return value;
  }

  readVaruint(context) {
    let value = 0n;
    let shift = 0n;
    let count = 0;
    let last = 0;
    while (true) {
      const byte = this.readByte(context);
      count += 1;
      if (count > 10) throw new Error(`oversized varuint in ${context}`);
      last = byte & 0x7f;
      value |= BigInt(last) << shift;
      if ((byte & 0x80) === 0) break;
      shift += 7n;
    }
    if (count > 1 && last === 0) throw new Error(`non-canonical varuint in ${context}`);
    if (value > BigInt(Number.MAX_SAFE_INTEGER)) throw new Error(`varuint exceeds safe range in ${context}`);
    return Number(value);
  }

  readVarbytes(max, min, context) {
    const length = this.readVaruint(`${context} length`);
    if (length < min || length > max) throw new Error(`${context} length ${length} is outside ${min}..${max}`);
    return this.readBytes(length, context);
  }

  assertEof(context = this.label) {
    if (this.remaining() !== 0) throw new Error(`trailing garbage after ${context}`);
  }
}

function parseKnownAttestation(tag, payload) {
  if (tag === PENDING_TAG) {
    const reader = new Reader(payload, "pending attestation payload");
    const uri = reader.readVarbytes(1000, 0, "pending URI");
    reader.assertEof("pending attestation payload");
    for (const byte of uri) {
      if (!PENDING_URI_BYTES.has(byte)) throw new Error("pending attestation URI contains a forbidden byte");
    }
    new TextDecoder("utf-8", { fatal: true }).decode(uri);
  } else if (BLOCK_HEIGHT_TAGS.has(tag)) {
    const reader = new Reader(payload, "block attestation payload");
    reader.readVaruint("block height");
    reader.assertEof("block attestation payload");
  }
}

function parseOperation(reader, tag, messageLength, depth) {
  let resultLength;
  if (tag === 0xf0 || tag === 0xf1) {
    const argument = reader.readVarbytes(MAX_MESSAGE_BYTES, 1, tag === 0xf0 ? "append argument" : "prepend argument");
    resultLength = messageLength + argument.length;
  } else if (tag === 0xf2) {
    if (messageLength === 0) throw new Error("reverse operation cannot consume an empty message");
    resultLength = messageLength;
  } else if (tag === 0xf3) {
    if (messageLength === 0 || messageLength > MAX_MESSAGE_BYTES / 2) {
      throw new Error("hexlify operation message is outside its allowed size");
    }
    resultLength = messageLength * 2;
  } else if (tag === 0x02 || tag === 0x03) {
    resultLength = 20;
  } else if (tag === 0x08 || tag === 0x67) {
    resultLength = 32;
  } else {
    throw new Error(`unknown OpenTimestamps operation tag 0x${tag.toString(16).padStart(2, "0")}`);
  }
  if (messageLength > MAX_MESSAGE_BYTES || resultLength < 1 || resultLength > MAX_MESSAGE_BYTES) {
    throw new Error("OpenTimestamps operation exceeds the 4096-byte message bound");
  }
  parseTimestamp(reader, resultLength, depth + 1);
}

function parseBranch(reader, tag, messageLength, depth) {
  if (tag === 0x00) {
    const attestationTag = reader.readBytes(8, "attestation tag").toString("hex");
    const payload = reader.readVarbytes(MAX_ATTESTATION_BYTES, 0, "attestation payload");
    parseKnownAttestation(attestationTag, payload);
  } else {
    parseOperation(reader, tag, messageLength, depth);
  }
}

function parseTimestamp(reader, messageLength, depth) {
  if (depth >= MAX_OPERATION_DEPTH) throw new Error("OpenTimestamps operation tree exceeds depth 256");
  let tag = reader.readByte("timestamp branch");
  while (tag === 0xff) {
    parseBranch(reader, reader.readByte("forked timestamp branch"), messageLength, depth);
    tag = reader.readByte("timestamp branch");
  }
  parseBranch(reader, tag, messageLength, depth);
}

export function verifyOtsBinding(recordBytes, proofBytes) {
  if (!Buffer.isBuffer(recordBytes)) recordBytes = Buffer.from(recordBytes);
  if (!Buffer.isBuffer(proofBytes)) proofBytes = Buffer.from(proofBytes);
  if (proofBytes.length > MAX_PROOF_BYTES) throw new Error(`proof exceeds ${MAX_PROOF_BYTES} bytes`);

  const reader = new Reader(proofBytes);
  const magic = reader.readBytes(MAGIC.length, "detached-proof magic");
  if (!magic.equals(MAGIC)) throw new Error("invalid OpenTimestamps detached-proof magic");
  const version = reader.readVaruint("detached-proof major version");
  if (version !== 1) throw new Error(`unsupported OpenTimestamps detached-proof major version ${version}`);
  const fileHashOperation = reader.readByte("detached file-hash operation");
  if (fileHashOperation !== 0x08) throw new Error("Fabius detached proof must use SHA-256 (operation 0x08)");
  const embeddedDigest = reader.readBytes(32, "detached file digest").toString("hex");
  const actualDigest = createHash("sha256").update(recordBytes).digest("hex");
  if (embeddedDigest !== actualDigest) {
    throw new Error(`detached digest mismatch: proof ${embeddedDigest}, record ${actualDigest}`);
  }
  parseTimestamp(reader, 32, 0);
  reader.assertEof("OpenTimestamps timestamp tree");
  return { digest: actualDigest, proofBytes: proofBytes.length, majorVersion: version };
}

function main() {
  const [recordArg = "provenance/sealed-commit.txt", proofArg = "provenance/sealed-commit.txt.ots"] = process.argv.slice(2);
  const recordPath = resolve(recordArg);
  const proofPath = resolve(proofArg);
  try {
    const result = verifyOtsBinding(readFileSync(recordPath), readFileSync(proofPath));
    console.log(`PASS OpenTimestamps structure and detached SHA-256 binding — ${result.digest}`);
  } catch (error) {
    console.error(`FAIL OpenTimestamps detached proof — ${error.message}`);
    process.exitCode = 1;
  }
}

if (import.meta.url === pathToFileURL(process.argv[1] || "").href) main();
