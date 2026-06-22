# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tool for executing SQL queries on BigQuery database"""

import json
import logging

import google.api_core.exceptions
import google.auth.exceptions
from google.cloud import bigquery

from ..config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    bigquery_client = bigquery.Client(
        project=config.project_id
    )  # Initialize client once
except google.auth.exceptions.DefaultCredentialsError as e:
    logger.error(f"Error initializing BigQuery client: {e}")
    bigquery_client = None
except google.api_core.exceptions.GoogleAPICallError as e:
    logger.error(f"BigQuery API error initializing client: {e}")
    bigquery_client = None


def execute_sql_query(sql_query: str) -> str:
    """
    Executes a generated SQL query against BigQuery and returns the result.

    Args:
        sql_query (str): The SQL query to execute.

    Returns:
        str: A JSON containing the query results.
    """
    if not bigquery_client:
        return json.dumps(
            {"error": "BigQuery client is not initialized."}, indent=2
        )
    logger.info(f"Executing SQL query:\n{sql_query}")
    try:
        query_job = bigquery_client.query_and_wait(sql_query)
        results_df = query_job.to_dataframe()
        return json.dumps(
            results_df.to_dict(orient="records"), indent=2, default=str
        )
    except google.api_core.exceptions.GoogleAPICallError as e:
        return json.dumps({"error": f"BigQuery API error: {e}"}, indent=2)


def load_table_schema() -> str:
    """
    Loads the table schema from BigQuery.
    """
    if not bigquery_client:
        return "[Table schema not available - Client not initialized]"
    table_schema = None
    try:
        table_id = f"{config.project_id}.{config.dataset_id}.{config.table_id}"
        table = bigquery_client.get_table(table=table_id)

        schema_info = [
            f"{field.name}:{field.field_type}" for field in table.schema
        ]
        table_schema = f"Schema for `{table_id}`:\n\n{', '.join(schema_info)}"
        logger.error(f"Loaded the table schema {table_schema}\n")
    except google.api_core.exceptions.GoogleAPICallError as e:
        logger.error(f"BigQuery API error loading table schema: {e}\n")
        table_schema = "[Table schema not available - API Error]"

    return table_schema
