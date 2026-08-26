# Fabius Decor — generative-imagery prompt craft

The on-demand depth for `fabius-decor`'s generative-imagery concern. The skill is the contract; this is how you run it. Scout wide, strike narrow — a prompt is a structured slot fill, not a wish.

This obeys every `fabius-decor` law (one accent of intent, restraint, no padding). It is prompt craft, not a second design owner.

## The slot model

Model the prompt as **ordered slots**, not a sentence. Order matters — image models weight earlier tokens more.

| Slot | Status | Fill rule |
|---|---|---|
| subject | **required** | the literal thing. Fill from intent; never leave empty. |
| facial / detail | **required** | features, age, build, distinguishing detail. Sane default if silent. |
| styling | **required** | hair, wardrobe, makeup — *derived*, see the cascade below. |
| expression | optional | leave empty unless the user signals mood. Don't invent one. |
| **lighting** | **required** | never optional. Always a named style — see the lighting map. |
| scene | optional | environment/background. Empty beats a generic "in a studio". |
| technical / quality | optional | camera, lens, bokeh, resolution. Add when it earns its place. |

Rule: fill every **required** slot with an intelligent default even when the user is silent; leave **optional** slots empty rather than padding noise. An empty optional slot is signal — a filler one is drift.

## Lighting is mandatory

The single highest-leverage lever and the widest amateur-vs-pro gap. Never emit a prompt without it. Map the user's phrasing to a *named* style:

| User says | Named lighting |
|---|---|
| (nothing) | natural |
| "cinematic" | cinematic |
| "neon" / "cyberpunk" | neon |
| "soft" / "gentle" | soft |
| a named director / DP | that director's signature look |

If the user names a director, encode the *signature* (key/fill ratio, palette, contrast), not the name alone — the name is a pointer, the recipe is the lever.

## The dependency cascade

One high-level signal should propagate to several coupled slots. Derive; don't interrogate the user slot by slot.

```
era / setting  →  makeup  +  hair  +  wardrobe   (set together, not asked one at a time)
  ancient  →  traditional / period-appropriate
  modern   →  natural / contemporary
```

Gate era-inappropriate combinations at **error** level, not warning: a period costume must not map to modern or trend-of-the-moment beauty styling. A clash here is a bug, not a taste call.

## The conflict pass — run before emitting

Before returning any prompt, scan for clashes across four axes:

- **Cultural** — elements should belong to one coherent culture, not a mashup.
- **Temporal** — no modern + ancient mix (the cascade's gate, re-checked at the whole-prompt level).
- **Biological** — physical traits stay plausible for the stated subject.
- **Stylistic** — one coherent rendering language, not three fighting.

On a clash: **explain it → show the auto-correction → allow override.** Never silently rewrite the user's intent, and never ship the clash.

## Style is not identity

A **style** keyword is a rendering technique; it must not overwrite an **attribute** slot.

- "anime" = a render technique. An East-Asian subject rendered in anime style keeps their attributes — the style does not become the ethnicity.
- A style token touches the *technical/quality* and *styling* slots; it must never silently rewrite *subject* or *facial/detail*.

When a word could read as either style or identity, resolve it to style and leave the identity slot the user actually gave you intact.

## Library + free-text — division of labor

Two sources, merged into one prompt:

- **Library (reusable set).** General, recombinable elements you *can* enumerate: lighting recipes, camera/lens choices, color schemes, quality tags. Keep these as a curated set and recombine.
- **Free-text (open set).** Content no library can ever fully list: named characters, historical figures, specific powers, exotic materials. Let the model supply these.

Merge both into one coherent prompt. Select library elements by best **semantic fit to intent** — not by greedily maximizing raw "quality score". A perfectly-lit prompt that misses the mood is a worse fit than a plainer one that lands it.

## Structured color schemes (for design / poster prompts)

Define palettes **structurally**, not ad hoc, so they recombine and stay on-brand:

```
scheme = {
  base_hue:   0–360,           # the anchor
  saturation: [min, max],      # range, not a point
  lightness:  [min, max],
  variants:   [named hex …]    # concrete swatches
}
grouped under named moods:  warm/cute · modern/minimalist · …
```

Pick a mood, draw from its range — recombinable and consistent, never a one-off hex pulled from the air. This is the imagery cousin of the decor token contract ([../SKILL.md](../SKILL.md)): name it once, reference it everywhere.

## Completeness checklist — before returning a prompt

- [ ] **Subject identity** present and intact (not overwritten by a style word).
- [ ] **Lighting** named (mandatory — never empty).
- [ ] **Explicit visual style** stated when the task is style-relevant.
- [ ] **Quality / technical tags** where they earn it — camera, bokeh, resolution (e.g. 8K, photorealistic).
- [ ] **Conflict pass** run; any clash explained + auto-corrected + overridable.
- [ ] Optional slots **empty, not padded**, where the user gave no signal.

## Honesty — generalize, don't hardcode

The source repo is heavily culture-specific (Chinese directors, traditional-makeup names, Chinese color names). **Generalize the *rules*; do not hardcode the culture-specific *values* as universal defaults.** "Ancient → traditional makeup" is a sound cascade; baking one culture's traditional look in as *the* default is the failure mode.

Element counts the repo reports (e.g. ~1,246 elements, early-2026 snapshot) are *its* database size, not fabius rules — treat them as upstream metadata, never fabius's own numbers. The technique transfers; the table contents are point-in-time and parochial.

Pairs with `fabius-parcus` (no padded slots — the smallest prompt that lands the image) and [`visualization.md`](visualization.md) for the tokenized color rules shared with charts. No separate Figura palette library is bundled.

Adapted from huangserva/skill-prompt-generator (MIT) — re-expressed in fabius's own voice.
