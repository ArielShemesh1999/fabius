from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.workflow.events.request_input import RequestInput
from google.adk.agents.workflow.workflow_agent import WorkflowAgent
from google.adk.agents.workflow.workflow_context import Context
from google.genai.types import UserContent
from pydantic import BaseModel


# --- Data classes ---
class ActivitiesList(BaseModel):
    """Itinerary should be a list of dictionaries for each activity. Each
    activity has a name and a description"""

    itinerary: list[dict[str, str]]


# --- Agents ---
concierge_agent = LlmAgent(
    name="concierge_agent",
    model="gemini-2.5-flash",
    instruction="""
        You are the concierge agent as part of a larger workflow that 
        incorporates the users inputs: {node_input} and returns a list of activities an 
        accordance with those inputs. The input needs to contain at LEAST a 
        place. If there is no place given, then re-prompt the user for their
        desired place in question specifically. 

        If the user gives you more details about themselves then take those into 
        account when compiling a list of activities to do for the user.
    """,
    output_schema=ActivitiesList,
)


# --- Functions ---
async def initial_prompt(ctx: Context):
    """
    Gives the user the initial prompt that faces the user
    """
    input_message = """
        This is an interactive concierge workflow tasked with making you a great
        itinerary for you in your city of choice. If you give some details about 
        yourself or what you are generally looking for I can better personalize 
        your itinerary.
        For example, input your:
            City (Required),
            Age,
            Hobby,
            Example of attraction you liked
    """
    resp = {"user response": str}

    yield RequestInput(message=input_message, response_schema=resp)


async def get_user_feedback(node_input: ActivitiesList):
    """
    Retrieves the user's thoughts on the agents initial itinerary in order to
    either expand on, change the list, or exit the loop
    """
    message = f"""
        Here is your recommended base itinerary:\n{node_input}\n\n
        Which of these items appeal to you (if any)?
        """

    yield RequestInput(
        message=message,
        payload=node_input,
        response_schema={"user": "response"},
    )


async def process_feedback(node_input: str):
    yield UserContent(f"Feedback: {node_input}.")


# --- Workflow ---
root_agent = WorkflowAgent(
    name="root_agent",
    rerun_on_resume=True,
    edges=[
        (
            "START",
            initial_prompt,
            concierge_agent,
            get_user_feedback,
            process_feedback,
        ),
        (process_feedback, concierge_agent),
    ],
)
