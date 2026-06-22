import json

with open(
    "/Users/sgardezi/work/projects/kyc-agent-adk/global_kyc_agent/.adk/eval_history/global_kyc_agent_global_kyc_evals_1774567613.081574.evalset_result.json",
) as f:
    data = json.load(f)

for case in data["eval_case_results"]:
    eval_id = case["eval_id"]
    print(f"\n--- {eval_id} ---")
    events = case["eval_metric_result_per_invocation"][0]["actual_invocation"][
        "intermediate_data"
    ]["invocation_events"]

    tools = []
    for event in events:
        try:
            fc = event["content"]["parts"][0]["function_call"]
            if fc is not None:
                tools.append({"name": fc["name"], "args": fc["args"]})
        except Exception:
            pass

    print(json.dumps(tools, indent=4))
