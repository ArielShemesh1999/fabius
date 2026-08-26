#!/usr/bin/env node
// Development/release/proof-upgrade integrity gate.
// dev: the worktree may be dirty, but every owned version field must describe the
//      exact next patch after the newest signed release.
// release: additionally requires a clean HEAD exactly at that signed tag and binds
//          the anchor record's commit/tree to the tagged repository state.
// proof-upgrade: permits only a tracked proof modification at the tagged anchor or
//                one clean direct proof-only child; trusted Bitcoin confirmation is
//                separately required by verify-all.sh.

import { createHash } from "node:crypto";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { execFileSync, spawnSync } from "node:child_process";
import { dirname, join, resolve } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { verifyOtsBinding } from "./verify-ots-binding.mjs";

const ROOT = process.env.FABIUS_VERIFY_ROOT
  ? resolve(process.env.FABIUS_VERIFY_ROOT)
  : join(dirname(fileURLToPath(import.meta.url)), "..");
const TRUST_BOOTSTRAP_TAG = "v1.0.0-sealed";
const TRUST_BOOTSTRAP_OBJECT = "87b0e8d3458bc21a6e231cfaa63b3f14c128435f";
const TRUST_ROOT_SHA256 = "a3e825409eb5abe1030632fd414d95eb481fc93cf1a546ed692e83df3e6278bd";
const args = process.argv.slice(2);
const modeArg = args.find((a) => a.startsWith("--mode="))?.split("=")[1] || (args[args.indexOf("--mode") + 1]) || "dev";
if (!["dev", "release", "proof-upgrade"].includes(modeArg)) {
  throw new Error("usage: node scripts/verify-release.mjs --mode=dev|release|proof-upgrade");
}
const mode = modeArg;
const text = (p) => readFileSync(join(ROOT, p), "utf8");
const json = (p) => JSON.parse(text(p));
const git = (...argv) => execFileSync("git", argv, { cwd: ROOT, encoding: "utf8" }).trim();
const gitBytes = (...argv) => execFileSync("git", argv, { cwd: ROOT });
const sha256 = (p) => createHash("sha256").update(readFileSync(join(ROOT, p))).digest("hex");
const checks = [];
const check = (name, pass, detail = "") => checks.push({ name, pass: !!pass, detail });
const exactPaths = (actual, expected) => {
  const a = [...new Set(actual.filter(Boolean))].sort();
  const e = [...expected].sort();
  return a.length === e.length && a.every((value, index) => value === e[index]);
};
const commitChanges = (commit) => {
  if (!commit) return [];
  const fields = gitBytes("diff-tree", "--no-commit-id", "-r", "--no-renames", "--name-status", "-z", commit)
    .toString("utf8").split("\0").filter(Boolean);
  const changes = [];
  for (let i = 0; i < fields.length; i += 2) changes.push({ status: fields[i], path: fields[i + 1] || "" });
  return changes;
};

const plugin = json(".claude-plugin/plugin.json");
const marketplace = json(".claude-plugin/marketplace.json");
const runtimePackage = json("runtime/package.json");
const artifact = json("paper/artifact.json");
const version = plugin.version;
const semver = (v) => /^(\d+)\.(\d+)\.(\d+)$/.exec(v || "");
const parsed = semver(version);
check("plugin version is strict semver", !!parsed, version || "missing");

const tags = git("tag", "--list", "v*-sealed*", "--sort=-version:refname").split("\n").filter(Boolean);
const canonicalTags = tags.filter((tag) => /^v\d+\.\d+\.\d+-sealed$/.test(tag));
const newestTag = canonicalTags[0] || "";
const releasedVersion = newestTag.match(/^v(\d+\.\d+\.\d+)-sealed$/)?.[1] || "";
check("a canonical sealed release tag exists", !!newestTag, newestTag || "none");
let currentSigners = Buffer.alloc(0);
try { currentSigners = readFileSync(join(ROOT, "provenance/allowed_signers")); } catch {}
let bootstrapObject = "";
let bootstrapSigners = Buffer.alloc(0);
try { bootstrapObject = git("rev-parse", `refs/tags/${TRUST_BOOTSTRAP_TAG}`); } catch {}
try { bootstrapSigners = gitBytes("show", `${TRUST_BOOTSTRAP_TAG}:provenance/allowed_signers`); } catch {}
const bootstrapDigest = bootstrapSigners.length
  ? createHash("sha256").update(bootstrapSigners).digest("hex")
  : "";
check("historical signing bootstrap tag object and key digest are pinned",
  bootstrapObject === TRUST_BOOTSTRAP_OBJECT && bootstrapDigest === TRUST_ROOT_SHA256,
  `${bootstrapObject || "missing"} / ${bootstrapDigest || "missing"}`);
check("working trust root is byte-identical to the pinned historical root",
  currentSigners.length > 0 && currentSigners.equals(bootstrapSigners),
  TRUST_BOOTSTRAP_TAG);

