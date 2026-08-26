#!/usr/bin/env node
// Deterministic state-machine tests for release/proof verification. All git
// mutation is confined to a fresh temporary local clone; no network is used.

import { appendFileSync, mkdtempSync, readFileSync, rmSync, symlinkSync, unlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const VERIFY = join(ROOT, "scripts/verify-release.mjs");
const SELECT = join(ROOT, "scripts/select-verify-mode.sh");
const temp = mkdtempSync(join(tmpdir(), "fabius-release-state-"));
const repo = join(temp, "repo");
let passed = 0;
let failed = 0;

const run = (command, args, options = {}) => spawnSync(command, args, {
  cwd: options.cwd || ROOT,
  env: { ...process.env, ...(options.env || {}) },
  encoding: "utf8",
  timeout: 30_000,
});
const git = (...args) => {
  const result = run("git", args, { cwd: repo });
  if (result.status !== 0) throw new Error(`git ${args.join(" ")} failed: ${result.stderr}`);
  return result.stdout.trim();
};
const check = (label, ok, detail = "") => {
  console.log(`  ${ok ? "PASS" : "FAIL"}  ${label}${detail ? ` — ${detail}` : ""}`);
  if (ok) passed += 1;
  else failed += 1;
};
const verify = (mode) => run(process.execPath, [VERIFY, `--mode=${mode}`], {
  env: { FABIUS_VERIFY_ROOT: repo },
});
const select = (githubRef = "") => run("bash", [SELECT], {
  env: { FABIUS_VERIFY_ROOT: repo, GITHUB_REF: githubRef },
});
const proofVariant = (source, variant) => {
  const copy = Buffer.from(source);
  const marker = Buffer.from("https://", "ascii");
  const start = copy.indexOf(marker);
  if (start < 0) throw new Error("proof fixture has no pending calendar URI");
  const position = start + marker.length + (variant % 3);
  const value = copy[position];
  if (value < 0x61 || value > 0x7a) throw new Error("proof fixture calendar hostname is not lowercase ASCII");
  copy[position] = value === 0x7a ? 0x79 : value + 1;
  return copy;
};

console.log("== fabius release-state adversarial tests ==");
try {
  const clone = run("git", ["clone", "--local", "--no-hardlinks", "--quiet", ROOT, repo]);
  if (clone.status !== 0) throw new Error(clone.stderr || "local clone failed");
  const tag = git("tag", "--list", "v*-sealed", "--sort=-version:refname").split("\n")
    .find((value) => /^v\d+\.\d+\.\d+-sealed$/.test(value));
  if (!tag) throw new Error("no canonical sealed tag in test source");
  git("checkout", "--quiet", tag);
  git("config", "user.name", "Fabius Release Test");
  git("config", "user.email", "release-test@example.invalid");
  const tagObject = git("rev-parse", `refs/tags/${tag}`);
  const tagCommit = git("rev-parse", `${tag}^{}`);
  const proof = join(repo, "provenance/sealed-commit.txt.ots");
  const originalProof = readFileSync(proof);

  let result = verify("release");
  check("sealed tagged checkout passes release state", result.status === 0, `exit ${result.status}`);

  const signersPath = join(repo, "provenance/allowed_signers");
  const originalSigners = readFileSync(signersPath);
  writeFileSync(signersPath, Buffer.from("invalid test trust root\n"));
  result = verify("release");
  check("a release-tree trust-root replacement is rejected",
    result.status !== 0 && result.stdout.includes("FAIL  working trust root is byte-identical to the pinned historical root"),
    `exit ${result.status}`);
  writeFileSync(signersPath, originalSigners);

  const attackerKey = join(temp, "attacker-signing-key");
  const generatedKey = run("ssh-keygen", ["-q", "-t", "ed25519", "-N", "", "-C", "attacker@example.invalid", "-f", attackerKey]);
  if (generatedKey.status !== 0) throw new Error(`ssh-keygen failed: ${generatedKey.stderr}`);
  const attackerPublic = readFileSync(`${attackerKey}.pub`, "utf8").trim().split(/\s+/).slice(0, 2).join(" ");
  writeFileSync(signersPath, `fabius ${attackerPublic}\n`);
  git("add", "provenance/allowed_signers");
  git("commit", "--quiet", "-m", "test: replace release trust root");
  const forgedTag = run("git", [
    "-c", "gpg.format=ssh",
    "-c", `user.signingkey=${attackerKey}`,
    "tag", "-s", "-a", "v9.9.9-sealed", "-m", "test self-authorized release",
  ], { cwd: repo });
  if (forgedTag.status !== 0) throw new Error(`forged-tag fixture failed: ${forgedTag.stderr}`);
  result = verify("release");
  check("a self-authorized new release tag is rejected by the pinned signature chain",
    result.status !== 0 && result.stdout.includes("FAIL  every canonical sealed tag preserves and verifies against the pinned historical trust root"),
    `exit ${result.status}`);
  git("tag", "-d", "v9.9.9-sealed");
  git("reset", "--hard", "--quiet", tagCommit);

  git("update-ref", "-d", `refs/tags/${tag}`);
  git("tag", "-a", tag, "-m", "test unsigned replacement of recent release", tagCommit);
  result = verify("release");
  check("replacing a recent prior tag cannot create a trusted continuity root",
    result.status !== 0 && result.stdout.includes("FAIL  every canonical sealed tag preserves and verifies against the pinned historical trust root"),
    `exit ${result.status}`);
  git("update-ref", `refs/tags/${tag}`, tagObject);

  result = select();
  check("branch checkout at a sealed HEAD selects release", result.status === 0 && result.stdout.trim() === "release",
    result.stderr.trim() || result.stdout.trim());

  writeFileSync(proof, proofVariant(originalProof, 0));
  git("add", "provenance/sealed-commit.txt.ots");
  result = verify("proof-upgrade");
  check("one staged proof blob passes pre-commit proof state", result.status === 0, `exit ${result.status}`);
  result = verify("release");
  check("dirty proof delta cannot pass release state", result.status !== 0, `exit ${result.status}`);
  writeFileSync(proof, proofVariant(originalProof, 1));
  result = verify("proof-upgrade");
  check("staged and worktree proof divergence cannot pass pre-commit proof state",
    result.status !== 0 && result.stdout.includes("FAIL  proof upgrade is exactly one pre-commit or committed proof-only delta"),
    `exit ${result.status}`);
  git("reset", "--quiet", "HEAD", "--", "provenance/sealed-commit.txt.ots");
  git("checkout", "--", "provenance/sealed-commit.txt.ots");

  appendFileSync(join(repo, "PROVENANCE.md"), "\nunrelated test delta\n");
  result = verify("proof-upgrade");
  check("unrelated worktree delta cannot pass proof state",
    result.status !== 0 && result.stdout.includes("FAIL  proof upgrade is exactly one pre-commit or committed proof-only delta"),
    `exit ${result.status}`);
  git("checkout", "--", "PROVENANCE.md");

  unlinkSync(proof);
  symlinkSync("sealed-commit.txt", proof);
  result = verify("proof-upgrade");
  check("proof path type-change cannot pass pre-commit proof state",
    result.status !== 0 && result.stdout.includes("FAIL  proof upgrade is exactly one pre-commit or committed proof-only delta"),
    `exit ${result.status}`);
  unlinkSync(proof);
  writeFileSync(proof, originalProof);
  git("checkout", "--", "provenance/sealed-commit.txt.ots");

  unlinkSync(proof);
  git("add", "-u", "provenance/sealed-commit.txt.ots");
  writeFileSync(proof, Buffer.concat([originalProof, Buffer.from("replacement") ]));
  result = verify("proof-upgrade");
  check("staged deletion plus replacement cannot masquerade as a proof modification",
    result.status !== 0 && result.stdout.includes("FAIL  proof upgrade is exactly one pre-commit or committed proof-only delta"),
    `exit ${result.status}`);
  git("reset", "--quiet", "HEAD", "--", "provenance/sealed-commit.txt.ots");
  git("checkout", "--", "provenance/sealed-commit.txt.ots");

  writeFileSync(proof, proofVariant(originalProof, 0));
  git("add", "provenance/sealed-commit.txt.ots");
  git("commit", "--quiet", "-m", "test: proof-only child");
  result = verify("proof-upgrade");
  check("single clean proof-only child passes proof state", result.status === 0, `exit ${result.status}`);
  result = select();
  check("single clean proof-only child selects proof-upgrade",
    result.status === 0 && result.stdout.trim() === "proof-upgrade", result.stderr.trim() || result.stdout.trim());

  writeFileSync(proof, proofVariant(originalProof, 1));
  git("add", "provenance/sealed-commit.txt.ots");
  git("commit", "--quiet", "-m", "test: second proof child");
  result = verify("proof-upgrade");
  check("a second proof commit cannot bypass direct-child policy", result.status !== 0, `exit ${result.status}`);

  git("reset", "--hard", "--quiet", tagCommit);
  git("update-ref", "-d", `refs/tags/${tag}`);
  result = select();
  check("checkout with no sealed tag selects development", result.status === 0 && result.stdout.trim() === "dev",
    result.stderr.trim() || result.stdout.trim());

  git("update-ref", `refs/tags/${tag}`, tagCommit);
  result = select();
  check("lightweight canonical tag is rejected", result.status !== 0, `exit ${result.status}`);

  const restore = run("git", ["fetch", "--force", "--no-tags", "origin",
    `refs/tags/${tag}:refs/tags/${tag}`], { cwd: repo });
  const restoredType = git("cat-file", "-t", `refs/tags/${tag}`);
  const restoredSignature = run("git", ["-c", "gpg.ssh.allowedSignersFile=provenance/allowed_signers",
    "verify-tag", tag], { cwd: repo });
  check("exact force-fetch restores the annotated signed tag object",
    restore.status === 0 && restoredType === "tag" && restoredSignature.status === 0,
    `${restoredType}; verify exit ${restoredSignature.status}`);
  git("update-ref", `refs/tags/${tag}`, tagObject);

  git("tag", "-a", "v9.9.9-sealed", "-m", "test duplicate canonical tag", tagCommit);
  result = select();
  check("multiple canonical tags at HEAD are rejected", result.status !== 0, `exit ${result.status}`);
  git("tag", "-d", "v9.9.9-sealed");

  git("tag", "-a", "v9.9.9-sealed-extra", "-m", "test malformed suffix", tagCommit);
  result = select("refs/tags/v9.9.9-sealed-extra");
  check("malformed sealed-tag suffix is rejected", result.status !== 0, `exit ${result.status}`);
  git("tag", "-d", "v9.9.9-sealed-extra");

  result = select("refs/tags/v9.9.9-sealed");
  check("tag-event ref mismatch is rejected", result.status !== 0, `exit ${result.status}`);

  git("reset", "--hard", "--quiet", tagCommit);
  const recordPath = join(repo, "provenance/sealed-commit.txt");
  const recordTemplate = readFileSync(recordPath, "utf8");
  const parentTree = git("rev-parse", `${tagCommit}^{tree}`);
  writeFileSync(recordPath, recordTemplate
    .replace(/^commit:\s+[0-9a-f]{40}$/m, `commit:       ${tagCommit}`)
    .replace(/^tree:\s+[0-9a-f]{40}$/m, `tree:         ${parentTree}`));
  unlinkSync(proof);
  appendFileSync(join(repo, "SECURITY.md"), "\nanchor third-path test\n");
  git("add", "-A");
  git("commit", "--quiet", "-m", "test: malformed three-path anchor");
  git("tag", "-a", "v9.9.9-sealed", "-m", "test malformed anchor");
  result = verify("release");
  check("anchor deletion plus third path fails the exact two-M invariant",
    result.status !== 0 && result.stdout.includes("FAIL  release anchor commit changes exactly the record and detached proof"),
    `exit ${result.status}`);
} catch (error) {
  check("test harness completed", false, error.message);
} finally {
  rmSync(temp, { recursive: true, force: true });
}

console.log(`\n== ${passed} passed · ${failed} failed ==`);
process.exitCode = failed ? 1 : 0;
