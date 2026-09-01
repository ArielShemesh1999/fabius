#!/usr/bin/env node
// Verify the upstream registry (credits/upstream.json) against the working tree.
// Every registered upstream has a valid shape and an allowlisted license; every
// declared path exists; bundled trees carry LICENSE (+ NOTICE for Apache-2.0);
// informed-by references end with exactly one attribution paragraph and are never
// a SKILL.md; every informed-by upstream has a by-layer row in credits/README.md.
// Offline and deterministic by default. `--remote` adds one git ls-remote NOTE per
// pinned entry whose upstream HEAD has moved — a note, never a failure.

import { existsSync, readFileSync, statSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = process.env.FABIUS_VERIFY_ROOT
  ? resolve(process.env.FABIUS_VERIFY_ROOT)
  : join(dirname(fileURLToPath(import.meta.url)), "..");
const REGISTRY = "credits/upstream.json";
const CREDITS = "credits/README.md";
const SCHEMA = "fabius-upstream/v1";
const LICENSES = new Set(["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "CC0-1.0", "CC-BY-4.0", "Unlicense", "MPL-2.0"]);
const CONSUMED = new Set(["informed-by", "bundled"]);
const FIELDS = ["id", "repo", "owner", "license", "consumed_as", "fabius_layer", "fabius_paths",
  "pinned_commit", "pinned_version", "pinned_at", "notice_required", "sync", "notes"];
const REPO = /^https:\/\/github\.com\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)$/;
// Exactly one such paragraph per reference: "Informed by **<project>** (<owner>, <license>) … See credits/README.md."
const FOOTER = /^Informed by \*\*[^*]+\*\* \(.+?\).*See credits\/README\.md\.$/gm;
const BY_LAYER = "## Inspired / adapted from";
const remote = process.argv.includes("--remote");

const checks = [];
const check = (name, pass, detail = "") => checks.push({ name, pass: !!pass, detail });
const rule = (name, offenders, ok) => check(name, offenders.length === 0, offenders.length ? offenders.join("; ") : ok);
const isText = (v) => typeof v === "string" && v.trim().length > 0;
const isDate = (v) => typeof v === "string" && /^\d{4}-\d{2}-\d{2}$/.test(v) && !Number.isNaN(Date.parse(v));
const isSha = (v) => typeof v === "string" && /^[0-9a-f]{40}$/.test(v);
const abs = (p) => join(ROOT, p);
const exists = (p) => existsSync(abs(p));
const isDir = (p) => exists(p) && statSync(abs(p)).isDirectory();
const isFile = (p) => exists(p) && statSync(abs(p)).isFile();
const label = (entry, i) => (isText(entry?.id) ? entry.id : `entries[${i}]`);
const repoParts = (repo) => {
  const m = typeof repo === "string" ? repo.match(REPO) : null;
  return m && !m[2].endsWith(".git") ? { owner: m[1], name: m[2] } : null;
};

let registry = null;
try {
  registry = JSON.parse(readFileSync(abs(REGISTRY), "utf8"));
  check("registry parses as JSON", true, REGISTRY);
} catch (error) {
  check("registry parses as JSON", false, error.message);
}

let credits = null;
try {
  credits = readFileSync(abs(CREDITS), "utf8");
  check("credits/README.md is readable", true, `${credits.split("\n").length} lines`);
} catch (error) {
  check("credits/README.md is readable", false, error.message);
}

if (registry && typeof registry === "object") {
  check("registry schema id is fabius-upstream/v1", registry.schema === SCHEMA, String(registry.schema));
  check("registry carries an ISO generated date", isDate(registry.generated), String(registry.generated));
  const raw = Array.isArray(registry.entries) ? registry.entries : [];
  check("registry has a non-empty entries array", raw.length > 0, `${raw.length} entries`);
  const entries = raw.filter((e) => e && typeof e === "object" && !Array.isArray(e));
  check("every entry is an object", entries.length === raw.length, `${raw.length - entries.length} non-object`);

  // Shape rules — one line per rule, offenders named by id.
  rule("every entry carries exactly the thirteen schema fields", entries.flatMap((e, i) => {
    const keys = Object.keys(e);
    const missing = FIELDS.filter((f) => !keys.includes(f));
    const unknown = keys.filter((k) => !FIELDS.includes(k));
    return missing.length || unknown.length
      ? [`${label(e, i)}: ${[missing.length && `missing ${missing.join(",")}`, unknown.length && `unknown ${unknown.join(",")}`].filter(Boolean).join(", ")}`]
      : [];
  }), `${entries.length} entries`);
  rule("entry ids are kebab-case", entries.flatMap((e, i) => (/^[a-z0-9]+(-[a-z0-9]+)*$/.test(String(e.id)) ? [] : [label(e, i)])), "all kebab");
  const seen = new Map();
  for (const e of entries) if (isText(e.id)) seen.set(e.id, (seen.get(e.id) || 0) + 1);
  rule("entry ids are unique", [...seen].filter(([, n]) => n > 1).map(([id, n]) => `${id} ×${n}`), `${seen.size} ids`);
  rule("repo is an https GitHub URL", entries.flatMap((e, i) => (repoParts(e.repo) ? [] : [`${label(e, i)}: ${String(e.repo)}`])), "github.com/<owner>/<name>");
  rule("owner is a non-empty string", entries.flatMap((e, i) => (isText(e.owner) ? [] : [label(e, i)])), "all named");
  rule("license is in the SPDX allowlist", entries.flatMap((e, i) => (LICENSES.has(e.license) ? [] : [`${label(e, i)}: ${String(e.license)}`])),
    [...LICENSES].join(" "));
  rule("consumed_as is informed-by or bundled", entries.flatMap((e, i) => (CONSUMED.has(e.consumed_as) ? [] : [`${label(e, i)}: ${String(e.consumed_as)}`])),
    `${entries.filter((e) => e.consumed_as === "informed-by").length} informed-by · ${entries.filter((e) => e.consumed_as === "bundled").length} bundled`);
  rule("fabius_layer names an existing skill", entries.flatMap((e, i) => (isText(e.fabius_layer) && isDir(`skills/${e.fabius_layer}`) ? [] : [`${label(e, i)}: ${String(e.fabius_layer)}`])),
    "all resolve under skills/");
  const pathOk = (e, p) => typeof p === "string" && p.startsWith(`skills/${e.fabius_layer}/`) && !p.endsWith("/")
    && !p.includes("\\") && !p.split("/").includes("..") && !p.split("/").includes("");
  rule("fabius_paths are repo-relative and under the owning skill", entries.flatMap((e, i) => (Array.isArray(e.fabius_paths) && e.fabius_paths.length > 0
    ? e.fabius_paths.filter((p) => !pathOk(e, p)).map((p) => `${label(e, i)}: ${String(p)}`)
    : [`${label(e, i)}: fabius_paths must be a non-empty array`])), "all under skills/<fabius_layer>/");
  const paths = (e) => (Array.isArray(e.fabius_paths) ? e.fabius_paths.filter((p) => pathOk(e, p)) : []);
  rule("every fabius_paths entry exists on disk", entries.flatMap((e, i) => paths(e).filter((p) => !exists(p)).map((p) => `${label(e, i)}: ${p}`)),
    `${entries.reduce((n, e) => n + paths(e).length, 0)} paths`);
  rule("pinned_commit is null or a full 40-hex SHA", entries.flatMap((e, i) => (e.pinned_commit === null || isSha(e.pinned_commit) ? [] : [`${label(e, i)}: ${String(e.pinned_commit)}`])),
    `${entries.filter((e) => isSha(e.pinned_commit)).length} pinned`);
  rule("pinned_version is null or a non-empty string", entries.flatMap((e, i) => (e.pinned_version === null || isText(e.pinned_version) ? [] : [`${label(e, i)}: ${String(e.pinned_version)}`])),
    "ok");
  rule("pinned_at is an ISO date exactly when pinned_commit is set", entries.flatMap((e, i) => {
    const pinned = isSha(e.pinned_commit);
    return (pinned ? isDate(e.pinned_at) : e.pinned_at === null) ? [] : [`${label(e, i)}: ${String(e.pinned_at)}`];
  }), "pins dated, legacy null");
  rule("notice_required is true exactly for bundled Apache-2.0 entries", entries.flatMap((e, i) => {
    const expected = e.consumed_as === "bundled" && e.license === "Apache-2.0";
    return e.notice_required === expected ? [] : [`${label(e, i)}: ${String(e.notice_required)} (expected ${expected})`];
  }), `${entries.filter((e) => e.notice_required === true).length} require NOTICE`);
  rule("sync is manual", entries.flatMap((e, i) => (e.sync === "manual" ? [] : [`${label(e, i)}: ${String(e.sync)}`])), "nothing auto-fetches");
  rule("notes is one non-empty line", entries.flatMap((e, i) => (isText(e.notes) && !/[\r\n]/.test(e.notes) ? [] : [label(e, i)])), "ok");

  // Bundled trees: the upstream license travels with the files.
  const bundled = entries.filter((e) => e.consumed_as === "bundled");
  const bundledDirs = bundled.flatMap((e, i) => paths(e).filter(isDir).map((p) => ({ e, i, p })));
  rule("bundled paths are directories", bundled.flatMap((e, i) => paths(e).filter((p) => exists(p) && !isDir(p)).map((p) => `${label(e, i)}: ${p}`)),
    `${bundledDirs.length} trees`);
  rule("bundled trees carry LICENSE", bundledDirs.filter(({ p }) => !isFile(`${p}/LICENSE`)).map(({ e, i, p }) => `${label(e, i)}: ${p}`), "LICENSE in every tree");
  rule("bundled Apache-2.0 trees carry NOTICE", bundledDirs.filter(({ e, p }) => e.notice_required === true && !isFile(`${p}/NOTICE`)).map(({ e, i, p }) => `${label(e, i)}: ${p}`),
    `${bundledDirs.filter(({ e }) => e.notice_required === true).length} NOTICE trees`);

  // Informed-by references: own voice, attribution footer, never a SKILL.md.
  const informed = entries.filter((e) => e.consumed_as === "informed-by");
  rule("informed-by paths are markdown references, never a SKILL.md", informed.flatMap((e, i) => paths(e)
    .filter((p) => !p.endsWith(".md") || p.split("/").includes("SKILL.md") || (exists(p) && !isFile(p)))
    .map((p) => `${label(e, i)}: ${p}`)), `${informed.reduce((n, e) => n + paths(e).length, 0)} references`);
  rule("informed-by references end with exactly one attribution paragraph", informed.flatMap((e, i) => paths(e)
    .filter((p) => isFile(p) && p.endsWith(".md"))
    .map((p) => ({ p, n: (readFileSync(abs(p), "utf8").match(FOOTER) || []).length }))
    .filter(({ n }) => n !== 1)
    .map(({ p, n }) => `${label(e, i)}: ${p} (${n} paragraphs)`)), "one Informed-by paragraph each");
  // Only the by-layer table counts as a credits row — never the bundled-tree table or prose.
  const creditLines = (credits || "").split("\n");
  const start = creditLines.findIndex((line) => line.startsWith(BY_LAYER));
  const section = start < 0 ? [] : creditLines.slice(start + 1);
  const end = section.findIndex((line) => line.startsWith("#"));
  const rows = (end < 0 ? section : section.slice(0, end)).filter((line) => line.trimStart().startsWith("|")).map((line) => line.toLowerCase());
  rule("every informed-by upstream has a by-layer row in credits/README.md naming owner/repo and license", informed.flatMap((e, i) => {
    const parts = repoParts(e.repo);
    if (!parts || !credits || start < 0) return [`${label(e, i)}: no row match possible`];
    const token = `${parts.owner}/${parts.name}`.toLowerCase();
    const hit = rows.some((row) => row.includes(token) && row.includes(String(e.license).toLowerCase()));
    return hit ? [] : [`${label(e, i)}: ${token} (${e.license})`];
  }), `${informed.length} rows matched`);

  // Optional, network-only: report drift between pinned commit and upstream HEAD.
  if (remote) {
    for (const e of entries.filter((x) => isSha(x.pinned_commit) && repoParts(x.repo))) {
      const result = spawnSync("git", ["ls-remote", e.repo, "HEAD"], {
        encoding: "utf8", timeout: 30_000, env: { ...process.env, GIT_TERMINAL_PROMPT: "0" },
      });
      const head = (result.stdout || "").match(/^([0-9a-f]{40})\s+HEAD/m)?.[1];
      let note;
      if (!head) note = `ls-remote failed — ${(result.stderr || result.error?.message || "no HEAD line").trim().split("\n")[0]}`;
      else if (head === e.pinned_commit) note = `upstream HEAD matches pinned ${head.slice(0, 7)}`;
      else note = `upstream HEAD ${head.slice(0, 7)} ≠ pinned ${e.pinned_commit.slice(0, 7)} (pinned_at ${e.pinned_at})`;
      checks.push({ name: `${e.id}: ${note}`, pass: true, detail: "", note: true });
    }
  }
}

console.log("== fabius upstream registry ==\n");
for (const c of checks) console.log(`  ${c.note ? "NOTE" : c.pass ? "PASS" : "FAIL"}  ${c.name}${c.detail ? ` — ${c.detail}` : ""}`);
const scored = checks.filter((c) => !c.note);
const failed = scored.filter((c) => !c.pass).length;
console.log(`\n== ${scored.length - failed} passed · ${failed} failed ==`);
process.exitCode = failed ? 1 : 0;
