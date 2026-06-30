<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->
# Council protocol — the depth

The runnable reference is [`council.mjs`](council.mjs) (Node ≥18, zero dependencies). This doc is the spec it implements: the exact stage prompts, the anonymization scheme, and the aggregation math, so the protocol is reproducible by hand or in any other runtime (synapse, a Worker, a notebook). `SKILL.md` is the lean contract; this is the playbook.

## Roster — env-configured, never hardcoded

```
OPENROUTER_API_KEY   one key, every model (the live tier — you configure it)
COUNCIL_MODELS       comma-separated seats, e.g.
                     anthropic/claude-sonnet-4.5,openai/gpt-5.1,google/gemini-3-pro,x-ai/grok-4
COUNCIL_CHAIRMAN     the synthesizing model, e.g. anthropic/claude-opus-4.8
```

OpenRouter is the reference gateway for the same reason karpathy's *llm-council* uses it: one key, one request shape, every provider — so seat diversity costs no extra plumbing. The protocol is provider-agnostic; in the **synapse** console the same three stages run over fabius's native 5-provider runtime (`/api/fabius/run` + the `X-LLM-Key` vault) instead of OpenRouter — the stages and prompts are identical, only the transport changes. Keys live in env / the vault, **never** in the repo (`fabius-praesidium`: secrets-in-env).

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
3. The reviewer ranks **all** labels (it cannot tell which is its own — that is the whole point of the blind; the self-exclusion is enforced on the back end when tallying, see below). Dedupe the returned ranking first: a model that repeats a label must not double-count.

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

Parse the JSON (retry once on malformed output — `fabius-disciplina`). Map each label back to its model via that reviewer's shuffle map. **Exclude self-votes**: when tallying, skip the rank a model gave to its own (now de-shuffled) answer — its slot simply scores nothing — so no seat can lift itself. (Skip-in-place: the other seats keep their position points; only relative order matters for the leaderboard, and self can never score itself.)

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
         question independently and ranked each other's answers blind. Your job is to
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

The chairman's output is the council's answer. Then — for anything that can be run — `fabius-disciplina` proves it; the council improves the *answer*, it does not replace the *evidence*.

## Output contract (what a run returns)

```json
{
  "question": "...",
  "seats": ["anthropic/claude-sonnet-4.5", "openai/gpt-5.1", "..."],
  "chairman": "anthropic/claude-opus-4.8",
  "first_opinions": [{"model": "...", "answer": "..."}, ...],
  "leaderboard": [{"model": "...", "points": 7, "reasons": ["..."]}, ...],
  "final": "the chairman's synthesized answer"
}
```

Present the `final` first; keep `first_opinions` and `leaderboard` one expand away (progressive disclosure — `fabius-decor`).

## Running the reference

```bash
# wiring check — no key, no network, no cost (proves stages compose + Borda math)
node references/council.mjs --selftest

# a real council
export OPENROUTER_API_KEY=sk-or-...
export COUNCIL_MODELS=anthropic/claude-sonnet-4.5,openai/gpt-5.1,google/gemini-3-pro,x-ai/grok-4
export COUNCIL_CHAIRMAN=anthropic/claude-opus-4.8
node references/council.mjs "Should a 3-person startup use a monolith or microservices?"

# JSON out (pipe the full record)
node references/council.mjs --json "..."  > run.json
```

Cost is the gate, not an afterthought: a run is `len(COUNCIL_MODELS) × 2 + 1` model calls. The reference prints the call count so the spend is never a surprise (`fabius-fortuna`: cost-aware).

## Gotchas

- **Malformed ranking JSON** — models sometimes wrap JSON in prose. Extract the first balanced `{…}`; retry once with a "JSON only" reminder; if still bad, give that reviewer a neutral (all-equal) ballot rather than crashing the run.
- **Odd seat dropped mid-run** — recompute K from the *survivors*, not the configured count, or the Borda scores skew.
- **Self-leak via writing style** — anonymization strips the name, not the voice; a model may still recognize its own prose. Self-vote exclusion on the back end is the backstop, so never skip it.
- **Latency** — stages 1 and 2 are each a full fan-out; run them concurrently within a stage, but stage 2 needs all of stage 1 first (a real barrier). Stage 3 is a single call. Budget for the slowest seat twice plus the chair.
