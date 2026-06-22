---
name: fabius-disciplina-review
description: Review changes since a fixed point (commit, branch, tag, or merge-base) on two axes in parallel — Standards (does the code follow documented conventions?) and Spec (does it match the originating issue/PRD?). Use when the user wants to review a branch, PR, or work-in-progress, or asks to "review since X".
---

# Review

Two-axis review of the diff between `HEAD` and a fixed point the user supplies:

- **Standards** — does the code conform to this repo's documented coding standards?
- **Spec** — does the code faithfully implement the originating issue / PRD / spec?

Both axes run as **parallel sub-agents** so they don't pollute each other's context; this skill aggregates their findings.

The issue tracker must be available — run `/setup-the-craft-set-skills` if `docs/agents/issue-tracker.md` is missing.

## Process

### 1. Pin the fixed point

Take whatever the user supplied — commit SHA, branch name, tag, `main`, `HEAD~5`. Don't be opinionated; pass it through. If they didn't specify, ask: "Review against what — a branch, a commit, or `main`?" Don't proceed until you have it.

Capture the diff command: `git diff <fixed-point>...HEAD` (three-dot, comparing against the merge-base). Note commits via `git log <fixed-point>..HEAD --oneline`.

### 2. Identify the spec source

Look in this order:

1. Issue references in commit messages (`#123`, `Closes #45`, GitLab `!67`) — fetch via `docs/agents/issue-tracker.md`.
2. A path the user passed as an argument.
3. A PRD/spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
4. If nothing is found, ask the user. If they say there isn't one, the **Spec** sub-agent skips and reports "no spec available".

### 3. Identify the standards sources

Common locations:

- `CLAUDE.md`, `AGENTS.md`
- `CONTRIBUTING.md`
- `CONTEXT.md`, `CONTEXT-MAP.md`, per-context `CONTEXT.md` files
- `docs/adr/` (architectural decisions count as standards)
- `.editorconfig`, `eslint.config.*`, `biome.json`, `prettier.config.*`, `tsconfig.json` — note these but don't re-check what tooling already enforces
- `STYLE.md`, `STANDARDS.md`, `STYLEGUIDE.md` at root or under `docs/`

Collect the file list. The **Standards** sub-agent will read them.

### 4. Spawn both sub-agents in parallel

Single message, two `Agent` tool calls. Use `general-purpose` for both.

**Standards sub-agent prompt:**

- Full diff command and commit list.
- List of standards-source files from step 3.
- Brief: "Read the standards docs. Then read the diff. Report — per file/hunk where relevant — every place the diff violates a documented standard. Cite the standard (file + rule). Distinguish hard violations from judgement calls. Skip anything tooling enforces. Under 400 words."

**Spec sub-agent prompt:**

- Diff command and commit list.
- Path or fetched contents of the spec.
- Brief: "Read the spec. Then read the diff. Report: (a) requirements missing or partial; (b) behaviour not asked for (scope creep); (c) requirements that appear implemented but look wrong. Quote the spec line for each finding. Under 400 words."

If the spec is missing, skip the Spec sub-agent and note this in the final report.

### 5. Aggregate

Present the two reports under `## Standards` and `## Spec`, verbatim or lightly cleaned. Do **not** merge or rerank — the axes are separate by design.

End with a one-line summary: total findings per axis, and the worst single issue flagged.

## Why two axes

A change can pass one axis and fail the other:

- Follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Does exactly what the issue asked but breaks conventions → **Spec pass, Standards fail.**

Separate reporting stops one axis from masking the other.
