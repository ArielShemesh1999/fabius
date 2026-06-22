---
name: fabius-decor-research-decision-room
description: Turn messy user research — interviews, support tickets, surveys, analytics — into a single HTML decision artifact with evidence ledger, theme map, opportunity matrix, and decision memo.
triggers:
  - "research decision room"
  - "user research synthesis"
  - "research synthesis dashboard"
  - "evidence-backed product decision"
  - "interview synthesis"
  - "opportunity solution tree"
  - "usability findings dashboard"
  - "qualitative research board"
---

# Research Decision Room Skill

Produce a single-page HTML decision artifact that turns messy evidence into a clear next move. Not a decorative research deck — a working room for debate: evidence, themes, confidence, tradeoffs, and recommended experiments visible together.

## Resource map

```text
research-decision-room/
├── SKILL.md
├── example.html
└── references/
    ├── checklist.md
    └── evidence-model.md
```

Read `references/evidence-model.md` before synthesis. Run `references/checklist.md` before emitting the artifact.

## When to use

Use when the user has any mix of:
- Interview notes, usability observations, support tickets, sales call notes, app-store reviews, NPS comments, survey open text, or analytics snippets.
- A decision that needs evidence: "Should we build X?", "Which onboarding path?", "Why are users dropping off?"
- A need to share findings with stakeholders who won't read a long report.

Do not use for pure visual inspiration, campaign ideation, or brand moodboards.

## Workflow

### Step 1 — Establish the decision frame

Identify the decision scope from the user's prompt. If not given, derive one from the evidence and label it as inferred.

Write a short frame with:
- Decision question
- Audience or segment
- Time horizon
- Known constraints
- What this artifact will not decide

If key context is missing but the task is not blocked, proceed with labelled assumptions.

### Step 2 — Build the evidence ledger

Normalize every useful signal into ledger rows using the model in `references/evidence-model.md`.

Each row must include:
- `id`: short stable id (`I-03`, `T-14`, `M-02`)
- `source_type`: interview, usability, support, survey, analytics, sales, field note, or stakeholder
- `segment`: user type or "unknown"
- `signal`: one-sentence observation
- `quote_or_metric`: direct quote, metric, or "not provided"
- `strength`: strong, medium, or weak
- `limitations`: why this evidence may be biased or incomplete

Never invent quotes, participant counts, dates, revenue impact, or metrics. If the user did not provide a number, use "not provided" and explain what evidence would increase confidence.

### Step 3 — Synthesize themes and tensions

Cluster evidence into 4–6 themes. For each:
- Name in plain human language (prefer verbs: "Teams abandon setup when the first blank state asks for too much" not "Onboarding problem")
- Evidence ids that support it
- Behavior behind it, not just the UI complaint
- Confidence: high, medium, or low
- Contradictions or segment differences

### Step 4 — Score opportunities

Create an opportunity matrix with 3–5 options. Score each 1–5 on:
- Evidence strength
- User pain
- Business leverage
- Implementation risk (5 = low risk, 1 = high risk)

Show total score, but add one sentence on why the top recommendation wins. Score does not replace judgment.

### Step 5 — Draft the decision memo

Write a memo with:
1. Recommended move
2. Why now
3. What evidence supports it
4. What could be wrong
5. What to measure next
6. Reversible next step

Keep it short enough to read in under one minute.

### Step 6 — Create the HTML artifact

Produce a self-contained `index.html`. Use active `DESIGN.md` for typography, spacing, and color roles. Keep information architecture stable:

1. Header: decision question, confidence, last-updated label
2. Executive readout: recommendation, risk, next experiment
3. Evidence ledger with filter chips
4. Theme map with evidence ids and confidence
5. Opportunity matrix
6. Decision memo
7. Experiment queue with owner, metric, success threshold
8. Assumptions and limitations

Vanilla JavaScript allowed for filtering evidence, switching views, or highlighting related ids. No framework dependency.

### Step 7 — Self-check and emit

Run the checklist. Then emit one concise orientation sentence and one HTML artifact:

```xml
<artifact identifier="research-decision-room" type="text/html" title="Research Decision Room">
<!doctype html>
<html>...</html>
</artifact>
```

Nothing after the closing `</artifact>`.
