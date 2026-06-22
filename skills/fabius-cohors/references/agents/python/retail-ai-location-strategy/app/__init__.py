import os
import google.auth

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id or "your-default-project")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

from app.agent import root_agent

__all__ = ["root_agent"]
