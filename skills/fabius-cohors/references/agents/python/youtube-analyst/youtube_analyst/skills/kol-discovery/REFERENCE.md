---
name: fabius-cohors-kol-discovery
description: Finds and ranks Key Opinion Leaders (KOLs) by engagement rate, active rate, and sentiment — not just view count — then surfaces the strongest candidates with transparent scoring rationale.
---

### Skill: KOL Discovery Workflow

**Objective**: Find and rank Key Opinion Leaders (KOLs) on a topic using strict performance metrics rather than raw view counts.

**Execution Steps**:
1. **Search**: Call `search_youtube` for videos on the topic. If the user specifies a timeframe (e.g., "last month"), call `get_date_range` first to get the `published_after` string.
2. **Data Gathering**: Call `get_video_details` and `get_channel_details` for the top candidates.
3. **Evaluate**:
   - Calculate `engagement_rate` and `active_rate` via `calculate_engagement_metrics`
   - Fetch comments and run `analyze_sentiment_heuristic` if needed
   - Calculate `match_score` to rank candidates objectively
4. **Report**: Present the top KOLs in a clear table. Explain why each was chosen (e.g., "12% engagement despite lower subscriber count"). Explicitly state which candidates were filtered out for high views but poor engagement.

**Next Actions**: Ask the user if they want to:
- See a visual engagement metrics chart
- Generate and publish a final HTML report
- Do a deep-dive transcript reading on any specific video from the list
