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

import base64
import json
import os

from fastapi.openapi.models import (
    OAuth2,
    OAuthFlowAuthorizationCode,
    OAuthFlows,
)
from google.adk.auth.auth_credential import (
    AuthCredential,
    AuthCredentialTypes,
    OAuth2Auth,
)
from google.adk.auth.auth_tool import AuthConfig
from google.adk.tools import ToolContext
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .utils import logger

# --- Environment Variables ---
AUTH_ID = os.getenv(
    "AUTH_ID",
    f"{os.getenv('GOOGLE_CLOUD_PROJECT')}-brand-aligner-agent-oauth-id",
)
MODE = os.getenv("MODE", "production")

OAUTH_TOKEN_URI = os.getenv(
    "OAUTH_TOKEN_URI", "https://oauth2.googleapis.com/token"
)
OAUTH_AUTH_URI_BASE = os.getenv(
    "OAUTH_AUTH_URI_BASE", "https://accounts.google.com/o/oauth2/v2/auth"
)

OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", "")

# --- Auth Configuration - relevant only for ADK ---
# --- Token retrieval is managed directly by Gemini Enterprise as part of agent registration ---
SCOPES = ["https://www.googleapis.com/auth/userinfo.email"]
auth_scheme = OAuth2(
    flows=OAuthFlows(
        authorizationCode=OAuthFlowAuthorizationCode(
            authorizationUrl=OAUTH_AUTH_URI_BASE,
            tokenUrl=OAUTH_TOKEN_URI,
            scopes={
                "https://www.googleapis.com/auth/userinfo.email": "See your primary Google Account email address",
            },
        )
    )
)

oauth_cred = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(
        client_id=OAUTH_CLIENT_ID,
        client_secret=OAUTH_CLIENT_SECRET,
    ),
)

auth_config = AuthConfig(
    auth_scheme=auth_scheme,
    raw_auth_credential=oauth_cred,
)


def _get_encoded_email_from_token(token: str) -> str:
    """Get user info from access token and base64 encode the email."""
    credentials = Credentials(token=token)
    service = build("oauth2", "v2", credentials=credentials)
    user_info = service.userinfo().get().execute()
    user_email = user_info.get("email") or ""
    email_bytes = user_email.encode("utf-8")
    encoded_bytes = base64.b64encode(email_bytes)
    encoded_email = encoded_bytes.decode("utf-8")
    logger.info("AUTH: Extracted user email and encoded it: %s", encoded_email)
    return encoded_email


def _get_token_from_state(tool_context: ToolContext, key: str) -> str | None:
    """Helper to get token from tool context state."""
    token = tool_context.state.get(key)
    if token:
        logger.info("AUTH: Retrieved token from state key: %s", key)
    else:
        logger.info("AUTH: No token found at state key: %s", key)
    return token


def get_user_id(tool_context: ToolContext) -> str | dict[str, str]:
    """Retrieves the user's id to use in the agent's operations."""
    # Gemini Enterprise logic - auth flow already finished!
    token = _get_token_from_state(
        tool_context, AUTH_ID
    ) or _get_token_from_state(tool_context, f"temp:{AUTH_ID}")

    if token:
        return _get_encoded_email_from_token(token)

    if MODE == "production":
        logger.info(
            "AUTH: No token found in state, and MODE is 'production'. Falling back to default session user..."
        )
        return tool_context.session.user_id

    # ADK logic - manage auth flow within the tool
    logger.info(
        "AUTH: No cached token found at key [%s]. Continuing..., ",
        f"temp:{AUTH_ID}",
    )
    TOKEN_CACHE_KEY = f"user_email_token-{tool_context.session.id}"

    creds = None
    cached_token_info = tool_context.state.get(TOKEN_CACHE_KEY)
    authenticated = False

    try:
        if cached_token_info:
            logger.info(
                "AUTH: Found cached token info at key [%s], attempting to load credentials..., ",
                TOKEN_CACHE_KEY,
            )
            try:
                creds = Credentials.from_authorized_user_info(
                    cached_token_info, SCOPES
                )
                if not creds.valid and creds.expired and creds.refresh_token:
                    logger.info("AUTH: Refreshing expired credentials.")
                    creds.refresh(Request())
                    tool_context.state[TOKEN_CACHE_KEY] = json.loads(
                        creds.to_json()
                    )
                elif not creds.valid:
                    creds = None
                    tool_context.state[TOKEN_CACHE_KEY] = None
            except Exception as e:
                logger.warning(
                    f"AUTH: Error loading/refreshing cached creds: {e}"
                )
                creds = None
                tool_context.state[TOKEN_CACHE_KEY] = None

        if creds and creds.valid:
            authenticated = True
        else:
            logger.info(
                "AUTH: No valid cached credentials found, checking for auth response."
            )
            exchanged_credential = tool_context.get_auth_response(auth_config)
            if exchanged_credential:
                logger.info(
                    "AUTH: Using exchanged credential from auth response."
                )
                access_token = exchanged_credential.oauth2.access_token
                refresh_token = exchanged_credential.oauth2.refresh_token
                creds = Credentials(
                    token=access_token,
                    refresh_token=refresh_token,
                    token_uri=auth_scheme.flows.authorizationCode.tokenUrl,
                    client_id=oauth_cred.oauth2.client_id,
                    client_secret=oauth_cred.oauth2.client_secret,
                    scopes=auth_scheme.flows.authorizationCode.scopes,
                )
                authenticated = True
            else:
                logger.info(
                    "AUTH: No exchanged credential found, initiating authentication flow."
                )
                tool_context.request_credential(auth_config)
                return {
                    "pending": True,
                    "message": "Awaiting user authentication.",
                }

        if authenticated and creds:
            tool_context.state[TOKEN_CACHE_KEY] = json.loads(creds.to_json())
            logger.info(
                f"AUTH: Cached/updated token under key: {TOKEN_CACHE_KEY}"
            )
            return _get_encoded_email_from_token(creds.token)
    except Exception:
        logger.exception("AUTH: Failed to retrieve user's email")
        logger.info(
            "AUTH: Falling back to session user_id: %s",
            tool_context.session.user_id,
        )
        return tool_context.session.user_id
