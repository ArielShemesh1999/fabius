#!/usr/bin/env node
// © 2026 Ariel Shemesh · fabius · provenance fab1- · github.com/shear559/fabius
//
// fabius-concilium — a runnable reference for the cross-model council.
//
// Convene N heterogeneous models on one question, then aggregate their answers into one:
//   stage 1  first opinions    — every seat answers the question independently (parallel)
//   stage 2  blind peer-review — each seat ranks all answers, identities stripped (own included; self-scores dropped at tally)
//   stage 3  chairman synthesis— one model fuses the ranked field into the final answer
//
// Zero dependencies (Node ≥18, native fetch). Every model through ONE OpenRouter key — same
// gateway karpathy's llm-council uses, so seat diversity costs no extra plumbing. The protocol
// is provider-agnostic: the identical three stages run over any harness or gateway that can
// reach several models — only the transport changes. Spec + exact prompts: ./council-protocol.md
//
// Usage:
//   node council.mjs --selftest                     # wiring + Borda check — no key, no network, no cost
//   export OPENROUTER_API_KEY=sk-or-...
//   export COUNCIL_MODELS=anthropic/claude-sonnet-5,openai/gpt-5.6-terra,google/gemini-3.1-pro-preview,mistralai/mistral-large
//   export COUNCIL_CHAIRMAN=anthropic/claude-opus-5
//   node council.mjs "Should a 3-person startup use a monolith or microservices?"
//   node council.mjs --json "..."   > run.json

import { pathToFileURL } from "node:url"; // node builtin — still zero npm dependencies

const DEFAULT_SEATS = "anthropic/claude-sonnet-5,openai/gpt-5.6-terra,google/gemini-3.1-pro-preview"; // fabius roster seats, odd count for tie-breaks; widen via COUNCIL_MODELS (e.g. add mistralai/mistral-large)
const DEFAULT_CHAIR = "anthropic/claude-opus-5";

const REVIEW_SYS =
  "You are a strict, impartial judge on a council of AI models. You are NOT told which model " +
  "wrote which response. Judge ONLY on accuracy, completeness, and insight — never on style, " +
  "length, or tone.";
const CHAIR_SYS =
  "You are the chairman of a council of AI models. The council answered a question independently " +
  "and ranked all anonymized answers blind, with each reviewer's self-score excluded by the backend. " +
  "Deliver the single best FINAL answer — not a vote tally " +
  "and not a copy of the top-ranked response. Take the strongest correct points, resolve the " +
  "contradictions the council exposed, correct any majority error you can verify, and explicitly " +
  "flag anything the council genuinely split on. Accurate first, then concise.";

// --- helpers ----------------------------------------------------------------------
const assert = (cond, msg) => { if (!cond) throw new Error(msg); };

// deterministic PRNG (seedable) so --selftest reproduces; real runs get a random seed
function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function shuffle(arr, rnd) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
// Pull the first valid balanced {…} object out of a model reply (models sometimes wrap
// JSON in prose). Braces inside JSON strings are data, not structure; escaped quotes do
// not end a string. Try the whole reply first so strict-schema output takes the shortest
// path, then inspect each prose-embedded object candidate without repairing its content.
function extractJSON(text) {
  const source = String(text ?? "");
  try { return JSON.parse(source.trim()); } catch { /* prose-wrapped or invalid */ }

  for (let start = source.indexOf("{"); start >= 0; start = source.indexOf("{", start + 1)) {
    let depth = 0;
    let inString = false;
    let escaped = false;
    for (let i = start; i < source.length; i++) {
      const ch = source[i];
      if (inString) {
        if (escaped) escaped = false;
        else if (ch === "\\") escaped = true;
        else if (ch === '"') inString = false;
        continue;
      }
      if (ch === '"') inString = true;
      else if (ch === "{") depth++;
      else if (ch === "}" && --depth === 0) {
        try { return JSON.parse(source.slice(start, i + 1)); } catch { break; }
      }
    }
  }
  return null;
}

function ballotSchema(labels) {
  return {
    type: "object",
    additionalProperties: false,
    required: ["ranking", "reasons"],
    properties: {
      ranking: {
        type: "array",
        minItems: labels.length,
        maxItems: labels.length,
        uniqueItems: true,
        items: { type: "string", enum: labels },
      },
      reasons: {
        type: "object",
        additionalProperties: false,
        required: labels,
        properties: Object.fromEntries(labels.map((label) => [label, { type: "string", minLength: 1 }])),
      },
    },
  };
}

