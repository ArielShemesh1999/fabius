# Copyright 2026 Google LLC
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

"""Provides services for guideline processing and multimodal evaluation."""

#  pylint: disable=logging-fstring-interpolation
#  pylint: disable=broad-exception-caught

import concurrent.futures
import hashlib
import json
import mimetypes
import os
import pathlib
import re
import time
from typing import Literal

import numpy as np
import pandas as pd
import vertexai
from google import genai
from google.api_core import exceptions
from google.cloud import storage
from google.genai import types as genai_types
from vertexai.generative_models import GenerativeModel
from vertexai.preview.evaluation import (
    CustomOutputConfig,
    EvalTask,
    PointwiseMetric,
    RubricBasedMetric,
    RubricGenerationConfig,
)

from .models import (
    Asset,
    AssetEvaluation,
    Category,
    Criterion,
    CriterionRubric,
    CriterionVerdict,
    Guideline,
    GuidelineResponse,
    GuidelineVerdict,
    Severity,
)
from .utils import logger

# --- Guideline Service ---

GUIDELINE_EXTRACTION_PROMPT = """
You are an expert in brand marketing and identity. Your task is to analyze the provided
brand guideline document and extract its core components into a structured JSON format.

The document is provided as a file.

Analyze the document and generate a JSON object containing:
1.  `name`: A concise and descriptive name for the guideline document
     (e.g., "Acme Corp Visual Identity Guide 2024").
2.  `description`: A brief, one-sentence summary of the guideline's purpose.
3.  `applicable_categories`: A list of categories where this guideline applies.
     Choose from: {categories}.
4.  `criteria`: A list of specific, actionable rules from the document.
    For each criterion, provide:
    - `name`: A short title for the rule (e.g., "Logo Clear Space").
    - `category`: A high-level category grouping for this rule (e.g. "Logo", "Typography", "Color", "Tone", "Composition").
    - `criterion_value`: The exact rule or instruction from the document.
    - `severity`: The importance of the rule. Assign 'BLOCKER' if the rule is a "must"
or "always" and 'WARNING' if it is a "should" or a recommendation.

Your output MUST be a single JSON object. Do not include any other text or explanations
before or after the JSON.

Example Output Format:
{{
  "name": "Example Brand Guide",
  "description": "Guidelines for visual and written content.",
  "applicable_categories": ["IMAGE", "VIDEO"],
  "criteria": [
    {{
      "name": "Logo Usage",
      "category": "Logo",
      "criterion_value": "The company logo must always be displayed in the top-left
      corner and should not be altered.",
      "severity": "BLOCKER"
    }},
    {{
      "name": "Primary Color Palette",
      "category": "Color",
      "criterion_value": "Use primarily blue (#0000FF) and white (#FFFFFF) for all
      marketing materials.",
      "severity": "WARNING"
    }}
  ]
}}

Now, analyze the provided document and generate the JSON.
"""


class GuidelineService:
    def __init__(self, project_id: str, location: str, model_name: str):
        self.project_id = project_id
        self.location = location
        self.model_name = model_name

    async def extract_guideline_from_doc(
        self, file_uri: str, mime_type: str
    ) -> GuidelineResponse:
        """Extracts structured guideline data from a document using Gemini."""
        try:
            client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location,
            )
            category_enums = [cat.value for cat in Category]
            prompt = GUIDELINE_EXTRACTION_PROMPT.format(
                categories=", ".join(category_enums)
            )
            guideline_file = genai_types.Part.from_uri(
                file_uri=file_uri, mime_type=mime_type
            )
            contents = genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=prompt), guideline_file],
            )

            logger.info(
                "Sending document to Gemini for extraction: %s...", file_uri
            )
            response = await client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": GuidelineResponse.model_json_schema(),
                },
            )
            if not response.parsed:
                raise ValueError("No parsed response from Gemini.")

            parsed_guideline = GuidelineResponse.model_validate(response.parsed)
            logger.info("Successfully extracted guideline data from Gemini.")
            return parsed_guideline
        except Exception as e:
            logger.error(f"Error during Gemini processing: {e}")
            raise Exception(f"Failed to process document with AI: {e!s}") from e


