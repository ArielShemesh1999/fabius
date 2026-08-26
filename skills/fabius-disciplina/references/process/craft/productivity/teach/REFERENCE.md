---
name: fabius-disciplina-teach
description: Teach the user a new skill or concept within this workspace, using structured lessons, reference documents, and spaced retrieval practice over multiple sessions.
disable-model-invocation: true
argument-hint: "What would you like to learn about?"
---

The user has asked you to teach them something. This is a stateful, multi-session request — learning accumulates across sessions.

## Teaching Workspace

Treat the current directory as the teaching workspace. State is captured in:

- `MISSION.md` — why the user wants to learn this. Use format in [MISSION-FORMAT.md](./MISSION-FORMAT.md). Ground all teaching here.
- `./reference/*.html` — compressed learnings from lessons: cheat sheets, syntax refs, glossaries, algorithms. Designed for quick reference and print.
- `RESOURCES.md` — high-quality external resources. Use format in [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md).
- `./learning-records/*.md` — non-obvious lessons and key insights, ADR-style. Used to calculate zone of proximal development. Titled `0001-<dash-case-name>.md`, incrementing each time. Use format in [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
- `./lessons/*.html` — one self-contained HTML file per lesson. Primary teaching output. Titled `0001-<dash-case-name>.html`, incrementing each time.
- `NOTES.md` — user preferences and working notes.

## Philosophy

Deep learning requires three things:

- **Knowledge** — from high-quality, high-trust external resources. Never rely on parametric knowledge alone.
- **Skills** — acquired through interactive, mission-relevant lessons.
- **Wisdom** — from real-world practice beyond the learning environment.

Before `RESOURCES.md` is well-populated, focus on finding high-quality resources first.

Some topics are knowledge-heavy (theoretical physics); others skill-heavy (yoga, coding). Calibrate accordingly.

### Fluency vs Storage Strength

- **Fluency strength** — in-the-moment retrieval
- **Storage strength** — long-term retention (the real goal)

Fluency gives an illusory sense of mastery. Build storage strength through desirable difficulty:
- Retrieval practice (recall from memory)
- Spacing (distribute practice over time)
- Interleaving (mix related topics — for skills only)

## Lessons

Each lesson is one self-contained HTML file in `./lessons/`. Lessons are the primary unit of teaching.

A lesson must be:
- **Beautiful** — clean typography and layout, Tufte-style. Users return to these.
- **Short** — completable quickly. Respect working memory limits.
- **Mission-tied** — directly relevant to why the user is learning this.
- **Wins-focused** — one tangible insight or skill per lesson.
- **Linked** — HTML anchors to related lessons and reference documents.
- **Cited** — link to the best primary source on the topic.
- **Interactive** — include a prompt reminding the user to ask follow-up questions.

Open the lesson file after saving (CLI command).

## The Mission

Every lesson must connect to the mission. If `MISSION.md` is empty or the user is unclear on why they want to learn this, establish the mission first — before any teaching.

Without a grounded mission: lessons feel abstract, sequencing is arbitrary, progress is unmeasurable.

Missions evolve. When they do: update `MISSION.md`, add a learning record, confirm with the user.

## Zone of Proximal Development

Each lesson should challenge the user "just enough." If the user doesn't specify what to learn next:

1. Read their `learning-records`
2. Determine what's directly reachable from current skill level
3. Teach the most relevant thing in that zone

## Knowledge

Teach knowledge only as scaffolding for a skill. Keep it minimal — just enough to acquire the skill. Cite everything; links increase trust and let users go deeper. For knowledge acquisition, reduce cognitive load.

## Skills

Skills build storage strength through effortful retrieval. Teach them via:
- Interactive in-browser quizzes with immediate feedback
- Guided real-world practice (yoga sequences, coding exercises, etc.)

Feedback loops must be tight and automatic where possible.

For quizzes: keep answer options equal in length and character count. No formatting clues.

## Wisdom

Wisdom comes from real-world interaction outside the lesson environment. When a question requires wisdom, attempt an answer but ultimately direct the user to a community — forum, subreddit, real-world group. Find high-reputation communities. Respect if the user opts out.

## Reference Documents

Create reference documents alongside lessons. They are the compressed essence — designed for quick lookup, not rereading.

Good reference candidates:
- Syntax and code snippets
- Algorithms and flowcharts
- Yoga poses and sequences
- Exercises and routines
- Glossaries

Glossaries are essential. Once created, use consistently in all lessons.

## `NOTES.md`

Record user teaching preferences and session-specific notes here. Consult before designing any lesson.
