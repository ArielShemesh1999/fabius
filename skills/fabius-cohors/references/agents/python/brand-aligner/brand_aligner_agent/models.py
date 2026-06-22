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

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Severity(StrEnum):
    BLOCKER = "BLOCKER"
    WARNING = "WARNING"


class Category(StrEnum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class CriterionRubric(BaseModel):
    """A record for storing a question, its ground truth answer, and justification."""

    guideline_id: str = ""  # simplifies testing
    criterion_id: str
    question: str
    gt_answer: str
    question_justification: str = ""  # simplifies testing


class CriterionVerdict(CriterionRubric):
    """A criterion rubric extended with the model's verdict."""

    verdict: str
    justification: str = ""  # simplifies testing
    criterion_name: str = ""  # Human readable name of the criterion
    category: str = ""  # High level category for the criterion


class GuidelineVerdict(BaseModel):
    """The verdict for a specific guideline."""

    guideline_id: str
    mean_score: float
    verdicts: list[CriterionVerdict]


class AssetEvaluation(BaseModel):
    """Detailed evaluation result for a single asset."""

    asset_id: str
    asset_name: str
    description: str
    guideline_verdicts: list[GuidelineVerdict]
    final_score: float


class Criterion(BaseModel):
    criterion_id: str = Field(
        default_factory=lambda: f"criterion_{uuid.uuid4().hex[:10]}",
        description="Unique identifier for the criterion",
    )
    name: str
    criterion_value: str
    severity: Severity
    category: str


class GuidelineBase(BaseModel):
    guideline_id: str = Field(
        default_factory=lambda: f"guide_{uuid.uuid4().hex[:10]}",
        description="Unique identifier for the guideline",
    )
    name: str
    description: str
    criteria: list[Criterion]


class Guideline(GuidelineBase):
    file_uri: str


class GuidelineResponse(GuidelineBase):
    applicable_categories: list[Category]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Asset(BaseModel):
    asset_id: str
    asset_uri: str
    asset_name: str
    asset_prompt: str
    category: Category
    video_reference_image_uris: list[str] = Field(default_factory=list)
