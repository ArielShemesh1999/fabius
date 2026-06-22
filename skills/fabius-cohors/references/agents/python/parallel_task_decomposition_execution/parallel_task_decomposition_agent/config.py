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

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("google_adk." + __name__)

# --- MCP Environment Setup ---

# Google Calendar Config
GOOGLE_OAUTH_CREDENTIALS_FILENAME = os.environ.get("GOOGLE_OAUTH_CREDENTIALS")
GOOGLE_OAUTH_CREDENTIALS_PATH = ""
if GOOGLE_OAUTH_CREDENTIALS_FILENAME:
    GOOGLE_OAUTH_CREDENTIALS_PATH = os.path.join(
        os.path.dirname(__file__), GOOGLE_OAUTH_CREDENTIALS_FILENAME
    )
else:
    logger.warning(
        "GOOGLE_OAUTH_CREDENTIALS environment variable is NOT set. This is required for the real Google Calendar tool."
    )

# Slack Config
SLACK_MCP_XOXP_TOKEN = os.environ.get("SLACK_MCP_XOXP_TOKEN")
if not SLACK_MCP_XOXP_TOKEN:
    logger.warning(
        "SLACK_MCP_XOXP_TOKEN environment variable is NOT set. This is required for the real Slack tool."
    )

# Gmail Config
GMAIL_CREDENTIALS_PATH = os.path.expanduser("~/.gmail-mcp/credentials.json")
if not os.path.exists(GMAIL_CREDENTIALS_PATH):
    logger.warning(
        "Gmail credentials not found at ~/.gmail-mcp/credentials.json."
    )
    logger.warning(
        "This is required for the real Gmail tool. Run 'npx @gongrzhe/server-gmail-autoauth-mcp auth'."
    )
