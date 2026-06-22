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
"""Selects a product from BigQuery based on a product name."""

import logging
import os

from google.api_core import exceptions as api_exceptions
from google.cloud import bigquery


def select_product_from_bq(product_name: str) -> dict:
    """
    Searches for a product in BigQuery by its name within the search_tags
    array.

    Args:
        product_name (str): The name of the product to search for.

    Returns:
        A dictionary representing the matched product row, or None if no match
        is found.
    """
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    dataset_id = "content_generation"
    table_id = "media_assets"

    client = bigquery.Client()

    # Normalize the product name for consistent searching.
    normalized_product_name = product_name.lower().strip()

    # Construct the query to search for the product name in the
    # search_tags array.
    query = f"""
        SELECT *
        FROM `{project_id}.{dataset_id}.{table_id}`
        WHERE '{normalized_product_name}' IN UNNEST(search_tags)
    """

    try:
        query_job = client.query(query)
        results = query_job.result()

        for row in results:
            return dict(row)

    except api_exceptions.GoogleAPICallError as e:
        logging.error("An error occurred: %s", e)
        return None

    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    product = select_product_from_bq("power drill")
    if product:
        logging.info("Found product:")
        logging.info(product)
    else:
        logging.info("Product not found.")
