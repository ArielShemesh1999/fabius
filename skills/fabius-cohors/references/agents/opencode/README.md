# OpenCode — Agent Definitions

[OpenCode](https://opencode.ai) is the open-source coding agent that runs in your terminal, IDE, or desktop. 160k★, 7.5M monthly developers. It pairs naturally with this catalog: import any ADK agent definition (Python / Go / Kotlin) as an OpenCode agent and run it against your own model.

## Why the agent corpus + OpenCode

OpenCode lets you compose **per-project specialist agents** with explicit permissions, custom system prompts, and per-agent model overrides. The 85 ADK samples in this repo provide ready-made domain prompts (claim adjudication, KYC, brand alignment, RAG, supply chain, etc.) you can paste into OpenCode agent markdown to instantly spin up a domain expert without re-engineering it from scratch.

## Install

```bash
curl -fsSL https://opencode.ai/install | bash
```

Desktop beta available for macOS, Windows, Linux.

## Core features

- **LSP integration** — auto-loads Language Server Protocols so the LLM sees real type info
- **Multi-session** — run multiple agents simultaneously on the same project
- **Shareable sessions** — generate links to sessions for reference and debugging
- **Auth flexibility** — connect via GitHub Copilot or OpenAI ChatGPT Plus/Pro accounts
- **Model flexibility** — 75+ LLM providers via [Models.dev](https://models.dev), including local models
- **Privacy** — OpenCode does not store any code or context data

## Agent definition format

Agents are defined in two formats: **JSON** inside `opencode.json`, or **markdown** files.

### Markdown location

- **Global:** `~/.config/opencode/agents/`
- **Per-project:** `.opencode/agents/`

The markdown filename becomes the agent identifier (`review.md` → `review` agent).

### Markdown frontmatter schema

```yaml
---
description: What the agent does (required)
mode: subagent|primary|all
model: provider/model-id
temperature: 0.0-1.0
top_p: 0.0-1.0
steps: number
disable: true|false
hidden: true|false  # subagents only
color: hex|theme-color
permission:
  read: allow|ask|deny
  edit: allow|ask|deny
  bash: allow|ask|deny|object
  task: object       # primary agents only
---
```

### JSON form (inside opencode.json)

```json
{
  "agent": {
    "review": {
      "description": "Reviews code for best practices",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-20250514"
    }
  }
}
```

## Agent types

| Type | Description | Built-in examples |
|------|-------------|-------------------|
| **Primary** | Main assistants you interact with directly; Tab to switch | Build (all tools), Plan (restricted) |
| **Subagent** | Specialized helpers invoked automatically or via `@mention` | General, Explore, Scout |

## Example: restrictive read-only reviewer

```yaml
---
description: Code review without edits
mode: subagent
permission:
  edit: deny
  bash: deny
---
You are a senior code reviewer. Read the diff, identify bugs, suggest improvements. Never modify files. Never run commands.
```

## Example: fine-grained bash control

```json
{
  "permission": {
    "bash": {
      "*": "ask",
      "git status *": "allow",
      "git diff *": "allow",
      "pnpm test *": "allow"
    }
  }
}
```

## Example: external prompt reference

```yaml
---
description: Claim adjudicator (ADK port)
mode: subagent
model: anthropic/claude-opus-4-5
permission:
  edit: deny
---
{file:../../python/claim-adjudication-agent/README.md}
```

The `{file:./path}` directive pulls an external prompt file in at load time — perfect for reusing ADK agent READMEs as OpenCode system prompts.

## Creation command

```bash
opencode agent create
```

Interactive tool generates agent configuration with guided setup for description, permissions, and identifier.

## Mapping ADK agents → OpenCode agents

Each agent in this repo's `python/`, `go/`, `kotlin/`, `java/`, `typescript/`, `android/` folders has a README describing its system prompt, tools, and capabilities. To port one to OpenCode:

1. Create `.opencode/agents/<agent-name>.md`
2. Write frontmatter (`description`, `mode`, `model`, `permission`)
3. Paste the ADK agent's prompt/role from its README as the markdown body
4. Restart OpenCode — agent appears under `@<agent-name>`

See [opencode/examples/](examples/) for ported agent stubs.

## Reference

- Docs: https://opencode.ai/docs
- Agents docs: https://opencode.ai/docs/agents
- Models: https://models.dev
- GitHub: https://github.com/sst/opencode
