---
name: fabius-cohors-debate-synthesizer
description: Extracts the strongest arguments from heated YouTube comment threads, identifies key battleground comments by reply count, and delivers a structured Pro vs. Con debate brief.
---

### Skill: Debate Synthesizer (Controversy Resolution)

**Objective**: Extract the strongest arguments from both sides of a heated debate in a YouTube comment section, without the user having to wade through toxic or redundant threads.

**Execution Steps**:
1. **Locate**: Call `search_youtube` to find highly polarizing videos on the requested topic.
2. **Fetch Top Comments**: Call `get_video_comments` for the top 1–2 videos with `order` set to `"relevance"`.
3. **Identify Battlegrounds**: In the returned comment list, find the 2–3 comments with the highest `reply_count` — these are the active debate threads.
4. **Deep Dive**: Call `get_comment_replies(comment_id)` on those high-reply comments to extract the actual arguments.
5. **Synthesize**: Group distinct technical and logical points into "Pro" and "Con" categories. Ignore ad-hominem attacks, spam, and low-value agreements ("+1", "this").
6. **Deliver** the "Debate Brief":
   - Top 3 strongest arguments per side, sourced from the community
   - Direct link to the source video

**HTML Publishing Rule**: If the user asks to publish, construct a clean HTML page with a Pro vs. Con table. Use `get_video_details` to embed the thumbnail. Publish the thumbnail via `publish_file` first, or link directly to the high-res URL from the API.

**Next Actions**: Ask the user if they want to publish the Debate Brief as a shareable HTML report.
