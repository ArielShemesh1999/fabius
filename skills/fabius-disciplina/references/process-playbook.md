# Fabius Disciplina — process playbook

Loaded on demand by `fabius-disciplina`. The skill has the six phases; this file has the worked detail: a debug walkthrough, the same loop turned on a performance regression, the test anti-patterns to avoid, and the review checklists for a brainstorm and a plan.

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

## A performance regression — the same loop, a different instrument

"It's slow" has no stack trace, so the hypothesize step quietly degrades into ranking suspects by file size. **File size is a bad proxy for cost.** Run the same six steps with measurement as the instrument:

1. **Baseline before you touch anything.** Fix the profile and keep it fixed for every later run: CPU throttled (`Emulation.setCPUThrottlingRate: 4`), a pinned network profile (Fast-3G via `Network.emulateNetworkConditions`), LCP/FCP/long-tasks read off a `PerformanceObserver`. An unbaselined fix is a change, not an improvement.
2. **Isolate by blocking — one dependency at a time.** Abort exactly one origin per variant (`page.route(url => re.test(url), r => r.abort())`) and read the delta against the baseline. That attributes cost to a *cause*, which bytes never do: on one page the fonts cost 1375ms of long tasks, the accessibility widget 1005ms, GSAP 879ms and the chat 338ms — the top cost was not the biggest file, and nothing in the byte list said so.
3. **Take a median, never a single sample.** LCP on one unchanged page swung 1212 / 1856 / 2240 ms across three identical runs. One sample of that spread reads as an ~80% regression that does not exist. Three runs minimum, compare medians, and treat a delta inside the run-to-run spread as no delta.
4. **A/B the obvious optimization too.** Preloading the LCP image and re-encoding the videos both measured as no-ops on that same page, so neither shipped. The convincing fix is a hypothesis like any other — it earns its place from a measured delta, not from being the thing everyone does.
5. **Re-measure live, and compare medians.** A local build hides the production CSP, the cache header and the real network. Same profile, same run count, before and after (`fabius-decor` owns the implementation of the fix; this layer owns the measurement that chooses it).

Loop: baseline → isolate by blocking → fix the top cost → re-measure live and compare medians.

## Test anti-patterns (these tests lie)

- **Testing the mock.** If the assertion only checks that a stub returned what you told the stub to return, it proves nothing. Test the real seam.
- **Asserting on incidental output.** Pinning an exact log string or whitespace makes the test fail on harmless change and pass on real regressions it doesn't cover. Assert the behavior, not the decoration.
- **Sleep-based waiting.** `sleep(2)` then assert is flaky by construction. Wait on the *condition* (poll for the state), not the clock.
- **One mega-test.** A test that exercises ten things tells you "something broke," not what. One behavior per test.
- **Test written after, to pass.** A test you wrote to match the code you already wrote confirms the code does what it does — not what it should. That's why red-comes-first: the failing run proves the test can fail.

## Proving: the result, not the return code

"Prove before done" has a specific trap for a tool-using agent: **the tool succeeds and the state is still wrong.** The API returns `201`, the shell exits `0`, the write "worked" — and the actual result is empty, malformed, or the wrong record. A terminal success is not a task success. So the proof asserts the **result state**, not the call's return code: read back what you wrote, confirm the row exists with the value you meant, look at the rendered page — never infer completion from the mere absence of an error.

And distrust your own confidence when the request is urgent. Prompts that carry urgency markers — "asap", "urgent", "broken", "already should be done" — pull an agent toward acting before it verifies. Urgency is the moment to **keep** the verify step, not skip it; that is exactly when a silent wrong-state ships unnoticed.

## Pair every instruction with a machine check

**If you tell an agent to implement X, ship the executable oracle that proves it did.** An instruction is a hope; a check is a verdict. Codegen without a conformance check produces **plausible-but-wrong** work — code shaped exactly like the thing you asked for that doesn't do it — and plausible-but-wrong is the single failure a human reviewer is worst at catching, because review reads for shape and the shape is right. The instruction and its oracle are one deliverable, not a nice-to-have pair.

Two shapes carry most of the weight:

- **A validator that hard-fails the artifact.** The prose says "the upgrade guide must include a real diff." The check parses the upgrade section and **fails the build** when it holds no unified diff — parsed, not eyeballed. Note where the check lands: on the *artifact*, so the instruction cannot be satisfied by a heading that says "Diff" over a paragraph describing one.
- **One contract test, consumed by every implementation.** The prose says "all five adapters honor the same contract." The check is a single contract-test suite that all five adapters import and run — so the contract is **executed five times** instead of **described once**. This is the shape that stops an instruction from rotting in one implementation silently: divergence turns a suite red on the commit that caused it, rather than becoming a bug report three months later from someone using adapter four.

**fabius already lives this law** — this section only *names* it so it's reusable. `evals/structural.mjs` is **19 machine checks over 15 markdown instruction files**: naming, frontmatter, per-file size budgets, reference integrity, manifest-vs-filesystem agreement, the seal's file hashes and Merkle root, and the coherence of the stated skill count. The skills are prose, and the prose is *tested* — a claim in a contract that drifts from the filesystem fails a run, it doesn't wait for a reader to notice. Nothing there is novel to the repo; what's worth carrying out of it is the rule: when fabius writes an instruction for someone else's agent, it ships the oracle too.

The check comes **first**, for the same reason red-comes-first above: an oracle that has never failed hasn't been shown capable of failing. And it inherits the anti-patterns above — assert the **behavior the instruction names**, not its decoration. A check that pins the exact wording of a guide isn't an oracle for "include a real diff"; it's a tripwire on prose, and it will fail on a rewrite that improved the guide while passing one that gutted it.

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
