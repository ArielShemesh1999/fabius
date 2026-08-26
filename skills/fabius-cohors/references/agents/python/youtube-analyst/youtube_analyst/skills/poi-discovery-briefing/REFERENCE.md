---
name: fabius-cohors-poi-discovery-briefing
description: Extracts local activity recommendations and audience sentiment from travel vlogs and publishes a shareable HTML BD report.
---

### Skill: POI & Activity Discovery Briefing (Travel BD)

**Objective**: Equip an OTA Business Development team with actionable data on local activities around a Point of Interest — extracted from travel vloggers, validated by audience sentiment, packaged as a shareable HTML report.

**Execution Steps**:

1. **Locate Content**: Call `search_youtube` to find travel vlogs for the target POI (e.g., "Mount Fuji travel vlog", "Things to do in Tokyo").

2. **Extract Activities**: Run `get_video_transcript` on the top 2–3 longest vlogs. Scan for specific activity names, restaurants, and sub-locations the vlogger mentions.

3. **Map Timestamps**: For each activity, call `generate_timestamp_url` to produce a direct jump-link to the exact second it's discussed.

4. **Community Audit**: Call `get_video_comments` on the same videos. Identify whether the audience validates or disputes each recommendation (e.g., "The boat ride is a tourist trap").

5. **Synthesize HTML Report**: Auto-format findings into a professional "BD Briefing" HTML document. For each activity include:
   - Activity name
   - Vlogger's verdict
   - Audience sentiment
   - `<a href="...">` timestamp link
   - High-res video thumbnail from `get_video_details` at the top of the report.

6. **Publish**: Call `publish_file(content=html_string, filename="poi_briefing.html")` to upload the HTML to cloud storage. Return the public URL so the user can share it immediately.
