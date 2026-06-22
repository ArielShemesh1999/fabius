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
import uuid

import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import (
    VertexAiRagRetrieval,
)
from openinference.instrumentation import using_session
from vertexai.preview import rag

from rag.tracing import instrument_adk_with_arize

from .prompts import return_instructions_root

load_dotenv()

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-east1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

_ = instrument_adk_with_arize()

# Initialize tools list
tools = []

# Only add RAG retrieval tool if RAG_CORPUS is configured
rag_corpus = os.environ.get("RAG_CORPUS")
if rag_corpus:
    ask_vertex_retrieval = VertexAiRagRetrieval(
        name="retrieve_rag_documentation",
        description=(
            "Use this tool to retrieve documentation and reference materials for the question from the RAG corpus,"
        ),
        rag_resources=[
            rag.RagResource(
                # please fill in your own rag corpus
                # here is a sample rag corpus for testing purpose
                # e.g. projects/123/locations/us-east1/ragCorpora/456
                rag_corpus=rag_corpus
            )
        ],
        similarity_top_k=10,
        vector_distance_threshold=0.6,
    )
    tools.append(ask_vertex_retrieval)

with using_session(session_id=uuid.uuid4()):
    root_agent = Agent(
        model="gemini-2.5-flash",
        name="ask_rag_agent",
        instruction=return_instructions_root(),
        tools=tools,
    )

app = App(
    root_agent=root_agent,
    name="rag_agent",
)
