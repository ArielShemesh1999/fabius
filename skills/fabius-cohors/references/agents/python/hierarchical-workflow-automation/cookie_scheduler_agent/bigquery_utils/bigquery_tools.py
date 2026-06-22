"""
BigQuery integration tools for the cookie delivery system using Google ADK first-party toolset.
This file implements BigQuery connectivity using Google's official ADK BigQuery tools.
"""

import logging
import os

import google.auth
from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from google.adk.tools.tool_context import ToolContext

# BigQuery Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
DATASET_ID = "cookie_delivery"
ORDERS_TABLE = "orders"


# Initialize the ADK BigQuery Toolset
def get_bigquery_toolset() -> BigQueryToolset:
    """
    Create and configure the ADK BigQuery toolset.
    Uses Application Default Credentials for authentication.
    """
    try:
        # Tool configuration - allows write operations for order management
        tool_config = BigQueryToolConfig(write_mode=WriteMode.ALLOWED)

        # Use Application Default Credentials (most common for production)
        application_default_credentials, _ = google.auth.default()

        # Create credentials config for ADC
        credentials_config = BigQueryCredentialsConfig(
            credentials=application_default_credentials
        )

        # Initialize the BigQuery toolset
        bigquery_toolset = BigQueryToolset(
            credentials_config=credentials_config,
            bigquery_tool_config=tool_config,
        )

        logging.info("ADK BigQuery toolset initialized successfully")
        return bigquery_toolset

    except Exception as e:
        logging.error(f"Failed to initialize BigQuery toolset: {e}")
        return None