# --- Eval Service ---

CRITERIA_FILTERING_PROMPT = """
You are an expert at interpreting brand guidelines for media assets.
Your task is to filter a list of brand criteria and only keep the ones that are relevant to the specific asset type provided.

**Instructions:**
1.  Review the asset type (e.g., "image", "video").
2.  Analyze the list of all available brand criteria.
3.  Identify which criteria are applicable to the given asset type. For example, criteria about "voiceover" or "pacing" are only relevant for "video", not "image". Criteria about "color palette" or "logo placement" could be relevant for both.
4.  Return a JSON object containing a single key, "relevant_criterion_ids", which is a list of the `criterion_id` strings for only the relevant criteria.

**Asset Type:**
{asset_type}

**All Brand Criteria:**
```json
{criteria_json}
```

**Output:**
"""

DSG_RUBRIC_GENERATION_PROMPT = """
Given a source prompt, your task is to create a set of precise Yes/No questions to check for two things:
1.  **Prompt Fidelity (DSG):** Is each key component of the source prompt present in the asset? This is for a Davidsonian Scene Graph (DSG) analysis.
2.  **General Quality (GQM):** Is the asset technically and aesthetically well-made, and free of common AI mistakes? This is for a General Quality & Mistakes (GQM) evaluation.

**Instructions:**

**Part 1: Prompt Fidelity Questions (DSG)**
IMPORTANT: Skip this step if the prompt is "No prompt".
- Analyze the source prompt and break it down into its key components.
- In the JSON output, create a "keywords" string where each component is enclosed in numbered brackets, like `{{1}}[component]`.
- Generate multiple Yes/No questions for each identified component.

**Part 2: General Quality Questions (GQM)**
- Generate additional Yes/No questions that address the following general quality dimensions:
  - **Object Permanence & Consistency:** Do objects or characters maintain a consistent appearance, position, and presence? Crucially, do characters or key objects unnaturally disappear, reappear, or teleport within what should be a continuous scene?
  - **Plausibility & Realism:** Do interactions like lighting, shadows, and basic physics appear natural? Do people and objects interact plausibly (e.g., not passing through solid items)?
  - **Aesthetic Quality:** Is the asset free of obvious visual glitches, artifacts, or excessive blur? Is the scene free of unnatural "morphing" (e.g., one object distorting into another, or one person's features blending into a different person)?
  - **Natural Movement (for video):** Is movement fluid and not distorted? If people are present, do they move naturally? Specifically, are transitions between actions (e.g., from walking to sitting, or standing to interacting) shown completely and plausibly? Or do characters "pop" or "snap" instantly from one pose or location to another (e.g., appearing suddenly in a chair instead of the action of sitting down)?

**Formatting Rules:**
- All questions must be phrased so that a "Yes" answer indicates compliance or high quality.
- The "answer" for all questions must be "yes" as this reflects the ground truth of what was requested in the prompt and the expected level of quality.
- Your output must be a single JSON object in the exact format shown in the example.

===
**EXAMPLE:**

**Source Prompt:** A close-up of a luxurious gold watch with a leather strap on a man's wrist.

**Answer:**
{{
  "keywords": "A {{1}}[close-up] of a {{2}}[luxurious] {{3}}[gold] watch with a {{4}}[leather strap] on a {{5}}[man's wrist].",
  "qas": [
    {{
      "criterion_id": "prompt-component-1",
      "question": "Is the image a close-up shot?",
      "justification": "DSG: The source prompt explicitly states a 'close-up' ({{1}}).",
      "answer": "yes"
    }},
    {{
      "criterion_id": "prompt-component-3",
      "question": "Is the watch case made of gold?",
      "justification": "DSG: The source prompt explicitly states the watch is 'gold' ({{3}}).",
      "answer": "yes"
    }},
    {{
      "criterion_id": "prompt-component-5",
      "question": "Is the watch displayed on a man's wrist?",
      "justification": "DSG: The source prompt specifies a 'man's wrist' ({{5}}).",
      "answer": "yes"
    }},
    {{
      "criterion_id": "gqm-artifacts",
      "question": "Is the image free of noticeable visual artifacts, distortions, or glitches?",
      "justification": "GQM: Checks for general aesthetic quality and common AI generation errors.",
      "answer": "yes"
    }},
    {{
      "criterion_id": "gqm-lighting",
      "question": "Are the lighting and shadows on the watch and wrist plausible and consistent?",
      "justification": "GQM: Checks for physical realism and plausibility.",
      "answer": "yes"
    }}
  ]
}}
===

**Source Prompt:**
{source_prompt}

**Answer:**
"""