function reviewRequest(labels) {
  return {
    response_format: {
      type: "json_schema",
      json_schema: { name: "council_ballot", strict: true, schema: ballotSchema(labels) },
    },
    provider: { require_parameters: true },
  };
}

function exactBallot(parsed, labels) {
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return false;
  const topKeys = Object.keys(parsed).sort();
  if (topKeys.length !== 2 || topKeys[0] !== "ranking" || topKeys[1] !== "reasons") return false;
  if (!Array.isArray(parsed.ranking) || parsed.ranking.length !== labels.length) return false;
  if (new Set(parsed.ranking).size !== labels.length || !labels.every((label) => parsed.ranking.includes(label))) return false;
  if (!parsed.reasons || typeof parsed.reasons !== "object" || Array.isArray(parsed.reasons)) return false;
  const reasonKeys = Object.keys(parsed.reasons);
  return reasonKeys.length === labels.length &&
    labels.every((label) => typeof parsed.reasons[label] === "string" && parsed.reasons[label].trim().length > 0);
}

// --- transport: one OpenRouter call -----------------------------------------------
const toMessages = (system, user) =>
  system ? [{ role: "system", content: system }, { role: "user", content: user }]
         : [{ role: "user", content: user }];

async function openrouterChat(model, messages, request = {}) {
  const key = process.env.OPENROUTER_API_KEY;
  if (!key) throw new Error("OPENROUTER_API_KEY not set");
  const r = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${key}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "https://github.com/shear559/fabius",
      "X-Title": "fabius-concilium",
    },
    body: JSON.stringify({ ...request, model, messages }),
  });
  if (!r.ok) throw new Error(`${model} → HTTP ${r.status}: ${(await r.text()).slice(0, 200)}`);
  const j = await r.json();
  const content = j.choices?.[0]?.message?.content;
  if (typeof content !== "string" || !content.trim()) throw new Error(`${model} → empty completion content`);
  return content;
}

async function preflightOpenRouterRoster({ seats, chairman, fetchImpl = fetch }) {
  const key = process.env.OPENROUTER_API_KEY;
  const headers = key ? { Authorization: `Bearer ${key}` } : {};
  const r = await fetchImpl("https://openrouter.ai/api/v1/models", { headers });
  if (!r.ok) throw new Error(`roster preflight → HTTP ${r.status}: ${(await r.text()).slice(0, 200)}`);
  const payload = await r.json();
  const live = new Set((payload.data || []).map((entry) => entry?.id).filter(Boolean));
  const requested = [...new Set([...seats, chairman])];
  const missing = requested.filter((model) => !live.has(model));
  if (missing.length) throw new Error(`unknown OpenRouter model id(s): ${missing.join(", ")}`);
  return requested;
}

// --- stage 2: one reviewer ranks the field, blind ---------------------------------
async function review(reviewerModel, question, opinions, chat, rnd, onRetry = () => {}) {
  const order = shuffle(opinions, rnd);                       // shuffle per reviewer — position carries no signal
  const labels = order.map((_, i) => `Response ${i + 1}`);
  const labelToModel = {};
  order.forEach((o, i) => (labelToModel[labels[i]] = o.model));
  const body = order.map((o, i) => `--- ${labels[i]} ---\n${o.answer}`).join("\n\n");
  const user =
    `Original question:\n${question}\n\nThe responses to rank:\n${body}\n\n` +
    `Rank ALL responses best-to-worst. Reply ONLY with compact JSON: ` +
    `{"ranking":["<best label>","...","<worst label>"],"reasons":{"<label>":"<one line for every label>"}}`;

  const request = reviewRequest(labels);
  let parsed = extractJSON(await chat(reviewerModel, REVIEW_SYS, user, request));
  if (!exactBallot(parsed, labels)) {
    onRetry(reviewerModel);
    parsed = extractJSON(await chat(reviewerModel, REVIEW_SYS, user + "\n\nYour previous ballot was invalid. Return the exact schema only.", request));
  }
  if (!exactBallot(parsed, labels)) return null;

  const ranking = parsed.ranking;
  const reasonsByLabel = parsed.reasons;
  const reasons = {};
  for (const l of labels) reasons[labelToModel[l]] = reasonsByLabel[l] || "";
  return { reviewer: reviewerModel, order: ranking.map((l) => labelToModel[l]), reasons };
}

