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
from typing import Any

from google.adk import Agent as AdkLlmAgent
from google.adk.agents import BaseAgent
from google.adk.models.base_llm import BaseLlm
from google.adk.planners import built_in_planner
from google.adk.plugins import ReflectAndRetryToolPlugin
from google.adk.runners import InMemoryRunner
from google.adk.tools import base_tool
from google.genai import types
from loguru import logger
from tau2.agent.llm_agent import LLMAgent, LLMAgentState
from tau2.data_model.message import (
    AssistantMessage,
    MultiToolMessage,
    ToolCall,
    ToolMessage,
    UserMessage,
)
from tau2.environment.tool import Tool


class AdkTool(base_tool.BaseTool):
    """Long running tool that escalates and stops invocation for ADK Agent"""

    def __init__(self, function_declaration: types.FunctionDeclaration):
        """Initialize the AdkTool with a function declaration.

        Args:
          function_declaration: The function declaration for the tool.
        """
        super().__init__(
            name=function_declaration.name,
            description=function_declaration.description,
            is_long_running=True,
        )
        self._function_declaration = function_declaration

    def _get_declaration(self):
        """Get the function declaration for the tool."""

        return self._function_declaration

    async def run_async(self, *, args, tool_context) -> Any:
        """Run the tool asynchronously."""

        tool_context.actions.escalate = True
        return None


def _create_agent(
    name: str,
    model: str | BaseLlm,
    instruction: str,
    tools: list[Tool],
    llm_args: dict[str, Any],
) -> BaseAgent:
    """Create an ADK LLM Agent with the given parameters.

    Args:
      name: The name of the agent.
      model: The LLM model to use.
      instruction: The system prompt/instruction for the agent.
      tools: The list of tools available to the agent.
      llm_args: Additional arguments for the LLM.

    Returns:
      An instance of BaseAgent (which also allows workflow agents).
    """
    adk_tools = [
        AdkTool(
            types.FunctionDeclaration(
                name=tool.openai_schema["function"]["name"],
                description=tool.openai_schema["function"].get(
                    "description", ""
                ),
                parameters_json_schema=tool.openai_schema["function"][
                    "parameters"
                ],
            )
        )
        for tool in tools
    ]

    generate_content_config = types.GenerateContentConfig()
    generate_content_config.temperature = llm_args.get(
        "temperature", 1
    )  # default to recommended temperature for gemini models

    thinking_level = None
    if (
        isinstance(model, str)
        and model.startswith("gemini-3")
        and "reasoning_effort" in llm_args
    ):
        thinking_level = llm_args["reasoning_effort"]

    thinking_config = types.ThinkingConfig(
        include_thoughts=True,
        thinking_level=thinking_level,
        thinking_budget=None,
    )

    return AdkLlmAgent(
        model=model,
        name=name,
        instruction=instruction,
        tools=adk_tools,
        planner=built_in_planner.BuiltInPlanner(
            thinking_config=thinking_config,
        ),
        generate_content_config=generate_content_config,
    )


