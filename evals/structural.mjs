#!/usr/bin/env node
// fabius structural tests — the invariants that hold with NO model, NO key, NO network.
//
// Where eval.mjs / harness.workflow.js measure whether the *stance* improves output,
// this file proves the *system* is well-formed: one router + one always-on core + ten
// single-owner specialists, every lean contract under budget (progressive disclosure),
// every reference resolvable, and the content-bound provenance seal intact. These are
// pass/fail facts, not judge opinions — they reproduce byte-for-byte on any clone.
//
//   node evals/structural.mjs            # run, print the report, exit non-zero on any FAIL
//   node evals/structural.mjs --json     # also write evals/structural.json
//
import { readFileSync, writeFileSync, existsSync, readdirSync } from "node:fs";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import { dirname, join, basename } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const sha256 = (b) => createHash("sha256").update(b).digest();
const sha256hex = (b) => createHash("sha256").update(b).digest("hex");

const checks = [];
const ok = (name, pass, detail) => checks.push({ name, pass: !!pass, detail });

// ---- load every skill contract --------------------------------------------------
const skillDir = join(ROOT, "skills");
const skillNames = readdirSync(skillDir).filter((d) => existsSync(join(skillDir, d, "SKILL.md")));
const skills = skillNames.map((d) => {
  const path = join(skillDir, d, "SKILL.md");
  const raw = readFileSync(path, "utf8");
  const fm = raw.match(/^---\n([\s\S]*?)\n---/);
  const name = (fm?.[1].match(/^name:\s*(.+)$/m)?.[1] || "").trim();
  const hasDesc = /^description:\s*>/m.test(fm?.[1] || "");
  return { dir: d, path, raw, bytes: Buffer.byteLength(raw), name, hasDesc };
});

// ---- 1. shape: 12 skills, one router, one always-on core, names unique ----------
ok("count: exactly twelve skill contracts", skills.length === 12, `${skills.length} found`);
ok("naming: every skill is fabius-prefixed", skills.every((s) => s.name === "fabius" || s.name.startsWith("fabius-")),
   skills.map((s) => s.name).join(", "));
ok("naming: frontmatter name matches its directory", skills.every((s) => s.name === s.dir),
   skills.filter((s) => s.name !== s.dir).map((s) => `${s.dir}≠${s.name}`).join(", ") || "all match");
const uniq = new Set(skills.map((s) => s.name));
ok("single-owner: no duplicate skill name", uniq.size === skills.length, `${uniq.size} unique`);
ok("router present: fabius", skills.some((s) => s.name === "fabius"));
ok("always-on core present: fabius-parcus", skills.some((s) => s.name === "fabius-parcus"));
ok("frontmatter: every contract declares name + description", skills.every((s) => s.name && s.hasDesc));

// ---- 2. progressive disclosure: every lean contract under budget -----------------
const BUDGET = 12000; // bytes; depth lives in references/, not in SKILL.md
const over = skills.filter((s) => s.bytes > BUDGET);
const maxBytes = Math.max(...skills.map((s) => s.bytes));
ok(`progressive disclosure: every SKILL.md ≤ ${BUDGET}B`, over.length === 0,
   `max ${maxBytes}B (${skills.find((s) => s.bytes === maxBytes).name}); ${over.length} over budget`);

// ---- 3. provenance fingerprint embedded in every contract -----------------------
const FP = "provenance fab1-";
const marked = skills.filter((s) => s.raw.includes(FP));
ok("provenance: fab1- fingerprint in every contract", marked.length === skills.length,
   `${marked.length}/${skills.length} marked`);

