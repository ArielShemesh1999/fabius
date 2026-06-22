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

from dotenv import load_dotenv
from fastapi.openapi.models import (
    OAuth2,
    OAuthFlowAuthorizationCode,
    OAuthFlows,
)
from google.adk.auth import AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.tools.application_integration_tool.application_integration_toolset import (
    ApplicationIntegrationToolset,
)

load_dotenv()

SNOW_CONNECTION_PROJECT_ID = os.getenv("SNOW_CONNECTION_PROJECT_ID")
SNOW_CONNECTION_REGION = os.getenv("SNOW_CONNECTION_REGION")
SNOW_CONNECTION_NAME = os.getenv("SNOW_CONNECTION_NAME")
SNOW_INSTANCE_NAME = os.getenv("SNOW_INSTANCE_NAME")
SNOW_OAUTH_SCOPES = os.getenv("SNOW_OAUTH_SCOPES")
AGENT_REDIRECT_URI = os.getenv("AGENT_REDIRECT_URI")
SNOW_CLIENT_ID = os.getenv("SNOW_CLIENT_ID")
SNOW_CLIENT_SECRET = os.getenv("SNOW_CLIENT_SECRET")

TOOL_INSTR = """
        **Tool Definition: ServiceNow Connector via Application Integration**

        This tool interacts with ServiceNow Incidents using an Application Integration Connector.
        It supports GET, LIST, and CREATE operations as defined for each entity.

         **Incident Getting:**

         If the user asks to get incident details:

        *   **Rendering User Response:**
            1. The user will input a sys_id value, use that value and the GET tool available to return the following (make it easy to read via rendering):
               - Incident Number (available in the "Number" JSON key/value)
               - Incident Description (available in the "Description" JSON key/value)
               - Ticket Creator (available in the "sys_created_by" JSON key/value)
               - Time of Creation (available in the "sys_created_on" JSON key/value)

        **Incident Creation:**

        If the user asks to create an incident:

        *   **Information Gathering:**
            1.  Collect minimal information from the user to describe the new incident. The only fields you should need to create an incident are the description, short_description, impact and urgency. Sample can be seen here:
            {
              "description": "My Macbook Pro mouse is broken, I need a new one delivered to my home",
              "short_description": "I need a new mouse for my Macbook Pro",
              "impact": 2.0,
              "urgency": 2.0
            }
            Deduce appropriate values for `impact`, and `urgency` based on the user-provided details.
        *   **User Confirmation:**
            1.  Before calling into the tool, present the summarized details (description, deduced category, impact, urgency) to the user.
            2.  Ask for explicit confirmation from the user to proceed with creation

        *   **Rendering User Response:**
            1. Please provide a reference to the ID returned in the response for tracking purposes

"""


oauth2_scheme = OAuth2(
    flows=OAuthFlows(
        authorizationCode=OAuthFlowAuthorizationCode(
            authorizationUrl=f"https://{SNOW_INSTANCE_NAME}.service-now.com/oauth_auth.do",
            tokenUrl=f"https://{SNOW_INSTANCE_NAME}.service-now.com/oauth_token.do",
            scopes={
                f"{SNOW_OAUTH_SCOPES}": "default",
            },
        )
    )
)

oauth2_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(
        client_id=SNOW_CLIENT_ID,
        client_secret=SNOW_CLIENT_SECRET,
        redirect_uri=AGENT_REDIRECT_URI,  # This is the ADK Web UI
    ),
)

snow_connector_tool = ApplicationIntegrationToolset(
    project=SNOW_CONNECTION_PROJECT_ID,
    location=SNOW_CONNECTION_REGION,
    connection=SNOW_CONNECTION_NAME,
    entity_operations={"Incident": ["GET", "LIST", "CREATE"]},
    tool_name_prefix="tool_snow",
    tool_instructions=TOOL_INSTR,
    auth_credential=oauth2_credential,
    auth_scheme=oauth2_scheme,
)