// --- aggregation: Borda count over the ballots, self-votes excluded ---------------
function borda(ballots, models) {
  const K = models.length;
  const score = Object.fromEntries(models.map((m) => [m, 0]));
  const reasons = Object.fromEntries(models.map((m) => [m, []]));
  for (const b of ballots) {
    b.order.forEach((m, pos) => {
      if (m === b.reviewer) return;                            // a seat never lifts itself
      score[m] += K - 1 - pos;
    });
    for (const m of models) if (b.reasons?.[m]) reasons[m].push(b.reasons[m]);
  }
  return models
    .map((m) => ({ model: m, points: score[m], reasons: reasons[m] }))
    .sort((a, b) => b.points - a.points);
}

// --- stage 3: chairman synthesis --------------------------------------------------
async function chair(chairman, question, opinions, leaderboard, chat) {
  const responses = opinions.map((o) => `--- ${o.model} ---\n${o.answer}`).join("\n\n");
  const board = leaderboard
    .map((e, i) => `${i + 1}. ${e.model} — ${e.points} pts — ${e.reasons[0] || ""}`)
    .join("\n");
  const user =
    `Question:\n${question}\n\nCouncil responses:\n${responses}\n\n` +
    `Blind ranking leaderboard (peer-reviewed, self-votes excluded):\n${board}\n\nWrite the final answer.`;
  return chat(chairman, CHAIR_SYS, user);
}

// --- the council ------------------------------------------------------------------
function resetCallAccounting(configuredSeats, accounting = {}) {
  Object.assign(accounting, {
    configured_seats: configuredSeats,
    live_seats: 0,
    retries: 0,
    actual: 0,
    clean_all_live: configuredSeats * 2 + 1,
    max: configuredSeats * 3 + 1,
  });
  return accounting;
}

async function runCouncil({ question, seats, chairman, chat, rnd, log = () => {}, accounting = {} }) {
  assert(typeof question === "string" && question.trim(), "council question must be a non-empty string");
  assert(Array.isArray(seats) && seats.length >= 2, "council needs at least two configured seats");
  const seatIds = seats.map((seat) => typeof seat === "string" ? seat.trim() : "");
  assert(seatIds.every(Boolean), "council seat ids must be non-empty strings");
  assert(seatIds.every((seat, i) => seat === seats[i]), "council seat ids must not carry surrounding whitespace");
  assert(new Set(seatIds).size === seatIds.length, "council seat ids must be distinct");
  assert(typeof chairman === "string" && chairman.trim(), "council chairman id must be a non-empty string");
  assert(typeof chat === "function", "council chat transport must be a function");
  assert(typeof rnd === "function", "council random source must be a function");

  const calls = resetCallAccounting(seats.length, accounting);
  const countedChat = async (...args) => {
    calls.actual++;
    return await chat(...args);
  };

  // stage 1 — first opinions, parallel & independent; a dead seat is dropped, never blank
  const settled = await Promise.allSettled(seats.map((m) => countedChat(m, "", question)));
  const opinions = [];
  settled.forEach((result, i) => {
    if (result.status === "fulfilled" && typeof result.value === "string" && result.value.trim()) {
      opinions.push({ model: seats[i], answer: result.value.trim() });
    }
    else if (result.status === "fulfilled") log(`seat dropped: ${seats[i]} — empty opinion`);
    else log(`seat dropped: ${seats[i]} — ${result.reason?.message || result.reason}`);
  });
  calls.live_seats = opinions.length;
  assert(opinions.length >= 2, `council needs ≥2 live seats, got ${opinions.length}`);
  const models = opinions.map((o) => o.model);

  // stage 2 — blind peer-review (real barrier: needs all of stage 1)
  const reviewed = await Promise.allSettled(models.map((m) =>
    review(m, question, opinions, countedChat, rnd, () => { calls.retries++; })));
  const ballots = [];
  reviewed.forEach((result, i) => {
    if (result.status === "fulfilled" && result.value) ballots.push(result.value);
    else if (result.status === "fulfilled") log(`reviewer dropped: ${models[i]} — invalid ballot after retry`);
    else log(`reviewer dropped: ${models[i]} — ${result.reason?.message || result.reason}`);
  });
  assert(ballots.length >= 1, "council has no valid review ballots after retry");
  const leaderboard = borda(ballots, models);

  // stage 3 — chairman fuses the field
  const finalRaw = await chair(chairman, question, opinions, leaderboard, countedChat);
  assert(typeof finalRaw === "string" && finalRaw.trim(), "chairman returned an empty final answer");
  const final = finalRaw.trim();
  const expected = calls.configured_seats + calls.live_seats + calls.retries + 1;
  assert(calls.actual === expected, `call accounting drift: actual ${calls.actual}, formula ${expected}`);
  assert(calls.actual <= calls.max, `call cap exceeded: actual ${calls.actual}, max ${calls.max}`);
  return {
    question, seats: models, chairman, call_accounting: { ...calls },
    first_opinions: opinions, valid_ballots: ballots.length, leaderboard, final,
  };
}