let chainValid = canonicalTags.length > 0 && bootstrapSigners.length > 0;
const chainFailures = [];
if (chainValid) {
  const trustDir = mkdtempSync(join(tmpdir(), "fabius-release-trust-"));
  const trustFile = join(trustDir, "allowed_signers");
  try {
    writeFileSync(trustFile, bootstrapSigners, { mode: 0o600 });
    for (const tag of [...canonicalTags].reverse()) {
      let type = "";
      let signers = Buffer.alloc(0);
      try { type = git("cat-file", "-t", `refs/tags/${tag}`); } catch {}
      try { signers = gitBytes("show", `${tag}:provenance/allowed_signers`); } catch {}
      const signature = spawnSync("git", ["-c", `gpg.ssh.allowedSignersFile=${trustFile}`, "verify-tag", tag],
        { cwd: ROOT, encoding: "utf8" });
      if (type !== "tag") chainFailures.push(`${tag}:not-annotated`);
      if (!signers.equals(bootstrapSigners)) chainFailures.push(`${tag}:trust-root-drift`);
      if (signature.status !== 0) chainFailures.push(`${tag}:bad-signature`);
    }
  } finally {
    rmSync(trustDir, { recursive: true, force: true });
  }
}
chainValid = chainValid && chainFailures.length === 0;
check("every canonical sealed tag preserves and verifies against the pinned historical trust root",
  chainValid, chainFailures.join(", ") || `${canonicalTags.length} tags / ${TRUST_BOOTSTRAP_TAG}`);

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

let otsBinding = null;
let otsBindingError = "";
try {
  otsBinding = verifyOtsBinding(
    readFileSync(join(ROOT, "provenance/sealed-commit.txt")),
    readFileSync(join(ROOT, "provenance/sealed-commit.txt.ots")),
  );
} catch (error) {
  otsBindingError = error.message;
}
check("detached OTS proof is structurally valid and bound to the exact release record",
  !!otsBinding, otsBinding?.digest || otsBindingError || "missing proof");

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
  const statusEntries = gitBytes("status", "--porcelain=v1", "-z", "--untracked-files=all")
    .toString("utf8").split("\0").filter(Boolean);
  const dirty = statusEntries.join("\n");
  check("release version equals newest signed tag", releasedVersion === version, `${version} / ${releasedVersion}`);
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
  let anchorChanges = [];
  try { anchorChanges = commitChanges(tagCommit); } catch {}
  const expectedAnchorPaths = ["provenance/sealed-commit.txt", "provenance/sealed-commit.txt.ots"];
  check("release anchor commit changes exactly the record and detached proof",
    anchorChanges.every((entry) => entry.status === "M")
      && exactPaths(anchorChanges.map((entry) => entry.path), expectedAnchorPaths),
    anchorChanges.map((entry) => `${entry.status} ${entry.path}`).join(", ") || "none");
  let taggedRecordMatches = false;
  try { taggedRecordMatches = git("show", `${newestTag}:provenance/sealed-commit.txt`) === record.trim(); } catch {}
  check("signed tag contains the current anchor record", taggedRecordMatches, newestTag);

  if (mode === "release") {
    check("release worktree is clean", dirty === "", dirty ? `${dirty.split("\n").length} changes` : "clean");
    check("release HEAD equals newest signed tag commit", head === tagCommit, `${head.slice(0, 12)} / ${tagCommit.slice(0, 12)}`);
  } else {
    const proofPath = "provenance/sealed-commit.txt.ots";
    const atTaggedAnchor = head === tagCommit;
    const proofStatus = statusEntries.length === 1 ? statusEntries[0].slice(0, 2) : "";
    // The proof must be staged with no divergent worktree bytes. Accepting MM
    // would verify one blob and let a plain commit record another; accepting an
    // unstaged-only delta would not bind any commit candidate at all.
    const preCommitUpgrade = atTaggedAnchor && statusEntries.length === 1
      && statusEntries[0].slice(3) === proofPath && proofStatus === "M ";
    const headParents = git("show", "-s", "--format=%P", head).split(/\s+/).filter(Boolean);
    let headChanges = [];
    try { headChanges = commitChanges(head); } catch {}
    const committedUpgrade = dirty === "" && headParents.length === 1 && headParents[0] === tagCommit
      && headChanges.length === 1 && headChanges[0].status === "M" && headChanges[0].path === proofPath;
    const headTags = git("tag", "--points-at", head, "--list", "v*-sealed")
      .split("\n").filter((tag) => /^v\d+\.\d+\.\d+-sealed$/.test(tag));
    check("committed proof-upgrade HEAD is not itself a sealed release tag",
      preCommitUpgrade || headTags.length === 0,
      preCommitUpgrade ? "pre-commit upgrade at tagged anchor" : headTags.join(", ") || "untagged");
    check("proof upgrade is exactly one pre-commit or committed proof-only delta",
      preCommitUpgrade !== committedUpgrade && (preCommitUpgrade || committedUpgrade),
      preCommitUpgrade ? "proof-only worktree delta" : committedUpgrade ? "proof-only immediate child" : "invalid state");
    let proofChanged = false;
    try {
      proofChanged = git("hash-object", proofPath) !== git("rev-parse", `${newestTag}:${proofPath}`);
    } catch {}
    check("proof upgrade changes the detached proof bytes", proofChanged, proofChanged ? "changed" : "unchanged or missing");
  }
}

console.log(`== fabius ${mode} integrity ==\n`);
for (const c of checks) console.log(`  ${c.pass ? "PASS" : "FAIL"}  ${c.name}${c.detail ? ` — ${c.detail}` : ""}`);
const failed = checks.filter((c) => !c.pass).length;
console.log(`\n== ${checks.length - failed} passed · ${failed} failed ==`);
if (mode === "dev") console.log("  NOTE  dev mode permits a dirty worktree; it does not authorize tagging, stamping, releasing or pushing.");
else if (mode === "release") console.log("  NOTE  release mode verifies a release that already exists; it never creates a tag, stamp, proof, release or push.");
else console.log("  NOTE  proof-upgrade mode permits only one confirmed detached-proof delta; it never stages, commits or pushes it.");
process.exitCode = failed ? 1 : 0;
