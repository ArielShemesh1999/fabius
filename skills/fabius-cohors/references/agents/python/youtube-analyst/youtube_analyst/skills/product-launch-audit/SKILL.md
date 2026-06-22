---
name: fabius-cohors-product-launch-audit
description: Audits a product launch by comparing creator verdicts against audience sentiment, then delivers an executive dashboard with a clear pitch angle.
---

### Skill: Product Launch Audit (Seller's Ammunition)

**Objective**: Give a seller a comprehensive audit of what creators AND audiences are saying about a client's product launch, distilled into a pitch-ready executive dashboard.

**Execution Steps**:

1. **Locate**: Call `search_youtube` for the product launch. Use `get_date_range` to filter by `published_after` set to 7–14 days ago to stay within the launch window.

2. **Creator Verdict**: Run `get_video_transcript` on the top 3 review videos. Identify what KOLs praise or criticize (price, features, UX, etc.).

3. **Audience Verdict**: Call `aggregate_comment_sentiment` on those same video IDs. Synthesize what actual consumers say — and whether it aligns with creator opinion.

4. **Synthesize the Pitch**: Identify the gap between creator and audience verdicts. Name the "Pitch Angle" — a specific campaign or messaging opportunity (e.g., "Audience thinks it's expensive; run ads emphasizing free-to-play to correct the misconception").

5. **Deliver Executive Dashboard**:
   - **The Good**: 1–2 positive bullet points.
   - **The Bad**: 1–2 negative bullet points.
   - **Pitch Angle**: Concrete recommendation for the client meeting.
   - **Direct Proof**: 2–3 timestamp links via `generate_timestamp_url` backing up the summary.

**Next Actions**: Ask if the user wants this dashboard published as a clean HTML asset via `publish_file`.
