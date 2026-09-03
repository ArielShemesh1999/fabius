<!-- © 2026 shear559 · fabius · reference depth for skills/fabius-archivum/SKILL.md -->

# Project records — one store, one page per project

The cross-session contract for a store that serves **many** projects. `memory-schema.md` gives page and line formats; this file gives the topology, the read gate, and the write-back contract. Every path here is a shape, never a location: the store's real location comes from the workspace's own declaration, never from a guess and never from this file.

## 1. Resolve the topology before testing for a store

Two sanctioned shapes, one set of conventions. Decide which is in play *before* asking whether memory exists — the per-repo test returns "none" inside a hub, and that false negative is how a duplicate store gets scaffolded.

**A. Central hub** — the default once a second project exists. One store outside every repo; every project has exactly ONE page in it.

```
<store>/
  <schema>.md          # how THIS store works — read first; co-owned with the human
  index.md             # catalog. READ FIRST at query time.
  log.md               # append-only, prefixed, signed, appended at the END
  projects.md          # map of content: one row per project → its page
  projects/<slug>.md   # THE canonical project record. One per project, never two.
  concepts/            # cross-project doctrine, shared by every project
  raw/                 # immutable sources — read, never edit
  outputs/             # generated artifacts (decks, charts, reports) — derivative
```

**B. In-project store** — one project, memory beside the code: a `MEMORY.md` index + `log.md` + topic pages, growing into `wiki/` (`decisions/` · `gotchas/` · `<topic>.md`) only once the page count demands it.

Never both for one project. A hub that already holds the project's page IS the answer: no second index is created in that repo, and nothing about the project is copied into the harness's own memory.

## 2. Opt-in resolution — offer once, read every time

1. **Resolve** — locate the store: the hub's schema file, or the project's own index. Found → opted in.
2. **Opted in ends the offer.** A store with a schema file and a page for this project is the opt-in. Never re-ask, never scaffold a second store, never read a missing repo-local index as a missing store.
3. **Not found anywhere** → offer setup once (hub or in-project; Obsidian or plain markdown), then work without it. Never block work; never scaffold implicitly.

Obsidian onboarding, when chosen: install → *Open folder as vault* on the **store root** — the folder holding the schema file, the index and the raw sources — never a subfolder, because opening the wiki folder alone leaves the schema and the sources outside the vault, so source links dangle and the graph loses a layer. Enable Graph view and a frontmatter-query plugin. In any semantic-search plugin, **exclude the raw-source and generated-output folders**: full-length sources and derivative artifacts dominate retrieval, and the curated pages are what should be embedded.

## 3. The project page contract

Frontmatter is the machine-readable index. Every value is a scalar an agent can act on: a date, an id, a url, an enum. Anything with a verb in it belongs in the dated body.

```yaml
---
name: stable-kebab-slug     # the id AND the filename: a wikilink resolves by filename, never by a field
description: one line       # what the index row shows
type: project
aliases: [alt-names]        # how a human will name it in chat — this is how "work on X" resolves
status: active | blocked | done | archived | abandoned
repo: <url, or an explicit "none — <why>">
workspace: <pointer to where the files actually live>
live_url: <url, or an explicit "none — <why>">   # READ this field; never construct one
updated: 2026-06-21         # when the PAGE changed
last_push: 2026-06-21       # when the WORK last landed on the remote
---
```