BAS_RUBRIC_GENERATION_PROMPT = """
Given a brand guideline with multiple criteria and additional free-text guidance, your task is to create a set of precise Yes/No questions to check for compliance. This is for a Brand Alignment Scorecard (BAS).

Generate a list of Yes/No questions based on both the brand criteria and the additional guidance provided.
Crucially, all questions must be phrased so that a "Yes" answer indicates compliance. For example, for a negative rule like "Avoid beaches", the question should be "Is the setting something other than a beach?".
The "answer" for each question must be "yes", as it represents the ground truth for compliance. For any question derived from a BLOCKER severity criterion, the "answer" MUST be "yes".

Your output must be a JSON object in the exact format shown in the example.

===
**EXAMPLE:**

**Brand Guideline Criteria to Enforce:**
- cr-logo-visible (Severity: BLOCKER): When a logo is present, it must be clearly visible and unobscured.
- cr-background-style (Severity: WARNING): The background should be simple and not distracting.
**Additional Guidance:**
Avoid showing any text other than the brand logo. Do not show the product in a beach setting.

**Answer:**
{{
  "qas": [
    {{
      "criterion_id": "cr-logo-visible",
      "question": "If a logo is present in the image, is it clearly visible and unobscured?",
      "justification": "This is a BLOCKER requirement from the brand guidelines (cr-logo-visible). An image without a logo is not in violation, but if a logo exists, it must be visible.",
      "answer": "yes"
    }},
    {{
      "criterion_id": "cr-background-style",
      "question": "Is the background simple and not distracting?",
      "justification": "This is a WARNING requirement from the brand guidelines (cr-background-style).",
      "answer": "yes"
    }},
    {{
      "criterion_id": "additional-guidance-text",
      "question": "Is the image free of any text other than the official brand logo?",
      "justification": "This is a requirement from the additional guidance. 'Yes' indicates compliance.",
      "answer": "yes"
    }},
    {{
      "criterion_id": "additional-guidance-setting",
      "question": "Is the product shown in a setting other than a beach?",
      "justification": "This is a requirement from the additional guidance. 'Yes' indicates compliance.",
      "answer": "yes"
    }}
  ]
}}
===

**BRAND GUIDELINE CRITERIA TO ENFORCE:**
{criteria}

**ADDITIONAL GUIDANCE (e.g., negative prompts):**
{additional_guidance}

**Answer:**
"""

RUBRIC_VALIDATOR_PROMPT = """
# Instructions
Analyze the **Source Images** and the **Generated Asset** below carefully. Your goal is to evaluate the **Generated Asset** against each rubric question. The asset may be an image or a video.
If the asset is an image, **Source Images** is going to be empty and you should apply your evaluation entirely on the **Generated Asset**.
If the asset is a video, know that **Source Images** are what was provided as input to generate the video, so the rubric questions might be assessing elements of the source images, generated video, or both.

For each question, provide a verdict of "Yes", "No", or "N/A" (Not Applicable) and a brief justification for your choice, based on comparing the **Generated Asset** and **Source Images** as described above to the rubrics.

- "Yes" means the **Generated Asset** complies with the question's statement.
- "No" means the **Generated Asset** does not comply.
- "N/A" means the question is not applicable to the asset.
- "Justification" should be a concise explanation (1-2 sentences) of why you chose the verdict.

{rubrics}

# Source Images
{source_images}

# Visual Asset to Evaluate
{response}

# Output Format
Provide your answer for each question in the following format.
<question>
Question: [Question Text]
Verdict: [Yes|No|N/A]
Justification: [Brief explanation for the verdict]
</question>
"""

