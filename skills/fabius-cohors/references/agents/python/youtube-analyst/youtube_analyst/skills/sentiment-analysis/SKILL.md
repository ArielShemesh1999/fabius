---
name: fabius-cohors-sentiment-analysis
description: Analyzes comment sentiment and keyword frequency to extract the true audience mood and key feedback on any video or product.
---

### Skill: Sentiment Analysis Workflow

**Objective**: Surface the real audience reaction to a video, product, or creator by analyzing comment sentiment — not just listing comments.

**Execution Steps**:

1. **Fetch Comments**: Call `get_video_comments` to pull 20–50 top comments for the target video.

2. **Analyze**:
   - Apply `analyze_sentiment_heuristic` combined with semantic reasoning to gauge overall mood (Positive / Neutral / Negative).
   - Extract the most frequently mentioned keywords, recurring complaints, and specific praises.

3. **Synthesize**: Write a cohesive executive summary of what the audience actually cares about. Do not just enumerate comments — distill the signal.

**Next Actions**: Ask if the user wants to visualize this sentiment data or publish it as a report.
