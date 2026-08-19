#!/usr/bin/env node
// © 2026 Ariel Shemesh · fabius · provenance fab1- · github.com/ArielShemesh1999/fabius
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
  "and ranked each other's answers blind. Deliver the single best FINAL answer — not a vote tally " +
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
// pull the first balanced {…} object out of a model reply (models wrap JSON in prose)
function extractJSON(text) {
  const s = text.indexOf("{");
  if (s < 0) return null;
  let depth = 0;
  for (let i = s; i < text.length; i++) {
    if (text[i] === "{") depth++;
    else if (text[i] === "}" && --depth === 0) {
      try { return JSON.parse(text.slice(s, i + 1)); } catch { return null; }
    }
  }
  return null;
}

// --- transport: one OpenRouter call -----------------------------------------------
const toMessages = (system, user) =>
  system ? [{ role: "system", content: system }, { role: "user", content: user }]
         : [{ role: "user", content: user }];

async function openrouterChat(model, messages) {
  const key = process.env.OPENROUTER_API_KEY;
  if (!key) throw new Error("OPENROUTER_API_KEY not set");
  const r = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${key}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "https://github.com/ArielShemesh1999/fabius",
      "X-Title": "fabius-concilium",
    },
    body: JSON.stringify({ model, messages }),
  });
  if (!r.ok) throw new Error(`${model} → HTTP ${r.status}: ${(await r.text()).slice(0, 200)}`);
  const j = await r.json();
  return j.choices?.[0]?.message?.content ?? "";
}

// --- stage 2: one reviewer ranks the field, blind ---------------------------------
async function review(reviewerModel, question, opinions, chat, rnd) {
  const order = shuffle(opinions, rnd);                       // shuffle per reviewer — position carries no signal
  const labels = order.map((_, i) => `Response ${i + 1}`);
  const labelToModel = {};
  order.forEach((o, i) => (labelToModel[labels[i]] = o.model));
  const body = order.map((o, i) => `--- ${labels[i]} ---\n${o.answer}`).join("\n\n");
  const user =
    `Original question:\n${question}\n\nThe responses to rank:\n${body}\n\n` +
    `Rank ALL responses best-to-worst. Reply ONLY with compact JSON: ` +
    `{"ranking":[${labels.map((l) => `"${l}"`).join(",")}],"reasons":{"<label>":"<one line>"}}`;

  let parsed = extractJSON(await chat(reviewerModel, REVIEW_SYS, user));
  if (!parsed || !Array.isArray(parsed.ranking))                // retry once on malformed output
    parsed = extractJSON(await chat(reviewerModel, REVIEW_SYS, user + "\n\nJSON only, no prose."));

  let ranking = parsed && Array.isArray(parsed.ranking) ? parsed.ranking.filter((l) => labelToModel[l]) : [];
  ranking = [...new Set(ranking)];                                     // dedupe — a repeated label must not double-count (would skew/negate Borda)
  for (const l of labels) if (!ranking.includes(l)) ranking.push(l);   // fill any missing → exactly K distinct positions
  const reasonsByLabel = (parsed && parsed.reasons) || {};
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
async function runCouncil({ question, seats, chairman, chat, rnd, log = () => {} }) {
  // stage 1 — first opinions, parallel & independent; a dead seat is dropped, never blank
  const settled = await Promise.allSettled(seats.map((m) => chat(m, "", question)));
  const opinions = [];
  settled.forEach((s, i) =>
    s.status === "fulfilled"
      ? opinions.push({ model: seats[i], answer: s.value })
      : log(`seat dropped: ${seats[i]} — ${s.reason.message}`)
  );
  assert(opinions.length >= 2, `council needs ≥2 live seats, got ${opinions.length}`);
  const models = opinions.map((o) => o.model);

  // stage 2 — blind peer-review (real barrier: needs all of stage 1)
  const ballots = await Promise.all(models.map((m) => review(m, question, opinions, chat, rnd)));
  const leaderboard = borda(ballots, models);

  // stage 3 — chairman fuses the field
  const final = await chair(chairman, question, opinions, leaderboard, chat);
  return { question, seats: models, chairman, first_opinions: opinions, leaderboard, final };
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
  const fake = async (model, system, user) => {
    calls++;
    if (system.includes("impartial judge")) {
      const labels = [...user.matchAll(/Response \d+/g)].map((m) => m[0]);
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
  // self-exclusion through the real path: prov/b's own ballot must award prov/b zero
  assert(borda([rev], ["prov/a", "prov/b", "prov/c"]).find((x) => x.model === "prov/b").points === 0,
    "borda: a reviewer's own ballot gives itself 0 points (self excluded on the integrated path)");

  // regression for the duplicate-label bug: a repeated label must not corrupt the count or go negative
  const dupFake = async (model, system, user) => {
    if (system.includes("impartial judge")) {
      const labels = [...user.matchAll(/Response \d+/g)].map((m) => m[0]);
      return JSON.stringify({ ranking: [labels[0], labels[0], ...labels], reasons: {} }); // repeats Response 1
    }
    return system.includes("chairman") ? "x" : "stub";
  };
  const revDup = await review("prov/a", "q?", trio, dupFake, mulberry32(1));
  assert(revDup.order.length === 3 && new Set(revDup.order).size === 3, "review: dedupes a repeated label to exactly K distinct");
  assert(borda([revDup], ["prov/a", "prov/b", "prov/c"]).every((r) => r.points >= 0), "borda: duplicate labels never produce a negative score");

  // full pipeline: shape + call accounting (reset the counter — earlier review() probes shared `fake`)
  const seats = ["prov/a", "prov/b", "prov/c"];
  calls = 0;
  const r = await runCouncil({ question: "q?", seats, chairman: "prov/chair", chat: fake, rnd: mulberry32(42) });
  assert(r.first_opinions.length === 3, "pipeline: 3 first opinions");
  assert(r.leaderboard.length === 3, "pipeline: 3-row leaderboard");
  assert(r.final.startsWith("SYNTH"), "pipeline: chairman produced the final");
  assert(calls === seats.length * 2 + 1, `pipeline: ${calls} calls should equal N*2+1 = 7`);
  console.log("selftest PASS — Borda + self-exclusion + de-shuffle round-trip + duplicate-label dedupe + N*2+1 call accounting");
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
  const chat = (m, s, u) => openrouterChat(m, toMessages(s, u));
  console.error(`convening ${seats.length} seats + chairman → ${seats.length * 2 + 1} model calls`);
  try {
    const r = await runCouncil({ question, seats, chairman, chat, rnd: mulberry32(Math.floor(Math.random() * 2 ** 32)), log: (m) => console.error(m) });
    jsonOut ? console.log(JSON.stringify(r, null, 2)) : printReport(r);
  } catch (e) { console.error("council failed:", e.message); process.exit(1); }
}

// run the CLI only when invoked as a script — `import`ing this module stays side-effect-free
if (import.meta.url === pathToFileURL(process.argv[1] || "").href) main();

export { runCouncil, borda, review, chair, extractJSON, shuffle, mulberry32, openrouterChat };
