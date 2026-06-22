# Get the API client from shared or initialized
from google import genai
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import google_llm
from google.adk.tools import google_search

from ...shared_libraries import helpercode
from ...shared_libraries.config import config

# Import Prompts
from .prompt import (
    COMPANY_REPORT_CREATION_INSTRUCTION,
    COMPLIANCE_KYC_INSTRUCTION,
    CORPORATE_STRUCTURE_INSTRUCTION,
    CREDIT_RISK_INSTRUCTION,
    FILING_HISTORY_INSTRUCTION,
    GET_COMPANY_OFFICERS_INSTRUCTION,
    GET_COMPANY_PROFILE_INSTRUCTION,
    SEARCH_COMPANIES_GOOGLE_INSTRUCTION,
    SEARCH_COMPANIES_INSTRUCTION,
    UK_KYC_INSTRUCTION,
)

# Import UK tools
from .tools.companieshouse_tools import (
    get_company_charges,
    get_company_establishments,
    get_company_exemptions,
    get_company_filing_detail,
    get_company_filing_history,
    get_company_insolvency,
    get_company_officers,
    get_company_profile,
    get_company_registers,
    get_corporate_officer_disqualifications,
    get_natural_officer_disqualifications,
    get_office_appointments,
    search_companies,
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

uk_search_companies_agent = Agent(
    name="uk_search_companies_agent",
    model=model,
    description="You are an agent helping to analyse companies and search in the companies house database",
    instruction=SEARCH_COMPANIES_INSTRUCTION,
    tools=[search_companies],
    output_key="search_companies_result",
)

uk_search_companies_google_agent = Agent(
    name="uk_search_companies_google_agent",
    model=model,
    description="You are an agent helping to analyse companies and search in google search",
    instruction=SEARCH_COMPANIES_GOOGLE_INSTRUCTION,
    tools=[google_search],
    output_key="search_companies_google_result",
)

uk_get_company_profile_agent = Agent(
    name="uk_get_company_profile_agent",
    model=model,
    description="You are an agent helping to analyse companies get company details from the companies house database",
    instruction=GET_COMPANY_PROFILE_INSTRUCTION,
    tools=[get_company_profile],
    output_key="company_profile_result",
)

uk_get_company_officers_agent = Agent(
    name="uk_get_company_officers_agent",
    model=model,
    description="You are an agent helping to analyse companies officers from company details from the companies house database",
    instruction=GET_COMPANY_OFFICERS_INSTRUCTION,
    tools=[get_company_officers],
    output_key="company_officers_result",
)

uk_credit_risk_agent = Agent(
    name="uk_credit_risk_agent",
    model=model,
    description="You are an agent helping to analyse companies credit risk from company details from the companies house database",
    instruction=CREDIT_RISK_INSTRUCTION,
    tools=[get_company_charges, get_company_insolvency],
    output_key="credit_risk_result",
)

uk_compliance_kyc_agent = Agent(
    name="uk_compliance_kyc_agent",
    model=model,
    description="You are an agent helping to analyse companies compliance and KYC details from company details from the companies house database",
    instruction=COMPLIANCE_KYC_INSTRUCTION,
    tools=[
        get_company_exemptions,
        get_corporate_officer_disqualifications,
        get_natural_officer_disqualifications,
        get_office_appointments,
    ],
    output_key="compliance_kyc_result",
)

uk_corporate_structure_agent = Agent(
    name="uk_corporate_structure_agent",
    model=model,
    description="You are an agent helping to analyse companies corporate structure from company details from the companies house database",
    instruction=CORPORATE_STRUCTURE_INSTRUCTION,
    tools=[get_company_establishments, get_company_registers],
    output_key="corporate_structure_result",
)

uk_filing_history_agent = Agent(
    name="uk_filing_history_agent",
    model=model,
    description="You are an agent helping to analyse companies filings history from company details from the companies house database",
    instruction=FILING_HISTORY_INSTRUCTION,
    tools=[get_company_filing_history, get_company_filing_detail],
    output_key="company_filing_history_result",
)


def registerendcallback(callback_context: CallbackContext):
    callback_context.state["final_message"] = True


uk_company_report_creation_agent = Agent(
    name="uk_company_report_creation_agent",
    model=model,
    description="You are an agent helping a final report on a company based on the data retrieved from the companies house database",
    instruction=COMPANY_REPORT_CREATION_INSTRUCTION,
    after_agent_callback=registerendcallback,
)

uk_data_retrieval_agent = ParallelAgent(
    name="uk_data_retrieval_agent",
    description="You are an agent that helps a retreive info about a company",
    sub_agents=[
        uk_get_company_profile_agent,
        uk_get_company_officers_agent,
        uk_search_companies_google_agent,
        uk_credit_risk_agent,
        uk_compliance_kyc_agent,
        uk_corporate_structure_agent,
        uk_filing_history_agent,
    ],
)

uk_report_generation_agent = SequentialAgent(
    name="uk_report_generation_agent",
    description="Generates a comprehensive report on a company.",
    sub_agents=[
        uk_search_companies_agent,
        uk_data_retrieval_agent,
        uk_company_report_creation_agent,
    ],
)

uk_kyc_agent = Agent(
    name="uk_kyc_agent",
    model=model,
    description="Companies House Assistant. Transfers to uk_report_generation_agent for comprehensive company analysis and reports.",
    instruction=UK_KYC_INSTRUCTION,
    sub_agents=[uk_report_generation_agent],
)
