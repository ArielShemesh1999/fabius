from functools import cached_property

from google import genai
from google.adk.models.google_llm import Gemini
from pydantic import Field


class GeminiWithLocation(Gemini):
    """Subclass of Gemini to ensure location is passed to the internal Client."""

    location: str = Field(default="global", description="Vertex AI location")

    @cached_property
    def api_client(self) -> genai.Client:
        return genai.Client(
            location=self.location,
            http_options=genai.types.HttpOptions(
                headers=self._tracking_headers(),
                retry_options=self.retry_options,
                base_url=self.base_url,
            ),
        )
