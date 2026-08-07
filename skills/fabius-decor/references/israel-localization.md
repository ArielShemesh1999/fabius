# Fabius Yisrael — Israeli & Hebrew localization

Loaded on demand by `fabius-decor` (pairs with **Fabius Bidi**). For software built for the **Israeli market** — Hebrew RTL that a native reader trusts, the Israeli *legal* obligations that ship with it (accessibility, anti-spam, privacy), and the Israeli data formats. The RTL/BiDi *mechanics* (logical CSS, isolation, mirroring, fonts) live in **Fabius Bidi**; this is the Israel-specific layer *on top* — the law, the formats, the i18n edge-cases. fabius ships blue-and-white by default.

**Honesty note.** Israeli law and rates change by amendment and by budget. Every ₪ figure, rate, and threshold below is stated as of **2026** and marked where it is volatile — treat those as **config-driven**, and verify the live figure before shipping compliance-critical UI. Legal claims are grounded in the governing statute/regulation, not invented.

## Accessibility is the law — IS 5568 (ת"י 5568)

In Israel, web accessibility is not a nicety — it is a **statutory duty already in force** (deadline for existing sites was **26 Oct 2017**; new sites must be born accessible).

- **The standard:** ת"י 5568 — the Standards Institution of Israel's adoption of W3C **WCAG**. Part 1 = web content; **Part 2 (2023) = digital documents** (PDF/office). **Read the chain, never a vendor page.** תקנה 35 binds a service provider to ת"י 5568 at level **AA**; the current Part 1 is the edition of **28 Sept 2023** (notice published ברשומות 22 Oct 2023, superseding the May 2021 edition, **zero amendment sheets since**); and that edition's own conformance notice declares it **identical to WCAG 2.0 of 11 December 2008**, bar the national changes and additions, digital documents excluded. So the **legal floor is WCAG 2.0 Level AA**, and only a new edition of 5568 raises it — a newer W3C Recommendation does not. Much of the Israeli accessibility trade writes "5568 = WCAG 2.1"; the standard's front matter says 2.0. Quote the front matter.
- **Write 2.2 AA into the spec anyway.** **WCAG 2.2** is the current W3C Recommendation (first published Oct 2023; current revision **12 Dec 2024**) and was approved as an ISO standard — **ISO/IEC 40500:2025** — on 21 Oct 2025. Content conforming to 2.2 conforms to 2.0 and 2.1 by construction, so one target clears the Israeli floor instead of three, and it is what tenders and audits increasingly ask about: target size, focus not obscured, dragging alternatives, accessible authentication. *(EN 301 549 — the EU yardstick an Israeli exporter is also measured against — is still harmonised at V3.2.1 / WCAG 2.1; a V4 citing 2.2 is expected, so 2.2 covers both without a second pass.)* Reading an old audit template: WCAG 2.2 **removed 4.1.1 Parsing** — don't carry it forward as a finding. The criteria themselves → **`references/platform-baseline.md`**.
- **The governing law:** חוק שוויון זכויות לאנשים עם מוגבלות (1998) + תקנות … (התאמות נגישות לשירות), 2013.
- **Accessibility statement (הצהרת נגישות) — mandatory.** Post the accommodations made + the coordinator's contact. A **missing/non-compliant statement is grounds for immediate suit with no prior-notice cure period** (unlike ordinary defects, which get a demand + ~60 days). Don't ship an Israeli site without one.
- **Accessibility coordinator (רכז נגישות):** required for any public-service provider with **25+ employees**.
- **Enforcement:** נציבות שוויון זכויות; civil damages **up to ₪50,000 per violation without proof of harm**, plus administrative sanctions.
- **Exemptions (turnover-based):** עוסק פטור → exempt; turnover **< ₪120k/yr** → 3-yr exemption; **₪120k–1M** → 3-yr exemption for *existing* sites only; **> ₪1M** → no automatic exemption (petition on undue-burden grounds). *(thresholds are config-driven.)*
- **Delta from plain WCAG for Hebrew:** `dir="rtl" lang="he"` on the root; the statement page + an accessibility menu/widget are a de-facto market expectation — its launcher pins with physical CSS at a very high `z-index` and will **not** flip with your `dir`, so clear its corner per the clearance carve-out in **Fabius Bidi**; validate contrast/labels on **actual Hebrew glyphs** and test with a Hebrew screen reader (NVDA/JAWS Hebrew, VoiceOver `he-IL`); mixed Hebrew+Latin+digits must satisfy WCAG 1.3.2 *meaningful sequence* — the bidi-isolation rule in **Fabius Bidi**.

## Anti-spam — Chok HaSpam (תיקון 40, §30א)

Commercial messaging to Israelis is **opt-in by law** (Amendment 40 to the Communications Law, §30א, in force since 1 Dec 2008). Getting this wrong is the most-litigated consumer issue in Israel.

