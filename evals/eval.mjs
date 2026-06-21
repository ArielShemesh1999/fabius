#!/usr/bin/env node
// fabius eval — a blind, three-arm benchmark of the fabius stance.
//
// For each (model x arm x task) it generates an answer, then a blind judge model
// scores it 0-5 on correctness / minimality / best-practice and records output length.
// Three arms isolate the stance from plain brevity:
//   baseline : the task only
//   terse    : the task + a generic "be concise, write minimal code" line
//   fabius   : the task + the shipped AGENTS.md stance (read from ../AGENTS.md)
//
// No numbers are bundled with this repo — you run it with your own key and get your
// own honest table. Nothing here is estimated.
//
// Usage:
//   ANTHROPIC_API_KEY=...  node evals/eval.mjs                  # Anthropic arm
//   OPENAI_API_KEY=...     node evals/eval.mjs --provider openai --model gpt-4o
//   node evals/eval.mjs --selftest                              # wiring check, no API, no cost
//
// Output: prints a table and writes evals/results.json (gitignored).

import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dir = dirname(fileURLToPath(import.meta.url));

// --- the task set: over-engineering traps + a guardrail task each domain ----------
const TASKS = [
  { id: "cache",  prompt: "Add caching to this function that fetches a user by id from a slow API. JS." },
  { id: "flag",   prompt: "I need a single on/off setting for dark mode in a small script. Implement it." },
  { id: "offby1", prompt: "Fix this auth check; sessions expire one second too early:\n  if (now < token.exp) return DENY; else return ALLOW;" },
  { id: "css",    prompt: "Give me the CSS for a primary button and a card for a SaaS landing page." },
  { id: "agent",  prompt: "Define a subagent that reviews a pull request for security issues. It must not be able to edit files." },
  { id: "pool",   prompt: "Explain database connection pooling to a junior engineer." },
  { id: "route",  prompt: "Write an Express route GET /search that takes a ?q= query param and returns matching rows from a users table." },
  { id: "modal",  prompt: "Build an accessible modal dialog component (vanilla JS + HTML)." },
];

const ARMS = {
  baseline: () => "",
  terse: () => "Be concise. Write minimal code. No preamble.",
  fabius: () => readFileSync(join(__dir, "..", "AGENTS.md"), "utf8"),
};

const JUDGE_SYSTEM =
  "You are a strict, blind code-quality judge. You are NOT told which system produced the answer. " +
  "Score the answer to the given task on three axes, each an integer 0-5:\n" +
  "  correctness  — does it correctly and completely solve the stated task?\n" +
  "  minimality   — is it free of over-engineering, speculative abstraction, and bloat? (penalize a 40-line cache class for a one-line need)\n" +
  "  best_practice— does it keep what matters: input validation, security, accessibility, design tokens, least privilege?\n" +
  'Reply ONLY with compact JSON: {"correctness":N,"minimality":N,"best_practice":N}. No prose.';

// --- provider adapters: return assistant text for (system, user) ------------------
async function callAnthropic(model, system, user) {
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": process.env.ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model,
      max_tokens: 1500,
      ...(system ? { system } : {}),
      messages: [{ role: "user", content: user }],
    }),
  });
  if (!r.ok) throw new Error(`anthropic ${r.status}: ${await r.text()}`);
  const j = await r.json();
  return j.content.map((b) => b.text || "").join("");
}

async function callOpenAI(model, system, user) {
  const messages = system ? [{ role: "system", content: system }, { role: "user", content: user }]
                          : [{ role: "user", content: user }];
  const r = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: { "content-type": "application/json", authorization: `Bearer ${process.env.OPENAI_API_KEY}` },
    body: JSON.stringify({ model, max_tokens: 1500, messages }),
  });
  if (!r.ok) throw new Error(`openai ${r.status}: ${await r.text()}`);
  const j = await r.json();
  return j.choices[0].message.content;
}

// --- parse a judge reply into {correctness,minimality,best_practice}, clamped 0-5 -
export function parseScore(text) {
  const m = text.match(/\{[^}]*\}/);
  if (!m) throw new Error(`no JSON in judge reply: ${text.slice(0, 80)}`);
  const o = JSON.parse(m[0]);
  const clamp = (n) => Math.max(0, Math.min(5, Number(n)));
  return { correctness: clamp(o.correctness), minimality: clamp(o.minimality), best_practice: clamp(o.best_practice) };
}

