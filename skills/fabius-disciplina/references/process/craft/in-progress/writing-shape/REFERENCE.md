---
name: fabius-disciplina-writing-shape
description: Take a markdown file of raw material and shape it into a publishable article through a conversational session — drafting candidate openings, growing the piece paragraph by paragraph, arguing about format at each step. Use when the user has notes, fragments, or a rough draft and wants help turning it into something finished.
---

<what-to-do>

The user has passed (or will pass) a markdown file of raw material. Treat it as the input pile — anything from a tidy list of fragments to a wall of unstructured prose to a transcript. Read it end-to-end before doing anything else.

Run a shaping session that produces a separate article document. Do not edit the raw material file — it is read-only to this skill.

If the user did not say where to save the article, ask once and remember the path. The user may edit the article file between turns; always re-read it before writing so their edits are preserved.

</what-to-do>

<supporting-info>

## The loop

1. **Read the pile.** Read the input file in full. Form a sense of what's in it.
2. **Draft 2–3 candidate openings.** Each implies a different thesis or angle. Show all of them. Force the user to pick or compose a hybrid. The chosen opening defines what the rest of the article must do.
3. **Grow paragraph by paragraph.** After the opening lands, ask "given this opening, what does the reader need to hear next?" Pull material from the pile to answer. Argue about whether the next beat is a paragraph, a list, a table, a callout, a quote, a code block — each format choice should be deliberate and defensible.
4. **Append to the article file as you go.** Don't batch. Write each agreed paragraph or block immediately so the user can see the article taking shape.
5. **Loop step 3 until the article is done.** The user decides when it's done.

## Conversational feel

Push back. Refuse to let weak transitions slide. If a paragraph doesn't earn its place, cut it.

Specific moves to keep using:

- "What does this paragraph do for the reader that the previous one didn't?"
- "If I cut this, what breaks?"
- "Is this prose, or should it be a list? Why prose?"
- "This sentence is doing two jobs — split it or pick one."
- "The opening promised X. We've drifted to Y. Either re-thread it or change the opening."

## Pulling from the pile

Treat the raw material as a quarry, not a script. Pull a fragment, rework it to fit the surrounding paragraph, place it. A fragment may be split across paragraphs, merged with another, or paraphrased. The pile's job is to be mined; the article's job is to read as one voice.

If the pile lacks something the article needs, name the gap explicitly: "We need an example here and the pile doesn't have one — give me one now or we cut this section."

## Format arguments to actually have

Weigh these tradeoffs out loud with the user, not silently:

- **Prose vs. list.** Prose carries argument; lists carry parallel items. If items aren't truly parallel, prose is better. If they are, a list is faster to scan.
- **Inline vs. callout.** Tips, warnings, and asides go in callouts (`> [!TIP]`, `> [!NOTE]`) only if they'd genuinely derail the main argument inline. Otherwise leave them inline.
- **Table vs. repeated structure.** Same shape repeating 3+ times with the same fields → table. Otherwise prose with bold leads.
- **Quote vs. paraphrase.** Quote when the original wording is the point. Paraphrase when only the idea matters.
- **Code block vs. inline code.** Multi-line, runnable, or illustrative → block. Single token or identifier → inline.

## Writing rhythm

Append to the article file as each block is agreed. Re-read from disk before every write — the user may have edited between turns. Never overwrite blindly. If the user wants a paragraph rewritten, edit that paragraph in place; leave the rest alone.

## Out of scope

- Mining for new fragments not in the pile (name the gap and either get the user to fill it or cut the section).
- Editing the raw material file.
- Publishing, formatting for a specific platform, or adding frontmatter the user didn't ask for.

</supporting-info>
