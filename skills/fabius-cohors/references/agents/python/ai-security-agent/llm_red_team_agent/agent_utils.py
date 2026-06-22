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

import asyncio
from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai.errors import ClientError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


# Exception filter to ONLY retry on 429 errors (Resource Exhausted)
def is_resource_exhausted(exception):
    return (
        isinstance(exception, ClientError)
        and exception.code == HTTPStatus.TOO_MANY_REQUESTS
    )


@retry(
    retry=retry_if_exception_type(ClientError),  # Retry on ClientError
    wait=wait_exponential(multiplier=2, min=4, max=30),  # Wait 4s, 8s, 16s...
    stop=stop_after_attempt(3),  # Give up after 3 tries
)
def execute_sub_agent(agent: LlmAgent, prompt_text: str) -> str:
    """
    Runs a sub-agent by spinning up a temporary async loop in a SEPARATE THREAD.
    Args:
        agent (LlmAgent): The sub-agent to run.
        prompt_text (str): The prompt to send to the sub-agent.
    Returns:
        str: The response from the sub-agent.

    ARCHITECTURAL NOTE:
    -------------------
    This utilizes a ThreadPoolExecutor pattern here primarily for **Security State Isolation**.

    In a Red Teaming context, it is critical that the 'Attacker' (Red Team Agent) and
    'Target' (Banking Assistant) share zero context or memory. By instantiating a
    fresh Runner in a separate thread for each turn:

    1. It guarantees a "clean room" environment for the Target, preventing any
       accidental context leakage from the Orchestrator or Attacker.
    2. It ensures the Target's safety protocols are tested in a vacuum, mimicking
       a real-world stateless API request.
    """

    async def _run_internal():
        session_service = InMemorySessionService()
        session_id = "temp_task_session"
        await session_service.create_session(
            app_name="app", user_id="internal_bot", session_id=session_id
        )

        # Initialize Runner
        runner = Runner(
            agent=agent, app_name="app", session_service=session_service
        )

        content = types.Content(
            role="user", parts=[types.Part(text=prompt_text)]
        )
        result_text = ""

        # Run the Loop
        async for event in runner.run_async(
            new_message=content, user_id="internal_bot", session_id=session_id
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        result_text += part.text
        return result_text

    # Execute the async logic in a separate thread to avoid loop conflicts
    try:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, _run_internal())
            return future.result()
    except (RuntimeError, ValueError, TypeError) as e:
        return f"Error running sub-agent: {e!s}"