- **Consent first.** No **דבר פרסומת** (advertising message) without the recipient's **prior explicit consent**, across **email · SMS · fax · automated dialing**.
- **Every message must:** be labeled **"פרסומת"** (in email, in the subject/opening); identify the **advertiser** (name, address, contact); and state the **right + method to opt out**.
- **Unsubscribe (הסרה):** simple, **free**, and available **at least by the same channel** the message was sent. Honor withdrawal immediately.
- **Statutory damages: up to ₪1,000 per message, without proof of harm**, where sent knowingly — this is what drives Israel's spam class/small-claims volume.
- **Existing-customer exception:** consent isn't required if the recipient gave their details *in the course of a purchase/negotiation*, was told they'd be used for marketing, the messages concern **goods/services of the same kind**, and an opt-out was offered.

*(A lead form or email campaign for the Israeli market bakes these in — pairs with `fabius-mercatus`, whose copy owns the message; this owns the legal frame.)*

## Privacy — חוק הגנת הפרטיות + PPA + Amendment 13

Israel's Protection of Privacy Law (1981), overhauled by **Amendment 13 (תיקון 13), in force since 14 August 2025** — so it is **live and enforceable** now. Operate on a **GDPR-adjacent posture**.

- **Database registration narrowed:** the old broad רישום מאגר duty is largely gone — registration now targets **public bodies** and **data brokers (סוחרי מידע) holding data on > 10,000 people**; separately, processing **high-sensitivity data on 100,000+** carries a **notification** duty to the PPA.
- **PPA enforcement + fines:** the הרשות להגנת הפרטיות gains audit, administrative-investigation, and **administrative monetary sanctions** — reported magnitude **tens of thousands → millions of ₪** for extensive/ongoing violations, with a per-data-subject component. *(exact fine tables are config-driven — verify current.)*
- **DPO (ממונה על הגנת הפרטיות):** mandatory for public bodies, data brokers, entities whose core activity is large-scale processing of **sensitive** data, systematic-monitoring operations, and financial bodies.
- **High-sensitivity data (מידע בעל רגישות גבוהה):** health, genetic/biometric, political/religious views, sexual, criminal, financial/salary, and **location** data.
- **Also:** breach-notification duties; security-by-design per the 2017 Data Security Regulations.

