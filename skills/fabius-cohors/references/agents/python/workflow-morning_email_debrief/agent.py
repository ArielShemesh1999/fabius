from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.workflow.events.event import Event
from google.adk.agents.workflow.workflow_agent import WorkflowAgent
from googleapiclient.discovery import build


# --- Functions ---
def retrieve_and_list_emails(max_results: int = 5):
    """
    Fetches the latest emails from the user's inbox and returns their snippets.
    Args:
        max_results: The number of recent emails to retrieve.
    """
    # Note: Requires valid OAuth credentials in your environment
    service = build("gmail", "v1")
    results = (
        service.users()
        .messages()
        .list(userId="me", maxResults=max_results)
        .execute()
    )
    messages = results.get("messages", [])

    summaries = []
    for msg in messages:
        txt = (
            service.users().messages().get(userId="me", id=msg["id"]).execute()
        )
        summaries.append(f"Subject: {txt['snippet']}")

    result = "".join(summaries)
    yield Event(data={"emails": result})


# --- Subagents ---
format_news_agent = LlmAgent(
    name="format_news_agent",
    model="gemini-2.5-flash",
    instruction="""
        Take in the given emails from the user's inbox and distill them into 
        bullet point summaries to catch the user up on their important updates

        Emails: {node_input}
    """,
)

# --- Workflow Agent ---
root_agent = WorkflowAgent(
    name="root_agent",
    edges=[
        ("START", retrieve_and_list_emails, format_news_agent),
    ],
)
