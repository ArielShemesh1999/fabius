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

import os
from dataclasses import dataclass

import google.auth

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


@dataclass
class SecurityAuditConfig:
    """Configuration for red team security models and parameters.

    Attributes:
        evaluator_model: The model used for evaluating security vulnerabilities.
        red_team_model: The model used for generating red team attacks.
        target_model: The target model being audited for security vulnerabilities.
    """

    evaluator_model: str = "gemini-2.5-pro"
    red_team_model: str = "gemini-2.5-pro"
    target_model: str = "gemini-2.5-flash"


config = SecurityAuditConfig()
