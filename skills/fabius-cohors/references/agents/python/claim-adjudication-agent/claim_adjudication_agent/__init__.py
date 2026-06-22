"""Health claim advisor: facilitate health insurance claim processing."""

import os

import google.auth

from . import agent

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-east1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
os.environ.setdefault("GEMINI_FLASH", "gemini-2.5-flash")