#!/usr/bin/env node
// Deterministic receipt replay for the committed fabius benchmark artifacts.
// This does not pretend historical answer text exists: it recomputes every aggregate
// the committed raw score receipts can support, and requires the missing evidence to
// be declared explicitly in the canonical receipt.

import { readFileSync } from "node:fs";
import { isDeepStrictEqual } from "node:util";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const read = (p) => JSON.parse(readFileSync(join(ROOT, p), "utf8"));
const canonical = read("evals/results.benchmark.json");
const v5 = read("evals/results.v5.json");
const v6 = read("evals/results.v6.json");
const v7 = read("evals/results.v7.json");

const checks = [];
const check = (name, pass, detail = "") => checks.push({ name, pass: !!pass, detail });
const exact = (name, got, want) => check(name, isDeepStrictEqual(got, want),
  isDeepStrictEqual(got, want) ? "exact" : `got ${JSON.stringify(got)}; want ${JSON.stringify(want)}`);
const round = (n, places = 2) => +Number(n).toFixed(places);
// The historical Panel A category table used half-to-even decimal rounding.
// Reproduce the committed arithmetic instead of silently applying JS toFixed's
// half-away behavior at .125/.625 ties.
const roundEven = (n, places = 2) => {
  const factor = 10 ** places;
  const scaled = n * factor;
  const lower = Math.floor(scaled);
  const fraction = scaled - lower;
  if (Math.abs(fraction - 0.5) < 1e-10) return (lower % 2 === 0 ? lower : lower + 1) / factor;
  return Math.round(scaled) / factor;
};
const mean = (rows, key) => rows.reduce((s, r) => s + Number(r[key] || 0), 0) / (rows.length || 1);
const uniqueTuples = (rows, keys) => new Set(rows.map((r) => keys.map((k) => r[k]).join("\0"))).size;

// Panel A: recompute the published model/category cells from the 180 score rows.
check("Panel A schema: 180 unique model/arm/task rows", v5.perTask.length === 180 &&
  uniqueTuples(v5.perTask, ["tier", "arm", "task"]) === 180, `${v5.perTask.length} rows`);
check("Panel A schema: every row carries both judge totals", v5.perTask.every((r) =>
  r.byJudge && Object.keys(r.byJudge).length === 2), "two totals per row required");

const aByModel = {};
const aByModelArm = {};
const aAgg = (rows) => ({
  n: rows.length,
  total: round(mean(rows, "total")),
  chars: Math.round(mean(rows, "chars")),
  correctness: round(mean(rows, "correctness")),
  minimality: round(mean(rows, "minimality")),
  best_practice: round(mean(rows, "best_practice")),
});
for (const tier of v5._meta.generated_models) {
  const rows = v5.perTask.filter((r) => r.tier === tier);
  const arm = (name) => rows.filter((r) => r.arm === name);
  for (const name of v5._meta.arms) aByModelArm[`${tier}/${name}`] = aAgg(arm(name));
  const baseline = aByModelArm[`${tier}/baseline`].total;
  const terse = aByModelArm[`${tier}/terse`].total;
  const fabius = aByModelArm[`${tier}/fabius`].total;
  const baselineChars = aByModelArm[`${tier}/baseline`].chars;
  const fabiusChars = aByModelArm[`${tier}/fabius`].chars;
  aByModel[tier] = {
    baseline, terse, fabius,
    gain_vs_baseline: round(fabius - baseline),
    gain_vs_terse: round(fabius - terse),
    output_reduction_vs_baseline_pct: round(100 * (baselineChars - fabiusChars) / baselineChars, 1),
    baseline_chars: baselineChars,
    fabius_chars: fabiusChars,
  };
}
exact("Panel A replay: raw byModelArm", v5.byModelArm, aByModelArm);
exact("Panel A replay: raw byModel", v5.byModel, aByModel);
exact("Panel A replay: canonical byModel", canonical.panelA_quality_newest_claude.byModel, aByModel);

