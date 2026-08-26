#!/usr/bin/env node
// Deterministic adversarial controls for the paper artifact oracle. Mutations
// are confined to a fresh temporary fixture; the repository is read-only.

import { createHash } from "node:crypto";
import { copyFileSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const VERIFY = join(ROOT, "scripts/verify-paper-artifact.mjs");
const SOURCES = [
  "assets/architecture.svg",
  "assets/charts/render_figures.py",
  "assets/charts/svgplot.py",
  "assets/fabius-pixel.svg",
  "assets/fig-branching-accuracy.svg",
  "assets/fig-capability-ladder.svg",
  "assets/fig-plan-then-bind.svg",
  "assets/fig-recall-context.svg",
  "assets/fig-reflection-iteration.svg",
  "assets/fig-tool-value-gate.svg",
  "paper/build.py",
  "paper/build.sh",
  "paper/coherence-ext.html",
  "paper/coherence.html",
  "paper/proofs.json",
  "paper/template.html",
];
const temp = mkdtempSync(join(tmpdir(), "fabius-paper-artifact-"));
const fixture = join(temp, "fixture");
const emptyPath = join(temp, "empty-path");
let passed = 0;
let failed = 0;

const sha256 = (value) => createHash("sha256").update(value).digest("hex");
const check = (label, ok, detail = "") => {
  console.log(`  ${ok ? "PASS" : "FAIL"}  ${label}${detail ? ` — ${detail}` : ""}`);
  if (ok) passed += 1;
  else failed += 1;
};
const copy = (path) => {
  const destination = join(fixture, path);
  mkdirSync(dirname(destination), { recursive: true });
  copyFileSync(join(ROOT, path), destination);
};
const verify = (root, path = process.env.PATH || "") => spawnSync(process.execPath, [VERIFY], {
  cwd: root,
  env: { ...process.env, PATH: path, FABIUS_VERIFY_ROOT: root },
  encoding: "utf8",
  timeout: 30_000,
});
const readArtifact = () => JSON.parse(readFileSync(join(fixture, "paper/artifact.json"), "utf8"));
const writeArtifact = (artifact) => writeFileSync(join(fixture, "paper/artifact.json"), `${JSON.stringify(artifact, null, 2)}\n`);

function encodedText(value) {
  return [...value].map((character) => {
    if (character === "·") return "b7";
    return character.codePointAt(0).toString(16).padStart(2, "0");
  }).join("");
}

function minimalPdf(version, decoyVersion = "") {
  const marker = version
    ? `Whitepaper · v${version} Version ${version} Fabius v${version}`
    : "Unversioned page";
  const encoded = encodedText(marker);
  const content = `BT\n/F1 12 Tf\n<${encoded}> Tj\nET\n`;
  const decoyText = decoyVersion
    ? `Whitepaper · v${decoyVersion} Version ${decoyVersion} Fabius v${decoyVersion}`
    : "";
  const decoyContent = decoyText ? `BT /F1 12 Tf <${encodedText(decoyText)}> Tj ET\n` : "";
  const decoy = decoyText ? `7 0 obj
<< /Length ${Buffer.byteLength(decoyContent)} >>
stream
${decoyContent}endstream
endobj
` : "";
  const cmap = `/CIDInit /ProcSet findresource begin
12 dict begin
begincmap
/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def
/CMapName /Adobe-Identity-UCS def
/CMapType 2 def
1 begincodespacerange
<00> <FF>
endcodespacerange
1 beginbfchar
<B7> <00B7>
endbfchar
1 beginbfrange
<20> <7E> <0020>
endbfrange
endcmap
CMapName currentdict /CMap defineresource pop
end
end`;
  return Buffer.from(`%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type0 /BaseFont /Fixture /Encoding /Identity-H /ToUnicode 6 0 R >>
endobj
5 0 obj
<< /Length ${Buffer.byteLength(content)} >>
stream
${content}endstream
endobj
6 0 obj
<< /Length ${Buffer.byteLength(cmap)} >>
stream
${cmap}
endstream
endobj
${decoy}trailer
<< /Root 1 0 R >>
%%EOF
`, "latin1");
}

console.log("== fabius paper artifact adversarial tests ==");
try {
  mkdirSync(fixture, { recursive: true });
  mkdirSync(emptyPath);
  for (const path of SOURCES) copy(path);
  copy(".claude-plugin/plugin.json");
  copy("paper/artifact.json");
  copy("paper/fabius-as-a-system.pdf");

  let result = verify(ROOT, emptyPath);
  check("current artifact passes with no external PDF tools on PATH", result.status === 0,
    `exit ${result.status}`);

  result = verify(fixture);
  check("isolated byte-identical fixture passes", result.status === 0, `exit ${result.status}`);

  const artifactPath = join(fixture, "paper/artifact.json");
  const originalArtifact = readFileSync(artifactPath);
  result = spawnSync("python3", [join(fixture, "paper/build.py"), "--write-artifact"], {
    cwd: fixture,
    encoding: "utf8",
    timeout: 30_000,
  });
  check("artifact writer reproduces the committed manifest byte-for-byte",
    result.status === 0 && readFileSync(artifactPath).equals(originalArtifact),
    `exit ${result.status}`);

  const proofPath = join(fixture, "paper/proofs.json");
  const originalProofs = readFileSync(proofPath);
  writeFileSync(proofPath, Buffer.concat([originalProofs, Buffer.from("\n") ]));
  result = verify(fixture);
  check("unrecorded paper-source drift is rejected",
    result.status !== 0 && result.stdout.includes("FAIL  source digest: paper/proofs.json"),
    `exit ${result.status}`);
  writeFileSync(proofPath, originalProofs);

  let artifact = readArtifact();
  artifact.version = "2.6.3";
  writeArtifact(artifact);
  result = verify(fixture);
  check("stale artifact version is rejected",
    result.status !== 0 && result.stdout.includes("FAIL  artifact version matches the plugin"),
    `exit ${result.status}`);
  writeFileSync(artifactPath, originalArtifact);

  artifact = readArtifact();
  artifact.sha256 = "0".repeat(64);
  writeArtifact(artifact);
  result = verify(fixture);
  check("stale artifact PDF digest is rejected",
    result.status !== 0 && result.stdout.includes("FAIL  artifact digest matches the rendered PDF"),
    `exit ${result.status}`);
  writeFileSync(artifactPath, originalArtifact);

  const pdfPath = join(fixture, "paper/fabius-as-a-system.pdf");
  const originalPdf = readFileSync(pdfPath);
  const stalePdf = minimalPdf("2.6.3");
  writeFileSync(pdfPath, stalePdf);
  artifact = readArtifact();
  artifact.sha256 = sha256(stalePdf);
  artifact.pages = 1;
  writeArtifact(artifact);
  result = verify(fixture);
  check("digest-matched PDF with stale rendered version markers is rejected",
    result.status !== 0
      && result.stdout.includes("PASS  artifact digest matches the rendered PDF")
      && result.stdout.includes("PASS  PDF object and stream structure is readable")
      && result.stdout.includes("PASS  PDF exposes machine-readable rendered text")
      && result.stdout.includes("FAIL  rendered PDF marker: Whitepaper title")
      && result.stdout.includes("FAIL  rendered PDF marker: Version metadata")
      && result.stdout.includes("FAIL  rendered PDF marker: Fabius footer"),
    `exit ${result.status}`);
  writeFileSync(pdfPath, originalPdf);
  writeFileSync(artifactPath, originalArtifact);

  const decoyPdf = minimalPdf("", "2.6.4");
  writeFileSync(pdfPath, decoyPdf);
  artifact = readArtifact();
  artifact.sha256 = sha256(decoyPdf);
  artifact.pages = 1;
  writeArtifact(artifact);
  result = verify(fixture);
  check("an unreferenced current-version text stream cannot satisfy rendered markers",
    result.status !== 0
      && result.stdout.includes("PASS  PDF exposes machine-readable rendered text")
      && result.stdout.includes("FAIL  rendered PDF marker: Whitepaper title")
      && result.stdout.includes("FAIL  rendered PDF marker: Version metadata")
      && result.stdout.includes("FAIL  rendered PDF marker: Fabius footer"),
    `exit ${result.status}`);
  writeFileSync(pdfPath, originalPdf);
  writeFileSync(artifactPath, originalArtifact);
} catch (error) {
  check("test harness completed", false, error.message);
} finally {
  rmSync(temp, { recursive: true, force: true });
}

console.log(`\n== ${passed} passed · ${failed} failed ==`);
process.exitCode = failed ? 1 : 0;
