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
import logging

from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from mcp import StdioServerParameters

from .config import (
    GOOGLE_OAUTH_CREDENTIALS_PATH,
    SLACK_MCP_XOXP_TOKEN,
)

logger = logging.getLogger("google_adk." + __name__)

# The gmail_mcp_tool shows an example MCP setup.
# MCP Tools can be used to integrate with email providers that have MCP servers.
# Users can uncomment if they connect their own MCP credentials and configs.
gmail_mcp_tool = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["@xxx/server-gmail-autoauth-mcp"],
        ),
    ),
)

# The slack_mcp_tool shows an example MCP setup.
# MCP Tools can be used to integrate with Slack.
# Users can uncomment if they connect their own MCP credentials and configs.
slack_mcp_tool = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "slack-mcp-server@latest", "--transport", "stdio"],
            env={"SLACK_MCP_XOXP_TOKEN": SLACK_MCP_XOXP_TOKEN},
        ),
    ),
)

# The calendar_mcp_tool shows an example MCP setup.
# MCP Tools can be used to integrate with calendar services.
# Users can uncomment if they connect their own MCP credentials and configs.
calendar_mcp_tool = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@xxx/google-calendar-mcp",
            ],
            env={"GOOGLE_OAUTH_CREDENTIALS": GOOGLE_OAUTH_CREDENTIALS_PATH},
        ),
    ),
)


async def publish_email_announcement(email_content: str) -> dict[str, str]:
    """
    Mocks publishing the email announcement to a third-party email service.
    Users can add their own integration logic here or replace this tool with an MCP tool.
    """
    logger.info("Publishing Email Announcement")
    return {"status": "success", "message": "Email announcement published."}


async def publish_slack_message(
    slack_content: str, channels: list[str]
) -> dict[str, str]:
    """
    Mocks publishing the Slack message to a list of third-party Slack channels asynchronously.
    Users can add their own integration logic here or replace this tool with an MCP tool.
    """

    async def post_to_channel(channel: str):
        """Simulates an async API call to post to a single channel."""
        logger.info("Posting to #%s...", channel)

        # await asyncio.sleep(0.1)
        logger.info("Successfully posted to #%s", channel)

    logger.info("Publishing Slack Message to channels: %s", ", ".join(channels))

    tasks = [post_to_channel(channel) for channel in channels]
    await asyncio.gather(*tasks)

    return {
        "status": "success",
        "message": f"Slack message published to {len(channels)} channels.",
    }


async def create_calendar_event(
    title: str, description: str, start_time: str, end_time: str
) -> dict[str, str]:
    """
    Mocks creating a calendar event.
    Users can add their own integration logic here or replace this tool with an MCP tool.
    """
    logger.info("Creating Calendar Event")
    logger.info("  Title: %s", title)
    logger.info("  Description: %s", description)
    logger.info("  Start: %s", start_time)
    logger.info("  End: %s", end_time)
    return {"status": "success", "message": "Calendar event created."}
