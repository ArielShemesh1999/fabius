import math
import os

import sec_api

from ....shared_libraries import helpercode

PROJECT_ID = helpercode.get_project_id()
try:
    SEC_API_KEY = helpercode.access_secret_version(PROJECT_ID, "SECAPIKey")
except Exception as e:
    SEC_API_KEY = None
    print(f"Warning: Failed to access SECAPIKey secret: {e}")


def flatten_filing(filing):
    """
    Flatten nested filing data for non-derivative transactions.
    """
    base_data = {
        "periodOfReport": filing.get("periodOfReport", "N/A"),
        "issuerCik": filing.get("issuer", {}).get("cik", "N/A"),
        "issuerTicker": filing.get("issuer", {}).get("tradingSymbol", "N/A"),
        "reportingOwner": filing.get("reportingOwner", {}).get("name", "N/A"),
        "filedAt": filing.get("filedAt", "N/A"),
    }
    Transactions = []

    # Process non-derivative transactions (most common stock buys/sells)
    if (
        "nonDerivativeTable" in filing
        and "transactions" in filing["nonDerivativeTable"]
    ):
        for transaction in filing["nonDerivativeTable"]["transactions"]:
            amounts = transaction.get("amounts", {})
            post_amounts = transaction.get("postTransactionAmounts", {})
            coding = transaction.get("coding", {})

            shares = amounts.get("shares", 0)
            price = amounts.get("pricePerShare", 0)

            # Handle potential None values or missing keys
            shares = shares if shares is not None else 0
            price = price if price is not None else 0

            entry = {
                "securityTitle": transaction.get("securityTitle", "N/A"),
                "codingCode": coding.get("code", "N/A"),
                "acquiredDisposed": amounts.get("acquiredDisposedCode", "N/A"),
                "shares": shares,
                "sharePrice": price,
                "total": math.ceil(shares * price),
                "sharesOwnedFollowingTransaction": post_amounts.get(
                    "sharesOwnedFollowingTransaction", "N/A"
                ),
            }
            Transactions.append({**base_data, **entry})
    return Transactions


def flatten_filings(filings):
    """
    Flatten a list of filings.
    """
    unflattened_list = list(map(flatten_filing, filings))
    return [item for sublist in unflattened_list for item in sublist]


def get_insider_transactions(
    ticker: str, start_date: str | None = None, end_date: str | None = None
) -> str:
    """
    Retrieve insider trading transactions (Forms 3, 4, 5) for a specific company.

    Args:
        ticker: The stock ticker symbol (e.g., "AAPL").
        start_date: Optional. Start date in YYYY-MM-DD format.
        end_date: Optional. End date in YYYY-MM-DD format.

    Returns:
        A formatted string summarizing the insider transactions.
    """
    if os.environ.get("MOCK_SEC_API") == "true":
        return "Found 2 insider transactions (Mock Mode):\n- 2026-02-01: Elon Musk Disposed 1000 shares of Common Stock at $200 (Total: $200000)\n- 2026-03-01: Drew Baglino Acquired 500 shares of Common Stock at $190 (Total: $95000)\n"

    insider_api = sec_api.InsiderTradingApi(api_key=SEC_API_KEY)

    query = f"issuer.tradingSymbol:{ticker}"
    if start_date and end_date:
        query += f" AND filedAt:[{start_date} TO {end_date}]"
    elif start_date:
        query += f" AND filedAt:[{start_date} TO 9999-12-31]"
    elif end_date:
        query += f" AND filedAt:[0000-01-01 TO {end_date}]"

    search_query = {
        "query": query,
        "from": "0",
        "size": "50",
        "sort": [{"filedAt": {"order": "desc"}}],
    }

    try:
        response = insider_api.get_data(search_query)
        filings = response.get("transactions", [])

        if not filings:
            return f"No insider transactions found for ticker {ticker}."

        processed_data = flatten_filings(filings)

        if not processed_data:
            return f"Found {len(filings)} filings for {ticker}, but no non-derivative transactions found in them."

        result = f"Found {len(processed_data)} insider transactions (showing up to top 10):\n"
        for _, trade in enumerate(processed_data[:10]):
            reporting_person = trade.get("reportingOwner", "Unknown")
            security = trade.get("securityTitle", "Unknown Security")
            action = (
                "Acquired"
                if trade.get("acquiredDisposed") == "A"
                else "Disposed"
            )
            shares = trade.get("shares", 0)
            price = trade.get("sharePrice", 0)
            total = trade.get("total", 0)
            filed_at = trade.get("filedAt", "Unknown Date")

            result += f"- {filed_at}: {reporting_person} {action} {shares} shares of {security} at ${price} (Total: ${total})\n"

        return result
    except Exception as e:
        return f"Error executing insider trading search: {e}"
