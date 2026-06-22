from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentConfig(BaseSettings):
    """
    Configuration for the Technical Designer Agent.
    """

    default_llm: str = Field(default="gemini-2.5-pro", alias="DEFAULT_LLM")
    spanner_project_id: str | None = Field(
        default=None, alias="SPANNER_PROJECT_ID"
    )
    spanner_instance_id: str | None = Field(
        default=None, alias="SPANNER_INSTANCE_ID"
    )
    spanner_database_id: str | None = Field(
        default=None, alias="SPANNER_DATABASE_ID"
    )

    model_config = SettingsConfigDict(
        env_prefix="AGENT_",
        env_ignore_empty=True,
        env_file=".env",
        env_file_encoding="utf-8",
        cli_parse_args=False,
        extra="ignore",
        populate_by_name=True,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


config = AgentConfig()
