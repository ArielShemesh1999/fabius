#!/usr/bin/env node
// Deterministic adversarial controls for the upstream registry gate. The real
// registry and credits file are copied into a temporary fixture with minimal
// synthetic targets (placeholder LICENSE/NOTICE files, stub references carrying
// the attribution footer); every mutation happens there. Offline; no network.

import { copyFileSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const VERIFY = join(ROOT, "scripts/verify-upstream.mjs");
const temp = mkdtempSync(join(tmpdir(), "fabius-upstream-"));
const fixture = join(temp, "fixture");
let passed = 0;
let failed = 0;

const check = (label, ok, detail = "") => {
  console.log(`  ${ok ? "PASS" : "FAIL"}  ${label}${detail ? ` — ${detail}` : ""}`);
  if (ok) passed += 1;
  else failed += 1;
};
const write = (rel, text) => {
  mkdirSync(dirname(join(fixture, rel)), { recursive: true });
  writeFileSync(join(fixture, rel), text);
};
const verify = () => spawnSync(process.execPath, [VERIFY], {
  cwd: fixture, env: { ...process.env, FABIUS_VERIFY_ROOT: fixture }, encoding: "utf8", timeout: 30_000,
});
const registryPath = join(fixture, "credits/upstream.json");
const original = readFileSync(join(ROOT, "credits/upstream.json"), "utf8");
const originalCredits = readFileSync(join(ROOT, "credits/README.md"), "utf8");
const registry = JSON.parse(original);
const writeRegistry = (mutate) => {
  const copy = JSON.parse(original);
  mutate(copy);
  writeFileSync(registryPath, `${JSON.stringify(copy, null, 2)}\n`);
};
const restore = () => {
  writeFileSync(registryPath, original);
  writeFileSync(join(fixture, "credits/README.md"), originalCredits);
  seedTargets();
};
const footer = (name) => `Informed by **${name}** (owner, MIT) — studied, re-expressed; no upstream files bundled. See credits/README.md.\n`;
const stub = (name) => `<!-- fixture -->\n# ${name}\n\n${footer(name)}`;
const seedTargets = () => {
  for (const entry of registry.entries) {
    mkdirSync(join(fixture, "skills", entry.fabius_layer), { recursive: true });
    for (const path of entry.fabius_paths) {
      if (entry.consumed_as === "bundled") {
        write(`${path}/LICENSE`, `${entry.license} placeholder\n`);
        if (entry.notice_required) write(`${path}/NOTICE`, "NOTICE placeholder\n");
      } else {
        write(path, stub(entry.id));
      }
    }
  }
};
// Assert that one mutation flips the gate to FAIL on exactly the rule it targets.
const expectFail = (label, ruleName, mutate) => {
  mutate();
  const result = verify();
  check(label, result.status !== 0 && result.stdout.includes(`FAIL  ${ruleName}`), `exit ${result.status}`);
  restore();
};

console.log("== fabius upstream registry adversarial tests ==");
try {
  mkdirSync(join(fixture, "credits"), { recursive: true });
  copyFileSync(join(ROOT, "credits/upstream.json"), registryPath);
  copyFileSync(join(ROOT, "credits/README.md"), join(fixture, "credits/README.md"));
  seedTargets();

  const informed = registry.entries.find((e) => e.consumed_as === "informed-by");
  const apache = registry.entries.find((e) => e.consumed_as === "bundled" && e.notice_required === true);
  const bundled = registry.entries.find((e) => e.consumed_as === "bundled" && e.notice_required === false);
  if (!informed || !apache || !bundled) throw new Error("registry seed must contain an informed-by entry, a bundled Apache-2.0 entry and a bundled non-Apache entry");
  const token = informed.repo.replace("https://github.com/", "").toLowerCase();
  const inByLayer = (lines, fn) => {
    // Apply fn only to `|` rows inside the by-layer table (between its heading and the next heading).
    const start = lines.findIndex((line) => line.startsWith("## Inspired / adapted from"));
    const rest = lines.slice(start + 1);
    const end = rest.findIndex((line) => line.startsWith("#"));
    const stop = end < 0 ? lines.length : start + 1 + end;
    return lines.flatMap((line, i) => (i > start && i < stop && line.trimStart().startsWith("|") ? fn(line) : [line]));
  };
  const at = (predicate) => (copy) => copy.entries.find(predicate);
  const informedIn = at((e) => e.id === informed.id);
  const bundledIn = at((e) => e.id === bundled.id);

  let result = verify();
  check("isolated fixture built from the committed registry passes", result.status === 0, `exit ${result.status}`);

  expectFail("non-allowlisted license is rejected", "license is in the SPDX allowlist",
    () => writeRegistry((c) => { informedIn(c).license = "GPL-3.0-only"; }));
  expectFail("allowlist is case-sensitive SPDX", "license is in the SPDX allowlist",
    () => writeRegistry((c) => { bundledIn(c).license = "mit"; }));
  expectFail("missing fabius path is rejected", "every fabius_paths entry exists on disk",
    () => writeRegistry((c) => { informedIn(c).fabius_paths = [`skills/${informed.fabius_layer}/references/does-not-exist.md`]; }));
  expectFail("path outside the owning skill is rejected", "fabius_paths are repo-relative and under the owning skill",
    () => writeRegistry((c) => { informedIn(c).fabius_paths = ["credits/README.md"]; }));
  expectFail("abbreviated commit is rejected", "pinned_commit is null or a full 40-hex SHA",
    () => writeRegistry((c) => { informedIn(c).pinned_commit = informed.pinned_commit.slice(0, 7); }));
  expectFail("forty non-hex characters are rejected", "pinned_commit is null or a full 40-hex SHA",
    () => writeRegistry((c) => { informedIn(c).pinned_commit = "g".repeat(40); }));
  expectFail("pinned commit without pinned_at is rejected", "pinned_at is an ISO date exactly when pinned_commit is set",
    () => writeRegistry((c) => { informedIn(c).pinned_at = null; }));
  expectFail("duplicate id is rejected", "entry ids are unique",
    () => writeRegistry((c) => { c.entries[1].id = c.entries[0].id; }));
  expectFail("non-https or non-GitHub repo URL is rejected", "repo is an https GitHub URL",
    () => writeRegistry((c) => { informedIn(c).repo = informed.repo.replace("https://", "http://"); }));
  expectFail("repo URL with a .git suffix is rejected", "repo is an https GitHub URL",
    () => writeRegistry((c) => { informedIn(c).repo = `${informed.repo}.git`; }));
  expectFail("unknown field is rejected", "every entry carries exactly the thirteen schema fields",
    () => writeRegistry((c) => { informedIn(c).auto_update = true; }));
  expectFail("missing field is rejected", "every entry carries exactly the thirteen schema fields",
    () => writeRegistry((c) => { delete bundledIn(c).notes; }));
  expectFail("notice_required on an informed-by entry is rejected", "notice_required is true exactly for bundled Apache-2.0 entries",
    () => writeRegistry((c) => { informedIn(c).notice_required = true; }));
  expectFail("bundled Apache-2.0 entry declaring no notice is rejected", "notice_required is true exactly for bundled Apache-2.0 entries",
    () => writeRegistry((c) => { at((e) => e.id === apache.id)(c).notice_required = false; }));
  expectFail("non-manual sync is rejected", "sync is manual",
    () => writeRegistry((c) => { bundledIn(c).sync = "auto"; }));
  expectFail("missing NOTICE in a bundled Apache-2.0 tree is rejected", "bundled Apache-2.0 trees carry NOTICE",
    () => rmSync(join(fixture, apache.fabius_paths[0], "NOTICE")));
  expectFail("missing LICENSE in a bundled tree is rejected", "bundled trees carry LICENSE",
    () => rmSync(join(fixture, bundled.fabius_paths[0], "LICENSE")));
  expectFail("informed-by entry pointing at a SKILL.md is rejected", "informed-by paths are markdown references, never a SKILL.md",
    () => {
      write(`skills/${informed.fabius_layer}/SKILL.md`, "---\nname: fixture\n---\n");
      writeRegistry((c) => { informedIn(c).fabius_paths = [`skills/${informed.fabius_layer}/SKILL.md`]; });
    });
  expectFail("informed-by reference without the attribution paragraph is rejected", "informed-by references end with exactly one attribution paragraph",
    () => write(informed.fabius_paths[0], "# no footer\n\nRe-expressed, but the credit line is gone.\n"));
  expectFail("a bare credits/README.md mention inside a table row is not an attribution paragraph", "informed-by references end with exactly one attribution paragraph",
    () => write(informed.fabius_paths[0], "# table only\n\n| pairs with | why |\n|---|---|\n| credits | see credits/README.md |\n"));
  expectFail("two attribution paragraphs are rejected", "informed-by references end with exactly one attribution paragraph",
    () => write(informed.fabius_paths[0], `# doubled\n\n${footer(informed.id)}\n${footer(informed.id)}`));
  expectFail("informed-by upstream without a by-layer credits row is rejected", "every informed-by upstream has a by-layer row in credits/README.md naming owner/repo and license",
    () => {
      const pruned = inByLayer(originalCredits.split("\n"), (line) => (line.toLowerCase().includes(token) ? [] : [line])).join("\n");
      writeFileSync(join(fixture, "credits/README.md"), pruned);
    });
  expectFail("credits row that omits the license is rejected", "every informed-by upstream has a by-layer row in credits/README.md naming owner/repo and license",
    () => {
      const stripped = inByLayer(originalCredits.split("\n"), (line) => [line.toLowerCase().includes(token) ? line.split(informed.license).join("see repo") : line]).join("\n");
      writeFileSync(join(fixture, "credits/README.md"), stripped);
    });
  expectFail("a matching row outside the by-layer table does not count", "every informed-by upstream has a by-layer row in credits/README.md naming owner/repo and license",
    () => {
      const lines = originalCredits.split("\n");
      const moved = inByLayer(lines, (line) => (line.toLowerCase().includes(token) ? [] : [line]));
      const row = lines.find((line) => line.trimStart().startsWith("|") && line.toLowerCase().includes(token));
      writeFileSync(join(fixture, "credits/README.md"), `${moved.join("\n")}\n\n## Appendix\n\n${row}\n`);
    });
  expectFail("wrong schema id is rejected", "registry schema id is fabius-upstream/v1",
    () => writeRegistry((c) => { c.schema = "fabius-upstream/v2"; }));

  result = verify();
  check("restored fixture passes again", result.status === 0, `exit ${result.status}`);
} catch (error) {
  check("test harness completed", false, error.message);
} finally {
  rmSync(temp, { recursive: true, force: true });
}

console.log(`\n== ${passed} passed · ${failed} failed ==`);
process.exitCode = failed ? 1 : 0;
