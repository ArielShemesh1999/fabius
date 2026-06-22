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

"""Config module for the supply chain agent."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from google.genai import types

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

logger = logging.getLogger(__name__)


class AgentConfig:
    """
    Configuration for the Agent.
    """

    # GCP project id and location
    project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT")
    location: str = os.getenv("GOOGLE_CLOUD_LOCATION")

    # Gemini model config
    model_name: str = os.getenv("GEMINI_MODEL_NAME")
    temperature: float = float(os.getenv("GEMINI_MODEL_TEMPERATURE") or 0.3)
    top_p: float = float(os.getenv("GEMINI_MODEL_TOP_P") or 0.95)
    include_thoughts: bool = (
        os.getenv("GEMINI_MODEL_INCLUDE_THOUGHTS", "False").lower() == "true"
    )
    thinking_level: str = os.getenv("GEMINI_MODEL_THINKING_LEVEL") or "HIGH"
    thinking_budget: int = int(os.getenv("GEMINI_MODEL_THINKING_BUDGET") or -1)

    # supply chain table
    dataset_id: str = os.getenv("BIGQUERY_DATASET_ID")
    table_id: str = os.getenv("BIGQUERY_TABLE_ID")

    # weather next table (Optional)
    weather_next_dataset_id: str | None = os.getenv(
        "WEATHER_NEXT_BIGQUERY_DATASET_ID"
    )
    weather_next_table_id: str | None = os.getenv(
        "WEATHER_NEXT_BIGQUERY_TABLE_ID"
    )
    # geo maps api key (Optional)
    geo_maps_api_key: str | None = os.getenv("GOOGLE_GEOMAP_API_KEY")

    # code interpreter extension name (Optional)
    code_interpreter_extension_name: str | None = os.getenv(
        "CODE_INTERPRETER_EXTENSION_NAME"
    )

    # Gemini thinking config
    _thinking_config: types.ThinkingConfig | None = None

    def get_thinking_config(self):
        """Returns the thinking config based on the model name"""
        if "gemini-2.5" in self.model_name:
            return types.ThinkingConfig(
                include_thoughts=self.include_thoughts,
                thinking_budget=self.thinking_budget,
            )
        else:
            return types.ThinkingConfig(
                include_thoughts=self.include_thoughts,
                thinking_level=self.thinking_level,
            )

    @property
    def thinking_config(self) -> types.ThinkingConfig:
        """Get thinking config, loading it if necessary."""
        if self._thinking_config is None:
            self._thinking_config = self.get_thinking_config()
        assert self._thinking_config is not None
        return self._thinking_config


config = AgentConfig()