_QUESTION_BLOCK_REGEX = re.compile(r"<question>(.*?)</question>", re.DOTALL)
_QUESTION_REGEX = re.compile(
    r"Question:(.*?)Verdict:", re.DOTALL | re.IGNORECASE
)
_VERDICT_REGEX = re.compile(r"Verdict:\s*(Yes|No|N/A)", re.IGNORECASE)
_JUSTIFICATION_REGEX = re.compile(
    r"Justification:(.*)", re.DOTALL | re.IGNORECASE
)


def _parse_json_to_rubrics(json_response: str):
    """Custom parsing function for the rubric generation step (Yes/No)."""
    clean_response = re.sub(
        r"(.*```json|```.*)", "", json_response.strip(), flags=re.DOTALL
    )
    try:
        data = json.loads(clean_response)
        rubrics = []
        rubrics_for_validator = []
        for qa in data.get("qas", []):
            record = CriterionRubric(
                criterion_id=qa.get("criterion_id", "unknown"),
                question=qa["question"],
                gt_answer=qa.get("answer", "yes").lower(),
                question_justification=qa.get("justification", ""),
                guideline_id="",  # Will be populated later
            )
            rubrics.append(record)
            rubrics_for_validator.append(
                f"<question>{record.question}</question>"
            )
        return {
            "questions": "\n".join(rubrics_for_validator),
            "rubrics_internal": rubrics,
        }
    except (json.JSONDecodeError, KeyError) as e:
        logger.exception(
            f"Error parsing rubric generation JSON: {clean_response}"
        )
        return {"questions": f"Error: {e}", "rubrics_internal": []}


def _parse_validator_results(results: list[str]):
    """Custom parsing function for the rubric validation step."""
    verdicts = {}
    for result in results:
        question_blocks = _QUESTION_BLOCK_REGEX.findall(result)
        for block in question_blocks:
            question_match = _QUESTION_REGEX.search(block)
            verdict_match = _VERDICT_REGEX.search(block)
            justification_match = _JUSTIFICATION_REGEX.search(block)

            if question_match and verdict_match and justification_match:
                question = question_match.group(1).strip().lower()
                verdict = verdict_match.group(1).strip().lower()
                justification = justification_match.group(1).strip()

                verdicts[question] = {
                    "verdict": verdict,
                    "justification": justification,
                }

    return {"verdicts": verdicts}


def _compute_scores_from_result(df: pd.DataFrame, guideline: Guideline | None):
    """Computes final scores and verdicts from the evaluation result table."""
    scores = []
    criterion_verdicts = []

    severity_map = (
        {c.criterion_id: c.severity for c in guideline.criteria}
        if guideline
        else {}
    )
    criterion_name_map = (
        {c.criterion_id: c.name for c in guideline.criteria}
        if guideline
        else {}
    )
    criterion_category_map = (
        {c.criterion_id: c.category for c in guideline.criteria}
        if guideline
        else {}
    )

    for _, row in df.iterrows():
        verdicts = row.get("gecko_metric/verdicts", {})
        rubrics = row.get("rubrics_internal", [])

        for rubric in rubrics:
            verdict_dict = verdicts.get(rubric.question.lower(), {})
            verdict = verdict_dict.get("verdict", "no verdict")
            justification = verdict_dict.get(
                "justification", rubric.question_justification
            )  # backwards compatibility

            gt_answer = rubric.gt_answer
            if severity_map.get(rubric.criterion_id, "") == Severity.BLOCKER:
                gt_answer = "yes"

            # Determine criterion name and category
            c_name = criterion_name_map.get(rubric.criterion_id, "")
            c_category = criterion_category_map.get(rubric.criterion_id, "")

            if not c_name:
                if rubric.criterion_id.startswith("prompt-component"):
                    c_name = "Prompt Adherence"
                    c_category = "Prompt Adherence"
                elif rubric.criterion_id.startswith("gqm-"):
                    c_name = "General Quality"
                    c_category = "General Quality"
                elif rubric.criterion_id.startswith("additional-guidance"):
                    c_name = "Additional Guidance"
                    c_category = "Additional Guidance"

            criterion_verdicts.append(
                CriterionVerdict(
                    guideline_id=rubric.guideline_id,
                    criterion_id=rubric.criterion_id,
                    criterion_name=c_name,
                    category=c_category,
                    question=rubric.question,
                    gt_answer=gt_answer,
                    question_justification=rubric.question_justification,
                    verdict=verdict,
                    justification=justification,
                )
            )

            if verdict == "n/a":
                continue

            score = 1.0 if verdict == gt_answer else 0.0
            scores.append(score)

    mean_score = np.mean(scores) if scores else -1.0
    return mean_score, criterion_verdicts


