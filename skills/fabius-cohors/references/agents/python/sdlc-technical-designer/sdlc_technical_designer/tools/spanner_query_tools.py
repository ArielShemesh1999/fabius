import google.auth
from google.adk.tools.spanner import SpannerToolset
from google.adk.tools.spanner.settings import Capabilities, SpannerToolSettings
from google.adk.tools.spanner.spanner_credentials import (
    SpannerCredentialsConfig,
)


class SpannerQueryTools:
    @classmethod
    def get_toolset(cls) -> list:
        """
        Provides a list containing the available SpannerToolset to be consumed by an agent
        """
        return [
            SpannerToolset(
                credentials_config=cls.get_credentials_config(),
                spanner_tool_settings=cls.get_tool_settings(),
            )
        ]

    @staticmethod
    def get_tool_settings():
        tool_settings = SpannerToolSettings(
            capabilities=[Capabilities.DATA_READ],
        )
        return tool_settings

    @staticmethod
    def get_credentials_config():
        application_default_credentials, _ = google.auth.default()
        credentials_config = SpannerCredentialsConfig(
            credentials=application_default_credentials,
        )
        return credentials_config
