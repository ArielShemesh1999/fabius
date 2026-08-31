<!-- © 2026 shear559 · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · release evidence: PROVENANCE.md · github.com/shear559/fabius -->
# Council protocol — the depth

The runnable reference is [`council.mjs`](council.mjs) (Node ≥18, zero dependencies). This doc is the spec it implements: the exact stage prompts, the anonymization scheme, and the aggregation math, so the protocol is reproducible by hand or in any other runtime (a harness, a Worker, a notebook). `SKILL.md` is the lean contract; this is the playbook.

## Roster — env-configured, never hardcoded

```
OPENROUTER_API_KEY   one key, every model (the live tier — you configure it)
COUNCIL_MODELS       comma-separated seats, e.g.
                     anthropic/claude-sonnet-5,openai/gpt-5.6-terra,google/gemini-3.1-pro-preview,mistralai/mistral-large
COUNCIL_CHAIRMAN     the synthesizing model, e.g. anthropic/claude-opus-5
```

**Resolve every seat and chairman id against the gateway's live model list before the run** (`GET /api/v1/models`). The reference fails this preflight before spending any completion calls when an id is absent; a transport failure after a valid preflight is logged and dropped. Without preflight, the council can complete looking healthy while using a narrower field than configured. Model ids churn faster than this document — treat the roster above as an example, not a guarantee.

OpenRouter is the reference gateway for the same reason karpathy's *llm-council* uses it: one key, one request shape, every provider — so seat diversity costs no extra plumbing. The protocol is provider-agnostic: any harness or gateway that can reach several models can run the same three stages instead of OpenRouter — the stages and prompts are identical, only the transport changes. Keys live in env, **never** in the repo (`fabius-praesidium`: secrets-in-env).

## Stage 1 — first opinions (parallel, independent)

Each seat gets the user's question **unmodified**. No system prompt that hints a council exists — you want each model's honest standalone answer.

```
SYSTEM:  (none, or the caller's own system prompt verbatim)
USER:    {the user's question}
```

Fan out all N concurrently. Collect `{model, answer}` for each. A seat that errors or times out is dropped with a logged note (`fabius-machina`: no silent failure) — the council proceeds with the survivors, never a blank seat.

## Stage 2 — anonymized peer-review (the blind ranking)

For each reviewing model, build a packet of **all** first opinions **including its own**, then:

1. **Strip identity** — label responses `Response 1, Response 2, …` (or `A, B, …`). Never include the model name.
2. **Shuffle per reviewer** — the label→model map is randomized independently for each reviewer, so position carries no signal and no reviewer can infer "Response 1 is always GPT".
3. The reviewer ranks **all** labels exactly once (it cannot tell which is its own — that is the whole point of the blind; the self-exclusion is enforced on the back end when tallying, see below). A duplicate, missing, unknown, or extra label makes the ballot invalid; never repair or complete it.

```
SYSTEM:  You are a strict, impartial judge on a council of AI models. You are NOT told
         which model wrote which response. Judge ONLY on accuracy, completeness, and
         insight — never on style, length, or tone.
USER:    Original question:
         {the user's question}

         The responses to rank:
         --- Response 1 ---
         {answer at shuffled slot 1}
         --- Response 2 ---
         {answer at shuffled slot 2}
         ...

         Rank ALL responses best-to-worst. Reply ONLY with compact JSON:
         {"ranking":[<best label>, ...,<worst label>],
          "reasons":{"<label>":"<one line>", ...}}
```

**Constrain the ballot at the API, not at the parser.** The ballot is a fixed, trivially-schematizable shape (`{ranking: [labels], reasons: {label: string}}`), which is exactly the case enforced structured output solves — so declare it instead of hoping for clean prose. On the reference gateway that is `response_format: {type:"json_schema", json_schema:{name, strict:true, schema}}`, with the label set declared as a closed enumeration, **plus** `provider: {require_parameters: true}` in the provider preferences. Both halves are load-bearing: without the second flag the call can route to an endpoint that translates your schema into its own format or treats it as a strong hint, and you are back to parsing prose without knowing it. Enforcement is the first line; the parser below is what you fall back to on a gateway that can't.

Parse and validate the JSON against the exact ballot (retry once on malformed or invalid output — `fabius-disciplina`; then drop and log it). Map each label back to its model via that reviewer's shuffle map. **Exclude self-votes**: when tallying, skip the rank a model gave to its own (now de-shuffled) answer — its slot simply scores nothing — so no seat can lift itself. (Skip-in-place: the other seats keep their position points; only relative order matters for the leaderboard, and self can never score itself.)

## Aggregation — Borda count over the rankings

With K responses, a rank position scores `K − position` (1st of K → K−1 points, last → 0). Sum each model's points across **all reviewers** (minus the self-vote already excluded). The result is a leaderboard:

