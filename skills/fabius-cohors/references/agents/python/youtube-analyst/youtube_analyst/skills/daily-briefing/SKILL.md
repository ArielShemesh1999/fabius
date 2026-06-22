---
name: fabius-cohors-daily-briefing
description: Delivers a high-signal briefing on events in a specific location and timeframe, backed by primary video sources with engagement filtering and transcript ingestion.
---

### Skill: What Matters Today (Location & Time Briefing)

**Objective**: Provide a high-signal briefing on events in a specific location within a specific timeframe (e.g., "the past 24 hours in Hong Kong"), backed by primary video sources.

**Execution Steps**:
1. **Time Context**: Call `get_current_date_time` and `get_date_range` (or calculate manually for exact 24-hour windows) to get the RFC 3339 cutoff timestamp.
2. **Search**: Call `search_youtube` with aggressive filtering:
   - Pass the timestamp from step 1 into `published_after`
   - Pass the relevant country code to `region_code` (e.g., `'HK'` for Hong Kong)
   - Apply `relevance_language` where appropriate
3. **Filter & Rank**: Call `get_video_details` and `calculate_engagement_metrics` for the results. Discard low-engagement spam, auto-generated news bots, and clickbait. Keep only verified or high-engagement sources.
4. **Ingest (Preferred)**: Call `get_video_transcript` on the top 2–3 clips. Do not rely solely on titles.
5. **Deliver** a structured "Daily Briefing":
   - 3–5 key events in the location
   - Per event: 2-sentence summary + direct link to the source video (or timestamped URL if the segment is within a longer broadcast)

**Next Actions**: Ask the user if they want to dive deeper into any story (comments/sentiment) or publish the briefing as an HTML report.
