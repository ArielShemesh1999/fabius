---
name: fabius-cohors-industry-landscape-briefing
description: Equips sellers with macro industry trends by analyzing trending video data and specific analyst or competitor channels, delivering an executive dashboard with timestamped evidence.
---

### Skill: Industry Landscape Briefing (Seller's Radar)

**Objective**: Give a seller high-level macro trends in a specific industry (e.g., Mobile Gaming, Fintech) before a client meeting — going beyond keyword noise to find actual industry movements.

**Execution Steps**:
1. **Time Context**: Call `get_date_range("week")` to set the timeframe.
2. **Trending Analysis**: Call `get_trending_videos` with a relevant `video_category_id` (e.g., `"20"` for Gaming, `"28"` for Science/Tech) and the `region_code` for the seller's market.
3. **Analyst Channel Audit** (optional but recommended): Ask the user if they follow a specific industry analyst or B2B channel. If so, call `search_channel_videos` to pull what that authority published this week.
4. **Ingest**: Call `get_video_transcript` on the top 2–3 videos from steps 2–3. Synthesize the actual industry shift being discussed, not just titles.
5. **Deliver** the "Executive Dashboard":
   - **Macro Trend**: 1-sentence summary of the biggest industry shift this week
   - **Competitor Actions**: Are competitors mentioned? What are they doing?
   - **Direct Proof**: 2–3 clickable timestamp links via `generate_timestamp_url` to the exact moments industry shifts are analyzed

**Next Actions**: Ask the user if they want to publish this briefing as a clean HTML asset using `publish_file`.
