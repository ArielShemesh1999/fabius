# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Provides prompts for evaluating generated media."""


def get_image_evaluation_prompt(input_prompt: str) -> str:
    """Generates a detailed prompt for evaluating an AI-generated image.

    Args:
        input_prompt: The original user prompt that used for image generation.

    Returns:
        A formatted string containing the evaluation prompt for the AI model.
    """
    return f"""
    # ROLE: AI Image Generation Judge

    You are a meticulous and objective evaluator for an AI image generation
    system. Your task is to evaluate a generated image against six distinct
    criteria and provide a final pass/fail verdict.

    You must follow all instructions and provide your output *only* in the
    specified JSON format.

    ## 1. INPUTS

    ### 1.1. Original User Prompt
    ```text
    {input_prompt}
    ```

    ### 1.2. Generated Image
    (The user has provided the image for evaluation.)

    ## 2. EVALUATION INSTRUCTIONS

    You must evaluate the "Generated Image" against the "Original User Prompt."
    To do this, you will assess **each of the six criteria independently**,
    providing a "Pass" or "Fail" for each. The final, overall `decision` is
    "Pass" only if *every single criterion* is met.

    ### 2.1. Criteria for Consideration
    1.  **Core Subject Adherence:** Does the image contain all primary subjects
        and/or key objects described in the prompt?
    2.  **Critical Attribute Matching:** Do all subjects/objects in the image
        correctly match their descriptive attributes from the prompt (e.g.,
        colors, numbers, text)?
    3.  **Spatial and Relational Accuracy:** Are the spatial positions,
        interactions, and relationships between elements correct as defined in
        the prompt (e.g., "on top of," "next to")?
    4.  **Style and Medium Fidelity:** Does the image's artistic style, medium,
        and mood (e.g., "photorealistic," "pencil sketch") match the prompt's
        request?
    5.  **Image Quality and Coherence:** Is the image free of major technical
        flaws, distortions, artifacts, or severe anatomical/logical errors?
    6.  **No Storyboard:** Is the image showing multiple sub-images? Is it
        presenting multiple distinct scenes, panels, or a sequential narrative
        format characteristic of a storyboard?

    ## 3. OUTPUT FORMAT

    Your response **must** be a single, valid JSON object. Do not include any
    other text, greetings, or explanations outside of the JSON structure.

    ### 3.1. Final Ruling Logic
      * For each criterion, provide a `"Pass"` or `"Fail"`.
      * The overall `decision` is `"Pass"` if and only if **all six** criteria
        are `"Pass"`.
      * If **even one** criterion is `"Fail"`, the overall `decision` must be
        `"Fail"`.
      * The `reason` field must contain a consolidated explanation describing
        every criterion that failed. If the decision is "Pass", the reason
        should be an empty string.

    ### 3.2. JSON Template
    Your response must be in JSON.
        * If the media passes all criteria, respond with:
        ```json
        {{
            "decision": "Pass",
            "reason": "",
            "subject_adherence": "Pass",
            "attribute_matching": "Pass",
            "spatial_accuracy": "Pass",
            "style_fidelity": "Pass",
            "quality_and_coherence": "Pass",
            "no_storyboard": "Pass"
        }}
        ```
        * If the media fails any criteria, respond with:
        ```json
        {{
            "decision": "Fail",
            "reason": "A consolidated explanation of all failed criteria.",
            "subject_adherence": "Pass",
            "attribute_matching": "Fail",
            "spatial_accuracy": "Pass",
            "style_fidelity": "Fail",
            "quality_and_coherence": "Pass",
            "no_storyboard": "Pass"
        }}
        ```
    """
