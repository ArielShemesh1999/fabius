---
name: fabius-cohors-deep-exploration
description: Reads transcripts across multiple videos, synthesizes core arguments, and generates direct timestamp jump-links to the exact moments that answer the user's query.
---

### Skill: Deep Exploration & Timestamp Targeting

**Objective**: Save the user from watching hours of video by autonomously reading transcripts, synthesizing core arguments, and generating direct jump-links to the exact moments of interest.

**Execution Steps**:
1. **Locate**: Call `search_youtube` to find 3–5 highly relevant videos. Prioritize diverse creators for broader perspectives.
2. **Ingest**: Call `get_video_transcript(video_id)` for each video to pull full closed captions with timestamps.
   - Fallback: If a transcript is unavailable, call `get_video_details` and read the description instead.
3. **Target**: Analyze transcripts to find the exact moments where each creator addresses the user's query.
4. **Link Generation (MANDATORY)**: For each key moment, call `generate_timestamp_url(video_id, timestamp)` to create a direct clickable URL. Do NOT guess or manually construct `?t=` parameters.
5. **Deliver** the "Knowledge Report":
   - Per video: 2-sentence summary of the creator's unique angle, followed by the direct timestamp URL to the key insight

**HTML Publishing Rule**: If publishing to HTML, ensure all `<a>` href attributes use exact URLs returned by `generate_timestamp_url`. Never use plain `https://youtu.be/ID` when a specific moment is referenced.

**Next Actions**: Ask the user if they want to publish this as a permanent HTML Knowledge Report, or provide feedback on accuracy.
