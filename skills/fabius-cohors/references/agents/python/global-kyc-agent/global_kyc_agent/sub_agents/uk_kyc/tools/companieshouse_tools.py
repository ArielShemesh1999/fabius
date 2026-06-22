import requests
from companieshouse import CompaniesHouseClient

from ....shared_libraries import helpercode

HTTP_NOT_FOUND = 404

PROJECT_ID = helpercode.get_project_id()

try:
    chclient = CompaniesHouseClient(
        api_key=helpercode.access_secret_version(
            PROJECT_ID, "CompaniesHouseAPIKey"
        )
    )
except Exception as e:
    chclient = None
    print(f"Warning: Failed to initialize CompaniesHouseClient: {e}")


def search_companies(search_query: str):
    """
    Searches for companies in the Companies House database based on the given search query.

    Args:
        search_query (str): The search query. Usually a name of a company

    Returns:
        A dictionary containing the search results.
    """
    try:
        return chclient.search_companies(search_query)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == HTTP_NOT_FOUND:
            return {"items": [], "total_results": 0}
        raise
    except Exception as e:
        return {"error": str(e)}


def get_company_profile(company_number: str):
    """
    Gets the profile of a company in the Companies House database based on the given company number.

    Args:
        company_number: The company number of the company. Usaully returned in the company search response

    Returns:
        A dictionary containing the company profile.
    """
    try:
        return chclient.get_company_profile(company_number)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == HTTP_NOT_FOUND:
            return {"error": "Company not found"}
        raise
    except Exception as e:
        return {"error": str(e)}


def get_company_officers(company_number: str):
    """
    Gets the company officers from the Companies House database based on the given company number.

    Args:
        company_number: The company number.

    Returns:
        A dictionary containing the company officers details.
    """
    try:
        return chclient.get_company_officers(company_number)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == HTTP_NOT_FOUND:
            return {"items": [], "total_results": 0}
        raise
    except Exception as e:
        return {"error": str(e)}


def get_company_address(company_number: str):
    """
    Gets the registered office address of a company.

    Args:
        company_number: The company number.

    Returns:
        A dictionary containing the registered office address.
    """
    try:
        return chclient.get_company_registered_office_address(company_number)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == HTTP_NOT_FOUND:
            return {"error": "Address not found"}
        raise
    except Exception as e:
        return {"error": str(e)}


def get_company_establishments(company_number: str):
    """
    Gets the UK establishments of a company.

    Args:
        company_number: The company number.

    Returns:
        A dictionary containing the UK establishments.
    """
    try:
        return chclient.get_company_uk_establishments(company_number)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == HTTP_NOT_FOUND:
            return {"items": []}
        raise
    except Exception as e:
        return {"error": str(e)}


def get_company_registers(company_number: str):
    """
    Gets the company registers.

    Args:
        company_number: The company number.

    Returns:
        A dictionary containing the company registers.
    """
    try:
        return chclient.get_company_registers(company_number)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == HTTP_NOT_FOUND:
            return {"registers": {}}
        raise
    except Exception as e:
        return {"error": str(e)}


def get_company_exemptions(company_number: str):
    """
    Gets the company exemptions.

    Args:
        company_number: The company number.

    Returns:
        A dictionary containing the company exemptions.
    """
    try:
        return chclient.get_company_exemptions(company_number)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == HTTP_NOT_FOUND:
            return {"exemptions": {}}
        raise
    except Exception as e:
        return {"error": str(e)}


def get_company_charges(company_number: str):
    """
    Gets the company charges (mortgages).

    Args:
        company_number: The company number.

    Returns:
        A dictionary containing the company charges.
    """
    try:
        return chclient.get_company_charges(company_number)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == HTTP_NOT_FOUND:
            return {"items": [], "total_count": 0}
        raise
    except Exception as e:
        return {"error": str(e)}


def get_company_insolvency(company_number: str):
    """
    Gets the company insolvency records.

    Args:
        company_number: The company number.

    Returns:
        A dictionary containing the insolvency records.
    """
    try:
        return chclient.get_company_insolvency(company_number)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == HTTP_NOT_FOUND:
            return {"cases": []}
        raise
    except Exception as e:
        return {"error": str(e)}


def get_company_filing_history(company_number: str):
    """
    Gets the company filing history.

    Args:
        company_number: The company number.

    Returns:
        A dictionary containing the filing history.
    """
    try:
        return chclient.get_company_filing_history(company_number)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == HTTP_NOT_FOUND:
            return {"items": [], "total_count": 0}
        raise
    except Exception as e:
        return {"error": str(e)}


def get_company_filing_detail(company_number: str, transaction_id: str):
    """
    Gets the details of a specific company filing.

    Args:
        company_number: The company number.
        transaction_id: The transaction ID.

    Returns:
        A dictionary containing the filing details.
    """
    try:
        return chclient.get_company_filing_detail(
            company_number, transaction_id
        )
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == HTTP_NOT_FOUND:
            return {"error": "Filing not found"}
        raise
    except Exception as e:
        return {"error": str(e)}


def get_corporate_officer_disqualifications(officer_id: str):
    """
    Gets corporate officer disqualifications.

    Args:
        officer_id: The officer ID.

    Returns:
        A dictionary containing the disqualification details.
    """
    try:
        return chclient.get_corporate_officer_disqualifications(officer_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == HTTP_NOT_FOUND:
            return {"disqualifications": []}
        raise
    except Exception as e:
        return {"error": str(e)}


def get_natural_officer_disqualifications(officer_id: str):
    """
    Gets natural officer disqualifications.

    Args:
        officer_id: The officer ID.

    Returns:
        A dictionary containing the disqualification details.
    """
    try:
        return chclient.get_natural_officer_disqualifications(officer_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == HTTP_NOT_FOUND:
            return {"disqualifications": []}
        raise
    except Exception as e:
        return {"error": str(e)}


def get_office_appointments(officer_id: str):
    """
    Gets office appointments for an officer.

    Args:
        officer_id: The officer ID.

    Returns:
        A dictionary containing the appointments.
    """
    try:
        return chclient.get_office_appointments(officer_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == HTTP_NOT_FOUND:
            return {"appointments": []}
        raise
    except Exception as e:
        return {"error": str(e)}
