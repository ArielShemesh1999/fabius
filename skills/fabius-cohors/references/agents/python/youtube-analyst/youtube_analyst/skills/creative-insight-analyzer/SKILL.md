---
name: fabius-cohors-creative-insight-analyzer
description: Deconstructs high-performing or viral videos to extract actionable creative insights — hook mechanics, pacing, narrative structure — from transcript and metadata.
---

### Skill: Creative Insight & Viral Analysis

**Objective**: Deconstruct high-performing or viral videos to extract actionable creative insights. Analyze hook mechanics, narrative pacing, and audio-visual rhythm that drive retention and engagement.

**Execution Steps**:
1. **Locate & Validate**: Use `search_youtube` (or accept a video ID from the user). Call `get_video_details` to confirm duration and metadata. If the video exceeds 20 minutes, ask whether to analyze the full video or a specific segment.
2. **Disclaimer (CRITICAL)**: Before analysis, output this exact message:
   *"⚠️ **Note on Analysis Scope:** This analysis is based strictly on the video's **transcript, title, and metadata** — frame-by-frame visual analysis is not available in this configuration."*
3. **Metadata Audit**: Use `get_video_details` to evaluate the packaging — title, tags, description. Is the title clickbait, professional, or curiosity-inducing?
4. **Script Ingestion**: Call `get_video_transcript(video_id)`. Analyze as a senior creative director:
   - First 5 seconds: the hook script
   - Narrative rhythm: how transitions between topics maintain attention
   - Core narrative structure
5. **Deliver** the "Creative Insight Report":
   - **The Hook**: What happens in the first 3–5 seconds?
   - **Visual Elements**: Editing pace, color grading, on-screen text, face-cam usage (inferred from transcript cues and metadata)
   - **Rhythm & Retention**: How pacing and audio prevent viewer drop-off
   - **Actionable Takeaway**: 1–2 things the user can apply to their own content strategy

**Next Actions**:
1. Ask the user if they want to publish this report as a shareable HTML asset using `publish_file`.
2. Ask: *"Would you like me to run this video through Google's ABCD framework to evaluate it as an advertisement?"* (If yes, invoke `abcd_framework_audit`.)
