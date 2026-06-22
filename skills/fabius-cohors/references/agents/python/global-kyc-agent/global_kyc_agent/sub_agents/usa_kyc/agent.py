import datetime

# Get the API client from shared or initialized
from google import genai
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.models import google_llm
from google.adk.tools.function_tool import FunctionTool

from ...shared_libraries import helpercode
from ...shared_libraries.config import config

# Import Prompts
from .prompt import (
    REPORT_CREATION_INSTRUCTION,
    SEC_FILING_INSTRUCTION,
    SEC_INSIDER_INSTRUCTION,
    SEC_REPORT_INSTRUCTION,
    SEC_SEARCH_INSTRUCTION,
    USA_KYC_INSTRUCTION,
)
from .tools.insider_trading import get_insider_transactions

# Import USA tools
from .tools.sec import (
    extract_filing_section,
    full_text_search,
    get_recent_filings,
)

model = google_llm.Gemini(model=config.gemini_model)
try:
    api_client = genai.Client(
        vertexai=True, project=helpercode.get_project_id(), location="global"
    )
    model.api_client = api_client
except Exception as e:
    api_client = None
    print(f"Warning: Failed to initialize genai.Client: {e}")


def get_current_date() -> str:
    """Returns the current date in YYYY-MM-DD format."""
    return datetime.date.today().strftime("%Y-%m-%d")


get_current_date_tool = FunctionTool(get_current_date)


usa_sec_search_agent = Agent(
    name="usa_sec_search_agent",
    model=model,
    description="Agent for searching across all recent SEC filings for specific topics or keywords.",
    instruction=SEC_SEARCH_INSTRUCTION,
    tools=[get_current_date_tool, full_text_search],
    output_key="sec_search_results",
)

usa_sec_filing_agent = Agent(
    name="usa_sec_filing_agent",
    model=model,
    description="Agent for finding and extracting specific sections from a company's SEC filings.",
    instruction=SEC_FILING_INSTRUCTION,
    tools=[get_recent_filings, extract_filing_section],
    output_key="sec_filing_extracts",
)

usa_sec_insider_agent = Agent(
    name="usa_sec_insider_agent",
    model=model,
    description="Agent for tracking insider trading transactions (Forms 3, 4, 5).",
    instruction=SEC_INSIDER_INSTRUCTION,
    tools=[get_current_date_tool, get_insider_transactions],
    output_key="sec_insider_results",
)

usa_sec_report_agent = Agent(
    name="usa_sec_report_agent",
    model=model,
    description="Agent that synthesizes raw SEC filing text into comprehensive financial reports.",
    instruction=SEC_REPORT_INSTRUCTION,
    output_key="sec_final_report",
)

usa_sec_master_agent = SequentialAgent(
    name="usa_sec_master_agent",
    description="Master agent that coordinates SEC search, extraction, and report generation.",
    sub_agents=[
        usa_sec_search_agent,
        usa_sec_filing_agent,
        usa_sec_insider_agent,
        usa_sec_report_agent,
    ],
)

usa_report_creation_agent = Agent(
    name="usa_report_creation_agent",
    model=model,
    description="You are an agent helping an investment analyst create a report on an asset or stock",
    instruction=REPORT_CREATION_INSTRUCTION,
)

usa_data_retrieval_agent = ParallelAgent(
    name="usa_data_retrieval_agent",
    description="You are an agent that helps a financial analyst to retrieve info about a company or stock",
    sub_agents=[usa_sec_master_agent],
)

usa_sequential_agent = SequentialAgent(
    name="usa_sequential_agent",
    description="you are the agent that runs the process for collecting the data and creating the report",
    sub_agents=[usa_data_retrieval_agent, usa_report_creation_agent],
)

usa_kyc_agent = Agent(
    name="usa_kyc_agent",
    model=model,
    description="You are an agent helping an investment analyst at an asset manager",
    instruction=USA_KYC_INSTRUCTION,
    tools=[get_current_date_tool],
    sub_agents=[usa_sequential_agent],
)
