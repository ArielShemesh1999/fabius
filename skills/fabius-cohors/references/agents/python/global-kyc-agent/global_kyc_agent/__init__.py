import os
import sys

import google.auth
from dotenv import load_dotenv

load_dotenv()

_, project_id = google.auth.default()
if project_id:
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# Ensure the parent directory is in sys.path to allow absolute imports like 'from global_kyc_agent...'
package_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(package_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from . import agent as agent  # noqa: E402
