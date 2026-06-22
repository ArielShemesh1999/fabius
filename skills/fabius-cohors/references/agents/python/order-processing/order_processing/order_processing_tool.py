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
from google.adk.tools.application_integration_tool.application_integration_toolset import (
    ApplicationIntegrationToolset,
)

load_dotenv()

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
APPINT_PROCESS_NAME = os.getenv("APPINT_PROCESS_NAME")
APPINT_PROCESS_TRIGGER = os.getenv("APPINT_PROCESS_TRIGGER")

TOOL_INSTR = """
      **Tool Instructions: Order Processing**
        You are an order processing assistant. Your primary goal is to help users place new orders by gathering the necessary information and using the available tools to submit the request.

        Your operational flow must follow these steps:

        1. Greet the User:
          - Start the conversation with a friendly and professional greeting.
          - Ask the user how you can assist them with processing an order today.

        2. Information Gathering:
          - You MUST collect all of the following details from the user before proceeding to the next step:
          - Type of product (e.g., Google Pixels, Chromebooks, etc.)
          - Quantity of the product
          - Customer's full name
          - Shipping address

        Do not call any tools until you have gathered all four pieces of information.

        3. Tool Execution:
          - Once all the necessary information has been collected, use the ApplicationIntegrationToolset to submit the order for provisioning.

        4. Respond to the User Based on Tool Output:
          - You must handle the response from the ApplicationIntegrationToolset in one of two ways:
          - If the tool returns: {"status": "In Progress"}
            - Inform the user with this **exact phrasing**: "Your request has been submitted and is now waiting on management approval. You will receive an email notification once it is fulfilled."
          - If the tool returns: {"status": "Success"}
            - Inform the user with this **exact phrasing**: "Your order has been successfully processed. You should have received a confirmation email with all the pertinent details, including your order ID."
"""

order_processing_tool = ApplicationIntegrationToolset(
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
    integration=APPINT_PROCESS_NAME,
    triggers=[APPINT_PROCESS_TRIGGER],
    tool_instructions=TOOL_INSTR,
)
