#!/usr/bin/env node
// fabius structural tests — the invariants that hold with NO model, NO key, NO network.
//
// Where eval.mjs / harness.workflow.js measure whether the *stance* improves output,
// this file proves the *system* is well-formed: one router + one always-on core + thirteen
// single-owner specialists, every lean contract under budget (progressive disclosure), every
// flattened description under the discovery budget, every reference resolvable (markdown links
// AND backtick-quoted mentions), no sealed-set drift (manifest file list == on-disk set), and
// the content-bound provenance seal intact. These are pass/fail facts, not judge opinions —
// they reproduce byte-for-byte on any clone.
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
// flatten a YAML frontmatter scalar (block scalar or inline) to a single-line string
const flattenKey = (fmText, key) => {
  const lines = (fmText || "").split("\n");
  const i = lines.findIndex((l) => new RegExp(`^${key}:`).test(l));
  if (i === -1) return "";
  const first = lines[i].replace(new RegExp(`^${key}:\\s*`), "");
  const parts = [];
  if (first && !/^[|>][-+]?\s*$/.test(first)) parts.push(first); // inline value, not a block indicator
  for (let j = i + 1; j < lines.length; j++) {
    if (/^\S/.test(lines[j])) break; // next top-level key ends the block
    parts.push(lines[j].trim());
  }
  return parts.join(" ").replace(/\s+/g, " ").trim();
};
const flattenDescription = (fmText) => flattenKey(fmText, "description");

const skills = skillNames.map((d) => {
  const path = join(skillDir, d, "SKILL.md");
  const raw = readFileSync(path, "utf8");
  const fm = raw.match(/^---\n([\s\S]*?)\n---/);
  const name = (fm?.[1].match(/^name:\s*(.+)$/m)?.[1] || "").trim();
  const hasDesc = /^description:\s*>/m.test(fm?.[1] || "");
  const descFlat = flattenDescription(fm?.[1] || "");
  return { dir: d, path, raw, fm: fm?.[1] || "", bytes: Buffer.byteLength(raw), name, hasDesc, descFlat };
});

// ---- 1. shape: 15 skills, one router, one always-on core, names unique ----------
ok("count: exactly fifteen skill contracts", skills.length === 15, `${skills.length} found`);
ok("naming: every skill is fabius-prefixed", skills.every((s) => s.name === "fabius" || s.name.startsWith("fabius-")),
   skills.map((s) => s.name).join(", "));
ok("naming: frontmatter name matches its directory", skills.every((s) => s.name === s.dir),
   skills.filter((s) => s.name !== s.dir).map((s) => `${s.dir}≠${s.name}`).join(", ") || "all match");
const uniq = new Set(skills.map((s) => s.name));
ok("single-owner: no duplicate skill name", uniq.size === skills.length, `${uniq.size} unique`);
ok("router present: fabius", skills.some((s) => s.name === "fabius"));
ok("always-on core present: fabius-parcus", skills.some((s) => s.name === "fabius-parcus"));
ok("frontmatter: every contract declares name + description", skills.every((s) => s.name && s.hasDesc));

// every description, flattened to a single line, fits the discovery budget.
// Measured in BYTES, not JS string length: these contracts are read by several harnesses and a
// budget enforced downstream is a byte budget, while `—` and `·` cost 3 and 2 bytes each. Counting
// code units passes a description that a byte-counting reader truncates or rejects — decor's sat
// at 1013 "chars" and 1028 bytes. Bytes is the conservative unit, so bytes is the gate.
const DESC_BUDGET = 1024;
const descLen = (s) => Buffer.byteLength(s.descFlat, "utf8");
const descOver = skills.filter((s) => descLen(s) > DESC_BUDGET);
const maxDesc = Math.max(...skills.map(descLen));
ok(`frontmatter: every flattened description ≤ ${DESC_BUDGET} bytes`, descOver.length === 0,
   `max ${maxDesc} bytes (${skills.find((s) => descLen(s) === maxDesc).name}); ${descOver.length} over`);