class EvalService:
    """Evaluation service."""

    def __init__(
        self,
        project_id: str,
        location: str,
        model_name: str,
        bucket_name: str,
        batch_size: int = 50,
    ):
        vertexai.init(project=project_id, location=location)
        self.model_name = model_name
        self.gecko_metric = RubricBasedMetric(
            generation_config=None,  # Provided dynamically per-run
            critique_metric=PointwiseMetric(
                metric="gecko_metric",
                metric_prompt_template=RUBRIC_VALIDATOR_PROMPT,
                custom_output_config=(
                    CustomOutputConfig(
                        return_raw_output=True,
                        parsing_fn=_parse_validator_results,
                    )
                ),
            ),
        )
        self.batch_size = batch_size
        self.filtering_model = GenerativeModel(self.model_name)
        self.storage_client = storage.Client(project=project_id)
        self.bucket = self.storage_client.bucket(bucket_name)

    def _get_asset_type(
        self, asset_uri: str
    ) -> Literal["video", "image", "unknown"]:
        """Determines if the asset is a video or image based on MIME type."""
        mime_type = _get_mime_type(asset_uri)
        if mime_type.startswith("video/"):
            return "video"
        if mime_type.startswith("image/"):
            return "image"
        return "unknown"

    def _filter_relevant_criteria(
        self, all_criteria: list[Criterion], asset_type: str
    ) -> list[Criterion]:
        """Uses an LLM to filter a list of criteria to only those relevant to the asset type."""
        if not all_criteria or asset_type == "unknown":
            return all_criteria

        criteria_dict_list = [
            {
                "criterion_id": c.criterion_id,
                "criterion_value": c.criterion_value,
                "severity": c.severity.name,
            }
            for c in all_criteria
        ]
        criteria_json = json.dumps(criteria_dict_list, indent=2)
        prompt = CRITERIA_FILTERING_PROMPT.format(
            asset_type=asset_type, criteria_json=criteria_json
        )

        try:
            response = self.filtering_model.generate_content(prompt)
            clean_response = re.sub(
                r"(.*```json|```.*)", "", response.text.strip(), flags=re.DOTALL
            )
            result_json = json.loads(clean_response)
            relevant_ids = set(result_json.get("relevant_criterion_ids", []))

            if not relevant_ids:
                logger.warning(
                    "Criteria filtering returned no relevant IDs. Proceeding with all criteria."
                )
                return all_criteria

            filtered_criteria = [
                c for c in all_criteria if c.criterion_id in relevant_ids
            ]
            logger.info(
                f"Filtered criteria for asset type '{asset_type}'. "
                f"Original count: {len(all_criteria)}, New count: {len(filtered_criteria)}"
            )
            return filtered_criteria
        except (json.JSONDecodeError, exceptions.GoogleAPICallError) as e:
            logger.exception(
                f"Error during criteria filtering LLM call: {e}. Proceeding with all criteria."
            )
            return all_criteria

    def evaluate_asset(
        self,
        asset: Asset,
        guidelines: list[Guideline],
        additional_guidance: str,
        user_id: str,
        app_name: str,
    ) -> AssetEvaluation:
        """Evaluates a single visual asset against a set of guidelines using the Vertex AI Eval Service."""
        asset_id = asset.asset_id
        asset_uri = asset.asset_uri
        prompt = asset.asset_prompt or "No prompt"
        valid_prompt = prompt and prompt != "No prompt"
        video_reference_image_uris = asset.video_reference_image_uris
        logger.info(f"Processing asset: {asset_id} ({asset_uri})")
        guideline_verdicts = []
        guideline_scores = []
        asset_type = self._get_asset_type(asset_uri)

        guideline_id = (
            "dsg_prompt_adherence_and_gqm_quality"
            if valid_prompt
            else "gqm_quality"
        )

        dsg_score, dsg_verdicts = self._run_evaluation_task(
            prompt_template=DSG_RUBRIC_GENERATION_PROMPT,
            prompt_params={"source_prompt": prompt},
            asset_uri=asset_uri,
            reference_image_paths=video_reference_image_uris,
            guideline_id=guideline_id,
            user_id=user_id,
            app_name=app_name,
            use_cache=False,
        )
        guideline_verdicts.append(
            GuidelineVerdict(
                guideline_id=guideline_id,
                mean_score=dsg_score,
                verdicts=dsg_verdicts,
            )
        )
        if dsg_score != -1:
            guideline_scores.append(dsg_score)

        for guideline in guidelines:
            if not guideline.criteria:
                logger.warning(
                    f"Guideline {guideline.guideline_id} has no criteria, skipping."
                )
                continue

            relevant_criteria = (
                self._filter_relevant_criteria(guideline.criteria, asset_type)
                if len(guideline.criteria) > self.batch_size
                else guideline.criteria
            )
            filtered_guideline = guideline.model_copy(
                update={"criteria": relevant_criteria}
            )
            criteria_str = "\n".join(
                [
                    f"- {c.criterion_id} (Severity: {c.severity.name}): {c.criterion_value}"
                    for c in filtered_guideline.criteria
                ]
            )
            bas_score, bas_verdicts = self._run_evaluation_task(
                prompt_template=BAS_RUBRIC_GENERATION_PROMPT,
                prompt_params={
                    "criteria": criteria_str,
                    "additional_guidance": additional_guidance or "None",
                },
                asset_uri=asset_uri,
                reference_image_paths=video_reference_image_uris,
                guideline_id=filtered_guideline.guideline_id,
                guideline=filtered_guideline,
                user_id=user_id,
                app_name=app_name,
                use_cache=True,
            )
            guideline_verdicts.append(
                GuidelineVerdict(
                    guideline_id=filtered_guideline.guideline_id,
                    mean_score=bas_score,
                    verdicts=bas_verdicts,
                )
            )
            if bas_score != -1:
                guideline_scores.append(bas_score)

        asset_final_score = np.mean(guideline_scores) if guideline_scores else 0
        return AssetEvaluation(
            asset_id=asset_id,
            asset_name=asset.asset_name,
            description=prompt,
            guideline_verdicts=guideline_verdicts,
            final_score=asset_final_score,
        )

    def _run_batch_evaluation(
        self, batch_dataset: pd.DataFrame
    ) -> pd.DataFrame | None:
        """Runs evaluation for a single batch of rubrics with retry logic."""
        max_retries = 2
        backoff_factor = 2
        initial_delay = 2

        eval_task = EvalTask(dataset=batch_dataset, metrics=[self.gecko_metric])

        # Extract batch size for logging
        batch_size = (
            len(batch_dataset.at[0, "rubrics_internal"])
            if "rubrics_internal" in batch_dataset.columns
            else "unknown"
        )

        for attempt in range(max_retries):
            try:
                eval_result = eval_task.evaluate(
                    response_column_name="generated_asset", retry_timeout=300
                )
                logger.info(
                    f"Successfully evaluated batch with {batch_size} rubrics on attempt {attempt + 1}."
                )
                return eval_result.metrics_table
            except (
                exceptions.ResourceExhausted,
                exceptions.DeadlineExceeded,
            ) as e:
                if attempt < max_retries - 1:
                    delay = initial_delay * (backoff_factor**attempt)
                    logger.warning(
                        f"Retryable error on batch, attempt {attempt + 1}/{max_retries}. Retrying in {delay} seconds. Error: {e}"
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        f"Failed to evaluate batch after {max_retries} attempts. Error: {e}"
                    )
                    return None
            except Exception as e:
                logger.error(
                    f"An unexpected error occurred on batch attempt {attempt + 1}: {e}"
                )
                return None
        return None

    def _get_or_generate_rubrics(
        self,
        prompt_template: str,
        prompt_params: dict,
        asset_uri: str,
        reference_image_paths: list[str],
        guideline_id: str,
        user_id: str,
        app_name: str,
        use_cache: bool = True,
    ) -> list[CriterionRubric]:
        """Retrieves rubrics from cache or generates them using Gecko metric."""
        blob = None
        if use_cache:
            # 1. Compute hash for cache key
            content_str = f"{guideline_id}|{prompt_template}|{json.dumps(prompt_params, sort_keys=True)}"
            content_hash = hashlib.md5(content_str.encode()).hexdigest()
            blob_name = f"{app_name}/{user_id}/{user_id}/processed_rubrics_{guideline_id}_{content_hash}.json"
            blob = self.bucket.blob(blob_name)

            # 2. Check cache
            if blob.exists():
                logger.info(
                    f"Cache hit: Loading rubrics for {guideline_id} from {blob_name}"
                )
                try:
                    json_data = blob.download_as_text()
                    data = json.loads(json_data)
                    return [CriterionRubric(**item) for item in data]
                except Exception as e:
                    logger.warning(
                        f"Failed to load cached rubrics: {e}. Regenerating."
                    )

        # 3. Generate rubrics if miss, disabled, or load failed
        logger.info(
            f"Generating rubrics for {guideline_id} (cache used: {use_cache})"
        )
        rubric_gen_config = RubricGenerationConfig(
            prompt_template=prompt_template.format(**prompt_params),
            parsing_fn=_parse_json_to_rubrics,
            model=GenerativeModel(self.model_name),
        )
        self.gecko_metric.generation_config = rubric_gen_config

        generated_asset_json_str = _create_multimodal_json_string([asset_uri])
        source_images_json_str = _create_multimodal_json_string(
            reference_image_paths
        )
        eval_dataset = pd.DataFrame(
            [
                {
                    "generated_asset": generated_asset_json_str,
                    "source_images": source_images_json_str,
                }
            ]
        )

        eval_dataset_with_rubrics = self.gecko_metric.generate_rubrics(
            eval_dataset
        )

        if (
            eval_dataset_with_rubrics.empty
            or "rubrics_internal" not in eval_dataset_with_rubrics.columns
        ):
            logger.warning("No rubrics were generated.")
            return []

        rubrics = eval_dataset_with_rubrics.at[0, "rubrics_internal"]
        if not rubrics:
            logger.warning("Rubrics list is empty.")
            return []

        # 4. Save to cache if enabled
        if use_cache and blob:
            try:
                # Ensure guideline_id is set
                for r in rubrics:
                    r.guideline_id = guideline_id

                serialized_rubrics = [r.model_dump() for r in rubrics]
                blob.upload_from_string(
                    json.dumps(serialized_rubrics, indent=2),
                    content_type="application/json",
                )
                logger.info(f"Saved generated rubrics to cache: {blob.name}")
            except Exception as e:
                logger.error(f"Failed to save rubrics to cache: {e}")

        return rubrics

    def _execute_evaluation(
        self,
        rubrics: list[CriterionRubric],
        asset_uri: str,
        reference_image_paths: list[str],
        guideline: Guideline | None,
    ):
        """Executes the evaluation using the provided rubrics."""
        generated_asset_json_str = _create_multimodal_json_string([asset_uri])
        source_images_json_str = _create_multimodal_json_string(
            reference_image_paths
        )

        eval_dataset = pd.DataFrame(
            [
                {
                    "generated_asset": generated_asset_json_str,
                    "source_images": source_images_json_str,
                }
            ]
        )

        eval_dataset["rubrics_internal"] = eval_dataset[
            "rubrics_internal"
        ].astype(object)
        eval_dataset["rubrics"] = ""

        rubric_batches = [
            rubrics[i : i + self.batch_size]
            for i in range(0, len(rubrics), self.batch_size)
        ]
        all_metrics_tables = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_batch = {}
            for batch in rubric_batches:
                rubrics_str = "\n".join(
                    [f"<question>{r.question}</question>" for r in batch]
                )

                batch_dataset = eval_dataset.copy()
                batch_dataset.at[0, "rubrics_internal"] = batch
                batch_dataset.at[0, "rubrics"] = rubrics_str

                future = executor.submit(
                    self._run_batch_evaluation, batch_dataset
                )
                future_to_batch[future] = batch

            for future in concurrent.futures.as_completed(future_to_batch):
                try:
                    result_table = future.result()
                    if result_table is not None:
                        all_metrics_tables.append(result_table)
                except Exception as exc:
                    logger.error(f"A batch generated an exception: {exc}")

        if not all_metrics_tables:
            metrics_table = pd.DataFrame()
        else:
            metrics_table = pd.concat(all_metrics_tables, ignore_index=True)

        if (
            not metrics_table.empty
            and "rubrics_internal" in metrics_table.columns
        ):
            for row_index in metrics_table.index:
                new_rubrics = [
                    CriterionRubric(
                        guideline_id=row.guideline_id,
                        criterion_id=row.criterion_id,
                        question=row.question,
                        gt_answer=row.gt_answer,
                        question_justification=row.question_justification,
                    )
                    for row in metrics_table.loc[row_index, "rubrics_internal"]
                ]
                metrics_table.at[row_index, "rubrics_internal"] = new_rubrics

        return _compute_scores_from_result(metrics_table, guideline)

    def _run_evaluation_task(
        self,
        prompt_template: str,
        prompt_params: dict,
        asset_uri: str,
        reference_image_paths: list[str],
        guideline_id: str,
        user_id: str,
        app_name: str,
        guideline: Guideline | None = None,
        use_cache: bool = True,
    ):
        """Helper to run evaluation task with caching support."""
        try:
            rubrics = self._get_or_generate_rubrics(
                prompt_template=prompt_template,
                prompt_params=prompt_params,
                asset_uri=asset_uri,
                reference_image_paths=reference_image_paths,
                guideline_id=guideline_id,
                user_id=user_id,
                app_name=app_name,
                use_cache=use_cache,
            )

            if not rubrics:
                return 0.0, []

            logger.info(
                "%d rubrics ready for guideline %s.", len(rubrics), guideline_id
            )
            return self._execute_evaluation(
                rubrics, asset_uri, reference_image_paths, guideline
            )

        except Exception:
            logger.exception(
                f"Error during EvalTask for guideline '{guideline_id}'"
            )
            return 0.0, []


