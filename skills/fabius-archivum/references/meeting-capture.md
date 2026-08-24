<!-- © 2026 Ariel Shemesh · fabius · reference depth for skills/fabius-archivum/SKILL.md -->

# Meeting capture — from a raw transcript to a filed record

The `meeting.capture` capability, from fabius's own research: a meeting
that isn't turned into a structured, retrievable record within the same day is knowledge the
team pays to re-derive. Archivum owns this because the deliverable IS memory — the record, the
entities it links, and the brief the next meeting starts from.

**The honest boundary.** fabius is rules, not a recorder. Audio capture and transcription
belong to the harness or whatever capture tool the user runs; the capability fabius owns
starts at a **transcript (or messy raw notes)** and ends at a **filed, linked, verified
record**. Never claim to have "heard" the meeting — quote the transcript.

## 1 · The notes-merge contract

The user's own fragmentary notes are **signal, not noise** — they mark what mattered to the
person in the room. Merge them with the transcript; never discard them for a "cleaner"
summary. The transcript supplies completeness; the user's notes supply salience; the record
carries both.

## 2 · The record — one fixed shape

```
# <meeting> · <date> · <participants>
TL;DR        — 2–3 sentences, the outcome first
Decisions    — what was decided · who decided · the stated why
Actions      — owner · task · due date  (no owner = flag it, don't invent one)
Open         — questions raised and not resolved
Numbers      — every figure quoted, verbatim, with who said it
Next         — agreed follow-ups / next meeting
```

Rules: a decision without a stated why gets `why: not stated` — never a plausible guess.
An action without an owner or date is listed as unowned — surfacing that gap is part of the
value. Every number is quoted from the transcript, never rounded or reconstructed. Attribution
uncertainty (crosstalk, unclear speaker) is marked, not smoothed.

## 3 · Before the meeting — the brief is a recall, not a search

The pre-meeting brief is archivum doing its normal job: recall prior records for the same
people / project / topic (`[[slug]]` links), open actions from last time, unresolved
questions, and the one-line history of the relationship. A brief is worth producing only when
memory holds something — an empty brief is skipped, not padded.

## 4 · After the meeting — file, link, draft

1. **File** the record as one page per meeting under the project's memory (schema in
   [`memory-schema.md`](memory-schema.md)); index line + log line as always.
2. **Link** entities — people, projects, products named in the meeting get/update their pages;
   decisions that change a standing decision **supersede** it explicitly.
3. **Draft** the follow-up (summary to participants, or the action-item nudge) — a DRAFT is
   the deliverable; **sending is the user's act**, never fabius's (the acting ladder in
   [`../../fabius/references/orchestration-doctrine.md`](../../fabius/references/orchestration-doctrine.md)).
4. **Verify gate as always**: only what the transcript actually supports compounds into
   memory; summaries of summaries decay — the record quotes the source.

## 5 · Analysis on demand

Across filed records the normal retrieval answers arrive cheaply: "what did we decide about X
and when", "what's still open with Y", "every commitment made to Z". That is not a new
capability — it is the wiki doing its job because the records were filed in one shape.
