def merge_agents():
    ch_path = "companies_house_agent/agent.py"
    edgar_path = "edgar_agent/agent.py"
    target_path = "global_kyc_agent/agent.py"

    with open(ch_path) as f:
        ch_content = f.read()

    with open(edgar_path) as f:
        edgar_content = f.read()

    # Rename root agents to avoid conflict
    ch_content = ch_content.replace(
        'name="root_agent",', 'name="uk_kyc_agent",'
    )
    ch_content = ch_content.replace(
        "root_agent = Agent(", "uk_kyc_agent = Agent("
    )

    edgar_content = edgar_content.replace(
        'name="investment_agent",', 'name="usa_kyc_agent",'
    )
    edgar_content = edgar_content.replace(
        "root_agent = Agent(", "usa_kyc_agent = Agent("
    )

    # We need to preserve imports at the top.
    # Let's combine them carefully. Actually, since edgar is mostly at the bottom, we can just append.
    # But edgar has imports at the top. Let's move edgar's imports to the top.

    merged_content = """
# ==========================================
# GLOBAL KYC AGENT MERGED FILE
# ==========================================
import sys
import datetime
import os
from zoneinfo import ZoneInfo

from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import agent_tool
from google.adk.tools import google_search
from google.adk.tools.function_tool import FunctionTool
from .config import config

# --- UK Imports ---
from .tools.companieshouse_tools import (
    search_companies, get_company_profile, get_company_officers, get_company_address,
    get_company_establishments, get_company_registers, get_company_exemptions,
    get_company_charges, get_company_insolvency, get_corporate_officer_disqualifications,
    get_natural_officer_disqualifications, get_office_appointments, get_company_filing_history,
    get_company_filing_detail
)

from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.utils.context_utils import Aclosing

# --- USA Imports ---
from google import genai
from google.adk.models import google_llm
from .helpercode import get_project_id
from .tools.sec import full_text_search, get_recent_filings, extract_filing_section
from .tools.insider_trading import get_insider_transactions

"""

    # We skip imports in the files by finding where the real code starts
    # For CH, look for "class SubAgentEvent(Event):"
    ch_code = ch_content[ch_content.find("class SubAgentEvent(Event):") :]

    # For Edgar, look for "def get_current_date() -> str:"
    edgar_code = edgar_content[
        edgar_content.find("def get_current_date() -> str:") :
    ]

    merged_content += f"""
# ==========================================
# COMPANIES HOUSE (UK) AGENTS
# ==========================================
{ch_code}

# ==========================================
# EDGAR (USA) AGENTS
# ==========================================
{edgar_code}

# ==========================================
# GLOBAL ROUTER AGENT
# ==========================================
global_kyc_agent = Agent(
    name="global_kyc_agent",
    model=config.gemini_model,
    description="Global KYC Agent that routes requests appropriately based on the geographical location of the company (UK vs USA).",
    instruction=(
        "You are the Global KYC Router Agent. Your purpose is to determine which sub-agent to use based on the user's request. "
        "If the user is asking about a UK company or specifically requests Companies House data, use the `uk_kyc_agent`. "
        "If the user is asking about a US company or specifically requests SEC/EDGAR or insider trading data, use the `usa_kyc_agent`. "
        "Ensure you delegate fully to the appropriate sub-agent and return its findings as a comprehensive report."
    ),
    sub_agents=[uk_kyc_agent, usa_kyc_agent]
)

"""

    with open(target_path, "w") as f:
        f.write(merged_content)
        print("Successfully merged agent files into", target_path)


if __name__ == "__main__":
    merge_agents()