// ---- 4. reference integrity: every linked references/*.md resolves on disk -------
// resolve the FULL markdown link target relative to the skill dir, so cross-skill
// links (../fabius/references/routing-policy.md) and local ones both check correctly.
let refTotal = 0, refMissing = [];
for (const s of skills) {
  const links = [...s.raw.matchAll(/\]\(([^)`]*references\/[a-z0-9-]+\.md)\)/g)].map((m) => m[1].replace(/^`|`$/g, ""));
  for (const link of new Set(links)) {
    refTotal++;
    if (!existsSync(join(skillDir, s.dir, link))) refMissing.push(`${s.dir} → ${link}`);
  }
}
ok("reference integrity: every linked references/*.md exists", refMissing.length === 0,
   `${refTotal - refMissing.length}/${refTotal} resolve` + (refMissing.length ? ` — missing: ${refMissing.join(", ")}` : ""));

// ---- 5. plugin manifest == filesystem (no phantom / dropped skills) --------------
const plugin = JSON.parse(readFileSync(join(ROOT, ".claude-plugin", "plugin.json"), "utf8"));
const declared = (plugin.skills || []).map((p) => basename(p)).sort();
const onDisk = skills.map((s) => s.name).sort();
ok("manifest: plugin.json skill list == skills on disk",
   JSON.stringify(declared) === JSON.stringify(onDisk),
   declared.length === onDisk.length ? `${declared.length} skills, sets equal` : `declared ${declared.length} vs disk ${onDisk.length}`);
ok("manifest: version is 1.0.0", plugin.version === "1.0.0", plugin.version);

// ---- 6. content-bound seal: file hashes + Merkle root recompute & match ----------
const manifest = JSON.parse(readFileSync(join(ROOT, "provenance", "seal-manifest.json"), "utf8"));
let hashMismatch = [];
for (const [p, want] of Object.entries(manifest.files)) {
  const got = existsSync(join(ROOT, p)) ? sha256hex(readFileSync(join(ROOT, p))) : "MISSING";
  if (got !== want) hashMismatch.push(p);
}
ok(`seal: all ${manifest.count} sealed files hash-match the manifest`, hashMismatch.length === 0,
   `${Object.keys(manifest.files).length - hashMismatch.length}/${Object.keys(manifest.files).length} match` +
   (hashMismatch.length ? ` — drift: ${hashMismatch.join(", ")}` : ""));

// recompute the binary Merkle root exactly as provenance/seal-skills.sh does
let leaves = Object.entries(manifest.files)
  .map(([p, h]) => sha256(Buffer.from(p + "\x00" + h, "utf8")))
  .sort(Buffer.compare);
let level = leaves;
while (level.length > 1) {
  const nxt = [];
  for (let i = 0; i < level.length; i += 2) {
    const a = level[i], b = i + 1 < level.length ? level[i + 1] : level[i];
    nxt.push(sha256(Buffer.concat([a, b])));
  }
  level = nxt;
}
const root = level[0].toString("hex");
ok("seal: recomputed Merkle root matches the manifest", root === manifest.merkle_root,
   root === manifest.merkle_root ? root.slice(0, 16) + "…" : `got ${root.slice(0, 16)}… want ${manifest.merkle_root.slice(0, 16)}…`);

// ---- 7. count coherence: canonical docs say "twelve"/"ten", no stale counts ------
for (const [file, must] of [["README.md", "twelve"], ["ARCHITECTURE.md", "twelve"], ["AGENTS.md", "twelve"]]) {
  const t = readFileSync(join(ROOT, file), "utf8").toLowerCase();
  ok(`coherence: ${file} states "${must}" skills`, t.includes(must), t.includes(must) ? "present" : "missing");
}

// ---- report ----------------------------------------------------------------------
const passed = checks.filter((c) => c.pass).length;
console.log("== fabius structural tests ==\n");
for (const c of checks) console.log(`  ${c.pass ? "PASS" : "FAIL"}  ${c.name}${c.detail ? `  — ${c.detail}` : ""}`);
console.log(`\n  ${passed}/${checks.length} passed`);

if (process.argv.includes("--json")) {
  writeFileSync(join(ROOT, "evals", "structural.json"),
    JSON.stringify({ passed, total: checks.length, checks }, null, 2) + "\n");
  console.log("  wrote evals/structural.json");
}
process.exit(passed === checks.length ? 0 : 1);
