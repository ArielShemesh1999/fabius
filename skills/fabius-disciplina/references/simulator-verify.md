# Fabius Disciplina — the on-simulator prove loop

The on-demand depth for `fabius-disciplina`'s *prove* step on a UI app. The skill is the contract; this is how you run it on a device. Scout wide, strike narrow — assert by meaning, screenshot last.

This is the iOS instantiation of phase 6 (*prove before "done"*): a claim that a UI app works needs evidence from a real-ish device, not green code. The three load-bearing principles — **semantic-tree assertion**, **progressive-disclosure build output**, **token budgeting** — generalize to any UI-on-device verification (Android emulator, web headless, native). iOS `simctl`/`xcodebuild` is the worked example.

## The loop, in order

| # | Step | Cheap default |
|---|------|---------------|
| 1 | **Health-check** the environment | xcode-select path, simulator runtime present, a target device exists |
| 2 | **Build + test** via an `xcodebuild` wrapper | summary line + result-bundle id, not the full log |
| 3 | **Boot + launch** | `xcrun simctl boot <udid>` → install → `launch` |
| 4 | **Assert state via the accessibility tree** | find by text / type / id — the verification that actually counts |
| 5 | **Screenshot** | only for visual confirmation, never as the primary check |
| 6 | **On FAILURE, capture full state** | screenshot + UI hierarchy + logs + device info, one artifact |

Verification is **structured tree assertion first, pixels last.** Steps 1–4 prove the screen reached state X; step 5 is for a human's eyes; step 6 only fires when something broke.

## Why the tree beats coordinate tapping

Query the live UI by semantic **meaning** — label, type, id, fuzzy text — not by pixel coordinates.

- **Cheaper.** A tree query is structured text; a screenshot is a large image every check. Asserting "is the screen at state X" off the tree costs orders of magnitude less than a screenshot per check.
- **More robust.** Coordinates break on every layout shift, font scale, device size, or rotation. A semantic query survives all of them — it asks *what is on screen*, not *where*.

Make the tree the **default** for any "did we reach state X" assertion. Reserve screenshots for two jobs only: visual-diff (regression) and bug reports.

## Progressive-disclosure build output

Never dump the full `xcodebuild` log into the model. It is mostly noise and it is expensive.

- Return a **summary line** + a **result-bundle id**, e.g. `Build succeeded · 0 errors · 3 warnings [xcresult-7f3a…]`.
- Fetch specific errors / warnings / logs **on demand** by id.
- Parse from the **`.xcresult` bundle**, not by scraping stdout — the bundle is structured; stdout scraping is brittle.
- **Cap** the number of errors shown (first N); link the rest.

## Screenshot token budgeting

When you do send an image, size it to the question. Always resize/compress **before** sending.

| Preset | Use for |
|--------|---------|
| `quarter` | quick "is something there" check |
| `half` | default — readable, cheap |
| `full` | only when pixel detail genuinely matters (visual-diff, a rendering bug) |

The upstream skill **reports** ~96% token reduction from sizing/compression, and a task pass-rate of 100% vs 46% without it. Treat those as *reported by the skill*, not fabius-measured numbers.

## Minimal pure-`simctl` cheat sheet

No framework needed. `booted` is a literal device id — use it directly.

```bash
xcrun simctl list devices | grep Booted              # find the running device
xcrun simctl boot <udid>                              # or: open -a Simulator
xcrun simctl install booted MyApp.app
xcrun simctl launch booted com.example.MyApp
xcrun simctl io booted screenshot shot.png
xcrun simctl io booted recordVideo clip.mp4           # ^C to stop
xcrun simctl spawn booted log stream --predicate 'process == "MyApp"'
xcrun simctl get_app_container booted com.example.MyApp data   # sandbox path
```

Lead with pure `xcrun simctl` (no extra install). IDB is optional and itself flaky — reach for it only when plain `simctl` can't express the assertion.

## Troubleshooting — problem → fix

| Symptom | Fix |
|---------|-----|
| Simulator won't boot | `killall Simulator && xcrun simctl erase <udid>` |
| `No booted devices` | `open -a Simulator` |
| App won't launch | `simctl terminate booted <id>` then `launch` again |
| Accessibility tree empty | app must be **foreground** — relaunch and bring it forward |
| Storage full | `xcrun simctl erase <udid>` — **destructive**, wipes the device |

## Reusable test recipes

- **Smoke** — boot → launch → a11y audit (tree present, key element found) → one screenshot. The fast "it runs and the main screen loads" gate.
- **Visual regression** — `baseline.png` vs `current.png` pixel diff against a pass/fail threshold. Fail loud when the diff exceeds it.
- **Multi-device matrix** — loop `create → boot → install → launch → screenshot → delete` across a device list. Clean up every device you create.
- **Full bug-report snapshot** — screenshot + UI hierarchy + logs + device info collected into one markdown artifact. This is step 6 of the loop, packaged.

## Design contract for any agent-facing CLI wrapper

The general template behind a good `simctl`/`xcodebuild` wrapper — reuse it for any device verifier:

- Every command supports `--json`, `--help`, `--verbose`.
- **Default output 3–5 lines.** Detail is opt-in (`--verbose`, or fetch-by-id), never the default firehose.
- **Auto-detect the booted device** — don't make the agent pass a udid it has to go look up.
- **Never `shell=True`.** Pass argv lists; no string interpolation into a shell.
- Make operational limits — **timeouts, output caps** — **env vars**, so the same skill works on a fast laptop and a slow CI runner without edits.
- **Prove with a number** where feasible: a before/after task-success rate beats "it built."

Keep the owning SKILL.md **lean**: this is the iOS-specific instantiation of the existing *prove* discipline (`../SKILL.md`, phase 6), not a competing process verb. It generalizes — the principles, not the `simctl` commands, are the reusable part. The library it belongs to is indexed in `../../../CORPUS.md`.

---

Adapted from conorluddy/ios-simulator-skill (MIT) — re-expressed in fabius's own voice.
