#!/usr/bin/env node
// Verify the runtime's truthful packaging boundary. The runtime is intentionally
// repo-local: it must not advertise an npm bin that installs without skills/ + seal.

import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, readdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const read = (p) => JSON.parse(readFileSync(join(ROOT, p), "utf8"));
const pkg = read("runtime/package.json");
const plugin = read(".claude-plugin/plugin.json");
const checks = [];
const check = (name, pass, detail = "") => checks.push({ name, pass: !!pass, detail });
const walkFiles = (dir, rel = "") => readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
  const childRel = rel ? `${rel}/${entry.name}` : entry.name;
  const childAbs = join(dir, entry.name);
  return entry.isDirectory() ? walkFiles(childAbs, childRel) : [childRel];
});

check("runtime package version matches plugin version", pkg.version === plugin.version, `${pkg.version} / ${plugin.version}`);
check("runtime package is private", pkg.private === true, String(pkg.private));
check("repo-local runtime exposes no standalone npm bin", !Object.hasOwn(pkg, "bin"), pkg.bin ? JSON.stringify(pkg.bin) : "no bin");
check("repo-local boundary is explicit in package description", /repo-local/i.test(pkg.description || "") && /not a standalone npm cli/i.test(pkg.description || ""), pkg.description || "missing");
check("package uses an explicit file allowlist", Array.isArray(pkg.files) && pkg.files.length > 0, `${pkg.files?.length || 0} patterns`);

let packed = null;
try {
  const text = execFileSync("npm", ["pack", "--dry-run", "--json", "--ignore-scripts"], {
    cwd: join(ROOT, "runtime"), encoding: "utf8", stdio: ["ignore", "pipe", "pipe"],
  });
  packed = JSON.parse(text)[0];
  check("npm dry-run can enumerate the repo-local component", !!packed && Array.isArray(packed.files), `${packed?.entryCount || 0} files`);
} catch (error) {
  check("npm dry-run can enumerate the repo-local component", false, String(error.stderr || error.message || error));
}

if (packed) {
  const files = new Set(packed.files.map((f) => f.path));
  const allowedPackedPath = (p) => p === "package.json" || p === "README.md" || p === "fabius.mjs"
    || /^src\/.+\.mjs$/.test(p) || /^test\/.+\.test\.mjs$/.test(p) || p === "tools/fetch-vectors.sh";
  const unexpected = [...files].filter((p) => !allowedPackedPath(p));
  check("dry-run tarball contains only the declared repo-local surface",
    unexpected.length === 0, unexpected.join(", ") || "allowlist only");
  const requiredEntries = ["package.json", "README.md", "fabius.mjs", "tools/fetch-vectors.sh"];
  check("dry-run tarball contains every declared entry/support file",
    requiredEntries.every((p) => files.has(p)), requiredEntries.filter((p) => !files.has(p)).join(", ") || "all present");
  const actualSources = walkFiles(join(ROOT, "runtime", "src"))
    .filter((p) => p.endsWith(".mjs")).map((p) => `src/${p}`);
  check("package allowlist contains every runtime source, including untracked development files",
    actualSources.every((p) => files.has(p)), `${actualSources.filter((p) => !files.has(p)).length} missing`);
  const actualTests = walkFiles(join(ROOT, "runtime", "test"))
    .filter((p) => p.endsWith(".test.mjs")).map((p) => `test/${p}`);
  check("package allowlist contains every runtime test, including untracked development files",
    actualTests.every((p) => files.has(p)), `${actualTests.filter((p) => !files.has(p)).length} missing`);
  const leakedVectors = [...files].filter((p) => p.startsWith("test/vectors/"));
  check("ignored fetched vectors cannot leak into a pack", leakedVectors.length === 0, leakedVectors.join(", ") || "none");
  check("package metadata still exposes no bin", !packed.bin, packed.bin ? JSON.stringify(packed.bin) : "none");
}

const home = mkdtempSync(join(tmpdir(), "fabius-package-check-"));
try {
  const doctor = spawnSync(process.execPath, [join(ROOT, "runtime/fabius.mjs"), "doctor"], {
    cwd: ROOT, env: { ...process.env, FABIUS_HOME: home, NO_COLOR: "1" }, encoding: "utf8", timeout: 20_000,
  });
  const doctorText = `${doctor.stdout || ""}\n${doctor.stderr || ""}`;
  check("repo-local doctor exits successfully", doctor.status === 0, `exit ${doctor.status}`);
  check("repo-local doctor loads exactly fifteen contracts", /15 skill contract\(s\) loaded/.test(doctorText), "expected 15");
  const sealMatches = /seal:\s+\d+\/\d+ files match the sealed manifest/.test(doctorText) && !/DRIFT|UNSEALED/.test(doctorText);
  check("repo-local doctor verifies the seal without drift", sealMatches,
    sealMatches ? "sealed manifest matched" : (/DRIFT|UNSEALED/.test(doctorText) ? "drift/unsealed reported" : "match line missing"));

  const version = spawnSync(process.execPath, [join(ROOT, "runtime/fabius.mjs"), "version"], { cwd: ROOT, encoding: "utf8", timeout: 5_000 });
  check("runtime CLI version matches plugin version", version.status === 0 && version.stdout.trim() === plugin.version,
    `CLI ${version.stdout.trim() || "(empty)"}; plugin ${plugin.version}`);
} finally {
  rmSync(home, { recursive: true, force: true });
}

console.log("== fabius package truth ==\n");
for (const c of checks) console.log(`  ${c.pass ? "PASS" : "FAIL"}  ${c.name}${c.detail ? ` — ${c.detail}` : ""}`);
const failed = checks.filter((c) => !c.pass).length;
console.log(`\n== ${checks.length - failed} passed · ${failed} failed ==`);
process.exitCode = failed ? 1 : 0;