def _get_mime_type(file_path: str) -> str:
    """Guesses the MIME type of a file based on its extension."""
    p = pathlib.Path(file_path)
    f = os.path.basename(file_path)
    file_name = (
        f if "." in f else str(p.parents[0]).replace(f"{p.parents[1]!s}/", "")
    )
    logger.info(f"Determining MIME type for file: {file_name}")
    mime_type, _ = mimetypes.guess_type(file_name)
    if not mime_type:
        if any(file_name.lower().endswith(ext) for ext in [".png"]):
            return "image/png"
        if any(file_name.lower().endswith(ext) for ext in [".jpg", ".jpeg"]):
            return "image/jpeg"
        if any(
            file_name.lower().endswith(ext) for ext in [".mp4", ".mov", ".avi"]
        ):
            return "video/mp4"
        return "application/octet-stream"
    return mime_type


def _create_multimodal_json_string(file_paths: list[str]) -> str:
    """Creates a JSON string conforming to the ContentMap.Contents protobuf
    structure that the EvalTask expects.
    """
    parts_list = []
    for path in file_paths:
        parts_list.append(
            {"file_data": {"file_uri": path, "mime_type": _get_mime_type(path)}}
        )

    content_map_contents = {"contents": [{"parts": parts_list}]}

    return json.dumps(content_map_contents)
