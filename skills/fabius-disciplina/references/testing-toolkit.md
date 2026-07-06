# Fabius Disciplina — the test, prove & debug toolkit

Loaded on demand by `fabius-disciplina`. The process **tooling** (2026) behind the discipline: the red-green-refactor loop, verification-before-completion, and root-cause debugging. *(No HF entry — code/SWE models belong to `fabius-doctrina`; this is tooling only.)* License flags where they bite (jqwik's anti-AI clause, Semgrep's rules license).

## Test frameworks

| Tool | License | Note |
|---|---|---|
| **pytest** | MIT | The Python red-green backbone — plain-assert, fixtures, `-x --lf` to iterate on the first failure; the harness every other Python tool here plugs into. |
| **Vitest** | MIT | Vite-native JS/TS — the *tightest* watch loop (see the failing assertion re-run as you type); built-in coverage/snapshots/mocking. |
| **Jest** | MIT | Incumbent for established JS codebases / React Native. *ESM/TS is clunkier than Vitest — prefer Vitest greenfield; review snapshots or they rot into rubber-stamps.* |
| **Playwright** | Apache-2.0 | **The `verify` tool** — drive the real flow in a real browser (auto-waiting kills flakiness, trace viewer for post-mortem). **WebKit = the honest iOS-Safari proxy** (the *verify-live-not-just-code* law). Exposes CDP for deep instrumentation. |
| **Cypress** | MIT (runner) | Tactile time-travel runner for human-in-the-loop verify. *No real Safari/WebKit; parallelization pushes to paid Cloud — Playwright wins on breadth.* |

## Property-based & fuzz — inputs you didn't think of

| Tool | License | Note |
|---|---|---|
| **Hypothesis** | MPL-2.0 | The dominant Python property tester — states invariants, finds + **shrinks** minimal counterexamples (used by CPython itself). **HypoFuzz** (2025) adds coverage-guided fuzzing on the same `@given` tests. |
| **fast-check** | MIT | The JS/TS equivalent (plugs into Vitest/Jest) — its shrinker reports a minimal reproducer to drop straight into a regression test. |
| **jqwik** | ⚠️ EPL-2.0 **+ anti-AI clause** | JVM property testing on JUnit 5. **Two flags:** since v1.10 the license carries an **Anti-AI Usage Clause** (review before AI-adjacent use), and the project is **maintenance-mode only**. |

## Mutation — the honest "is it actually done?"

Coverage's blind spot: a covered line with no real assertion. Mutation testing mutates your source and checks whether tests *catch* it.

- **mutmut** (BSD-3) — Python; can write a surviving mutant to disk so you see the exact untested behavior. *(Needs `fork()` — WSL on Windows; slow, scope to changed files.)*
- **StrykerJS** (Apache-2.0) — JS/TS; HTML report ranks surviving mutants by file → an actionable weak-test list. *Use `--incremental`/`--since` or CI budgets blow up.*

## Coverage — necessary, not sufficient

- **Coverage.py** (Apache-2.0, via `pytest-cov`) — enable **branch** coverage (`--cov-branch`) + a `fail-under` gate so "done" has a number. But **line coverage overstates confidence** — pair with mutation testing. *(JS: v8/istanbul ship inside Vitest/Jest.)*

## Debug & profile — instrument the defect, don't guess

- **debugpy** (dual EPL/MIT) — attach a real debugger to a live/remote/containerized Python process (`--listen --wait-for-client`); editor-agnostic via DAP. **pdb++** (BSD) is the lighter `pytest --pdb` REPL.
- **py-spy** (MIT) — low-overhead sampling profiler that attaches to a *running* process: `dump` a stuck PID for instant stacks (deadlocks), `record` for a flamegraph, no restart. *(Needs ptrace/sudo.)* **Scalene** (Apache) for line-level CPU+GPU+memory; JS → Chrome DevTools Performance panel.

## Correctness linters — start the debug loop from clean code

- **Ruff** (MIT) — millisecond Python lint+format replacing a whole stack; catches real bugs (mutable defaults, undefined names). *Not a type checker — pair with mypy/pyright/ty.*
- **ESLint** (MIT) — JS/TS front line; typed rules (`no-floating-promises`, `exhaustive-deps`) catch unhandled async / missing effect deps. *Flat config is the norm now; delegate formatting to Prettier/Biome.*
- **Semgrep** (⚠️ engine LGPL-2.1) — codify a fixed bug as a **custom rule so it can't regress** — the *ship-every-finding-with-a-regression-test* discipline at codebase scale. **Flag:** Semgrep-authored *rules* are under a restrictive non-OSS license and deep analysis is paid — write your own rules or use the permissive **Opengrep** fork to stay clean.

## Pairs with

`fabius-disciplina` (the brainstorm→plan→TDD→prove→debug loop these serve), the `verify` skill (Playwright drives the real flow), `fabius-doctrina` (evaluating a *model* is doctrina's turf; this is code), and `fabius-parcus` (Ruff/one-tool over a lint stack; don't add a test framework a one-line change doesn't need).
