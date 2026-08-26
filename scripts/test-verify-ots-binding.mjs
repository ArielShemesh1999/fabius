#!/usr/bin/env node
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { verifyOtsBinding } from "./verify-ots-binding.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const MAGIC = Buffer.from("004f70656e54696d657374616d7073000050726f6f6600bf89e2e884e89294", "hex");
const record = Buffer.from("deterministic Fabius OTS binding test\n");
const digest = createHash("sha256").update(record).digest();
const unknownAttestation = Buffer.concat([
  Buffer.from([0x00]),
  Buffer.from("0102030405060708", "hex"),
  Buffer.from([0x00]),
]);
const valid = Buffer.concat([MAGIC, Buffer.from([0x01, 0x08]), digest, unknownAttestation]);

let passed = 0;
let failed = 0;
const check = (label, fn, expected = "") => {
  try {
    fn();
    if (expected) throw new Error(`expected failure containing: ${expected}`);
    console.log(`  PASS  ${label}`);
    passed += 1;
  } catch (error) {
    if (expected && String(error.message).includes(expected)) {
      console.log(`  PASS  ${label}`);
      passed += 1;
    } else {
      console.log(`  FAIL  ${label} — ${error.message}`);
      failed += 1;
    }
  }
};

console.log("== OpenTimestamps binding parser tests ==");
check("minimal structurally valid SHA-256 proof binds the exact record", () => verifyOtsBinding(record, valid));
check("the repository proof is structurally valid and digest-bound", () => verifyOtsBinding(
  readFileSync(join(ROOT, "provenance/sealed-commit.txt")),
  readFileSync(join(ROOT, "provenance/sealed-commit.txt.ots")),
));
check("arbitrary bytes are rejected", () => verifyOtsBinding(record, Buffer.from("not an ots proof")), "truncated proof");
check("correct magic and digest followed by garbage is rejected", () => verifyOtsBinding(
  record,
  Buffer.concat([MAGIC, Buffer.from([0x01, 0x08]), digest, Buffer.from([0x99])]),
), "unknown OpenTimestamps operation tag");
check("a proof for different record bytes is rejected", () => verifyOtsBinding(Buffer.from("different\n"), valid), "detached digest mismatch");
check("a truncated proof is rejected", () => verifyOtsBinding(record, valid.subarray(0, valid.length - 1)), "truncated proof");
check("an overlong varuint is rejected", () => verifyOtsBinding(
  record,
  Buffer.concat([MAGIC, Buffer.from([0x81, 0x00, 0x08]), digest, unknownAttestation]),
), "non-canonical varuint");
check("an unknown timestamp operation is rejected", () => verifyOtsBinding(
  record,
  Buffer.concat([MAGIC, Buffer.from([0x01, 0x08]), digest, Buffer.from([0x7f])]),
), "unknown OpenTimestamps operation tag");
check("trailing bytes after a complete proof are rejected", () => verifyOtsBinding(
  record,
  Buffer.concat([valid, Buffer.from([0x00])]),
), "trailing garbage");

console.log(`\n== ${passed} passed · ${failed} failed ==`);
process.exitCode = failed ? 1 : 0;
