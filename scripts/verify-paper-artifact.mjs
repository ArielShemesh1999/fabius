#!/usr/bin/env node
// Bind the rendered whitepaper to its complete repository input set and prove
// the three release-version labels are present in the PDF's own text streams.
// Deliberately uses only Node built-ins: pdftotext/pdfinfo are not release
// dependencies.

import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { inflateSync } from "node:zlib";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = process.env.FABIUS_VERIFY_ROOT
  ? resolve(process.env.FABIUS_VERIFY_ROOT)
  : join(dirname(fileURLToPath(import.meta.url)), "..");

// Independent of paper/build.py by design. A source omitted from the builder's
// manifest must still fail here rather than silently narrowing the seal.
const EXPECTED_SOURCES = Object.freeze([
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
]);
const PDF_PATH = "paper/fabius-as-a-system.pdf";
const ARTIFACT_PATH = "paper/artifact.json";

const checks = [];
const check = (name, pass, detail = "") => checks.push({ name, pass: !!pass, detail });
const bytes = (path) => readFileSync(join(ROOT, path));
const text = (path) => bytes(path).toString("utf8");
const sha256Bytes = (value) => createHash("sha256").update(value).digest("hex");
const sha256File = (path) => existsSync(join(ROOT, path)) ? sha256Bytes(bytes(path)) : "";
const sourceDigest = (entries) => sha256Bytes(Buffer.from(
  entries.map(({ file, sha256 }) => `${file}\0${sha256}\n`).join(""),
  "utf8",
));
const sameJson = (left, right) => JSON.stringify(left) === JSON.stringify(right);

function parseObjects(pdf) {
  const source = pdf.toString("latin1");
  const marker = /(?:^|[\r\n])(\d+)\s+(\d+)\s+obj\b/g;
  const positions = [];
  let match;
  while ((match = marker.exec(source))) {
    positions.push({ id: Number(match[1]), generation: Number(match[2]), bodyStart: marker.lastIndex, markerStart: match.index });
  }
  const objects = new Map();
  const errors = [];
  for (let index = 0; index < positions.length; index += 1) {
    const item = positions[index];
    const next = positions[index + 1]?.markerStart ?? pdf.length;
    const chunk = pdf.subarray(item.bodyStart, next);
    const chunkText = chunk.toString("latin1");
    const endObject = chunkText.lastIndexOf("endobj");
    if (endObject < 0) {
      errors.push(`object ${item.id} has no endobj`);
      continue;
    }
    const body = chunk.subarray(0, endObject);
    const bodyText = body.toString("latin1");
    const streamMarker = /stream\r?\n/.exec(bodyText);
    const dictionary = streamMarker ? bodyText.slice(0, streamMarker.index) : bodyText;
    let stream = null;
    if (streamMarker) {
      const streamStart = streamMarker.index + streamMarker[0].length;
      const directLength = /\/Length\s+(\d+)\b/.exec(dictionary)?.[1];
      let streamEnd = directLength ? streamStart + Number(directLength) : bodyText.indexOf("endstream", streamStart);
      if (streamEnd < streamStart || streamEnd > body.length) {
        errors.push(`object ${item.id} has an invalid stream length`);
      } else {
        stream = body.subarray(streamStart, streamEnd);
        if (/\/FlateDecode\b/.test(dictionary)) {
          try {
            stream = inflateSync(stream);
          } catch {
            errors.push(`object ${item.id} has an invalid Flate stream`);
            stream = null;
          }
        }
      }
    }
    if (objects.has(item.id)) errors.push(`duplicate object ${item.id}`);
    objects.set(item.id, { id: item.id, generation: item.generation, dictionary, stream });
  }
  return { objects, errors };
}

function utf16be(hex) {
  const value = Buffer.from(hex.replace(/\s/g, ""), "hex");
  if (value.length % 2 !== 0) return "";
  let output = "";
  for (let index = 0; index < value.length; index += 2) output += String.fromCharCode(value.readUInt16BE(index));
  return output;
}

