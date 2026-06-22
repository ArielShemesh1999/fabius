---
name: fabius-decor-fal-vision
description: Analyze images via fal.ai vision models — segment objects, detect, run OCR, describe, and answer visual questions.
triggers:
  - "fal vision"
  - "image analysis"
  - "object detection"
  - "ocr image"
  - "visual qa"
  - "segment"
---

# fal-vision

Analyze images — segment objects, detect, run OCR, describe, and answer visual questions via fal.ai vision models.

## When to use

Invoke when an image needs structured understanding: extracting text (OCR), identifying objects, segmenting regions, generating captions, or answering questions about visual content.

## How to use

Ask the agent to invoke this skill by name (`fal-vision`) or with one of the trigger phrases in the frontmatter.

Provide:
- A **source image URL** (or uploaded file)
- The **analysis task**: segment / detect / OCR / describe / visual-QA
- For visual-QA: the specific question to answer

The fal.ai vision model returns structured results (bounding boxes, text, captions, or answers).
