import json

with open(
    "/Users/sgardezi/work/projects/kyc-agent-adk/eval/global_kyc.test.json"
) as f:
    eval_set = json.load(f)

# Subset of static tool calls for UK
uk_expected = [
    {"name": "transfer_to_agent", "args": {"agent_name": "uk_kyc_agent"}},
    {
        "name": "transfer_to_agent",
        "args": {"agent_name": "uk_report_generation_agent"},
    },
    {"name": "search_companies", "args": {"search_query": "Tesco"}},
    {"name": "get_company_profile", "args": {"company_number": "00445790"}},
    {"name": "get_company_officers", "args": {"company_number": "00445790"}},
    {"name": "get_company_charges", "args": {"company_number": "00445790"}},
    {
        "name": "get_company_establishments",
        "args": {"company_number": "00445790"},
    },
    {"name": "get_company_exemptions", "args": {"company_number": "00445790"}},
]

# Subset of static tool calls for USA
usa_expected = [
    {"name": "transfer_to_agent", "args": {"agent_name": "usa_kyc_agent"}},
    {
        "name": "transfer_to_agent",
        "args": {"agent_name": "usa_sequential_agent"},
    },
    {"name": "get_recent_filings", "args": {"ticker": "AAPL"}},
    {"name": "get_current_date", "args": {}},
]

for case in eval_set["eval_cases"]:
    if case["eval_id"] == "eval/global_kyc_uk_report_test":
        case["conversation"][0]["intermediate_data"]["tool_uses"] = uk_expected
    elif case["eval_id"] == "eval/global_kyc_usa_report_test":
        case["conversation"][0]["intermediate_data"]["tool_uses"] = usa_expected

with open(
    "/Users/sgardezi/work/projects/kyc-agent-adk/eval/global_kyc.test.json", "w"
) as f:
    json.dump(eval_set, f, indent=2)