function parseCmap(object) {
  const source = object?.stream?.toString("latin1") || "";
  const mapping = new Map();
  const widths = new Set();
  let match;
  const codeSpace = source.match(/begincodespacerange([\s\S]*?)endcodespacerange/)?.[1] || "";
  const codeRange = /<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>/g;
  while ((match = codeRange.exec(codeSpace))) widths.add(match[1].length / 2);

  for (const section of source.matchAll(/beginbfchar([\s\S]*?)endbfchar/g)) {
    const pair = /<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>/g;
    while ((match = pair.exec(section[1]))) mapping.set(match[1].toUpperCase(), utf16be(match[2]));
  }
  for (const section of source.matchAll(/beginbfrange([\s\S]*?)endbfrange/g)) {
    const range = /<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(?:<([0-9A-Fa-f]+)>|\[([^\]]*)\])/g;
    while ((match = range.exec(section[1]))) {
      const first = Number.parseInt(match[1], 16);
      const last = Number.parseInt(match[2], 16);
      const sourceWidth = match[1].length;
      if (match[3]) {
        let destination = Number.parseInt(match[3], 16);
        const destinationWidth = match[3].length;
        for (let code = first; code <= last; code += 1, destination += 1) {
          mapping.set(code.toString(16).toUpperCase().padStart(sourceWidth, "0"),
            utf16be(destination.toString(16).padStart(destinationWidth, "0")));
        }
      } else {
        const destinations = [...match[4].matchAll(/<([0-9A-Fa-f]+)>/g)].map((value) => value[1]);
        for (let code = first; code <= last; code += 1) {
          const destination = destinations[code - first];
          if (destination) mapping.set(code.toString(16).toUpperCase().padStart(sourceWidth, "0"), utf16be(destination));
        }
      }
    }
  }
  if (widths.size === 0) {
    for (const key of mapping.keys()) widths.add(key.length / 2);
  }
  return { mapping, widths: [...widths].sort((left, right) => right - left) };
}

function extractPdfText(pdf) {
  const parsed = parseObjects(pdf);
  const fontCmaps = new Map();
  for (const object of parsed.objects.values()) {
    if (!/\/Type\s*\/Font\b/.test(object.dictionary)) continue;
    const cmapObject = /\/ToUnicode\s+(\d+)\s+\d+\s+R/.exec(object.dictionary)?.[1];
    if (cmapObject) fontCmaps.set(object.id, parseCmap(parsed.objects.get(Number(cmapObject))));
  }

  const ambiguousFonts = new Set();
  const pageObjects = [...parsed.objects.values()]
    .filter((object) => /\/Type\s*\/Page\b/.test(object.dictionary))
    .sort((left, right) => left.id - right.id);
  const pageRecords = pageObjects.map((page) => {
    const resourceObject = /\/Resources\s+(\d+)\s+\d+\s+R/.exec(page.dictionary)?.[1];
    const resources = resourceObject
      ? parsed.objects.get(Number(resourceObject))?.dictionary || ""
      : page.dictionary;
    const fonts = new Map();
    for (const section of resources.matchAll(/\/Font\s*<<([\s\S]*?)>>/g)) {
      for (const binding of section[1].matchAll(/\/([^\s/<>()]+)\s+(\d+)\s+\d+\s+R/g)) {
        const name = binding[1];
        const objectId = Number(binding[2]);
        if (fonts.has(name) && fonts.get(name) !== objectId) ambiguousFonts.add(`${page.id}:${name}`);
        fonts.set(name, objectId);
      }
    }
    const contentArray = /\/Contents\s*\[([^\]]*)\]/.exec(page.dictionary)?.[1];
    const contents = contentArray
      ? [...contentArray.matchAll(/(\d+)\s+\d+\s+R/g)].map((match) => Number(match[1]))
      : [Number(/\/Contents\s+(\d+)\s+\d+\s+R/.exec(page.dictionary)?.[1])].filter(Number.isInteger);
    return { contents, fonts };
  });

  const decodeHex = (hex, fontName, fonts) => {
    const cmap = fontCmaps.get(fonts.get(fontName));
    if (!cmap) return "";
    const source = hex.replace(/\s/g, "").toUpperCase();
    let output = "";
    for (let offset = 0; offset < source.length;) {
      let matched = false;
      for (const width of cmap.widths) {
        const length = width * 2;
        const code = source.slice(offset, offset + length);
        if (code.length === length && cmap.mapping.has(code)) {
          output += cmap.mapping.get(code);
          offset += length;
          matched = true;
          break;
        }
      }
      if (!matched) {
        output += "\uFFFD";
        offset += 2;
      }
    }
    return output;
  };

  let output = "";
  for (const page of pageRecords) {
    for (const contentId of page.contents) {
      const content = parsed.objects.get(contentId)?.stream?.toString("latin1") || "";
      if (!/\bBT\b/.test(content)) continue;
      let currentFont = "";
      const token = /(?:\/([^\s/<>()]+)\s+[-+]?\d*\.?\d+\s+Tf)|(?:<([0-9A-Fa-f\s]+)>\s*Tj)|(?:\[([\s\S]*?)\]\s*TJ)/g;
      let match;
      while ((match = token.exec(content))) {
        if (match[1]) currentFont = match[1];
        else if (match[2]) output += decodeHex(match[2], currentFont, page.fonts);
        else {
          for (const value of match[3].matchAll(/<([0-9A-Fa-f\s]+)>/g)) {
            output += decodeHex(value[1], currentFont, page.fonts);
          }
        }
      }
      output += "\n";
    }
  }
  return { text: output, errors: parsed.errors, ambiguousFonts: [...ambiguousFonts], pages: pageRecords.length };
}

