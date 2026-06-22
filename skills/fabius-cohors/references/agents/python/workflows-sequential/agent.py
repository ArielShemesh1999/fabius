from datetime import datetime
from zoneinfo import ZoneInfo

from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.workflow.base_node import START
from google.adk.agents.workflow.events.event import Event
from google.adk.agents.workflow.workflow_agent import WorkflowAgent

city_generator_agent = LlmAgent(
    name="city_generator_agent",
    model="gemini-2.5-flash",
    instruction="""Return the name of a random city.
      Return only the name of the city and the continent that its from and 
      nothing else, strictly in this format type: "America/New York". 
    """,
    output_key="city",
)


def lookup_time_function(city: str):
    """Yield the current time in the specified city and save it to the state."""
    time_str = datetime.now(ZoneInfo(f"{city}")).strftime("%H:%M:%S")
    new_city = city.split("/")[1]
    yield Event(data={"time_info": f"{time_str}", "city": new_city})


city_report_agent = LlmAgent(
    name="city_report_agent",
    model="gemini-2.5-flash",
    instruction="""
        Return a sentence of the following format and print it to the user:
        It is {time_info} in {city} right now.
    """,
)

root_agent = WorkflowAgent(
    name="root_agent",
    edges=[
        (START, city_generator_agent, lookup_time_function, city_report_agent)
    ],
)