*(Threat-modeling an Israeli product's data handling pairs with `fabius-praesidium`; this layer supplies the local obligations.)*

## Israeli data formats & validation

**תעודת זהות (Israeli ID) — 9 digits, mod-10 check.** Left-pad short numbers to 9 first. Weights `1,2,1,2,1,2,1,2,1`; multiply each digit, and if a product > 9 subtract 9 (sum its digits); the total must be `≡ 0 (mod 10)`.

```js
// e.g. 123456782 → valid
function validTeudatZehut(id){
  id = String(id).padStart(9, '0');
  if (!/^\d{9}$/.test(id)) return false;
  const sum = [...id].reduce((acc, ch, i) => {
    let n = +ch * ((i % 2) + 1);        // weights 1,2,1,2...
    if (n > 9) n -= 9;
    return acc + n;
  }, 0);
  return sum % 10 === 0;
}
```

| Field | Rule |
|---|---|
| **Phone** | `+972`, trunk `0` dropped after it. Mobile `05x` (050/052/053/054/055/058…); landline geographic `02` Jerusalem · `03` Center · `04` North · `08` South · `09` Sharon; VoIP `07x`. Display `0XX-XXXXXXX` / `0X-XXXXXXX`. |
| **Postal code (מיקוד)** | **7 digits** (5-digit expired Jan 2013); often `XXXXX XX`. |
| **Company / tax** | **ח"פ** 9 digits (incorporated companies start with **5**); **עוסק מורשה** charges VAT (VAT id = ח"פ or owner's ת"ז); **עוסק פטור** below the annual ceiling (**≈ ₪120k**, updated yearly — config), doesn't charge VAT. *(ח"פ has no officially published check-digit — don't assert one.)* |
| **VAT (מע"מ)** | **18%** since 1 Jan 2025 (a further rise to 19% for 2026 was **not** adopted). **Config-driven — never hardcode; it changes by budget.** |
| **Currency** | New Shekel **₪ / ILS**, subunit **agora (1/100)**; `Intl.NumberFormat('he-IL',{style:'currency',currency:'ILS'})` → the **₪ sits *after* the number** (`1,234.50 ₪`) in an RTL context. Don't hardcode a `₪`-prefix. |
| **Date** | Little-endian **DD.MM.YYYY** (dot most common); Hebrew calendar via `Intl.DateTimeFormat('he-IL-u-ca-hebrew', …)`. Numbers inside a date read LTR. |

## Hebrew i18n

- **Plurals: `one` / `two` / `other` — NOT `many`.** Modern CLDR (`Intl.PluralRules('he')`) has exactly three cardinal categories; the `many` bucket was **removed in CLDR 24 (2013)**. Libraries pinned to old CLDR still emit a stale `many` form and break. The category devs forget is the **dual `two`** — always ship a distinct 2-form:

  ```
  one:   פריט אחד
  two:   שני פריטים
  other: {n} פריטים
  ```

- **Formatting:** always via `Intl` with `he-IL` (numerals, grouping, the trailing ₪). Never hand-place the symbol.
- **Punctuation — distinct Unicode code points, not ASCII:** geresh **׳ U+05F3** (abbreviations, single-letter gematria) ≠ apostrophe `'`; gershayim **״ U+05F4** (acronyms — **תשפ״ד**, **צה״ל**; multi-letter numerals) ≠ quote `"`; maqaf **־ U+05BE** (the Hebrew hyphen, sits high — **בית־לחם**) ≠ `-`.

## Hebrew in documents — the "reversed in Word/PDF" bug

Low-level PDF/doc engines place glyphs in **logical (memory) order**, do **no bidi reordering**, and set **no RTL run** — so Hebrew comes out visually reversed and mixed Hebrew+digits scrambles. The fix is to run the Unicode Bidi Algorithm and set direction:

- **`python-bidi`** — reorders a logical Hebrew string to correct visual order before drawing. **Hebrew needs bidi reordering but NOT reshaping** — `arabic_reshaper` is an Arabic-only cursive-joining step; applying it to Hebrew is a common mistake.
- **ReportLab** — 4.4.0+ (2025) added native HarfBuzz shaping + RTL (`rlbidi`, experimental); on older versions pre-process through `python-bidi`.
- **python-docx** — set `w:bidi` on the paragraph and `w:rtl` on the run (write the XML; there's no first-class API) + a Hebrew font.
- **WeasyPrint / HTML→PDF** — `direction: rtl` + `lang="he"` on the root; it honors CSS bidi when the markup is right. Do **not** add `unicode-bidi: plaintext` here — it re-resolves each *line's* base direction from that line's first strong character and so defeats the explicit RTL paragraph direction the next bullet requires: any Latin-first heading, table cell or SKU line flush-**lefts** in the output. Reserve it for a block of genuinely per-line-unknown user text (→ **Fabius Bidi**).
- **Universal:** embed a font that actually **contains Hebrew glyphs** (verify cmap coverage — missing-glyph fallback yields tofu) and set an **explicit RTL paragraph direction**.

## gov.il design (IGDS)

Israel's **National Digital Agency (מערך הדיגיטל הלאומי)** ships the **Israeli Government Design System** — a component library that is **WCAG 2.1 AA by default, framework-agnostic, Hebrew-RTL-first**, distributed as a Figma community file, and slated to be mandatory for new government digital projects. For a public-sector or gov-adjacent Israeli product, aim at IGDS's patterns and typography rather than inventing chrome. *(Its exact mandated token set/typeface — reportedly in the Assistant/Rubik/Almoni/Ploni family range — should be read from the live IGDS file; don't assert a specific brand font blind.)* Hebrew open fonts and the missing-glyph rule → **Fabius Materia** / **Fabius Bidi**.

## The Israeli ship checklist

- [ ] `dir="rtl" lang="he"` on the root; WCAG **2.2 AA** validated on **Hebrew glyphs** + a Hebrew screen reader (תקנה 35 → ת"י 5568 → WCAG **2.0** AA is the legal floor; 2.2 is the spec target).
- [ ] **Both** contrast floors measured on rendered Hebrew — 4.5:1 text, **3:1 non-text** (focus ring, input border, chart series, meaningful hairline). Hebrew has no ascenders or descenders and a different stroke rhythm, so a pair that passed on Latin is not proof.
- [ ] **Accessibility statement** page present; **רכז נגישות** appointed if ≥ 25 employees.
- [ ] The accessibility widget's launcher is cleared with **physical** padding (it does not flip with `dir`), and every interactive control is **hit-tested** with `document.elementsFromPoint(cx, cy)[0]` — no send button, no CTA, sits under it.
- [ ] Any marketing message: prior **opt-in**, labeled **"פרסומת"**, sender identified, free **הסרה** on the same channel.
- [ ] Personal-data handling: registration/notification if triggered, **DPO** where required, breach-notification ready (Amendment 13 posture).
- [ ] **ת"ז**, phone, postal, ח"פ validated; **VAT rate + עוסק-פטור ceiling are config**, not literals.
- [ ] Plurals cover **one / two / other**; numbers/currency via `Intl('he-IL')`; geresh/gershayim/maqaf are the real code points.
- [ ] Generated Hebrew documents run through bidi (python-bidi / ReportLab shaping / `w:rtl`) with a Hebrew-glyph font — verified **not** reversed.

## Pairs with · credit

**Fabius Bidi** (RTL/BiDi mechanics — the layer under this), **Fabius Materia** (Hebrew open fonts), `fabius-mercatus` (the Chok-HaSpam-compliant message), `fabius-praesidium` (the privacy threat-model + IS-5568 enforcement posture). **Credit:** this layer's coverage was *informed by* the Israeli-market skill set **Skills-IL** (agentskills.co.il · github.com/skills-il, **MIT**) — studied for what an Israel-ready product must handle, then authored originally in fabius's own voice per the repo's originality charter (see `credits/`).
