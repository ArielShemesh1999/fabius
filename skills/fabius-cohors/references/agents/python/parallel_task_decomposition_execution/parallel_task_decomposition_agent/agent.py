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

from google.adk.agents import Agent, LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search

from .prompts.prompts import (
    CALENDAR_PUBLISHER_INSTRUCTION,
    EMAIL_DRAFTER_INSTRUCTION,
    EMAIL_PUBLISHER_INSTRUCTION,
    EVENT_DETAILS_EXTRACTOR_INSTRUCTION,
    MESSAGE_ENHANCER_INSTRUCTION,
    ROOT_AGENT_INSTRUCTION,
    SLACK_DRAFTER_INSTRUCTION,
    SLACK_PUBLISHER_INSTRUCTION,
    SUMMARY_AGENT_INSTRUCTION,
)
from .tools import (
    create_calendar_event,
    publish_email_announcement,
    publish_slack_message,
)

logger = logging.getLogger("google_adk." + __name__)

email_drafting_agent = SequentialAgent(
    name="email_drafting_agent",
    description="Drafts and sends an email announcement.",
    sub_agents=[
        Agent(
            name="email_drafter",
            model="gemini-2.5-flash",
            instruction=EMAIL_DRAFTER_INSTRUCTION,
            output_key="drafted_email",
        ),
        Agent(
            name="email_publisher",
            model="gemini-2.5-flash",
            instruction=EMAIL_PUBLISHER_INSTRUCTION,
            output_key="email_publication_result",
            tools=[
                publish_email_announcement,
                # The gmail_mcp_tool shows an example MCP setup.
                # MCP Tools can be used to integrate with email providers that have MCP servers.
                # Users can uncomment if they connect their own MCP credentials and configs.
                # gmail_mcp_tool,
            ],
        ),
    ],
)

slack_drafting_agent = SequentialAgent(
    name="slack_drafting_agent",
    description="Drafts and sends a Slack message to multiple channels.",
    sub_agents=[
        Agent(
            name="slack_drafter",
            model="gemini-2.5-flash",
            instruction=SLACK_DRAFTER_INSTRUCTION,
            output_key="drafted_slack_message",
        ),
        Agent(
            name="slack_publisher",
            model="gemini-2.5-flash",
            instruction=SLACK_PUBLISHER_INSTRUCTION,
            output_key="slack_publication_result",
            tools=[
                publish_slack_message,
                # The slack_mcp_tool shows an example MCP setup.
                # MCP Tools can be used to integrate with Slack.
                # Users can uncomment if they connect their own MCP credentials and configs.
                # slack_mcp_tool,
            ],
        ),
    ],
)

calendar_creation_agent = SequentialAgent(
    name="calendar_creation_agent",
    description="Creates a Google Calendar event.",
    sub_agents=[
        Agent(
            name="event_details_extractor",
            model="gemini-2.5-flash",
            instruction=EVENT_DETAILS_EXTRACTOR_INSTRUCTION,
            output_key="event_details",
        ),
        Agent(
            name="calendar_publisher",
            model="gemini-2.5-flash",
            instruction=CALENDAR_PUBLISHER_INSTRUCTION,
            output_key="calendar_creation_result",
            tools=[
                create_calendar_event,
                # The calendar_mcp_tool shows an example MCP setup.
                # MCP Tools can be used to integrate with calendar services.
                # Users can uncomment if they connect their own MCP credentials and configs.
                # calendar_mcp_tool,
            ],
        ),
    ],
)

broadcast_agent = ParallelAgent(
    name="broadcast_agent",
    description="Broadcasts the announcement to email, Slack, and Google Calendar simultaneously.",
    sub_agents=[
        email_drafting_agent,
        slack_drafting_agent,
        calendar_creation_agent,
    ],
)

summary_agent = LlmAgent(
    name="summary_agent",
    model="gemini-2.5-flash",
    instruction=SUMMARY_AGENT_INSTRUCTION,
    description="Summarizes the results of the broadcast.",
)


main_flow_agent = SequentialAgent(
    name="main_flow_agent",
    description="Handles the main flow of enhancing the message and broadcasting it.",
    sub_agents=[
        Agent(
            name="message_enhancer",
            description="Enhances the user's message to make it more detailed and informative.",
            model="gemini-2.5-flash",
            instruction=MESSAGE_ENHANCER_INSTRUCTION,
            tools=[google_search],
            output_key="enhanced_message",
        ),
        broadcast_agent,
        summary_agent,
    ],
)

root_agent = Agent(
    name="announcement_coordinator",
    description="Aura: Your assistant for broadcasting important announcements across the company.",
    model="gemini-2.5-flash",
    instruction=ROOT_AGENT_INSTRUCTION,
    sub_agents=[main_flow_agent],
)
