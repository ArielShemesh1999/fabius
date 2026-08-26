---
name: fabius-disciplina-write-a-skill
description: Create new agent skills with proper structure, progressive disclosure, and bundled resources. Use when user wants to create, write, or build a new skill.
---

# Writing Skills

## Process

1. **Gather requirements** — ask:
   - What task or domain does the skill cover?
   - What specific use cases should it handle?
   - Does it need executable scripts or just instructions?
   - Any reference materials to include?

2. **Draft the skill** — create:
   - `SKILL.md` with concise instructions
   - Additional reference files if content exceeds 500 lines
   - Utility scripts if deterministic operations are needed

3. **Review with user** — present draft and ask:
   - Does this cover your use cases?
   - Anything missing or unclear?
   - Should any section be more or less detailed?

## Skill Structure

```
skill-name/
├── SKILL.md           # Main instructions (required)
├── REFERENCE.md       # Detailed docs (if needed)
├── EXAMPLES.md        # Usage examples (if needed)
└── scripts/           # Utility scripts (if needed)
    └── helper.js
```

## SKILL.md Template

```md
---
name: skill-name
description: Brief description of capability. Use when [specific triggers].
---

# Skill Name

## Quick start

[Minimal working example]

## Workflows

[Step-by-step processes with checklists for complex tasks]

## Advanced features

[Link to separate files: See [REFERENCE.md](REFERENCE.md)]
```

## Description Requirements

The description is **the only thing the agent sees** when deciding which skill to load. It appears in the system prompt alongside all other installed skills.

**Goal**: give the agent just enough to know:
1. What capability this skill provides
2. When and why to trigger it (specific keywords, contexts, file types)

**Format**:
- Max 1024 chars
- Write in third person
- First sentence: what it does
- Second sentence: "Use when [specific triggers]"

**Good:**
```
Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction.
```

**Bad:**
```
Helps with documents.
```

The bad example gives the agent no basis to distinguish this from other document skills.

## When to Add Scripts

Add utility scripts when:
- Operation is deterministic (validation, formatting)
- Same code would be regenerated repeatedly
- Errors need explicit handling

Scripts save tokens and improve reliability over generated code.

## When to Split Files

Split into separate files when:
- `SKILL.md` exceeds 100 lines
- Content spans distinct domains
- Advanced features are rarely needed

## Review Checklist

- [ ] Description includes triggers ("Use when...")
- [ ] `SKILL.md` under 100 lines
- [ ] No time-sensitive information
- [ ] Consistent terminology throughout
- [ ] Concrete examples included
- [ ] References stay one level deep
