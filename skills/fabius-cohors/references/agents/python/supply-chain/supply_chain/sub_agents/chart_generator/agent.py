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

"""Chart Generator Agent: provides relevant charts from the available data"""

import logging
import warnings

from google.adk.agents import LlmAgent
from google.adk.code_executors import VertexAiCodeExecutor
from google.adk.planners import BuiltInPlanner
from google.genai import types

from ...config import config
from . import prompts

warnings.filterwarnings("ignore", category=UserWarning)

# Configure logging for debug purposes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_safe_executor(kwargs):
    return SafeVertexAiCodeExecutor(**kwargs)


class SafeVertexAiCodeExecutor(VertexAiCodeExecutor):
    """
    A wrapper around VertexAiCodeExecutor that implements __deepcopy__ and __reduce__
    to fix RecursionError and SerializationError during agent deployment.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kwargs = kwargs

    def __deepcopy__(self, memo):
        return SafeVertexAiCodeExecutor(**self._kwargs)

    def __reduce__(self):
        # Capture the resource_name from the created extension to avoid re-creation on remote
        kwargs = self._kwargs.copy()
        try:
            if hasattr(self, "_extension") and hasattr(
                self._extension, "resource_name"
            ):
                logger.debug(
                    f"DEBUG: Capturing resource_name in pickle: {self._extension.resource_name}"
                )
                kwargs["resource_name"] = self._extension.resource_name
            else:
                logger.debug(
                    "DEBUG: No extension or resource_name found in SafeVertexAiCodeExecutor"
                )
        except Exception:
            logger.debug(
                "DEBUG: Error capturing resource_name in SafeVertexAiCodeExecutor pickle",
                exc_info=True,
            )
        return (create_safe_executor, (kwargs,))


chart_generator_agent = LlmAgent(
    model=config.model_name,
    name="ChartGeneratorAgent",
    code_executor=SafeVertexAiCodeExecutor(
        optimize_data_file=True,
        stateful=True,
        resource_name=config.code_interpreter_extension_name,
    ),
    description="Generate charts from the available data",
    instruction=prompts.CHART_GENERATOR_AGENT_PROMPT,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.temperature,
        top_p=config.top_p,
    ),
    planner=BuiltInPlanner(thinking_config=config.thinking_config),
    output_key="chart_generator_result",
)
