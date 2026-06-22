# Copyright 2025 Google LLC
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

"""This module provides a set of tools for interacting with Google BigQuery.

It includes functionalities for checking dataset and table existence, retrieving
table schemas and data previews, validating dataset and table names, querying
information schema, finding relevant datasets, and validating data within tables
based on user-defined rules.
"""

import json
from typing import Any

from google.cloud import bigquery

from ..config import config


def get_bigquery_client() -> bigquery.Client:
    """Get a configured BigQuery client."""
    return bigquery.Client(project=config.project_id)


def bigquery_job_details_tool(job_id: str) -> dict[str, Any]:
    """Retrieve details of a BigQuery job.

    Args:
        job_id (str): The ID of the BigQuery job.

    Returns:
        Dict[str, Any]: Job details including query and error information.
    """
    client = get_bigquery_client()
    try:
        job = client.get_job(job_id)
        query = job.query if isinstance(job, bigquery.QueryJob) else "N/A"
        errors = job.error_result

        return {
            "query": query,
            "status": job.state,
            "error": errors["message"] if errors else None,
            "created": job.created.isoformat(),
            "started": job.started.isoformat() if job.started else None,
            "ended": job.ended.isoformat() if job.ended else None,
        }
    except Exception as e:
        return {"error": f"Error getting job details: {e}"}


def get_udf_sp_tool(dataset_id: str, routine_type: str | None = None) -> str:
    """Retrieve UDFs and Stored Procedures from a BigQuery dataset.

    Args:
        dataset_id (str): The dataset ID to search.
        routine_type (Optional[str]): Filter by routine type ('FUNCTION' or
          'PROCEDURE').

    Returns:
        str: JSON string containing routine information.
    """
    client = get_bigquery_client()

    query = f"""
        SELECT 
            routine_name,
            routine_type,
            routine_body,
            specific_name,
            ddl,
            routine_definition,
            created,
            last_modified
        FROM `{config.project_id}.{dataset_id}.INFORMATION_SCHEMA.ROUTINES`
        {f"WHERE routine_type = '{routine_type}'" if routine_type else ""}
        ORDER BY routine_type, routine_name
    """

    try:
        query_job = client.query(query)
        results = query_job.result()
        routine_info_list = [dict(row.items()) for row in results]

        if not routine_info_list:
            return json.dumps(
                {
                    "message": (
                        f"No {'UDFs' if routine_type == 'FUNCTION' else 'Stored Procedures' if routine_type == 'PROCEDURE' else 'routines'} found"
                        f" in dataset '{dataset_id}'."
                    )
                },
                indent=2,
            )

        return json.dumps(routine_info_list, indent=2, default=str)

    except Exception as e:
        return json.dumps(
            {
                "error": (
                    f"Error retrieving routines from dataset '{dataset_id}': {e}"
                )
            },
            indent=2,
        )


def validate_table_data(
    dataset_id: str, table_id: str, rules: list[dict[str, Any]]
) -> dict[str, Any]:
    """Validate data in a BigQuery table against specified rules.

    Args:
        dataset_id (str): The dataset ID.
        table_id (str): The table ID.
        rules (List[Dict[str, Any]]): List of validation rules.

    Returns:
        Dict[str, Any]: Validation results.
    """
    client = get_bigquery_client()
    validation_results = []

    for rule in rules:
        try:
            column = rule["column"]
            rule_type = rule["type"]
            value = rule.get("value")

            if rule_type == "not_null":
                query = f"""
                    SELECT COUNT(*) as null_count
                    FROM `{config.project_id}.{dataset_id}.{table_id}`
                    WHERE {column} IS NULL
                """
            elif rule_type == "unique":
                query = f"""
                    SELECT {column}, COUNT(*) as count
                    FROM `{config.project_id}.{dataset_id}.{table_id}`
                    GROUP BY {column}
                    HAVING COUNT(*) > 1
                """
            elif rule_type == "value":
                query = f"""
                    SELECT COUNT(*) as invalid_count
                    FROM `{config.project_id}.{dataset_id}.{table_id}`
                    WHERE {column} != {value}
                """
            else:
                validation_results.append(
                    {
                        "rule": rule,
                        "status": "error",
                        "message": f"Unknown rule type: {rule_type}",
                    }
                )
                continue

            query_job = client.query(query)
            results = query_job.result()
            row = next(iter(results))

            validation_results.append(
                {
                    "rule": rule,
                    "status": "pass" if row[0] == 0 else "fail",
                    "details": dict(row.items()),
                }
            )

        except Exception as e:
            validation_results.append(
                {"rule": rule, "status": "error", "message": str(e)}
            )

    return {
        "dataset": dataset_id,
        "table": table_id,
        "validations": validation_results,
    }


def sample_table_data_tool(
    dataset_id: str,
    table_id: str,
    sample_size: int = 10,
    random_seed: int | None = None,
) -> str:
    """Sample data from a BigQuery table using RAND() function.

    Args:
        dataset_id (str): The dataset ID.
        table_id (str): The table ID.
        sample_size (int): Number of rows to sample. Defaults to 10.
        random_seed (Optional[int]): Seed for random sampling. If provided,
          ensures reproducible results.

    Returns:
        str: JSON string containing sampled data.
    """
    try:
        client = get_bigquery_client()

        # Build the query with optional random seed
        seed_clause = (
            f"SET @seed = {random_seed};" if random_seed is not None else ""
        )
        query = f"""
            {seed_clause}
            SELECT *
            FROM `{config.project_id}.{dataset_id}.{table_id}`
            ORDER BY {"RAND(@seed)" if random_seed is not None else "RAND()"}
            LIMIT {sample_size}
        """

        query_job = client.query(query)
        results = query_job.result()

        # Convert results to list of dictionaries
        sample_data = [dict(row.items()) for row in results]

        return json.dumps(
            {
                "status": "success",
                "dataset": dataset_id,
                "table": table_id,
                "sample_size": sample_size,
                "random_seed": random_seed,
                "data": sample_data,
            },
            indent=2,
            default=str,
        )

    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)
