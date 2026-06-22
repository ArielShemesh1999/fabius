import hashlib
import logging
import tempfile

import google.auth
import requests
from bs4 import BeautifulSoup
from google.cloud import secretmanager

logger = logging.getLogger("MarketMind")


def get_text_from_url(url):
    try:
        request_header = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }
        response = requests.get(url, headers=request_header)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text(
            strip=True
        )  # Extracts and cleans all text from the HTML
        return text

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return ""


def access_secret_version(project_id, secret_id, version_id="latest"):
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    logger.warning(response.payload.data.decode("UTF-8"))
    # Return the decoded payload.
    return response.payload.data.decode("UTF-8")


def create_temp_credentials_file(credentials_json):
    """
    Writes a JSON object to a temporary file and returns the file path.
    """
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".json"
    ) as temp_file:
        temp_file.write(credentials_json)
    temp_file_path = temp_file.name
    logger.warning(temp_file_path)

    with open(
        temp_file_path, encoding="utf-8"
    ) as f:  # Opens the file in read mode with UTF-8 encoding
        contents = f.read()
        logger.warning(contents)

    return temp_file_path


def get_project_id():
    """Gets the current GCP project ID.

    Returns:
        The project ID as a string.
    """

    try:
        _, project_id = google.auth.default()
        return project_id
    except google.auth.exceptions.DefaultCredentialsError as e:
        print(f"Error: Could not determine the project ID. {e}")
        return None


# def _get_session():
#     from streamlit.runtime import get_instance
#     from streamlit.runtime.scriptrunner import get_script_run_ctx
#     runtime = get_instance()
#     session_id = get_script_run_ctx().session_id
#     session_info = runtime._session_mgr.get_session_info(session_id)
#     if session_info is None:
#         raise RuntimeError("Couldn't get your Streamlit Session object.")
#     return session_info.session


# class ContextFilter(logging.Filter):
#     def filter(self, record):
#         record.user_ip = _get_session().id
#         return super().filter(record)

# def init_logging():
#     # Make sure to instanciate the logger only once
#     # otherwise, it will create a StreamHandler at every run
#     # and duplicate the messages

#     # create a custom logger
#     logger = logging.getLogger("MarketMind")
#     if logger.handlers:  # logger is already setup, don't setup again
#         return
#     logger.propagate = False
#     logger.setLevel(logging.INFO)
#     # in the formatter, use the variable "user_ip"
#     formatter = logging.Formatter("[%(name)s:%(user_ip)s] %(levelname)s - %(message)s")
#     handler = logging.StreamHandler()
#     handler.setLevel(logging.INFO)
#     handler.addFilter(ContextFilter())
#     handler.setFormatter(formatter)
#     logger.addHandler(handler)


def get_md5_hash(text):
    """Calculates the MD5 hash of a given text string.

    Args:
      text: The input string.

    Returns:
      The hexadecimal representation of the MD5 hash.
    """
    m = hashlib.md5()
    m.update(text.encode("utf-8"))  # Encode the string to bytes using UTF-8
    return m.hexdigest()


# def get_currentdate():
#     return {'current_date': f"""{datetime.date.today()}"""}

# function_handler = {
#     "current_date": get_currentdate,
# }