// --- build the user prompt for an arm (stance goes first, then the task) ----------
export function buildPrompt(armText, task) {
  return armText ? `${armText}\n\n---\n\nTask:\n${task}` : `Task:\n${task}`;
}

const total = (s) => s.correctness + s.minimality + s.best_practice;

async function run({ provider, model, judgeModel }) {
  const call = provider === "openai" ? callOpenAI : callAnthropic;
  const rows = [];
  for (const armName of Object.keys(ARMS)) {
    const armText = ARMS[armName]();
    for (const task of TASKS) {
      const answer = await call(model, "", buildPrompt(armText, task.prompt));
      const judgeReply = await call(
        judgeModel,
        JUDGE_SYSTEM,
        `TASK:\n${task.prompt}\n\nANSWER:\n${answer}`
      );
      const scores = parseScore(judgeReply);
      rows.push({ model, arm: armName, task: task.id, scores, chars: answer.length });
      process.stderr.write(`  ${armName}/${task.id}: ${total(scores)}/15 (${answer.length} chars)\n`);
    }
  }
  return rows;
}

function summarize(rows) {
  const byArm = {};
  for (const r of rows) {
    (byArm[r.arm] ||= []).push(r);
  }
  const out = [];
  for (const arm of Object.keys(byArm)) {
    const rs = byArm[arm];
    const avg = (f) => (rs.reduce((a, r) => a + f(r), 0) / rs.length);
    out.push({
      arm,
      total: +avg((r) => total(r.scores)).toFixed(2),
      chars: Math.round(avg((r) => r.chars)),
    });
  }
  return out;
}

// --- selftest: exercise the pure wiring with no API, no cost ----------------------
function selftest() {
  const assert = (c, m) => { if (!c) throw new Error(`selftest failed: ${m}`); };

  // arms build distinct prompts; fabius arm actually carries the shipped stance
  assert(buildPrompt("", "X") === "Task:\nX", "baseline prompt shape");
  assert(buildPrompt("BE LEAN", "X").startsWith("BE LEAN"), "arm text leads the prompt");
  assert(ARMS.fabius().includes("scout wide"), "fabius arm reads the real AGENTS.md stance");
  assert(ARMS.terse() !== ARMS.baseline(), "terse differs from baseline");

  // judge parser is lenient about surrounding prose but strict about range
  const s = parseScore('here: {"correctness":5,"minimality":4,"best_practice":7}');
  assert(s.correctness === 5 && s.minimality === 4, "parses judge JSON");
  assert(s.best_practice === 5, "clamps out-of-range scores to 0-5");

  // summarize aggregates per arm
  const sum = summarize([
    { arm: "baseline", scores: { correctness: 3, minimality: 3, best_practice: 3 }, chars: 100 },
    { arm: "fabius",   scores: { correctness: 4, minimality: 5, best_practice: 4 }, chars: 50 },
  ]);
  assert(sum.find((x) => x.arm === "fabius").total === 13, "summarize totals per arm");
  console.log("selftest: ok — harness wiring verified, no API calls made.");
}

function arg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : def;
}

async function main() {
  if (process.argv.includes("--selftest")) return selftest();

  const provider = arg("provider", "anthropic");
  const defaults = { anthropic: "claude-sonnet-4-6", openai: "gpt-4o" };
  const model = arg("model", defaults[provider]);
  const judgeModel = arg("judge", provider === "openai" ? "gpt-4o" : "claude-opus-4-8");

  if (provider === "anthropic" && !process.env.ANTHROPIC_API_KEY) throw new Error("set ANTHROPIC_API_KEY (or run --selftest)");
  if (provider === "openai" && !process.env.OPENAI_API_KEY) throw new Error("set OPENAI_API_KEY (or run --selftest)");

  console.error(`running: ${provider}/${model}, judged blind by ${judgeModel}`);
  const rows = await run({ provider, model, judgeModel });
  writeFileSync(join(__dir, "results.json"), JSON.stringify(rows, null, 2));

  const sum = summarize(rows);
  const base = sum.find((s) => s.arm === "baseline");
  console.log("\narm        total/15   avg chars   Δ vs baseline");
  for (const s of sum) {
    const d = (s.total - base.total >= 0 ? "+" : "") + (s.total - base.total).toFixed(2);
    console.log(`${s.arm.padEnd(10)} ${String(s.total).padStart(6)}   ${String(s.chars).padStart(9)}   ${s.arm === "baseline" ? "—" : d}`);
  }
  console.log("\nwrote evals/results.json");
}

main().catch((e) => { console.error(e.message); process.exit(1); });