// --- pretty report ----------------------------------------------------------------
function printReport(r) {
  console.log(`\n${"═".repeat(64)}\nFINAL — chairman ${r.chairman}\n${"═".repeat(64)}\n${r.final}\n`);
  console.log(`${"─".repeat(64)}\nBlind leaderboard (self-votes excluded)\n${"─".repeat(64)}`);
  r.leaderboard.forEach((e, i) => console.log(`  ${i + 1}. ${e.model.padEnd(34)} ${e.points} pts`));
  console.log(`\n${"─".repeat(64)}\nFirst opinions\n${"─".repeat(64)}`);
  r.first_opinions.forEach((o) => console.log(`\n### ${o.model}\n${o.answer}`));
}

// --- selftest: no key, no network — proves the math + the pipeline shape -----------
async function selftest() {
  // unit: Borda with a hand-computed expected result (self-votes excluded)
  const lb = borda(
    [
      { reviewer: "A", order: ["B", "C", "A"], reasons: {} }, // B:2 C:1 (A self-skip)
      { reviewer: "B", order: ["A", "B", "C"], reasons: {} }, // A:2 C:0 (B self-skip)
      { reviewer: "C", order: ["A", "B", "C"], reasons: {} }, // A:2 B:1 (C self-skip)
    ],
    ["A", "B", "C"]
  );
  assert(lb[0].model === "A" && lb[0].points === 4, "borda: A should total 4");
  assert(lb.find((x) => x.model === "B").points === 3, "borda: B should total 3");
  assert(lb.find((x) => x.model === "C").points === 1, "borda: C should total 1");

  // pipeline: a fake transport that detects the stage from the system prompt
  let calls = 0;
  let capturedRequest;
  const fake = async (model, system, user, request) => {
    calls++;
    if (system.includes("impartial judge")) {
      capturedRequest = request;
      const labels = [...new Set([...user.matchAll(/Response \d+/g)].map((m) => m[0]))];
      return JSON.stringify({ ranking: labels, reasons: Object.fromEntries(labels.map((l) => [l, "ok"])) });
    }
    if (system.includes("chairman")) return "SYNTH: the synthesized final answer.";
    return `[${model}] stub answer.`;
  };
  const trio = [{ model: "prov/a", answer: "A" }, { model: "prov/b", answer: "B" }, { model: "prov/c", answer: "C" }];

  // integrated review(): de-anonymization must round-trip to a full distinct permutation of the seats
  const rev = await review("prov/b", "q?", trio, fake, mulberry32(7));
  assert(rev.order.length === 3 && new Set(rev.order).size === 3, "review: de-shuffle round-trips to a full distinct permutation");
  assert(rev.order.every((m) => ["prov/a", "prov/b", "prov/c"].includes(m)), "review: maps every label back to a real seat (no undefined)");
  const responseSchema = capturedRequest?.response_format?.json_schema;
  assert(responseSchema?.strict === true, "review: requests strict JSON Schema output");
  assert(capturedRequest?.provider?.require_parameters === true, "review: rejects providers that ignore the schema");
  assert(responseSchema.schema.properties.ranking.uniqueItems === true && responseSchema.schema.properties.ranking.minItems === 3,
    "review: schema requires exactly K unique labels");
  const braceLabels = ["Response 1", "Response 2"];
  const braceBallot = JSON.stringify({
    ranking: braceLabels,
    reasons: { "Response 1": "remove the stray }", "Response 2": "keep the literal { example" },
  });
  assert(exactBallot(extractJSON(braceBallot), braceLabels),
    "review: JSON string braces remain data and do not consume a valid exact ballot");
  assert(exactBallot(extractJSON(`preface ${braceBallot} suffix`), braceLabels),
    "review: a valid exact ballot can be extracted from prose without miscounting string braces");
  assert(!exactBallot({ ...JSON.parse(braceBallot), winner: "Response 1" }, braceLabels),
    "review: an extra top-level property is not an exact-schema ballot");
  // self-exclusion through the real path: prov/b's own ballot must award prov/b zero
  assert(borda([rev], ["prov/a", "prov/b", "prov/c"]).find((x) => x.model === "prov/b").points === 0,
    "borda: a reviewer's own ballot gives itself 0 points (self excluded on the integrated path)");

  // malformed, partial, or duplicate ballots retry once and are dropped; labels are never filled in.
  let invalidCalls = 0;
  const duplicateFake = async (model, system, user) => {
    invalidCalls++;
    const labels = [...new Set([...user.matchAll(/Response \d+/g)].map((m) => m[0]))];
    return JSON.stringify({ ranking: [labels[0], labels[0], labels[2]], reasons: Object.fromEntries(labels.map((l) => [l, "ok"])) });
  };
  assert(await review("prov/a", "q?", trio, duplicateFake, mulberry32(1)) === null,
    "review: duplicate ballot is dropped, not repaired");
  assert(invalidCalls === 2, "review: duplicate ballot gets exactly one retry");

  invalidCalls = 0;
  const partialFake = async (model, system, user) => {
    invalidCalls++;
    const labels = [...new Set([...user.matchAll(/Response \d+/g)].map((m) => m[0]))];
    return JSON.stringify({ ranking: labels.slice(0, 2), reasons: Object.fromEntries(labels.map((l) => [l, "ok"])) });
  };
  assert(await review("prov/a", "q?", trio, partialFake, mulberry32(1)) === null,
    "review: partial ballot is dropped, not completed with invented positions");
  assert(invalidCalls === 2, "review: partial ballot gets exactly one retry");

  invalidCalls = 0;
  const malformedFake = async () => { invalidCalls++; return "not json"; };
  assert(await review("prov/a", "q?", trio, malformedFake, mulberry32(1)) === null,
    "review: malformed ballot is dropped after retry");
  assert(invalidCalls === 2, "review: malformed ballot gets exactly one retry");

  // full pipeline: shape + clean-path call accounting (reset the counter — earlier review() probes shared `fake`)
  const seats = ["prov/a", "prov/b", "prov/c"];
  calls = 0;
  const r = await runCouncil({ question: "q?", seats, chairman: "prov/chair", chat: fake, rnd: mulberry32(42) });
  assert(r.first_opinions.length === 3, "pipeline: 3 first opinions");
  assert(r.leaderboard.length === 3, "pipeline: 3-row leaderboard");
  assert(r.valid_ballots === 3, "pipeline: reports 3 valid ballots");
  assert(r.final.startsWith("SYNTH"), "pipeline: chairman produced the final");
  assert(calls === 7 && r.call_accounting.actual === 7, "pipeline: clean all-live path uses 2N+1 = 7 calls");
  assert(r.call_accounting.retries === 0 && r.call_accounting.max === 10,
    "pipeline: clean path reports zero retries and reserves the 3N+1 = 10 cap");

  // A reviewer transport failure is isolated by allSettled; the other exact ballots still count.
  const drops = [];
  const flaky = async (model, system, user) => {
    if (system.includes("impartial judge") && model === "prov/b") throw new Error("review unavailable");
    if (system.includes("impartial judge")) {
      const labels = [...new Set([...user.matchAll(/Response \d+/g)].map((m) => m[0]))];
      return JSON.stringify({ ranking: labels, reasons: Object.fromEntries(labels.map((l) => [l, "ok"])) });
    }
    if (system.includes("chairman")) return "SYNTH: survived one reviewer failure.";
    return `[${model}] stub answer.`;
  };
  const resilient = await runCouncil({ question: "q?", seats, chairman: "prov/chair", chat: flaky, rnd: mulberry32(8), log: (m) => drops.push(m) });
  assert(resilient.valid_ballots === 2 && resilient.final.startsWith("SYNTH"), "pipeline: one failed reviewer does not abort the council");
  assert(drops.some((line) => line.includes("prov/b") && line.includes("review unavailable")), "pipeline: failed reviewer is logged");

  // A fulfilled transport response is not automatically a live opinion. Empty or
  // non-string content is a dead seat and must be dropped before labels and ballots exist.
  const emptyDrops = [];
  const oneEmpty = async (model, system, user) => {
    if (!system && model === "prov/c") return "   ";
    if (system.includes("impartial judge")) {
      const labels = [...new Set([...user.matchAll(/Response \d+/g)].map((m) => m[0]))];
      return JSON.stringify({ ranking: labels, reasons: Object.fromEntries(labels.map((l) => [l, "ok"])) });
    }
    if (system.includes("chairman")) return "SYNTH: ignored an empty seat.";
    return `[${model}] live opinion.`;
  };
  const withoutEmpty = await runCouncil({ question: "q?", seats, chairman: "prov/chair", chat: oneEmpty, rnd: mulberry32(11), log: (m) => emptyDrops.push(m) });
  assert(withoutEmpty.first_opinions.length === 2 && !withoutEmpty.seats.includes("prov/c"),
    "pipeline: fulfilled empty content is dropped instead of becoming a live seat");
  assert(withoutEmpty.call_accounting.live_seats === 2 && withoutEmpty.call_accounting.actual === 6,
    "pipeline: accounting uses only two live seats after an empty opinion");
  assert(emptyDrops.some((line) => line.includes("prov/c") && line.includes("empty opinion")),
    "pipeline: empty opinion drop is logged");

  const invalidDrops = [];
  const oneInvalid = async (model, system, user) => {
    if (system.includes("impartial judge") && model === "prov/b") return "{}";
    if (system.includes("impartial judge")) {
      const labels = [...new Set([...user.matchAll(/Response \d+/g)].map((m) => m[0]))];
      return JSON.stringify({ ranking: labels, reasons: Object.fromEntries(labels.map((l) => [l, "ok"])) });
    }
    if (system.includes("chairman")) return "SYNTH: dropped one invalid ballot.";
    return `[${model}] stub answer.`;
  };
  const exactOnly = await runCouncil({ question: "q?", seats, chairman: "prov/chair", chat: oneInvalid, rnd: mulberry32(9), log: (m) => invalidDrops.push(m) });
  assert(exactOnly.valid_ballots === 2, "pipeline: invalid ballot is absent from the tally after one retry");
  assert(invalidDrops.some((line) => line.includes("prov/b") && line.includes("invalid ballot after retry")),
    "pipeline: invalid ballot drop is logged");
  assert(exactOnly.call_accounting.actual === 8 && exactOnly.call_accounting.retries === 1,
    "pipeline: one invalid reviewer consumes one retry, is dropped, and reports N+M+R+1 = 8 actual calls");

  // Every reviewer returns malformed output once, then a valid exact ballot. This forces the
  // retry ceiling: N first opinions + N reviews + N retries + one chair = 3N+1.
  const retryAttempts = new Map();
  const retryAll = async (model, system, user) => {
    if (system.includes("impartial judge")) {
      const attempt = (retryAttempts.get(model) || 0) + 1;
      retryAttempts.set(model, attempt);
      if (attempt === 1) return "not json";
      const labels = [...new Set([...user.matchAll(/Response \d+/g)].map((m) => m[0]))];
      return JSON.stringify({ ranking: labels, reasons: Object.fromEntries(labels.map((l) => [l, "ok"])) });
    }
    if (system.includes("chairman")) return "SYNTH: all retry ballots recovered.";
    return `[${model}] stub answer.`;
  };
  const atCap = await runCouncil({ question: "q?", seats, chairman: "prov/chair", chat: retryAll, rnd: mulberry32(10) });
  assert(atCap.valid_ballots === 3 && atCap.call_accounting.retries === 3,
    "pipeline: each malformed first ballot retries exactly once and recovers");
  assert(atCap.call_accounting.actual === 10 && atCap.call_accounting.actual === atCap.call_accounting.max,
    "pipeline: all three retries reach, but never exceed, the 3N+1 cap");

  // Roster shape is rejected before the first paid call. Duplicate reviewer identities
  // make every rank look like a self-vote; blank ids cannot be attributed or audited.
  let preflightCalls = 0;
  const shouldNotCall = async () => { preflightCalls++; return "unexpected"; };
  for (const invalidSeats of [["same/model", "same/model"], ["prov/a", ""]]) {
    let rejected = false;
    try {
      await runCouncil({ question: "q?", seats: invalidSeats, chairman: "prov/chair", chat: shouldNotCall, rnd: mulberry32(12) });
    } catch (e) {
      rejected = /distinct|non-empty/.test(e.message);
    }
    assert(rejected, `preflight: invalid seat roster ${JSON.stringify(invalidSeats)} is rejected`);
  }
  assert(preflightCalls === 0, "preflight: invalid seat rosters spend zero completion calls");

  const emptyChair = async (model, system, user) => {
    if (system.includes("impartial judge")) {
      const labels = [...new Set([...user.matchAll(/Response \d+/g)].map((m) => m[0]))];
      return JSON.stringify({ ranking: labels, reasons: Object.fromEntries(labels.map((l) => [l, "ok"])) });
    }
    if (system.includes("chairman")) return "";
    return `[${model}] live opinion.`;
  };
  let emptyChairRejected = false;
  try { await runCouncil({ question: "q?", seats, chairman: "prov/chair", chat: emptyChair, rnd: mulberry32(13) }); }
  catch (e) { emptyChairRejected = e.message.includes("empty final answer"); }
  assert(emptyChairRejected, "pipeline: an empty chairman completion cannot be reported as a final answer");

  // The live roster is resolved before spending any model calls.
  const modelList = async () => ({ ok: true, json: async () => ({ data: [...seats, "prov/chair"].map((id) => ({ id })) }) });
  const roster = await preflightOpenRouterRoster({ seats, chairman: "prov/chair", fetchImpl: modelList });
  assert(roster.length === 4, "preflight: resolves every unique seat and chair id");
  let missingRejected = false;
  try { await preflightOpenRouterRoster({ seats, chairman: "prov/missing", fetchImpl: modelList }); }
  catch (e) { missingRejected = e.message.includes("prov/missing"); }
  assert(missingRejected, "preflight: rejects an unknown model id before the run");

  console.log("selftest PASS — string-safe strict JSON + exact-ballot retry/drop + empty-seat isolation + distinct-roster preflight + Borda + N+M+R+1 actual / 3N+1 cap");
}

