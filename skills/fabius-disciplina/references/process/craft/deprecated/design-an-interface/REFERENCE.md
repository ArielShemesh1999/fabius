---
name: fabius-disciplina-design-an-interface
description: Generate multiple radically different interface designs for a module using parallel sub-agents, then compare and synthesize. Use when exploring API shape, comparing module designs, or applying "design it twice".
---

# Design an Interface

Your first interface idea is rarely the best. Generate multiple radically different designs in parallel, then compare.

## Workflow

### 1. Gather Requirements

Before designing, understand:

- What problem does this module solve?
- Who are the callers? (other modules, external users, tests)
- What are the key operations?
- Any constraints? (performance, compatibility, existing patterns)
- What should be hidden vs exposed?

Ask: "What does this module need to do? Who will use it?"

### 2. Generate Designs (Parallel Sub-Agents)

Spawn 3+ sub-agents simultaneously via Task tool. Each must produce a **radically different** approach.

```
Prompt template for each sub-agent:

Design an interface for: [module description]

Requirements: [gathered requirements]

Constraints for this design:
- Agent 1: "Minimize method count — aim for 1-3 methods max"
- Agent 2: "Maximize flexibility — support many use cases"
- Agent 3: "Optimize for the most common case"
- Agent 4: "Take inspiration from [specific paradigm/library]"

Output:
1. Interface signature (types/methods)
2. Usage example (how caller uses it)
3. What this design hides internally
4. Trade-offs of this approach
```

### 3. Present Designs

Show each design with:

1. **Interface signature** — types, methods, params
2. **Usage examples** — how callers use it in practice
3. **What it hides** — complexity kept internal

Present sequentially so the user can absorb each before comparison.

### 4. Compare Designs

Compare on:

- **Interface simplicity**: fewer methods, simpler params
- **General-purpose vs specialized**: flexibility vs focus
- **Implementation efficiency**: does shape allow efficient internals?
- **Depth**: small interface hiding significant complexity (good) vs large interface with thin implementation (bad)
- **Ease of correct use** vs **ease of misuse**

Discuss trade-offs in prose, not tables. Highlight where designs diverge most.

### 5. Synthesize

The best design often combines insights from multiple options. Ask:

- "Which design best fits your primary use case?"
- "Any elements from other designs worth incorporating?"

## Evaluation Criteria

**Interface simplicity**: Fewer methods, simpler params = easier to learn and use correctly.

**General-purpose**: Handles future use cases without changes. Beware over-generalization.

**Implementation efficiency**: Does the interface shape allow efficient implementation, or force awkward internals?

**Depth**: Small interface hiding significant complexity = deep module (good). Large interface with thin implementation = shallow module (avoid).

## Anti-Patterns

- Don't let sub-agents produce similar designs — enforce radical difference via explicit constraints
- Don't skip comparison — the value is in contrast, not the individual designs
- Don't implement — this skill is about interface shape only
- Don't evaluate on implementation effort
