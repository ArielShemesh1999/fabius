#!/usr/bin/env node
// Guard the plugin's discovery boundary without rewriting upstream examples that
// intentionally teach authors to create a target project's SKILL.md.

import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SKILLS = join(ROOT, "skills");

const walk = (dir) => readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
  const child = join(dir, entry.name);
  return entry.isDirectory() ? walk(child) : [child];
});

const files = walk(SKILLS);
const skillFiles = files.filter((file) => file.endsWith(`${sep}SKILL.md`));
const nestedSkills = skillFiles.filter((file) => relative(SKILLS, file).split(sep).length !== 2);
const referenceFiles = files.filter((file) => file.endsWith(`${sep}REFERENCE.md`));
const referenceDirs = new Set(referenceFiles.map(dirname));
const EXPECTED_REFERENCE_COUNT = 226;

const intentionalPrefixes = [
  "skills/fabius-disciplina/references/process/craft/productivity/write-a-skill/",
  "skills/fabius-disciplina/references/process/discipline/writing-skills/",
];
const intentionalFiles = new Set([
  "skills/fabius-disciplina/references/process/craft/engineering/triage/AGENT-BRIEF.md",
  "skills/fabius-disciplina/references/process/discipline/systematic-debugging/CREATION-LOG.md",
]);

const intentionalTeachingFile = (rel) => intentionalFiles.has(rel)
  || intentionalPrefixes.some((prefix) => rel.startsWith(prefix));

const nearestReferenceDir = (file) => {
  let current = dirname(file);
  while (current.startsWith(`${SKILLS}${sep}`)) {
    if (referenceDirs.has(current)) return current;
    const parent = dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return null;
};

const stale = [];
let intentionalMentions = 0;

const recordPathIfStale = (source, lineNumber, token) => {
  const withoutFragment = token.replace(/[?#].*$/, "");
  if (!withoutFragment.endsWith("SKILL.md")) return;
  let target;
  if (withoutFragment.startsWith("skills/")) target = resolve(ROOT, withoutFragment);
  else if (withoutFragment.startsWith("./") || withoutFragment.startsWith("../")) {
    target = resolve(dirname(source), withoutFragment);
  } else return;
  if (!existsSync(target) && existsSync(join(dirname(target), "REFERENCE.md"))) {
    stale.push(`${relative(ROOT, source)}:${lineNumber}: ${token}`);
  }
};

for (const file of files) {
  let body;
  try {
    body = readFileSync(file, "utf8");
  } catch {
    continue;
  }
  if (body.includes("\0") || !body.includes("SKILL.md")) continue;

  const rel = relative(ROOT, file).split(sep).join("/");
  const teaching = intentionalTeachingFile(rel);
  const localReferenceDir = nearestReferenceDir(file);
  for (const [index, line] of body.split(/\r?\n/).entries()) {
    if (!line.includes("SKILL.md")) continue;
    const lineNumber = index + 1;

    for (const match of line.matchAll(/\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)/g)) {
      recordPathIfStale(file, lineNumber, match[1]);
    }
    for (const match of line.matchAll(/`((?:\.\.?\/|skills\/)[^`\s]*SKILL\.md(?:[?#][^`\s]*)?)`/g)) {
      recordPathIfStale(file, lineNumber, match[1]);
    }

    if (!localReferenceDir) continue;
    const externalSystemSkill = rel.endsWith("/hatch-pet/REFERENCE.md")
      && line.includes("skills/.system/imagegen/SKILL.md");
    const tableName = /^\|\s*`?([^|`]+?)`?\s*\|.*SKILL\.md/.exec(line)?.[1]?.trim();
    const tablePointsToLocalReference = tableName
      && existsSync(join(dirname(localReferenceDir), tableName, "REFERENCE.md"));
    if (teaching || externalSystemSkill || (tableName && !tablePointsToLocalReference)) {
      intentionalMentions += 1;
    } else {
      stale.push(`${rel}:${lineNumber}: local quarantined reference still says SKILL.md`);
    }
  }
}

const failures = [
  ...(referenceFiles.length === EXPECTED_REFERENCE_COUNT
    ? []
    : [`reference inventory: expected ${EXPECTED_REFERENCE_COUNT}, found ${referenceFiles.length}`]),
  ...nestedSkills.map((file) => `${relative(ROOT, file)}: nested discoverable skill`),
  ...new Set(stale),
];

console.log("== nested reference quarantine ==\n");
console.log(`  ${nestedSkills.length ? "FAIL" : "PASS"}  no nested discoverable SKILL.md files — ${nestedSkills.length} found`);
console.log(`  ${referenceFiles.length === EXPECTED_REFERENCE_COUNT ? "PASS" : "FAIL"}  quarantined reference inventory is complete — ${referenceFiles.length}/${EXPECTED_REFERENCE_COUNT}`);
console.log(`  ${stale.length ? "FAIL" : "PASS"}  no local references to renamed SKILL.md files — ${stale.length} found`);
console.log(`  INFO  ${skillFiles.length} public skills · ${referenceFiles.length} quarantined references · ${intentionalMentions} intentional or non-local upstream mentions`);
if (failures.length) {
  console.log("\nFailures:");
  for (const failure of failures) console.log(`  - ${failure}`);
}
process.exitCode = failures.length ? 1 : 0;
