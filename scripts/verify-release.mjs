#!/usr/bin/env node
// Development/release integrity gate.
// dev: the worktree may be dirty, but every owned version field must describe the
//      exact next patch after the newest signed release.
// release: additionally requires a clean HEAD exactly at that signed tag and binds
//          the anchor record's commit/tree to the tagged repository state.

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { execFileSync, spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const modeArg = args.find((a) => a.startsWith("--mode="))?.split("=")[1] || (args[args.indexOf("--mode") + 1]) || "dev";
if (!["dev", "release"].includes(modeArg)) throw new Error("usage: node scripts/verify-release.mjs --mode=dev|release");
const mode = modeArg;
const text = (p) => readFileSync(join(ROOT, p), "utf8");
const json = (p) => JSON.parse(text(p));
const git = (...argv) => execFileSync("git", argv, { cwd: ROOT, encoding: "utf8" }).trim();
const sha256 = (p) => createHash("sha256").update(readFileSync(join(ROOT, p))).digest("hex");
const checks = [];
const check = (name, pass, detail = "") => checks.push({ name, pass: !!pass, detail });

const plugin = json(".claude-plugin/plugin.json");
const marketplace = json(".claude-plugin/marketplace.json");
const runtimePackage = json("runtime/package.json");
const artifact = json("paper/artifact.json");
const version = plugin.version;
const semver = (v) => /^(\d+)\.(\d+)\.(\d+)$/.exec(v || "");
const parsed = semver(version);
check("plugin version is strict semver", !!parsed, version || "missing");

const tags = git("tag", "--list", "v*-sealed*", "--sort=-version:refname").split("\n").filter(Boolean);
const newestTag = tags.find((tag) => /^v\d+\.\d+\.\d+-sealed$/.test(tag)) || "";
const releasedVersion = newestTag.match(/^v(\d+\.\d+\.\d+)-sealed$/)?.[1] || "";
check("a canonical sealed release tag exists", !!newestTag, newestTag || "none");
const signature = newestTag ? spawnSync("git", ["-c", "gpg.ssh.allowedSignersFile=provenance/allowed_signers", "verify-tag", newestTag],
  { cwd: ROOT, encoding: "utf8" }) : { status: 1, stderr: "no tag" };
check("newest canonical sealed tag has an allowed signature", signature.status === 0, newestTag || "none");

const citationVersion = text("CITATION.cff").match(/^version:\s*([^\s]+)\s*$/m)?.[1] || "";
const benchmarkVersion = text("BENCHMARKS.md").match(/<!--\s*fabius-release:\s*([^\s]+)\s*-->/)?.[1] || "";
const issueVersion = text(".github/ISSUE_TEMPLATE/bug_report.yml").match(/fabius v(\d+\.\d+\.\d+)/)?.[1] || "";
const paperReadmeVersion = text("paper/README.md").match(/\(v(\d+\.\d+\.\d+)\)/)?.[1] || "";
const template = text("paper/template.html");
const templateVersions = [
  template.match(/Whitepaper · v(\d+\.\d+\.\d+)/)?.[1] || "",
  template.match(/<div class="meta-row">Version (\d+\.\d+\.\d+)/)?.[1] || "",
  template.match(/<div class="footer-tag">Fabius v(\d+\.\d+\.\d+)/)?.[1] || "",
];
const runtimeCliVersion = text("runtime/fabius.mjs").match(/const VERSION = '([^']+)'/)?.[1] || "";
const matrix = {
  "plugin.json": version,
  "marketplace metadata": marketplace.metadata?.version,
  "marketplace plugin": marketplace.plugins?.[0]?.version,
  "runtime package": runtimePackage.version,
  "runtime CLI": runtimeCliVersion,
  "CITATION.cff": citationVersion,
  "BENCHMARKS.md": benchmarkVersion,
  "bug template": issueVersion,
  "paper README": paperReadmeVersion,
  "paper artifact": artifact.version,
};
for (const [name, got] of Object.entries(matrix)) check(`version matrix: ${name}`, got === version, `${got || "missing"} / ${version}`);
check("version matrix: every paper template marker matches", templateVersions.length >= 3 && templateVersions.every((v) => v === version),
  templateVersions.join(", ") || "none");

check("paper artifact schema and path are canonical",
  artifact.schema === "fabius-paper-artifact/v1" && artifact.file === "paper/fabius-as-a-system.pdf",
  `${artifact.schema || "missing"} / ${artifact.file || "missing"}`);