const aByCat = {};
for (const cat of [...new Set(v5.perTask.map((r) => r.cat))]) {
  const rows = v5.perTask.filter((r) => r.cat === cat);
  const score = (arm) => roundEven(mean(rows.filter((r) => r.arm === arm), "total"));
  const baseline = score("baseline"), terse = score("terse"), fabius = score("fabius");
  aByCat[cat] = { baseline, terse, fabius,
    fab_minus_terse: roundEven(fabius - terse), fab_minus_base: roundEven(fabius - baseline) };
}
exact("Panel A replay: raw byCat", v5.byCat, aByCat);
exact("Panel A replay: canonical byCat", canonical.panelA_quality_newest_claude.byCat, aByCat);
const aJudgeDiffs = v5.perTask.map((row) => {
  const values = Object.values(row.byJudge || {});
  return values.length === 2 ? Math.abs(values[0] - values[1]) : NaN;
});
const aJudgeAgreement = {
  mean_abs_total_diff: round(aJudgeDiffs.reduce((sum, n) => sum + n, 0) / aJudgeDiffs.length),
  n: aJudgeDiffs.length,
  scale: "0-15 total",
};
check("Panel A replay: judge rows are complete", aJudgeDiffs.every(Number.isFinite), `${aJudgeDiffs.length} rows`);
exact("Panel A replay: raw judge agreement", v5.judgeAgreement, aJudgeAgreement);
exact("Panel A replay: canonical judge agreement", canonical.panelA_quality_newest_claude.judgeAgreement, aJudgeAgreement);
const aPooledBaseline = aAgg(v5.perTask.filter((r) => r.arm === "baseline"));
const aPooledTerse = aAgg(v5.perTask.filter((r) => r.arm === "terse"));
const aPooledFabius = aAgg(v5.perTask.filter((r) => r.arm === "fabius"));
const aPooled = {
  baseline: aPooledBaseline.total,
  terse: aPooledTerse.total,
  fabius: aPooledFabius.total,
  gain_vs_baseline: round(aPooledFabius.total - aPooledBaseline.total),
  gain_vs_terse: round(aPooledFabius.total - aPooledTerse.total),
  output_reduction_pct: round(100 * (aPooledBaseline.chars - aPooledFabius.chars) / aPooledBaseline.chars, 1),
};
exact("Panel A replay: raw pooled", v5.pooled, aPooled);

// Panel B: same arithmetic as the committed harness, over 108 per-item score rows.
check("Panel B schema: 108 unique model/arm/task rows", v6.perItem.length === 108 &&
  uniqueTuples(v6.perItem, ["tier", "arm", "task"]) === 108, `${v6.perItem.length} rows`);
check("Panel B schema: kind and bounds are valid", v6.perItem.every((r) =>
  ["exec", "rubric"].includes(r.kind) && r.total > 0 && r.passed >= 0 && r.passed <= r.total), "all bounded");
const pct = (rows) => {
  const total = rows.reduce((s, r) => s + r.total, 0);
  const passed = rows.reduce((s, r) => s + r.passed, 0);
  return { pts: round(passed), total, pct: total ? round(100 * passed / total, 1) : 0,
    chars: rows.length ? Math.round(mean(rows, "chars")) : 0 };
};
const bByModel = {};
const bByModelArm = {};
for (const tier of v6._meta.generated_models) {
  const get = (arm, kind = null) => pct(v6.perItem.filter((r) => r.tier === tier && r.arm === arm && (!kind || r.kind === kind)));
  const b = get("baseline"), t = get("terse"), f = get("fabius");
  const be = get("baseline", "exec"), te = get("terse", "exec"), fe = get("fabius", "exec");
  const br = get("baseline", "rubric"), tr = get("terse", "rubric"), fr = get("fabius", "rubric");
  bByModelArm[`${tier}/baseline`] = { overall: b, exec: be, rubric: br };
  bByModelArm[`${tier}/terse`] = { overall: t, exec: te, rubric: tr };
  bByModelArm[`${tier}/fabius`] = { overall: f, exec: fe, rubric: fr };
  bByModel[tier] = {
    baseline_pct: b.pct, terse_pct: t.pct, fabius_pct: f.pct,
    gain_vs_baseline: round(f.pct - b.pct, 1), gain_vs_terse: round(f.pct - t.pct, 1),
    exec: { baseline: be.pct, terse: te.pct, fabius: fe.pct, gain: round(fe.pct - be.pct, 1) },
    rubric: { baseline: br.pct, terse: tr.pct, fabius: fr.pct, gain: round(fr.pct - br.pct, 1) },
    output_cut_pct: b.chars ? round(100 * (b.chars - f.chars) / b.chars, 1) : 0,
  };
}
exact("Panel B replay: raw byModelArm", v6.byModelArm, bByModelArm);
exact("Panel B replay: raw byModel", v6.byModel, bByModel);
exact("Panel B replay: canonical byModel", canonical.panelB_mixed_verification.byModel, bByModel);
const bByTask = {};
for (const task of [...new Set(v6.perItem.map((r) => r.task))]) {
  const rows = v6.perItem.filter((r) => r.task === task);
  const score = (arm) => pct(rows.filter((r) => r.arm === arm)).pct;
  const baseline = score("baseline"), terse = score("terse"), fabius = score("fabius");
  bByTask[task] = { baseline, terse, fabius, gain: round(fabius - baseline, 1), kind: rows[0].kind };
}
exact("Panel B replay: raw byTask", v6.byTask, bByTask);
exact("Panel B replay: canonical byTask", canonical.panelB_mixed_verification.byTask, bByTask);
for (const kind of ["exec", "rubric", "all"]) {
  const rows = (arm) => v6.perItem.filter((r) => r.arm === arm && (kind === "all" || r.kind === kind));
  const pooled = { baseline: pct(rows("baseline")).pct, terse: pct(rows("terse")).pct, fabius: pct(rows("fabius")).pct };
  exact(`Panel B replay: raw pooled_${kind}`, v6[`pooled_${kind}`], pooled);
}

