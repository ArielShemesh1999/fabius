---
name: fabius-cohors-multi-video-synthesis
description: Synthesizes 10+ videos into a structured intelligence briefing — consensus, controversies, hidden gems, and timestamp jump-links.
---

### Skill: Autonomous Multi-Video Synthesis Pipeline

**Objective**: Run a high-density targeted extraction across 10+ videos to extract the signal, map the semantic landscape, and save the user hours of research.

**Execution Steps**:

1. **Broad Search**: Call `search_youtube` with `max_results=15` to cast a wide net.

2. **RoA Filtering (MANDATORY)**:
   - Fetch details for all 15 videos via `get_video_details`.
   - Score engagement with `calculate_engagement_metrics`.
   - Select the top 10 by Return on Attention (high engagement + relevant keywords + authoritative channel).
   - Tell the user which videos you dropped and why (e.g., "Filtering 5 low-engagement/clickbait results").

3. **Massive Ingestion**:
   - Pull transcripts for all 10 via `get_video_transcript`.
   - Where transcripts are unavailable, use `get_video_details` metadata/description as fallback.

4. **Semantic Mapping**:
   - Cross-reference all transcripts simultaneously.
   - Identify three layers: **Consensus** (3+ creators agree), **Controversies** (conflicting viewpoints), **Hidden Gems** (unique insight from a single expert).

5. **Precision Targeting**:
   - Every major argument must include at least one direct `?t=...` jump-link via `generate_timestamp_url`.

6. **Unified Report Delivery**:
   - Output a structured "Multi-Video Intelligence Briefing".
   - Include a Consensus vs. Controversy table.
   - List "Clips of Interest" with timestamp URLs.
   - Ask if the user wants a sentiment chart or a shareable HTML report.

**Key Principle**: You are not summarizing videos — you are synthesizing a knowledge artifact that does not exist anywhere else.
