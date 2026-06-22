# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the License);
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

from google.adk.agents import LlmAgent
from google.adk.tools import load_artifacts

from .tools import (
    asset_evaluator_tool,
    guideline_processor_tool,
    save_artifacts_to_gcs_tool,
    save_files_as_artifacts,
    save_plan_to_state_tool,
    search_user_files_tool,
)
from .utils import after_model_callback

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")

# --- AGENT DEFINITIONS ---

# 3. Summarizer Agent: Provides the final summary.
summarizer_agent = LlmAgent(
    name="summarizer_agent",
    model=MODEL_NAME,
    instruction="""
        You provide a final summary of the brand alignment evaluation.
        The evaluation results are in `session.state['evaluation_results']`.
        Your communication style is verbose and transparent.

        **WORKFLOW:**
        1.  Announce to the user that you are starting the final summary step. For example: "Step 3: Final Summary..."
        2.  Calculate the total number of assets and the average of the `final_score` across all evaluations.
        3.  Present this summary to the user as your final message.
    """,
    after_model_callback=after_model_callback,
)

# 2. Asset Evaluation Agent.
asset_evaluator_agent = LlmAgent(
    name="asset_evaluator_agent",
    model=MODEL_NAME,
    instruction="""
        You are an asset evaluation agent. Your job is to evaluate all visual assets listed in `session.state['asset_files']` against the brand guidelines.
        Your communication style is verbose and transparent.

        **WORKFLOW:**
        1.  Announce to the user that you are starting the asset evaluation step. For example: "Step 2: Evaluating Assets..."
        2.  Iterate through the `session.state['asset_files']` list. For EACH asset file:
            a. Prepare an asset dictionary containing:
               * `asset_name`: The name of the asset file from the state.
               * `asset_id`: A string representation of the index of the current asset (e.g., '1', '2', '3').
               * `category`: 'IMAGE' or 'VIDEO' based on file name / type.
               * `asset_prompt`: User provided prompt or empty string.
               * `video_reference_image_files`: Reference image file names for video assets (if any), else empty list.
            b. Call `asset_evaluator_tool` with this single asset dictionary.
            c. The tool will return a formatted Markdown report.
            d. Present the report to the user.
        3.  After evaluating ALL assets, call the `summarizer_agent` to proceed to the final summary.
    """,
    tools=[asset_evaluator_tool],
    sub_agents=[summarizer_agent],
    after_model_callback=after_model_callback,
)

# 1. Guideline Processing Agent.
guideline_processor_agent = LlmAgent(
    name="guideline_processor_agent",
    model=MODEL_NAME,
    instruction="""
        You are a guideline processing agent. Your job is to process all brand guideline files listed in `session.state['guideline_files']`.
        Your communication style is verbose and transparent.

        **WORKFLOW:**
        1.  Announce to the user that you are starting the guideline processing step. For example: "Step 1: Processing Guidelines..."
        2.  Iterate through `session.state['guideline_files']`. For EACH file:
            a. Call `guideline_processor_tool` with the file name from the state.
            b. The tool will return a formatted Markdown report.
            c. Present the report to the user.
        3.  After processing ALL guidelines, call the `asset_evaluator_agent` to proceed to the next step.
    """,
    tools=[guideline_processor_tool],
    sub_agents=[asset_evaluator_agent],
    after_model_callback=after_model_callback,
)

# 0. Root Agent (Planner).
root_agent = LlmAgent(
    name="brand_aligner_agent",
    model=MODEL_NAME,
    instruction="""
        You are a planning agent for a brand alignment evaluation service. Your job is to interact with the user to create a clear plan for execution, and then trigger that execution.
        Your communication style is verbose and transparent.

        **Primary Goal:** Identify brand guidelines and visual assets, get user confirmation, and then execute the plan.

        **Interaction Flow:**

        1.  **Analyze User Intent:**
            *   If it's a simple greeting like "hi", respond politely and do not proceed.
            *   If the user uploads files, or asks to search for files, or mentions evaluation, proceed to the next steps.

        2.  **Handle and Categorize Files:**
            *   **File Handling:** After the user uploads files or asks to find existing files, your first step is to call `save_artifacts_to_gcs_tool` to save any in-session files to persistent storage. After that, call `search_user_files_tool` to get a complete list of all user files.
            *   **Display:** The tool returns a list of file names which you can display to the user.
            *   **Confirmation:** After retrieving the complete list of files, classify them as **guideline files** or **asset files** depending on the file extension (PDF, MD and TEXT files are guidelines, while image and video files are assets), then interact with the user to confirm the exact list of **guideline files** and **asset files** to be used in the evaluation.

        3.  **Create and Confirm Plan:**
            *   Create a step-by-step plan of the tasks.
            *   Present this plan to the user for confirmation. For example:
                "I will process 1 guideline file and then evaluate 2 assets.
                1. Process and report on guideline: brand_book.pdf
                2. Evaluate and report on asset: logo.png
                3. Evaluate and report on asset: ad_video.mp4
                4. Provide a final summary."

        4.  **Store Plan:**
            *   After user confirmation, call `save_plan_to_state_tool` with the categorized lists of file names.

        5.  **Execute Plan:**
            *   If there are assets to evaluate, your final step is to call the `guideline_processor_agent` sub-agent to begin the execution chain.
            *   If there are no assets to evaluate, simply state that the planning is complete and do not call the agent.
    """,
    tools=[
        load_artifacts,
        save_artifacts_to_gcs_tool,
        save_plan_to_state_tool,
        search_user_files_tool,
    ],
    sub_agents=[guideline_processor_agent],
    before_model_callback=save_files_as_artifacts,
)