class AdkAgent(LLMAgent):
    """Agent that uses ADK to interact with LLMs and tools."""

    def __init__(
        self,
        tools: list[Tool],
        domain_policy: str,
        llm: str | None = None,
        llm_args: dict | None = None,
    ):
        """Initialize the AdkAgent with the given parameters.

        Args:
          tools: The list of tools available to the agent.
          domain_policy: The domain policy for the agent.
          llm: The LLM model to use.
          llm_args: Additional arguments for the LLM.
        """
        super().__init__(
            tools=tools, domain_policy=domain_policy, llm=llm, llm_args=llm_args
        )
        model_name = llm or "gemini-2.5-pro"
        assert "gemini" in model_name, (
            "AdkAgent only supports gemini models for this benchmark."
        )
        if model_name.startswith("vertex_ai/"):
            model_name = model_name.replace("vertex_ai/", "")
        if model_name.startswith("gemini/"):
            model_name = model_name.replace("gemini/", "")
        self._adk_root_agent = _create_agent(
            name="customer_service_agent",
            model=self.llm_args.get("model_obj", model_name),
            instruction=self.system_prompt,
            tools=tools,
            llm_args=llm_args,
        )

        error_handling_plugin = ReflectAndRetryToolPlugin(
            max_retries=3, throw_exception_if_retry_exceeded=False
        )

        self._runner = InMemoryRunner(
            agent=self._adk_root_agent,
            app_name="tau2_adk_app",
            plugins=[error_handling_plugin],
        )
        self._app_name = "tau2_adk_app"
        self._user_id = "tau2_user"
        try:
            self.session = asyncio.run(
                self._runner.session_service.create_session(
                    app_name=self._app_name,
                    user_id=self._user_id,
                )
            )
        except RuntimeError:
            self.session = None

    async def async_setup(self) -> None:
        """Asynchronous setup for the AdkAgent."""

        if self.session is None:
            self.session = await self._runner.session_service.create_session(
                app_name=self._app_name, user_id=self._user_id
            )

    async def _run_prompt_async(
        self,
        new_message: str | None,
        function_responses: list[types.FunctionResponse] | None = None,
    ) -> AssistantMessage:
        """Run the prompt asynchronously and return the assistant message.

        Args:
          new_message: The new message from the user.
          function_responses: The list of function responses from tools.

        Returns:
          An AssistantMessage containing the response from the agent.
        """
        if new_message is not None:
            content = types.Content(
                role="user", parts=[types.Part.from_text(text=new_message)]
            )
        else:
            content = types.Content(
                role="user",
                parts=[
                    types.Part(function_response=fr)
                    for fr in function_responses
                ],
            )

        logger.info(f"** User says: {content.model_dump(exclude_none=True)}")
        text_content = ""
        tool_calls: list[ToolCall] = []
        async for event in self._runner.run_async(
            user_id=self._user_id,
            session_id=self.session.id,
            new_message=content,
        ):
            if event is None or event.content is None:
                continue

            logger.info(f"** Event received: {event.content.parts}")
            for part in event.content.parts:
                if part.function_call:
                    logger.info(
                        f"** Tool call: {part.function_call.name} with arguments"
                        f" {part.function_call.args}"
                    )
                    self.add_long_running_call_info(
                        (part.function_call.id, part.function_call.name)
                    )
                    tool_calls.append(
                        ToolCall(
                            id=part.function_call.id,
                            name=part.function_call.name,
                            arguments=part.function_call.args,
                            requestor="assistant",
                        )
                    )
                elif part.text:
                    if not part.thought:
                        text_content += part.text
                else:
                    logger.info(f"** Other part type received: {part}")

        return AssistantMessage(
            role="assistant",
            content=text_content or None,
            tool_calls=tool_calls or None,
        )

    def generate_next_message(
        self, message: Any, state: LLMAgentState
    ) -> tuple[AssistantMessage, LLMAgentState]:
        """Generate the next message from the agent based on the input message.

        Args:
          message: The input message from the user or tool.
          state: The current state of the agent.

        Returns:
          A tuple containing the assistant message and the updated agent state.
        """
        if isinstance(message, MultiToolMessage):
            state.messages.extend(message.tool_messages)
        else:
            state.messages.append(message)

        if getattr(self, "session", None) is None:
            try:
                asyncio.run(self.async_setup())
            except RuntimeError as e:
                raise RuntimeError(
                    "Cannot create ADK session: an event loop is already running."
                ) from e

        if isinstance(message, UserMessage):
            assistant_message = asyncio.run(
                self._run_prompt_async(new_message=message.content)
            )
        elif isinstance(message, ToolMessage):
            call_id, call_name = self.pop_long_running_call_info_with_id(
                message.id
            )
            if not call_id or not call_name:
                call_id, call_name = self.pop_long_running_call_info()

            json_response = {"result": message.content}
            function_response = types.FunctionResponse(
                id=call_id,
                name=call_name,
                response=json_response,
            )
            assistant_message = asyncio.run(
                self._run_prompt_async(
                    new_message=None, function_responses=[function_response]
                )
            )
        elif isinstance(message, MultiToolMessage):
            function_responses = []
            for tm in message.tool_messages:
                call_id, call_name = self.pop_long_running_call_info_with_id(
                    tm.id
                )
                if not call_id or not call_name:
                    call_id, call_name = self.pop_long_running_call_info()

                json_response = {"result": tm.content}
                function_response = types.FunctionResponse(
                    id=call_id,
                    name=call_name,
                    response=json_response,
                )
                function_responses.append(function_response)
            assistant_message = asyncio.run(
                self._run_prompt_async(
                    new_message=None, function_responses=function_responses
                )
            )
        else:
            assistant_message = asyncio.run(
                self._run_prompt_async(new_message="")
            )

        state.messages.append(assistant_message)
        return assistant_message, state

    def add_long_running_call_info(self, call_info: tuple[str, str]):
        """Add information about a long-running call.

        Args:
          call_info: A tuple containing the call ID and call name.
        """
        if not hasattr(self, "long_running_call_infos"):
            self.long_running_call_infos = []
        self.long_running_call_infos.append(call_info)

    def pop_long_running_call_info(self):
        """Pop the oldest long-running call information.

        Returns:
          A tuple containing the call ID and call name, or None if no information
          is available.
        """
        if (
            hasattr(self, "long_running_call_infos")
            and self.long_running_call_infos
        ):
            return self.long_running_call_infos.pop(0)
        return None

    def pop_long_running_call_info_with_id(
        self, call_id: str
    ) -> tuple[str, str] | None:
        """Pop long-running call information by call ID.

        Args:
          call_id: The ID of the long-running call to pop.

        Returns:
          A tuple containing the call ID and call name, or None if no information
          is available.
        """
        if (
            hasattr(self, "long_running_call_infos")
            and self.long_running_call_infos
        ):
            for i, (stored_call_id, _call_name) in enumerate(
                self.long_running_call_infos
            ):
                if stored_call_id == call_id:
                    return self.long_running_call_infos.pop(i)
        return None