// every top-level frontmatter key is canonical. Repo policy is snake_case `when_to_use` —
// Claude Code documents it and grok-build reads it as its documented fallback alias; the
// kebab-case `when-to-use` is an explicit FAIL. Other legal Claude keys (allowed-tools,
// model, …) are deliberately banned — adding one later is an intentional whitelist edit.
const CANONICAL_KEYS = new Set(["name", "description", "when_to_use", "license", "metadata"]);
const topKeys = (fmText) => (fmText || "").split("\n")
  .filter((l) => /^[A-Za-z0-9_-]+:/.test(l)).map((l) => l.match(/^([A-Za-z0-9_-]+):/)[1]);
const keyViolations = [];
for (const s of skills) {
  for (const k of topKeys(s.fm)) {
    if (k === "when-to-use") keyViolations.push(`${s.dir} → when-to-use (kebab-case; policy is when_to_use)`);
    else if (!CANONICAL_KEYS.has(k)) keyViolations.push(`${s.dir} → ${k}`);
  }
}
ok("frontmatter: keys canonical (name · description · when_to_use · license · metadata)",
   keyViolations.length === 0, keyViolations.length ? `banned: ${keyViolations.join(", ")}` : "all canonical");

// description + optional when_to_use share one combined discovery budget, both flattened
const COMBINED_BUDGET = 1536;
const combLen = (s) => Buffer.byteLength(s.descFlat + flattenKey(s.fm, "when_to_use"), "utf8");
const combOver = skills.filter((s) => combLen(s) > COMBINED_BUDGET);
const maxComb = Math.max(...skills.map(combLen));
ok(`frontmatter: description + when_to_use ≤ ${COMBINED_BUDGET} bytes flattened`, combOver.length === 0,
   `max ${maxComb} bytes (${skills.find((s) => combLen(s) === maxComb).name}); ${combOver.length} over`);