function canonicalMarker(value) {
  return value.normalize("NFKC").toLowerCase().replace(/\s+/g, "");
}

function run() {
  const plugin = JSON.parse(text(".claude-plugin/plugin.json"));
  const artifact = JSON.parse(text(ARTIFACT_PATH));
  const version = plugin.version || "";
  check("plugin version is strict semver", /^\d+\.\d+\.\d+$/.test(version), version || "missing");
  check("artifact schema and path are canonical",
    artifact.schema === "fabius-paper-artifact/v1" && artifact.file === PDF_PATH,
    `${artifact.schema || "missing"} / ${artifact.file || "missing"}`);
  check("artifact version matches the plugin", artifact.version === version,
    `${artifact.version || "missing"} / ${version || "missing"}`);

  const declaredSources = Array.isArray(artifact.sources) ? artifact.sources : [];
  const declaredPaths = declaredSources.map((entry) => entry?.file || "");
  check("source inventory is exact and canonically ordered", sameJson(declaredPaths, EXPECTED_SOURCES),
    `${declaredPaths.length} declared / ${EXPECTED_SOURCES.length} expected`);
  const declaredByPath = new Map(declaredSources.map((entry) => [entry?.file, entry?.sha256]));
  const actualSources = EXPECTED_SOURCES.map((file) => ({ file, sha256: sha256File(file) }));
  for (const entry of actualSources) {
    check(`source digest: ${entry.file}`, !!entry.sha256 && declaredByPath.get(entry.file) === entry.sha256,
      `${declaredByPath.get(entry.file) || "missing"} / ${entry.sha256 || "missing file"}`);
  }
  const actualSourceDigest = sourceDigest(actualSources);
  check("aggregate source digest matches", artifact.source_sha256 === actualSourceDigest,
    `${artifact.source_sha256 || "missing"} / ${actualSourceDigest}`);

  const buildScript = text("paper/build.sh");
  const mathjaxVersion = buildScript.match(/^MATHJAX_VERSION=([^\s]+)$/m)?.[1] || "";
  const mathjaxSha = buildScript.match(/^MATHJAX_SHA256=([0-9a-f]{64})$/m)?.[1] || "";
  const expectedExternal = [{ name: "MathJax tex-svg.js", version: mathjaxVersion, sha256: mathjaxSha }];
  check("external render input is pinned in build.sh", !!mathjaxVersion && !!mathjaxSha,
    `${mathjaxVersion || "missing"} / ${mathjaxSha || "missing"}`);
  check("artifact binds the exact external render input", sameJson(artifact.external_sources, expectedExternal),
    `MathJax ${mathjaxVersion || "missing"}`);

  const template = text("paper/template.html");
  const templateVersions = [
    template.match(/Whitepaper · v(\d+\.\d+\.\d+)/)?.[1] || "",
    template.match(/<div class="meta-row">Version (\d+\.\d+\.\d+)/)?.[1] || "",
    template.match(/<div class="footer-tag">Fabius v(\d+\.\d+\.\d+)/)?.[1] || "",
  ];
  check("template carries three exact current-version markers",
    templateVersions.length === 3 && templateVersions.every((value) => value === version),
    templateVersions.join(", ") || "none");
  const expectedMarkers = [`Whitepaper · v${version}`, `Version ${version}`, `Fabius v${version}`];
  check("artifact declares the exact rendered-marker contract", sameJson(artifact.rendered_markers, expectedMarkers),
    Array.isArray(artifact.rendered_markers) ? artifact.rendered_markers.join(" | ") : "missing");

  const pdf = bytes(PDF_PATH);
  const pdfLatin1 = pdf.toString("latin1");
  const actualPdfSha = sha256Bytes(pdf);
  check("artifact digest matches the rendered PDF", artifact.sha256 === actualPdfSha,
    `${artifact.sha256 || "missing"} / ${actualPdfSha}`);
  check("rendered artifact is a complete PDF", pdfLatin1.startsWith("%PDF-") && /%%EOF\s*$/.test(pdfLatin1),
    pdfLatin1.startsWith("%PDF-") ? "header + EOF required" : "missing PDF header");
  const pages = (pdfLatin1.match(/\/Type\s*\/Page\b/g) || []).length;
  check("artifact page count matches the rendered PDF", Number.isInteger(artifact.pages) && artifact.pages === pages && pages > 0,
    `${artifact.pages ?? "missing"} / ${pages}`);

  const extracted = extractPdfText(pdf);
  check("PDF object and stream structure is readable", extracted.errors.length === 0,
    extracted.errors.slice(0, 3).join("; ") || "no parse errors");
  check("PDF font resources are unambiguous", extracted.ambiguousFonts.length === 0,
    extracted.ambiguousFonts.join(", ") || "unambiguous");
  check("PDF exposes machine-readable rendered text", extracted.text.length > 0, `${extracted.text.length} decoded characters`);
  const normalized = canonicalMarker(extracted.text);
  const families = [
    { label: "Whitepaper title", regex: /whitepaper·v(\d+\.\d+\.\d+)/g },
    { label: "Version metadata", regex: /version(\d+\.\d+\.\d+)/g },
    { label: "Fabius footer", regex: /fabiusv(\d+\.\d+\.\d+)/g },
  ];
  for (const family of families) {
    const observed = [...normalized.matchAll(family.regex)].map((match) => match[1]);
    check(`rendered PDF marker: ${family.label}`,
      observed.length === 1 && observed[0] === version,
      `${observed.join(", ") || "missing"} / expected ${version}`);
  }
  for (const marker of expectedMarkers) {
    check(`rendered PDF contains: ${marker}`, normalized.includes(canonicalMarker(marker)), marker);
  }

  console.log("== fabius paper artifact oracle ==\n");
  for (const result of checks) {
    console.log(`  ${result.pass ? "PASS" : "FAIL"}  ${result.name}${result.detail ? ` — ${result.detail}` : ""}`);
  }
  const failed = checks.filter((result) => !result.pass).length;
  console.log(`\n== ${checks.length - failed} passed · ${failed} failed ==`);
  process.exitCode = failed ? 1 : 0;
}

try {
  run();
} catch (error) {
  console.error(`== fabius paper artifact oracle ==\n\n  FAIL  verifier aborted — ${error.message}`);
  process.exitCode = 1;
}