- `updated` ≠ `last_push`. One is the page, one is the work; `last_push` behind the tree's head means the page is behind reality.
- **Absent and empty are different claims.** A required field holds a value or is omitted — a blank reads as a verified negative and stops the agent from asking. Where the negative is the fact, write it out with a reason.
- **A renamed or superseded project** keeps its old slug as a stub with a `superseded_by` pointer, so old links and aliases still resolve. A stub is a pointer, never a record: never read state off it.
- **Never invent an enum value.** A status outside the enum is invisible to every query built on the enum.
- **Body section order is fixed**, because the gate reads the top of the page: `## Links` (repo · workspace · live) · `## Brief` · `## Stack` · `## Health` (what is green/red now, with the evidence) · `## Open items` (each with its next step) · `## Decisions` (dated, signed) · `## Gotchas` · `## Recent activity` · `## Related`. Dated entries live only inside `## Recent activity` — never above the brief, never after `## Related`. **State the section's order in the store's schema and never mix the two**: a page a session reads top-down puts the newest entry FIRST, so the current state survives a truncated read; an append-only shared *log* is the opposite case — an atomic `>>` append can only grow downward, so its newest line is last. A page whose order is undeclared gets both, and then neither end can be trusted.
- **Cap the page.** Read-in-full is a promise the page must stay small enough to keep. Past a stated cap, rotate: move older dated entries to an archive page, keep every canonical section on the live page, and never delete a decision or a gotcha — rotate it. A page too large to read in a session silently converts the gate into a truncated read, which is worse than no gate: the agent still reports that it read the page.
- **Only what the project IS gets the project type.** A sub-page (a plan, a migration note, an audit) is its own type, linked from `## Related`, or the work queue fills with notes.

## 4. The read gate — a precondition, not a dial

Work that names a project reads that project's ONE page IN FULL before the first edit: brief · stack · decisions · health · open items · live URL. Not the index row, not a grep hit.

1. **Resolve the slug by alias, never by filename guess.** Match the name against filenames and `aliases`; two hits → ask which, in one line, listing the candidates. No hit → run the create protocol before working.
2. **Read the whole page**, frontmatter first. On a long page the canonical sections may sit below a journal — do not skim the top and start.
3. **Don't re-derive what the page records.** A dated decision is settled: reopen it only if the human reopens it or the cross-check contradicts it. A gotcha is a trap already paid for.
4. **Stop condition.** A named project with no page in a declared store → propose the page and say so; do not start blind, and do not scaffold a competing store.

The recall dial governs *unrelated* memory and prior conclusions; it never gates the page for the project in hand — that page is the brief. Fresh-eyes routes (security, incident, outage, rollback, error recovery) still read the page's **state** — stack, addresses, constraints, open items — because it is data the work needs to act at all. What they defer is the page's prior *conclusions*: read those after the current evidence, labelled as prior.

## 5. Staleness — the page is a claim, the tree is the fact

A hand-maintained page, especially an unversioned one, is an assertion: its dates say what a past writer believed. Before trusting it, and always before reporting state to the human, diff it against reality:

- the tree's newest commit and the newest commit on the remote, against `last_push`;
- the version or tag file, against any version the page names;
- the live address, if the work touches it — a recorded URL says what was deployed, not what is serving, and a redirect verifies the wrong page.

Reality wins on **facts**; the page wins on **intent** — never delete a recorded decision because the code no longer shows it. A page can also contradict itself (frontmatter synced, body stale): verify, then fix both. Never report a page claim as verified, and never *silently* correct one — name the wrong claim in the log line so the drift is on the record.

**Resolve the pointer, then confirm it is the only working copy** of that artifact. Two clones of one remote at different heads means the cross-check may be validating the wrong tree.

## 6. One record, one owner

Project state — status, decisions, open threads, addresses, versions — lives on the canonical page and nowhere else.

- **Not in a harness's own memory.** That store holds cross-project behavior: preferences, standing rules, environment facts. It is machine-local and often invisible to a second agent, so a project fact parked there is invisible half the time. A fact written into both eventually disagrees with itself, and the non-canonical copy is the one that rots unseen — while being the one that loads automatically.
- **Not inside the project repo**, when a hub already holds the page. A repo-local store forks the record, and in a public repo it publishes it.
- Split by OWNER, not by audience. A fact that belongs to one project goes on its page; a fact that belongs to every project goes in the shared concepts folder and is linked from the pages that need it.

## 7. Sync-after — finishing, not follow-up

Work that isn't written back didn't happen. Before reporting done, in the same session, under the store's write authority:

1. **Frontmatter** — bump `updated` always; bump `last_push` only when a push actually landed on the remote, verified against the remote and not against a local commit; move `status` if the lifecycle changed; repair any address that changed.
2. **Body** — add one dated entry to `## Recent activity`, at the end the store's schema declares as newest (top, for a page read top-down); correct every sentence the work falsified, the lede and the brief first; append to `## Decisions` (`- [YYYY-MM-DD] decision — why (<agent>)`) only for a decision that constrains future work; append to `## Gotchas` for a trap that cost real time; rewrite `## Open items` to the next concrete step; restate `## Health` for whatever was actually verified.
3. **Log** — append exactly ONE entry, at the END of the log:

```
## [YYYY-MM-DD] <op> | <slug> — <what changed, one line> (<agent>)

- <what was done — name revisions; say landed or local>
- <what was verified and how — the address, the gate, the count>
```

4. **Report** both paths in one line.

Keep the op verb set **closed** and small (ingest · query · lint · new-project · update · build · fix · deploy · release · audit · sync) and map anything else onto one of them. An open verb set is not a facet: it cannot be filtered, grouped, or audited.

The record and the log move **together or not at all**. Advancing the log without the page leaves a divergence only the log can see — and a page whose date is today but whose body describes last week is worse than an untouched page: it looks fresh and reads wrong.

A read-only question proposes the record and leaves storage untouched.

## 8. Two writers, one store

Assume a second agent — or a second session — on the same store. An unversioned store has no merge tool and no undo, so every write is final.

- **Append at the END, append-only.** An atomic append is safe under concurrency; a read-modify-rewrite of a shared log is how a large history disappears with no error. Read the log with a tail, never load the whole file to add one line.
- **Sign every log entry and every decision line** with the writing agent's name. Unsigned means *predates signing*, never "mine" — never infer authorship from an unsigned entry.
- **Patch, never regenerate.** Edit the section you own; never rewrite a whole page.
- **Re-read a page immediately before editing it** — another writer may have touched it since your read. If its date is newer than what this session read, merge; don't overwrite.
- **Never edit, re-date, or reorder another writer's entry**, including a legacy out-of-order one: leave it, don't imitate it.
- Write the direction and the signature rule **inside the log itself**. The next writer reads the file, not the docs.

## 9. Retrieval — what the store can actually promise

The index, the project map and grep are the retrieval path an agent can rely on. A semantic index is optional, and it decays:

- **Read the live config, never a document that describes it.** An embedding model, a minimum chunk length or an exclusion list quoted in prose goes stale silently, and a threshold a build no longer has cannot be applied.
- **Vectors are keyed by the model that wrote them.** Change the model and the persisted index is a different index; it needs a full re-embed, which is usually a human action in a GUI — so never promise it from a session, and never assume it ran.
- **A semantic miss is not evidence of absence.** A page written after the last index pass, or never embedded, cannot be found by search. Confirm with grep before concluding the store has nothing.
- **One huge append-only log dominates block retrieval.** Query it with grep and tail, and rotate it by period once it outgrows a file.
- **Cap only what is injected every turn.** A context-injected auto-index is capped and consolidated past the cap. A browsable catalog is **not** capped: one row per project, never merged — merging rows deletes the navigation the gate depends on. Past a comfortable size, split into sections and inject only the matching section.

## 10. Coverage and lint — check both directions

A record with no artifact is a fossil. An **artifact with no record is the dangerous direction**, because it produces no error: the gate finds nothing and the agent proceeds from whatever it half-remembers. Diff the two on a schedule, not on hope.

Lint on a cadence denominated in the store's real unit of work — project syncs, not ingests, if project work is what it holds:

- pages missing the type discriminator, carrying a duplicate key, or leaving a required field blank;
- pointers that resolve to nothing, or to a tree that is not the one the page describes;
- `last_push` and `updated` against the tree, for every active project;
- log order ascending, every recent entry signed, one heading grammar;
- page size against the cap; sections above `## Recent activity` intact;
- a stated convention nobody enforces — either lint it or delete it. Prefer three enforced conventions to ten aspirational ones.

## 11. The store's own schema file is authoritative for that store

A store's schema file wins over any general doctrine, this file included: the queries, the maps and the human's habits are written against it. Map the doctrine onto the store rather than reshaping the store — index to its index, log to its log, project record to its project page — and never scaffold a second store to satisfy a shape. Where reality and the schema disagree, one of them is wrong and both are broken until reconciled: fix it in the same session, and log it.

A read protocol may only name fields the page template guarantees. Every field the gate tells an agent to read must be a required section of the template, and every required section must appear in the gate. A field named by one and not the other is the defect — the agent fills the gap by guessing.