// Panel D: the canonical receipt publishes a compact projection of the raw aggregates.
const DIMS = ["task_success", "instruction_obedience", "scope_control", "technical_correctness", "safety", "token_efficiency", "quality"];
const dAggregateConsistent = (actual, rows) => {
  const failures = [];
  const fields = ["n", "total", "chars", "check_rate", ...DIMS].sort();
  if (!isDeepStrictEqual(Object.keys(actual || {}).sort(), fields)) failures.push("field set");
  if (actual?.n !== rows.length) failures.push(`n ${actual?.n}/${rows.length}`);
  const close = (key, exactValue, halfUnit) => {
    if (!Number.isFinite(actual?.[key]) || Math.abs(actual[key] - exactValue) > halfUnit + 1e-9) {
      failures.push(`${key} ${actual?.[key]}/${exactValue}`);
    }
  };
  close("total", mean(rows, "total"), 0.005);
  close("chars", mean(rows, "chars"), 0.5);
  close("check_rate", 100 * rows.reduce((s, r) => s + r.checks_passed, 0) /
    Math.max(1, rows.reduce((s, r) => s + r.checks_total, 0)), 0.05);
  for (const dim of DIMS) close(dim, mean(rows, dim), 0.005);
  return failures;
};
const dMapConsistent = (name, actual, groups) => {
  const failures = [];
  const actualKeys = Object.keys(actual || {}).sort();
  const expectedKeys = Object.keys(groups).sort();
  if (!isDeepStrictEqual(actualKeys, expectedKeys)) failures.push(`keys ${actualKeys.length}/${expectedKeys.length}`);
  for (const [key, rows] of Object.entries(groups)) {
    if (actual?.[key]) failures.push(...dAggregateConsistent(actual[key], rows).map((f) => `${key}:${f}`));
  }
  check(name, failures.length === 0, failures.length ? failures.slice(0, 6).join(", ") : `${expectedKeys.length} cells`);
};
for (const [label, raw, published] of [
  ["Sonnet", v7.sonnet_full, canonical.panelD_fbs_run.sonnet5_full_suite],
  ["Haiku", v7.haiku_smoke, canonical.panelD_fbs_run.haiku45_smoke],
]) {
  const expectedRows = raw._meta.tasks * 3;
  check(`Panel D ${label} schema: complete unique mode/task rows`, raw.perTask.length === expectedRows &&
    uniqueTuples(raw.perTask, ["id", "mode"]) === expectedRows, `${raw.perTask.length}/${expectedRows}`);
  const modes = ["BASE", "FAB", "FAB_MEMORY"];
  const dByModeGroups = Object.fromEntries(modes.map((mode) => [mode, raw.perTask.filter((r) => r.mode === mode)]));
  dMapConsistent(`Panel D ${label} replay: raw byMode arithmetic`, raw.byMode, dByModeGroups);
  const dByTierModeGroups = {};
  for (const tier of [...new Set(raw.perTask.map((r) => r.tier))]) {
    for (const mode of modes) dByTierModeGroups[`t${tier}/${mode}`] = raw.perTask.filter((r) => r.tier === tier && r.mode === mode);
  }
  dMapConsistent(`Panel D ${label} replay: raw byTierMode arithmetic`, raw.byTierMode, dByTierModeGroups);
  const dByCatModeGroups = {};
  for (const cat of [...new Set(raw.perTask.map((r) => r.cat))]) {
    for (const mode of modes) dByCatModeGroups[`${cat}/${mode}`] = raw.perTask.filter((r) => r.cat === cat && r.mode === mode);
  }
  dMapConsistent(`Panel D ${label} replay: raw byCatMode arithmetic`, raw.byCatMode, dByCatModeGroups);
  const delta = (x, y, key) => round(x[key] - y[key]);
  const B = raw.byMode.BASE, F = raw.byMode.FAB, M = raw.byMode.FAB_MEMORY;
  const dDeltas = {
    FAB_vs_BASE: { total: delta(F, B, "total"), ...Object.fromEntries(DIMS.map((k) => [k, delta(F, B, k)])),
      check_rate: delta(F, B, "check_rate"), output_cut_pct: round(100 * (B.chars - F.chars) / B.chars, 1) },
    FABMEM_vs_FAB: { total: delta(M, F, "total"), ...Object.fromEntries(DIMS.map((k) => [k, delta(M, F, k)])),
      check_rate: delta(M, F, "check_rate") },
    FABMEM_vs_BASE: { total: delta(M, B, "total"), ...Object.fromEntries(DIMS.map((k) => [k, delta(M, B, k)])),
      check_rate: delta(M, B, "check_rate"), output_cut_pct: round(100 * (B.chars - M.chars) / B.chars, 1) },
  };
  exact(`Panel D ${label} replay: raw deltas`, raw.deltas, dDeltas);
  const judgeDiffs = raw.perTask.map((row) => {
    const values = Object.values(row.byJudge || {});
    return values.length === 2 ? Math.abs(values[0] - values[1]) : NaN;
  });
  const judgeAgreement = {
    mean_abs_total_diff: roundEven(judgeDiffs.reduce((sum, n) => sum + n, 0) / judgeDiffs.length),
    n_two_judge: judgeDiffs.length,
    n_one_judge: raw.perTask.filter((row) => Object.values(row.byJudge || {}).length === 1).length,
    scale: "0-28",
  };
  check(`Panel D ${label} replay: judge rows are complete`, judgeDiffs.every(Number.isFinite), `${judgeDiffs.length} rows`);
  exact(`Panel D ${label} replay: raw judge agreement`, raw.judgeAgreement, judgeAgreement);
  for (const mode of modes) {
    const compact = { rubric_28: raw.byMode[mode].total, check_rate_pct: raw.byMode[mode].check_rate, chars: raw.byMode[mode].chars };
    exact(`Panel D ${label} replay: ${mode}`, published.byMode[mode], compact);
  }
  exact(`Panel D ${label} replay: canonical deltas`, published.deltas, dDeltas);
}

