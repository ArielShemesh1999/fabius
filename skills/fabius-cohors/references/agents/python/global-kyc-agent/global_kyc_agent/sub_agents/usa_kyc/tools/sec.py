import os

import sec_api
from google.adk.tools.function_tool import FunctionTool

from ....shared_libraries import helpercode

MAX_SECTION_LENGTH = 8000

PROJECT_ID = helpercode.get_project_id()
try:
    SEC_API_KEY = helpercode.access_secret_version(PROJECT_ID, "SECAPIKey")
except Exception as e:
    SEC_API_KEY = None
    print(f"Warning: Failed to access SECAPIKey secret: {e}")


def full_text_search(query: str, start_date: str, end_date: str) -> str:
    """
    Search the full text of SEC filings (like 10-K, 10-Q, 8-K) for a specific query string within a date range.

    Args:
        query: The phrase or topic to search for (e.g., "artificial intelligence", "supply chain").
        start_date: Start date for the search in YYYY-MM-DD format.
        end_date: End date for the search in YYYY-MM-DD format.

    Returns:
        A formatted string summarizing the matching filings.
    """
    if os.environ.get("MOCK_SEC_API") == "true":
        return "Found 2 filings (Mock Mode):\n- Tesla, Inc. (TSLA) filed a 10-K on 2026-01-01\n- Tesla, Inc. (TSLA) filed a 10-Q on 2026-04-01\n"

    search_api = sec_api.FullTextSearchApi(api_key=SEC_API_KEY)

    search_query = {
        "query": query,
        "formTypes": ["8-K", "10-Q", "10-K"],
        "startDate": f"{start_date}T00:00:00.000Z",
        "endDate": f"{end_date}T23:59:59.000Z",
    }

    try:
        response = search_api.get_filings(search_query)
        filings = response.get("filings", [])

        if not filings:
            return f"No filings found for query '{query}' between {start_date} and {end_date}."

        result = f"Found {len(filings)} filings (showing up to top 5):\n"
        for _, filing in enumerate(filings[:5]):
            company_name = filing.get("companyNameShort", "Unknown Company")
            ticker = filing.get("ticker", "N/A")
            form_type = filing.get("formType", "Unknown Form")
            filed_at = filing.get("filedAt", "Unknown Date")
            result += f"- {company_name} ({ticker}) filed a {form_type} on {filed_at}\n"

        return result
    except Exception as e:
        return f"Error executing full text search: {e}"


def get_recent_filings(ticker: str, form_type: str = "10-K") -> str:
    """
    Retrieve metadata for the most recent SEC filing of a specific type for a given company.

    Args:
        ticker: The stock ticker symbol of the company (e.g., "AAPL").
        form_type: The type of SEC form to retrieve (e.g., "10-K", "10-Q", "8-K"). Defaults to "10-K".

    Returns:
        A string containing the filing URL and exact document URL if found.
    """
    if os.environ.get("MOCK_SEC_API") == "true":
        return f"Found recent {form_type} for {ticker} filed on 2026-01-01.\nURL: https://www.sec.gov/Archives/edgar/data/1318605/000162828024002390/tsla-20231231.htm"

    query_api = sec_api.QueryApi(api_key=SEC_API_KEY)

    query = {
        "query": {
            "query_string": {
                "query": f'ticker:{ticker} AND formType:"{form_type}"'
            }
        },
        "from": "0",
        "size": "5",
        "sort": [{"filedAt": {"order": "desc"}}],
    }

    try:
        response = query_api.get_filings(query)
        filings = response.get("filings", [])
        if not filings:
            return f"No {form_type} filings found for ticker {ticker}."

        latest_filing = filings[0]
        link_to_filing = latest_filing.get(
            "linkToFilingDetails", "Not Available"
        )
        filed_at = latest_filing.get("filedAt", "Unknown Date")

        result = f"Found recent {form_type} for {ticker} filed on {filed_at}.\nURL: {link_to_filing}"
        return result

    except Exception as e:
        return f"Error querying filings for {ticker}: {e}"


def extract_filing_section(filing_url: str, section: str = "1A") -> str:
    """
    Extract a specific section from an SEC filing. This is especially useful for 10-K filings.

    Args:
        filing_url: The exact URL of the SEC filing details (e.g., from `get_recent_filings`).
        section: The section id to extract (e.g., '1A' for Risk Factors, '7' for Management Discussion). Defaults to '1A'.

    Returns:
        A string containing the extracted text.
    """
    if os.environ.get("MOCK_SEC_API") == "true":
        if section == "1A":
            return """--- START OF SECTION 1A ---
Item 1A. Risk Factors

We face many risks. Here are the big ones:

1. Key Personnel: We depend on Elon Musk. If he leaves or is distracted, we are in trouble.
2. Competition: The EV market is crowded. Legacy automakers and new players are aggressive.
3. Supply Chain: We need batteries and chips. Disruption hurts production.

...
--- END OF SECTION 1A ---"""
        elif section == "7":
            return """--- START OF SECTION 7 ---
Item 7. Management Discussion

We are doing well but face risks.
...
--- END OF SECTION 7 ---"""
        else:
            return f"--- START OF SECTION {section} ---\nMock content for section {section}\n--- END OF SECTION {section} ---"

    extractor_api = sec_api.ExtractorApi(api_key=SEC_API_KEY)

    try:
        section_text = extractor_api.get_section(filing_url, section, "text")

        # Truncate if it's exceedingly long
        if len(section_text) > MAX_SECTION_LENGTH:
            section_text = (
                section_text[:MAX_SECTION_LENGTH] + "\n...[Text Truncated]..."
            )

        return f"--- START OF SECTION {section} ---\n{section_text}\n--- END OF SECTION {section} ---"
    except Exception as e:
        return f"Error extracting section {section} from URL {filing_url}: {e}"


full_text_search = FunctionTool(full_text_search)
get_recent_filings = FunctionTool(get_recent_filings)
extract_filing_section = FunctionTool(extract_filing_section)
