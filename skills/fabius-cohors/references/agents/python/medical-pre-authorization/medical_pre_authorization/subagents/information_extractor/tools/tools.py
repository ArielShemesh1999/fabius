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
import logging
import os
import warnings
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
warnings.filterwarnings("ignore")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
logger = logging.getLogger(__name__)


def extract_treatment_name(user_query: str) -> str:
    """
    Extracts the treatment name from a user query using the Gemini model.
    Args:
        user_query: The user's input query.
    Returns:
        The extracted treatment name, or an empty string if not found.
    """
    # Initialize the Gemini model
    client = genai.Client(
        vertexai=True,
        project=GOOGLE_CLOUD_PROJECT,
        location=GOOGLE_CLOUD_LOCATION,
    )
    model = "gemini-2.5-flash"
    # Construct a prompt for the Gemini model to extract the treatment name
    si_text = f"""
    From the following user query, extract only the name of the medical treatment.
    If no specific treatment is mentioned, respond with "None".
    User Query: "{user_query}"
    Treatment Name:
    """
    contents = [
        types.Content(
            role="user", parts=[types.Part.from_text(text=user_query)]
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=1,
        seed=0,
        max_output_tokens=65535,
        system_instruction=[types.Part.from_text(text=si_text)],
        thinking_config=types.ThinkingConfig(
            thinking_budget=-1,
        ),
    )
    generated_text = ""
    try:
        # Stream the content generation and concatenate chunks
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            generated_text += chunk.text
    except Exception as e:
        print(f"An error occurred during content generation: {e}")
        return "Error generating response."
    return generated_text.strip()


def extract_policy_information(policy_file: str, treatment_name: str) -> str:
    """
    Extracts all information related to a specific treatment from insurance policy pdf
    using the Gemini model.
    Args:
        policy_file: The full text of the insurance policy.
        treatment_name: The name of the treatment to find information about.
    Returns:
        Relevant information about the treatment, or a message indicating it's not found.
    """
    client = genai.Client(
        vertexai=True,
        project=GOOGLE_CLOUD_PROJECT,
        location=GOOGLE_CLOUD_LOCATION,
    )
    # with open(policy_file_path, 'rb') as pdf_file:
    #     pdf_bytes = pdf_file.read()
    # Define the text part of the prompt
    prompt_text = types.Part.from_text(
        text=f"""
    You are an AI assistant specialized in analyzing insurance policy documents.
    Given the following insurance policy text, extract all details and clauses
    specifically related to the medical treatment named "{treatment_name}".
    Include information about coverage, exclusions, limits, conditions,
    and any other relevant terms.
    If "{treatment_name}" is not explicitly mentioned or no information
    is found regarding it, state "No specific information found for {treatment_name}."
    Insurance policy text: {policy_file}"""
    )
    model = "gemini-2.5-flash"
    contents = [
        types.Content(role="user", parts=[prompt_text]),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=65535,
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
        ),
    )
    summary_output = ""
    # Stream the content generation
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        summary_output += chunk.text
    return summary_output


def extract_medical_details(
    medical_report_file: str, treatment_name: str
) -> str:
    """
    Extracts all information related to a specific treatment from medical report pdf
    using the Gemini model
    Args:
        medical_report_file (str): The full text of the medical report.
        treatment_name: The name of the treatment to find information about.
    Returns: A summary of the relevant medical details
    """
    client = genai.Client(
        vertexai=True,
        project=GOOGLE_CLOUD_PROJECT,
        location=GOOGLE_CLOUD_LOCATION,
    )
    # Define the text part of the prompt
    prompt_text = types.Part.from_text(
        text="""You are an AI assistant specialized in analyzing medical reports.
    Given the following medical report txt, extract and summarize all relevant medical details specifically
    related to the treatment named \"{treatment_name}\". Include information about diagnosis, treatment plans,
    medications, procedures, and patient outcomes. If \"{treatment_name}\" is not explicitly mentioned or no
    information is found regarding it, state \\\"No specific information found for {treatment_name}.
    Medical report text {medical_report_file}"""
    )
    model = "gemini-2.5-flash"
    contents = [
        types.Content(role="user", parts=[prompt_text]),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=65535,
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
        ),
    )
    summary_output = ""
    # Stream the content generation
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        summary_output += chunk.text
    return summary_output
