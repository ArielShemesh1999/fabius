---
name: fabius-decor-faq-page
description: Generate a single FAQ page with collapsible accordion, real-time search, and category filtering from any domain brief.
triggers:
  - "faq"
  - "FAQ"
  - "frequently asked questions"
  - "help center"
  - "support page"
  - "Q&A"
  - "常见问题"
  - "帮助中心"
---

# FAQ Page Skill

Produce a single FAQ page with collapsible accordion sections, search, and category filtering.

## Workflow

1. **Read the active DESIGN.md** (injected above). Apply component tokens to accordion headers, search input, and category pills.
2. **Pick the domain** from the brief (SaaS, e-commerce, service) and write 12–18 real FAQ entries across 3–4 categories.
   - Fewer than 8 FAQs: ask for more content or generate realistic questions for the domain.
   - 1–5 FAQs: skip categories and search; show a simple list.
   - Answers over 100 words: use paragraphs or bullets.
3. **Sections**, in order:
   - **Header** — page title and optional one-sentence subtitle.
   - **Search bar** — prominent input with placeholder and icon; JS filters questions in real-time.
   - **Category filters** — 3–4 pill buttons (e.g. "Billing", "Account", "Technical", "General"). "All" selected by default.
   - **FAQ accordion** — collapsible question/answer pairs. Each item: clickable header with chevron/plus-minus icon; answer hidden by default, expands with smooth animation; `data-category` attribute for filter targeting.
   - **Footer CTA** — "Still have questions?" with contact link or support email.
4. **Write** a single `<!doctype html>` … `</html>` file with CSS and JS inline.
   - Accordion uses `<details>`/`<summary>` for progressive enhancement, or custom JS with proper ARIA attributes.
   - Search is case-insensitive; filters on question text and answer text.
   - Category filters show/hide by `data-category`.
   - Smooth expand/collapse via `max-height` or `grid-template-rows`.
   - `data-od-id` on header, search, categories, accordion container, footer.
5. **Self-check**:
   - Questions are specific and realistic — no generic placeholders.
   - Answers are 2–4 sentences, complete but concise.
   - Keyboard navigation: Tab through questions, Enter to expand.
   - Mobile-friendly: tappable headers, usable search.

## Output contract

```
<artifact identifier="faq-page" type="text/html" title="FAQ Page">
<!doctype html>
<html>...</html>
</artifact>
```

One sentence before the artifact, nothing after.

## Example entries by category

**Billing** — payment method update, accepted payment types, refund policy, subscription cancellation.

**Account** — password reset, email change, account deletion, data retention after cancel.

**Technical** — supported browsers, mobile app availability, data export, API rate limits.

**General** — what the product is, getting started, customer support availability, terms of service location.
