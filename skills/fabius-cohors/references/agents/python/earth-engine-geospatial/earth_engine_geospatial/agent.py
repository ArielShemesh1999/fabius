"""An Earth Engine enabled agent."""

import functools
import logging
import os

import ee
import google
from google.adk.agents import llm_agent

from . import prompt, tools

_PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")


@functools.cache
def _initialize_earth_engine():
    """Initializes the Earth Engine client exactly once."""
    try:
        if not _PROJECT_ID:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT environment variable not set."
            )

        scopes = [
            "https://www.googleapis.com/auth/earthengine",
            "https://www.googleapis.com/auth/cloud-platform",
        ]
        credentials, _ = google.auth.default(scopes=scopes)

        ee.Initialize(
            credentials,
            project=_PROJECT_ID,
            opt_url="https://earthengine-highvolume.googleapis.com",
        )
        logging.info(
            "Earth Engine initialized successfully for project: %s", _PROJECT_ID
        )

    except Exception as e:
        logging.exception("Failed to initialize Earth Engine: %s", e)
        raise


_initialize_earth_engine()

root_agent = llm_agent.Agent(
    name="ee_agent",
    model="gemini-2.5-pro",
    description="Agent to answer geo questions using Google Earth Engine.",
    tools=[
        tools.get_2017_2025_annual_changes,
    ],
    instruction=prompt.root_agent_prompt,
)