check("paper artifact digest matches committed PDF", artifact.sha256 === sha256("paper/fabius-as-a-system.pdf"),
  `${artifact.sha256 || "missing"} / ${sha256("paper/fabius-as-a-system.pdf")}`);
check("paper artifact declares a positive page count", Number.isInteger(artifact.pages) && artifact.pages > 0, String(artifact.pages));
const pdfBytes = readFileSync(join(ROOT, "paper/fabius-as-a-system.pdf")).toString("latin1");
check("paper artifact is structurally a PDF", pdfBytes.startsWith("%PDF-") && /%%EOF\s*$/.test(pdfBytes),
  pdfBytes.startsWith("%PDF-") ? "header + EOF required" : "missing PDF header");
const actualPages = (pdfBytes.match(/\/Type\s*\/Page\b/g) || []).length;
check("paper artifact page count matches the PDF", artifact.pages === actualPages && actualPages > 0,
  `${artifact.pages} / ${actualPages}`);

const head = git("rev-parse", "HEAD");
const tagCommit = newestTag ? git("rev-parse", `${newestTag}^{}`) : "";
if (mode === "dev") {
  if (semver(releasedVersion) && parsed) {
    const [, major, minor, patch] = semver(releasedVersion);
    const expected = `${major}.${minor}.${Number(patch) + 1}`;
    check("dev version is exactly the next unreleased patch", version === expected, `${version} / expected ${expected}`);
  } else check("dev version is exactly the next unreleased patch", false, "unparseable release version");
  const descends = newestTag && spawnSync("git", ["merge-base", "--is-ancestor", tagCommit, head], { cwd: ROOT }).status === 0;
  check("dev HEAD descends from the newest signed release", !!descends, `${head.slice(0, 12)} from ${tagCommit.slice(0, 12)}`);
  check("dev target has not already been tagged as released", !tags.includes(`v${version}-sealed`), `v${version}-sealed`);
} else {
  const dirty = git("status", "--porcelain=v1", "--untracked-files=all");
  check("release worktree is clean", dirty === "", dirty ? `${dirty.split("\n").length} changes` : "clean");
  check("release version equals newest signed tag", releasedVersion === version, `${version} / ${releasedVersion}`);
  check("release HEAD equals newest signed tag commit", head === tagCommit, `${head.slice(0, 12)} / ${tagCommit.slice(0, 12)}`);
  const record = text("provenance/sealed-commit.txt");
  const sealedCommit = record.match(/^commit:\s+([0-9a-f]{40})$/m)?.[1] || "";
  const sealedTree = record.match(/^tree:\s+([0-9a-f]{40})$/m)?.[1] || "";
  const tagParents = tagCommit ? git("show", "-s", "--format=%P", tagCommit).split(/\s+/).filter(Boolean) : [];
  let actualTree = "";
  try { actualTree = sealedCommit ? git("rev-parse", `${sealedCommit}^{tree}`) : ""; } catch {}
  check("release anchor record names a real commit/tree pair", !!sealedCommit && actualTree === sealedTree,
    `${sealedCommit.slice(0, 12) || "missing"} / ${sealedTree.slice(0, 12) || "missing"}`);
  check("release anchor record binds the tag's single immediate content parent",
    tagParents.length === 1 && sealedCommit === tagParents[0],
    `${sealedCommit.slice(0, 12) || "missing"} / parent ${tagParents.map((p) => p.slice(0, 12)).join(",") || "missing"}`);
  let taggedRecordMatches = false;
  try { taggedRecordMatches = git("show", `${newestTag}:provenance/sealed-commit.txt`) === record.trim(); } catch {}
  check("signed tag contains the current anchor record", taggedRecordMatches, newestTag);
}

console.log(`== fabius ${mode} integrity ==\n`);
for (const c of checks) console.log(`  ${c.pass ? "PASS" : "FAIL"}  ${c.name}${c.detail ? ` — ${c.detail}` : ""}`);
const failed = checks.filter((c) => !c.pass).length;
console.log(`\n== ${checks.length - failed} passed · ${failed} failed ==`);
if (mode === "dev") console.log("  NOTE  dev mode permits a dirty worktree; it does not authorize tagging, stamping, releasing or pushing.");
else console.log("  NOTE  release mode verifies a release that already exists; it never creates a tag, stamp, proof, release or push.");
process.exitCode = failed ? 1 : 0;
