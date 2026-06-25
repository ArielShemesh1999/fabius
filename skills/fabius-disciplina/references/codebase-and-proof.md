# Fabius Disciplina — scout the codebase, scout reality, prove in a browser

The on-demand depth for `fabius-disciplina`'s *scout* and *prove* steps when the unknown is a large codebase, a current-world fact, or a UI in a browser. The skill is the contract; this is how you run the loop well. These are capabilities fabius can **apply** by reaching for named ecosystem tools — fabius bundles no runtime; the optional live tier routes to ARCHITECTURE.md external connections. Tool names and versions are a point-in-time snapshot (early 2026); re-verify before you depend on one.

Scout wide, strike narrow. Three of these sharpen *how you understand* before an edit; two sharpen *how you prove* after it.

## 1. Scout the code with a graph, not a grep

On an unfamiliar or large repo, grepping for a symbol gives you matches, not understanding — and it floods the context with hits you have to read to discard. **Build a local code graph first.**

- Parse the repo with tree-sitter (14+ languages), store the symbol/call/import graph in **SQLite**, keep it **auto-synced** to the working tree (FSEvents / inotify). The graph is the index; the query is surgical. *(ecosystem: codegraph, GitNexus, Code Review Graph.)*
- Query the graph for the answers an edit actually needs: **impact analysis** (what calls this, what breaks if I change the signature), **dependency tracing** (what this module pulls in), **taint analysis** (does untrusted input reach this sink). One query returns the blast radius; a grep returns a wall of strings.
- **100% local** — the graph is built and queried on-device, no code leaves the machine. That is the precondition for using it on a client repo at all (→ `fabius-praesidium` owns the secrets/exfil boundary).

**Decision rule:** unfamiliar or large repo → build/query the graph **before** editing. Small repo you already hold in your head → a grep is fine; the graph is overhead. The graph earns its build cost exactly when the context wouldn't fit in your head otherwise.

## 2. Scout reality — verify current-world facts against the live web

Memory is where silent staleness begins. An API shape, a library's current state, a version number, a price — anything that **decays** — is not a thing to recall; it's a thing to check. The cost of a wrong remembered version is a whole plan built on a fact that stopped being true.

Two tiers, sized to the question:

- **Quick web search** — one current fact: the latest stable version, whether a flag still exists, today's pricing. Cheap, single-hop.
- **Deep multi-hop research** — a synthesis question that spans sources: how does library X handle Y now, what changed across a major version, what's the current consensus on an approach. *(Perplexity sonar-deep-research, Exa, Brave; keyless Firecrawl for a single-page scrape.)*

**Decision rule:** is the fact **current-world and decaying**? → check reality before you plan on it. Is it stable (an algorithm, a language semantic, the project's own code) → memory/the graph is fine. Encode the decision, not the version number; re-verify the number.

Web/DB search as a **live tier is optional and user-configured** — fabius ships no keys. When it's wired, it routes to ARCHITECTURE.md external connections; when it isn't, the rule still holds, you just satisfy it by hand.

## 3. Plan as files, not as chat

For multi-step or long-horizon work, the plan and the spec live **on disk**, not only in the conversation. A context reset wipes chat; a file survives it, and the agent re-reads the file to recover its place.

- Persist the `step → verify` plan (phase 3) and the spec to files the agent re-opens each cycle.
- This is what lets the loop run unattended across a reset — the durable artifact is the memory. *(Planning-with-Files reports 96.7% task pass on this discipline; treat that as reported, not fabius-measured.)*

The plan file is also the handoff artifact and the thing `fabius-archivum` files once the work resolves. Short tasks don't need it; the moment the work outlives one context window, the file is the difference between resuming and restarting.

## 4. Prove with a real browser — for any UI or web change

A passing unit test is **not** proof for a UI change. The law is fabius's own: *verify live, not just code.* Drive a real browser and assert the rendered state.

- **Playwright** — deterministic, no-vision: locators, `fill`, `click`, `screenshot`, full e2e. Assert by **locator/role/text** (the semantic handle), the same meaning-first principle as the simulator tree (→ `references/simulator-verify.md`) — not by pixel coordinate, which breaks on every layout shift.
- **Sandboxed browser** when you must run untrusted page logic — **QuickJS-WASM isolation**, no host file or network access. Reach for it only when isolation is the point; plain Playwright is the default.
- The check is **state on the real path**, not "the test is green." Navigate, act, read the live DOM, assert the user-visible outcome. Screenshot last — for a human's eyes and visual-diff, never as the primary assertion.

**Decision rule:** the change is anything a user sees in a browser → it isn't done until a browser drove it. "Almost works" and a code-only answer don't count (phase 6).

## 5. Enforce TDD with a gate, not a hope

Phase 4 is the iron law: no production code for non-trivial logic until a test fails first. Hope is not enforcement. When correctness genuinely matters, make the failing test a **gate**, not a suggestion.

- A **pre-edit hook** blocks writing implementation while no failing test exists — **RED → GREEN enforced** across 9+ test frameworks. The hook refuses the edit until red is real.
- This turns "I'll write the test after" — the anti-pattern that proves the code does what it does, not what it should (→ `references/process-playbook.md`) — into something the harness won't let you skip.

**Decision rule:** wire the gate when correctness is load-bearing and the cost of a silent regression is high. Don't gate throwaway prototypes, generated code, or pure config — the same narrow exceptions phase 4 already names, each with the human's sign-off.

---

The never-trim floor still holds underneath all of this: validation, security, and a11y are not candidates for the YAGNI ladder (→ `fabius-parcus`). These tools change *how you scout and prove*; they never license skipping the floor.

Each capability here is drawn from a named ecosystem tool and re-expressed in fabius's own voice — apply the discipline, credit the tool, ship nothing you haven't proven.