// Evidence limits are part of the receipt contract, not buried in prose.
check("canonical receipt schema is versioned", canonical._meta.receipt_schema === "fabius-benchmark-receipt/v2",
  canonical._meta.receipt_schema || "missing");
check("historical answer/artifact absence is declared", Array.isArray(canonical._meta.receipt_limitations) &&
  canonical._meta.receipt_limitations.some((s) => /candidate answer text/i.test(s)) &&
  canonical._meta.receipt_limitations.some((s) => /execution artifacts|stdout/i.test(s)), "explicit limitations required");
check("Panel C is marked aggregate-only with no committed raw receipt",
  canonical.panelC_external_demos.raw === null && canonical.panelC_external_demos.receipt_status === "aggregate-only; not independently replayable",
  canonical.panelC_external_demos.receipt_status || "missing");

const answerObjects = (value) => {
  if (!value || typeof value !== "object") return 0;
  return (Object.hasOwn(value, "answer") ? 1 : 0) + Object.values(value).reduce((n, v) => n + answerObjects(v), 0);
};
const historicalAnswers = answerObjects(v5) + answerObjects(v6) + answerObjects(v7);

console.log("== fabius committed receipt replay ==\n");
for (const c of checks) console.log(`  ${c.pass ? "PASS" : "FAIL"}  ${c.name}${c.detail ? ` — ${c.detail}` : ""}`);
console.log(`\n  NOTE  historical v5/v6/v7 candidate answer objects committed: ${historicalAnswers}; limitations are declared, not reconstructed`);
const failed = checks.filter((c) => !c.pass).length;
console.log(`\n== ${checks.length - failed} passed · ${failed} failed ==`);
process.exitCode = failed ? 1 : 0;