```
for reviewer in reviewers:
    for position, label in enumerate(reviewer.ranking):   # 0-based
        model = reviewer.shuffle_map[label]
        if model == reviewer.model: continue              # exclude self
        score[model] += (K - 1 - position)
leaderboard = sorted(score, desc)
```

The leaderboard is **evidence for the chairman, not the verdict.** A pure vote loses to the *majority-wrong* failure mode (four correlated seats converge on a plausible error, one strong seat is right). The chair reasons over content; the tally just tells it where the council's confidence sat.

## Stage 3 — chairman synthesis

The chairman is the only stage that sees identities (it needs to weight by track record and resolve specific contradictions). Give it the question, every first opinion **with model names**, and the leaderboard with reasons.

```
SYSTEM:  You are the chairman of a council of AI models. The council has answered a
         question independently and ranked all anonymized answers blind, with each
         reviewer's self-score excluded by the backend. Your job is to
         deliver the single best FINAL answer — not a vote tally and not a copy of the
         top-ranked response. Take the strongest correct points, resolve the
         contradictions the council exposed, correct any majority error you can verify,
         and explicitly flag anything the council genuinely split on. Be accurate first,
         then concise.
USER:    Question:
         {the user's question}

         Council responses:
         --- {model A} ---
         {answer A}
         --- {model B} ---
         {answer B}
         ...

         Blind ranking leaderboard (peer-reviewed, self-votes excluded):
         1. {model X} — {points} pts — {a representative reason}
         2. {model Y} — {points} pts — ...
         ...

         Write the final answer.
```

The chairman's output is the council's synthesized answer. Then — for anything that can be run — `fabius-disciplina` proves it; the council does not replace evidence or guarantee improvement over the best seat.

## Output contract (what a run returns)

```json
{
  "question": "...",
  "seats": ["anthropic/claude-sonnet-5", "openai/gpt-5.6-terra", "..."],
  "chairman": "anthropic/claude-opus-5",
  "call_accounting": {
    "configured_seats": 3,
    "live_seats": 3,
    "retries": 0,
    "actual": 7,
    "clean_all_live": 7,
    "max": 10
  },
  "first_opinions": [{"model": "...", "answer": "..."}, ...],
  "valid_ballots": 3,
  "leaderboard": [{"model": "...", "points": 7, "reasons": ["..."]}, ...],
  "final": "the chairman's synthesized answer"
}
```

Present the `final` first; keep `first_opinions` and `leaderboard` one expand away (progressive disclosure — `fabius-decor`).

## Running the reference

```bash
# wiring check — no key, no network, no cost (strict ballots, retry/drop, isolation, preflight, Borda)
node references/council.mjs --selftest

# a real council
export OPENROUTER_API_KEY=sk-or-...
export COUNCIL_MODELS=anthropic/claude-sonnet-5,openai/gpt-5.6-terra,google/gemini-3.1-pro-preview,mistralai/mistral-large
export COUNCIL_CHAIRMAN=anthropic/claude-opus-5
node references/council.mjs "Should a 3-person startup use a monolith or microservices?"

# JSON out (pipe the full record)
node references/council.mjs --json "..."  > run.json
```

Cost is the gate, not an afterthought. Let N be configured seats, M be first-opinion survivors, and R be malformed/invalid-ballot retries. A successful run makes exactly `N + M + R + 1` completion calls; `0 ≤ M ≤ N` and `0 ≤ R ≤ M`, so reserve **at most `3N + 1`**. The clean all-live/no-retry path is `2N + 1`. The reference prints the configured clean ceiling and retry cap before the run, then the actual N/M/R accounting afterward, so spend is never a surprise (`fabius-fortuna`: cost-aware). The roster preflight is one metadata request, not a completion call.

## Gotchas

- **Malformed ranking JSON** — models wrap JSON in prose whenever nothing stops them, so enforce the schema at the API first (stage 2); extracting the first balanced `{…}` and retrying once with a "JSON only" reminder is the fallback for gateways that can't enforce, not the first line. If a ballot still can't be recovered, **drop it and log the drop** — never synthesize one to keep the arithmetic tidy. Filling the missing labels in whatever order they currently sit is a full-strength *random* vote, and an all-equal ballot is not neutral either: with self-exclusion it hands every other seat the same points and the reviewer none. K is the number of **responses** being ranked and does not move when a reviewer drops out — only the number of ballots summed does.
- **Odd seat dropped mid-run** — recompute K from the *survivors*, not the configured count, or the Borda scores skew.
- **Self-leak via writing style** — anonymization strips the name, not the voice; a model may still recognize its own prose. Self-vote exclusion on the back end is the backstop, so never skip it.
- **Latency** — stages 1 and 2 are each a full fan-out; run them concurrently within a stage, but stage 2 needs all of stage 1 first (a real barrier). Stage 3 is a single call. Budget for the slowest seat twice plus the chair.