// --- main: CLI only when run directly, so the exports import cleanly elsewhere -----
async function main() {
  const args = process.argv.slice(2);
  if (args.includes("--selftest")) {
    try { await selftest(); process.exit(0); }
    catch (e) { console.error("selftest FAIL:", e.message); process.exit(1); }
    return;
  }
  const jsonOut = args.includes("--json");
  const question = args.filter((a) => !a.startsWith("--")).join(" ").trim();
  if (!question) {
    console.error('usage: node council.mjs [--json] "your question"   |   node council.mjs --selftest');
    process.exit(1);
  }
  const seats = (process.env.COUNCIL_MODELS || DEFAULT_SEATS).split(",").map((s) => s.trim()).filter(Boolean);
  const chairman = process.env.COUNCIL_CHAIRMAN || DEFAULT_CHAIR;
  const chat = (m, s, u, request) => openrouterChat(m, toMessages(s, u), request);
  const accounting = resetCallAccounting(seats.length);
  console.error(`convening ${seats.length} seats + chairman → completion-call budget: clean all-live ${accounting.clean_all_live}; retry cap ${accounting.max}`);
  try {
    await preflightOpenRouterRoster({ seats, chairman });
    const r = await runCouncil({ question, seats, chairman, chat, rnd: mulberry32(Math.floor(Math.random() * 2 ** 32)), log: (m) => console.error(m), accounting });
    console.error(`completion calls actual: ${accounting.actual} = N ${accounting.configured_seats} + M ${accounting.live_seats} + R ${accounting.retries} + chair 1 (cap ${accounting.max})`);
    jsonOut ? console.log(JSON.stringify(r, null, 2)) : printReport(r);
  } catch (e) {
    console.error(`completion calls before failure: ${accounting.actual} (retries ${accounting.retries}; cap ${accounting.max})`);
    console.error("council failed:", e.message);
    process.exit(1);
  }
}

// run the CLI only when invoked as a script — `import`ing this module stays side-effect-free
if (import.meta.url === pathToFileURL(process.argv[1] || "").href) main();

export { runCouncil, borda, review, chair, extractJSON, exactBallot, ballotSchema, reviewRequest, shuffle, mulberry32, openrouterChat, preflightOpenRouterRoster, resetCallAccounting };
