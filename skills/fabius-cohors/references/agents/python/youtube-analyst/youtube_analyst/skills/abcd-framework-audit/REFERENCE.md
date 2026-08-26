---
name: fabius-cohors-abcd-framework-audit
description: Evaluates a video asset against Google's ABCD framework (Attract, Brand, Connect, Direct) using transcript and metadata, scoring each dimension and delivering optimization recommendations.
---

### Skill: ABCD Framework Audit (YouTube Ads & Marketing)

**Objective**: Score a video against Google's official ABCD framework for effective YouTube creatives. Useful for advertisers, B2B marketers, and gaming publishers evaluating trailers or sponsored content.

**Execution Steps**:
1. **Context**: The user has already identified a video. Do not search for one unless asked.
2. **Disclaimer (CRITICAL)**: Before analysis, output this exact message:
   *"⚠️ **Note on Analysis Scope:** This audit is based strictly on the video's **transcript, title, and metadata** — frame-by-frame visual analysis is not available in this configuration."*
3. **Ingest**: Call `get_video_transcript(video_id)` and `get_video_details(video_id)`. Analyze both against the framework:
   - **Attract**: Does the script hook the viewer in the first 5 seconds?
   - **Brand**: When and how is the product/brand introduced? Natural or forced?
   - **Connect**: Does the script create emotional resonance for the target audience?
   - **Direct**: Is the CTA at the end clear and urgent?
4. **Deliver** the "ABCD Creative Audit":
   - **A – Attract**: Hook evaluation (score /10)
   - **B – Brand**: Product integration evaluation (score /10)
   - **C – Connect**: Emotional resonance and pacing evaluation (score /10)
   - **D – Direct**: CTA evaluation (score /10)
   - **Optimization Recommendations**: 2–3 specific, actionable changes to improve ad performance.

**Next Actions**: Ask the user if they want to publish this ABCD Audit Report as a shareable HTML asset using `publish_file`.