// license, when a contract declares one, must match the plugin manifest's license
const pluginLicense = JSON.parse(readFileSync(join(ROOT, ".claude-plugin", "plugin.json"), "utf8")).license;
const licenseOf = (fmText) => (fmText.match(/^license:\s*(.+)$/m)?.[1] || "").trim().replace(/^["']|["']$/g, "");
const licDeclared = skills.filter((s) => /^license:/m.test(s.fm));
const licMismatch = licDeclared.filter((s) => licenseOf(s.fm) !== pluginLicense);
ok("frontmatter: license matches plugin.json license (when declared)", licMismatch.length === 0,
   licMismatch.length ? `mismatch: ${licMismatch.map((s) => `${s.dir} → ${licenseOf(s.fm)}`).join(", ")}`
                      : `plugin license ${pluginLicense}; ${licDeclared.length}/${skills.length} declare it`);

// metadata, when a contract declares one, must carry a non-empty author
const metaAuthor = (fmText) => {
  const lines = (fmText || "").split("\n");
  const i = lines.findIndex((l) => /^metadata:/.test(l));
  if (i === -1) return null; // no metadata key — check passes vacuously
  for (let j = i + 1; j < lines.length; j++) {
    if (/^\S/.test(lines[j])) break; // next top-level key ends the block
    const m = lines[j].match(/^\s+author:\s*(.*)$/);
    if (m) return m[1].trim().replace(/^["']|["']$/g, "");
  }
  return ""; // metadata present, author missing
};
const metaDeclared = skills.filter((s) => metaAuthor(s.fm) !== null);
const metaBad = metaDeclared.filter((s) => !metaAuthor(s.fm));
ok("frontmatter: metadata carries non-empty author (when present)", metaBad.length === 0,
   metaBad.length ? `missing author: ${metaBad.map((s) => s.dir).join(", ")}`
                  : `${metaDeclared.length}/${skills.length} declare metadata`);

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

// ---- 4. reference integrity: every referenced references/ path resolves on disk --
// Two sources, both checked:
//   (a) markdown links — resolve the FULL link target relative to the skill dir, so
//       cross-skill links (../fabius/references/routing-policy.md) and local ones work.
//   (b) backtick-quoted mentions — inline `references/<path>` (files or dirs). The
//       lookbehind keeps us from re-capturing the tail of a longer ../…/references/ path
//       already covered by (a). Glob/wildcard paths are skipped (they name a set, not a file).
const hasGlob = (p) => /[*?[\]]/.test(p);
let refTotal = 0, refMissing = [];
for (const s of skills) {
  const links = [...s.raw.matchAll(/\]\(([^)`]*references\/[a-z0-9-]+\.md)\)/g)].map((m) => m[1].replace(/^`|`$/g, ""));
  const backticks = [...s.raw.matchAll(/`([^`]+)`/g)].map((m) => m[1]).filter((t) => t.includes("references/"))
    .flatMap((t) => t.match(/(?<![\w/.-])references\/[A-Za-z0-9._/-]+/g) || []);
  for (const link of new Set([...links, ...backticks])) {
    if (hasGlob(link)) continue;
    refTotal++;
    if (!existsSync(join(skillDir, s.dir, link))) refMissing.push(`${s.dir} → ${link}`);
  }
}
ok("reference integrity: every linked + backtick-quoted references/ path exists", refMissing.length === 0,
   `${refTotal - refMissing.length}/${refTotal} resolve` + (refMissing.length ? ` — missing: ${refMissing.join(", ")}` : ""));

// ---- 5. plugin manifest == filesystem (no phantom / dropped skills) --------------
const plugin = JSON.parse(readFileSync(join(ROOT, ".claude-plugin", "plugin.json"), "utf8"));
const declared = (plugin.skills || []).map((p) => basename(p)).sort();
const onDisk = skills.map((s) => s.name).sort();
ok("manifest: plugin.json skill list == skills on disk",
   JSON.stringify(declared) === JSON.stringify(onDisk),
   declared.length === onDisk.length ? `${declared.length} skills, sets equal` : `declared ${declared.length} vs disk ${onDisk.length}`);
ok("manifest: version is 2.4.0", plugin.version === "2.4.0", plugin.version);

// ---- 6. content-bound seal: file hashes + Merkle root recompute & match ----------
const manifest = JSON.parse(readFileSync(join(ROOT, "provenance", "seal-manifest.json"), "utf8"));

// no sealed-set drift: the manifest's file LIST must equal exactly the on-disk sealed set
// (every skills/*/SKILL.md + the three canonical docs). Hashes are checked separately below;
// this asserts membership only, so it stays green while the seal is re-computed out of band.
const sealedExpected = [...skills.map((s) => `skills/${s.dir}/SKILL.md`), "ARCHITECTURE.md", "CORPUS.md", "AGENTS.md"].sort();
const sealedActual = Object.keys(manifest.files).sort();
ok("seal: manifest file list == skills on disk + ARCHITECTURE/CORPUS/AGENTS",
   JSON.stringify(sealedActual) === JSON.stringify(sealedExpected),
   JSON.stringify(sealedActual) === JSON.stringify(sealedExpected)
     ? `${sealedActual.length} files, sets equal`
     : `manifest ${sealedActual.length} vs expected ${sealedExpected.length}` +
       (() => {
         const extra = sealedActual.filter((p) => !sealedExpected.includes(p));
         const missing = sealedExpected.filter((p) => !sealedActual.includes(p));
         return (extra.length ? ` — extra: ${extra.join(", ")}` : "") + (missing.length ? ` — missing: ${missing.join(", ")}` : "");
       })());

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

// ---- 7. count coherence: canonical docs all state the layer count, no stale counts ------
for (const [file, must] of [["README.md", "fifteen"], ["ARCHITECTURE.md", "fifteen"], ["AGENTS.md", "fifteen"]]) {
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
