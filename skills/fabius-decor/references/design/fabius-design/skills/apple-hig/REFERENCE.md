---
name: fabius-decor-apple-hig
description: Apple Human Interface Guidelines reference — 14 topic areas covering platforms, foundations, components, patterns, inputs, and technologies for iOS, macOS, visionOS, watchOS, and tvOS.
triggers:
  - "apple hig"
  - "human interface"
  - "ios design"
  - "macos design"
  - "visionos design"
---

# Apple HIG

Apply Apple Human Interface Guidelines to design decisions across Apple platforms.

## When to use

Use when the user asks about platform-appropriate UI patterns, component behavior, spacing, typography, or interaction design for iOS, macOS, visionOS, watchOS, or tvOS.

## Coverage areas

| Area | Topics |
|---|---|
| Platforms | iOS, iPadOS, macOS, watchOS, tvOS, visionOS |
| Foundations | Accessibility, color, icons, layout, motion, typography |
| Components | Bars, buttons, menus, pickers, popovers, sliders, toggles, text fields |
| Patterns | Drag and drop, editing, feedback, loading, modality, navigation, onboarding, search, settings |
| Inputs | Apple Pencil, cameras, Game Controller, gyroscope, keyboards, pointing devices, touch |
| Technologies | App Clips, augmented reality, CarPlay, in-app purchase, Live Activities, Machine Learning, SharePlay, WidgetKit |

## Workflow

1. Identify the target platform(s) and the specific design question.
2. Apply the relevant HIG principle — cite the section by name (e.g. "HIG: Modality > Sheets").
3. Recommend the canonical pattern; flag when the guideline allows platform-specific variance.
4. If the user's design deviates from HIG, explain the trade-off clearly without blocking the choice.

## Key principles to apply by default

- **Clarity** — legible text at every size, precise icons, generous white space.
- **Deference** — UI recedes; content leads.
- **Depth** — realistic motion and layering convey hierarchy without decoration for its own sake.
- **Consistency** — use system controls and standard gestures so users don't re-learn behavior.
- **Feedback** — every action gets an immediate, perceptible response.

## Platform-specific defaults

- **iOS/iPadOS**: Touch targets ≥ 44×44 pt; prefer bottom-anchored navigation (tab bar); modals via sheets.
- **macOS**: Menu bar integration; support keyboard shortcuts for all primary actions; window management via standard chrome.
- **watchOS**: Glanceable first; minimize text input; use complications for recurring data.
- **tvOS**: Focus-engine navigation; avoid hover-only states; large readable type at 10-ft distance.
- **visionOS**: Spatial layout respects user head position; avoid fixed-world elements; use ornaments for window chrome.
