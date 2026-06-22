"""
This module provides functionality to generate dbt model SQL files
from input files stored in Google Cloud Storage using Generative AI.
"""

import logging
import os

import vertexai
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel, Image

from ..constants import MODEL, STORAGE_CLIENT
from ..prompts import PARSING_INSTRUCTIONS

logger = logging.getLogger("plumber-agent")

# IMPORTING ENVIRONMENT VARIABLES FROM .env FILE
load_dotenv()

# ENABLING VERTEX AI
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)


def generate_dbt_model_sql(gcs_url: str) -> dict[str, str | None]:
    """
    Generates a dbt model SQL file from input data stored on Google Cloud Storage (GCS).

    This function performs the following steps:
      - Validates the input GCS URL.
      - Extracts bucket name, project name, file name, and file type from the URL.
      - Downloads the file from GCS.
      - Uses a generative model to convert CSV or image content into SQL code.
      - Uploads the generated SQL back to the appropriate location in the same GCS
        bucket, following dbt project conventions.
      - Adds metadata tags to the uploaded SQL file.

    Args:
        gcs_url (str): A GCS URL pointing to the input file (must start with
          "gs://").

    Returns:
        dict: A dictionary containing:
            - "output_path" (str or None): GCS path of the generated SQL, or None on
              failure.
            - "output_sql" (str or None): The generated SQL code, or None on failure.
            - "result" (str): "SUCCESS" or an error description.

    Raises:
        Does not raise exceptions; errors are caught and returned in the "result" field.
    """
    try:
        if not gcs_url.startswith("gs://"):
            return {"result": "Invalid gcs URL"}

        bucket_name, file_path = gcs_url[5:].split("/", 1)
        dbt_project_name = file_path.split("/")[0]
        file_name = file_path.split("/")[-1].split(".")[0]
        file_type = file_path.split("/")[-1].split(".")[1]

        bucket = STORAGE_CLIENT.bucket(bucket_name)
        blob = bucket.blob(file_path)

        model = GenerativeModel(MODEL)

        if not blob.exists():
            return {"result": "Object not available at input path"}

        file_bytes = blob.download_as_bytes()

        if file_type == "csv":
            file_content = file_bytes.decode("utf-8")
            response = model.generate_content(
                [PARSING_INSTRUCTIONS, file_content]
            )
        else:
            image = Image.from_bytes(file_bytes)
            response = model.generate_content([PARSING_INSTRUCTIONS, image])

        output_sql = response.text.replace("```sql", "").replace("```", "")
        output_blob = bucket.blob(dbt_project_name + f"/models/{file_name}.sql")

        tags = {"author": "dbt_adk_agent"}
        output_blob.metadata = tags

        output_blob.upload_from_string(output_sql, content_type="text/plain")
        return {
            "output_path": f"gs://{bucket_name}/{dbt_project_name}/models/{file_name}.sql",
            "output_sql": output_sql,
            "result": "SUCCESS",
        }
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.error("An error occurred: %s", err, exc_info=True)
        return {
            "output_path": None,
            "output_sql": None,
            "result": f"error - {err!s}",
        }