# Helper functions for the cookie delivery agent using ADK tools
def get_latest_order_from_bigquery(tool_context: ToolContext) -> dict:
    """
    Fetch the latest order with 'order_placed' status from BigQuery using ADK tools.
    This is a wrapper function that uses the ADK execute_sql tool.
    """
    logging.info("Fetching latest order from BigQuery using ADK toolset...")

    try:
        # The ADK toolset will be available in the agent's tools
        # This function provides the SQL query logic for the agent to use

        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{ORDERS_TABLE}`
        WHERE order_status = 'order_placed'
        ORDER BY created_at DESC
        LIMIT 1
        """

        # Return the query for the agent to execute using ADK execute_sql tool
        # The agent will handle the actual execution through the toolset
        return {
            "status": "query_ready",
            "query": query,
            "instruction": "Execute this query using the execute_sql tool to get the latest order",
            "expected_result": "order_data",
        }

    except Exception as e:
        logging.error(f"Error preparing BigQuery query: {e}")
        return {
            "status": "error",
            "message": f"Query preparation error: {e!s}",
        }


# Note: This function has been simplified to work with ADK toolset.
# The actual execution should be done through the ADK execute_sql tool.
def update_order_status_in_bigquery(
    tool_context: ToolContext, order_number: str, new_status: str
) -> dict:
    """
    Generate SQL to update order status in BigQuery using ADK tools.
    This function now returns SQL for execution by the ADK toolset instead of executing directly.
    """
    logging.info(
        f"Preparing order status update for {order_number} to {new_status}..."
    )

    try:
        query = f"""
        UPDATE `{PROJECT_ID}.{DATASET_ID}.{ORDERS_TABLE}`
        SET order_status = '{new_status}', 
            updated_at = CURRENT_TIMESTAMP()
        WHERE order_number = '{order_number}'
        """

        return {
            "status": "query_ready",
            "query": query,
            "instruction": f"Execute this query to update order {order_number} status to {new_status}",
            "order_number": order_number,
            "new_status": new_status,
        }

    except Exception as e:
        logging.error(f"Error preparing update query: {e}")
        return {"status": "error", "message": f"Update query error: {e!s}"}


def get_order_analytics_query(
    tool_context: ToolContext, days: int = 30
) -> dict:
    """
    Generate analytics query for BigQuery using ADK tools.
    """
    logging.info(f"Preparing analytics query for last {days} days...")

    try:
        query = f"""
        SELECT 
            order_status,
            COUNT(*) as order_count,
            AVG(total_amount) as avg_order_value,
            SUM(total_amount) as total_revenue
        FROM `{PROJECT_ID}.{DATASET_ID}.{ORDERS_TABLE}`
        WHERE DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
        GROUP BY order_status
        ORDER BY order_count DESC
        """

        return {
            "status": "query_ready",
            "query": query,
            "instruction": f"Execute this query to get order analytics for the last {days} days",
            "days": days,
        }

    except Exception as e:
        logging.error(f"Error preparing analytics query: {e}")
        return {
            "status": "error",
            "message": f"Analytics query error: {e!s}",
        }


def get_dataset_setup_queries() -> list[dict]:
    """
    Generate queries to set up the BigQuery dataset and tables.
    """
    queries = []

    # Create dataset query
    dataset_query = f"""
    CREATE SCHEMA IF NOT EXISTS `{PROJECT_ID}.{DATASET_ID}`
    OPTIONS (
        description = 'Cookie delivery order management dataset',
        location = 'US'
    )
    """

    queries.append(
        {
            "description": "Create cookie_delivery dataset",
            "query": dataset_query,
        }
    )

    # Create orders table query
    table_query = f"""
    CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{DATASET_ID}.{ORDERS_TABLE}` (
        order_id STRING NOT NULL,
        order_number STRING NOT NULL,
        customer_email STRING NOT NULL,
        customer_name STRING NOT NULL,
        customer_phone STRING,
        order_items ARRAY<STRUCT<
            item_name STRING,
            quantity INT64,
            unit_price FLOAT64
        >>,
        delivery_address STRUCT<
            street STRING,
            city STRING,
            state STRING,
            zip_code STRING,
            country STRING
        >,
        delivery_location STRING,
        delivery_request_date DATE,
        delivery_time_preference STRING,
        order_status STRING NOT NULL,
        total_amount FLOAT64,
        order_date TIMESTAMP,
        special_instructions STRING,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
    CLUSTER BY order_status
    """

    queries.append(
        {
            "description": "Create orders table with proper schema",
            "query": table_query,
        }
    )

    # Sample data insertion queries
    sample_orders = [
        {
            "order_id": "ORD12345",
            "order_number": "ORD12345",
            "customer_email": "john.doe@example.com",
            "customer_name": "John Doe",
            "customer_phone": "+1-555-0123",
            "delivery_location": "123 Main St, Anytown, CA 12345, USA",
            "delivery_request_date": "2025-09-16",
            "delivery_time_preference": "morning",
            "order_status": "order_placed",
            "total_amount": 63.50,
            "special_instructions": "Please ring doorbell twice",
        },
        {
            "order_id": "ORD12346",
            "order_number": "ORD12346",
            "customer_email": "jane.smith@example.com",
            "customer_name": "Jane Smith",
            "customer_phone": "+1-555-0124",
            "delivery_location": "456 Oak Ave, Springfield, CA 67890, USA",
            "delivery_request_date": "2025-09-17",
            "delivery_time_preference": "afternoon",
            "order_status": "order_placed",
            "total_amount": 99.00,
            "special_instructions": "Leave at front door",
        },
    ]

    for order in sample_orders:
        insert_query = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET_ID}.{ORDERS_TABLE}` 
        (order_id, order_number, customer_email, customer_name, customer_phone,
         order_items, delivery_address, delivery_location, delivery_request_date,
         delivery_time_preference, order_status, total_amount, order_date,
         special_instructions, created_at, updated_at)
        VALUES (
            '{order["order_id"]}',
            '{order["order_number"]}', 
            '{order["customer_email"]}',
            '{order["customer_name"]}',
            '{order["customer_phone"]}',
            [STRUCT('Chocolate Chip' as item_name, 12 as quantity, 2.50 as unit_price),
             STRUCT('Oatmeal Raisin' as item_name, 6 as quantity, 2.75 as unit_price)],
            STRUCT(
                '123 Main St' as street,
                'Anytown' as city, 
                'CA' as state,
                '12345' as zip_code,
                'USA' as country
            ),
            '{order["delivery_location"]}',
            DATE('{order["delivery_request_date"]}'),
            '{order["delivery_time_preference"]}',
            '{order["order_status"]}',
            {order["total_amount"]},
            CURRENT_TIMESTAMP(),
            '{order["special_instructions"]}',
            CURRENT_TIMESTAMP(),
            CURRENT_TIMESTAMP()
        )
        """

        queries.append(
            {
                "description": f"Insert sample order {order['order_number']}",
                "query": insert_query,
            }
        )

    return queries


# Note: Legacy compatibility functions have been removed.
# The ADK BigQuery toolset provides all necessary functionality through:
# - list_dataset_ids
# - get_dataset_info
# - list_table_ids
# - get_table_info
# - execute_sql
# - ask_data_insights
#
# For environment setup, use create_bigquery_environment.py script.
