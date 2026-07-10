# Fabius Disciplina — process playbook

Loaded on demand by `fabius-disciplina`. The skill has the six phases; this file has the worked detail: a debug walkthrough, the test anti-patterns to avoid, and the review checklists for a brainstorm and a plan.

## A debug, worked end to end

> *Symptom:* "Logout sometimes doesn't clear the session; the next user sees the previous cart."

1. **Reproduce.** Two browser profiles, log in as A, log out, log in as B → B sees A's cart ~1 in 5 times. Intermittent = a race or shared state, not a pure logic bug. The repro is the whole game; without it you are guessing.
2. **Minimize.** Drop the UI. Hit `POST /logout` then `GET /cart` in a loop with two session cookies. Fails ~20%. Now it's a 6-line script, not an app.
3. **Hypothesize (ranked, falsifiable).** (a) the session store key isn't per-user; (b) a cache in front of `/cart` keys on something stable across users; (c) logout clears the cookie but not the server session. Rank by what the 20% rate implies — a cache TTL race fits an intermittent rate better than an always-wrong key.
4. **Instrument.** Log the cache key and the resolved user id on each `/cart`. One assert: `assert cache_key.includes(user_id)`. Run the minimized loop.
5. **Read the evidence.** The cache key is the *route*, not the route + user — hypothesis (b). The 20% is the TTL window where A's response is still warm when B asks.
6. **Fix the cause.** Add the user id to the cache key. Not: shorten the TTL (hides it), not: disable the cache (symptom-removal at a cost).
7. **Regression-test.** The minimized two-cookie loop becomes a permanent test that fails on the old key and passes on the new one.

Note what a symptom-patch would have been: "clear the cache on logout." It would have *reduced* the rate and shipped — and the bug would have returned under load. Root cause means the explanation survives a second look.

## Test anti-patterns (these tests lie)

- **Testing the mock.** If the assertion only checks that a stub returned what you told the stub to return, it proves nothing. Test the real seam.
- **Asserting on incidental output.** Pinning an exact log string or whitespace makes the test fail on harmless change and pass on real regressions it doesn't cover. Assert the behavior, not the decoration.
- **Sleep-based waiting.** `sleep(2)` then assert is flaky by construction. Wait on the *condition* (poll for the state), not the clock.
- **One mega-test.** A test that exercises ten things tells you "something broke," not what. One behavior per test.
- **Test written after, to pass.** A test you wrote to match the code you already wrote confirms the code does what it does — not what it should. That's why red-comes-first: the failing run proves the test can fail.

## Proving: the result, not the return code

"Prove before done" has a specific trap for a tool-using agent: **the tool succeeds and the state is still wrong.** The API returns `201`, the shell exits `0`, the write "worked" — and the actual result is empty, malformed, or the wrong record. A terminal success is not a task success. So the proof asserts the **result state**, not the call's return code: read back what you wrote, confirm the row exists with the value you meant, look at the rendered page — never infer completion from the mere absence of an error.

And distrust your own confidence when the request is urgent. Prompts that carry urgency markers — "asap", "urgent", "broken", "already should be done" — pull an agent toward acting before it verifies. Urgency is the moment to **keep** the verify step, not skip it; that is exactly when a silent wrong-state ships unnoticed.

## Reviewing a brainstorm before you build

- Is the **problem** stated, separate from the solution?
- Are the **success criteria** checkable by something other than opinion?
- Were **2–3 approaches** weighed, with a recommendation and a reason — not one option presented as inevitable?
- Is the **scope** one coherent thing, or several subsystems that should be split?
- Did any **assumption** go unstated? Name it now.

## Reviewing a plan before you run it

- Does every step have a `verify:` that a machine or a quick check could confirm?
- Is each step small enough to hold in context at once?
- Is there a **tracer-bullet** path — one thin end-to-end slice — before the breadth work?
- What's the **rollback** if a step fails midway?
- Could the whole plan be shorter? (`fabius-parcus`: the lazy plan that works is the right plan.)

## Looping alone vs checking in

Strong, checkable criteria let the agent run the whole loop unattended — build, verify, fix, repeat — and only surface at a real decision or a real block. Weak criteria ("make it nice") force a human into every cycle. The work of phase 3 (the plan) is what buys the autonomy in phases 4–6.
