#!/usr/bin/env python3
"""
BigQuery Environment Setup Script
Creates the dataset, table, and populates sample data for the Cookie Delivery System.
"""

import logging
import os
import sys
from datetime import datetime

# Add the cookie_scheduler_agent directory to Python path
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "cookie_scheduler_agent"
    )
)

try:
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound
except ImportError as e:
    print(f"Error: Google Cloud BigQuery library not found: {e}")
    print("Please install it with: pip install google-cloud-bigquery")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# BigQuery Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
DATASET_ID = "cookie_delivery"
ORDERS_TABLE = "orders"


def create_orders_table(client: bigquery.Client) -> bool:
    """Create the orders table with proper schema."""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{ORDERS_TABLE}"

    try:
        client.get_table(table_id)
        logging.info(f"Table {table_id} already exists.")
        return True
    except NotFound:
        logging.info(f"Creating table {table_id}...")

        schema = [
            bigquery.SchemaField("order_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("order_number", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("customer_email", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("customer_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("customer_phone", "STRING"),
            bigquery.SchemaField(
                "order_items",
                "RECORD",
                mode="REPEATED",
                fields=[
                    bigquery.SchemaField("item_name", "STRING"),
                    bigquery.SchemaField("quantity", "INTEGER"),
                    bigquery.SchemaField("unit_price", "FLOAT"),
                ],
            ),
            bigquery.SchemaField(
                "delivery_address",
                "RECORD",
                fields=[
                    bigquery.SchemaField("street", "STRING"),
                    bigquery.SchemaField("city", "STRING"),
                    bigquery.SchemaField("state", "STRING"),
                    bigquery.SchemaField("zip_code", "STRING"),
                    bigquery.SchemaField("country", "STRING"),
                ],
            ),
            bigquery.SchemaField("delivery_location", "STRING"),
            bigquery.SchemaField("delivery_request_date", "DATE"),
            bigquery.SchemaField("delivery_time_preference", "STRING"),
            bigquery.SchemaField("order_status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("total_amount", "FLOAT"),
            bigquery.SchemaField("order_date", "TIMESTAMP"),
            bigquery.SchemaField("special_instructions", "STRING"),
            bigquery.SchemaField("created_at", "TIMESTAMP"),
            bigquery.SchemaField("updated_at", "TIMESTAMP"),
        ]

        table = bigquery.Table(table_id, schema=schema)
        table.description = (
            "Cookie delivery orders with customer and delivery information"
        )

        try:
            table = client.create_table(table, timeout=30)
            logging.info(
                f"Created table {table.project}.{table.dataset_id}.{table.table_id}"
            )
            return True
        except Exception as e:
            logging.error(f"Failed to create table: {e}")
            return False


def create_dataset(client: bigquery.Client) -> bool:
    """Create the BigQuery dataset if it doesn't exist."""
    dataset_id = f"{PROJECT_ID}.{DATASET_ID}"

    try:
        client.get_dataset(dataset_id)
        logging.info(f"Dataset {dataset_id} already exists.")
        return True
    except NotFound:
        logging.info(f"Creating dataset {dataset_id}...")
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        dataset.description = "Cookie delivery order management system"

        try:
            dataset = client.create_dataset(dataset, timeout=30)
            logging.info(f"Created dataset {dataset.dataset_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to create dataset: {e}")
            return False


def insert_sample_data(client: bigquery.Client, overwrite: bool = True) -> bool:
    """Insert sample data into the orders table."""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{ORDERS_TABLE}"

    try:
        table = client.get_table(table_id)
    except NotFound:
        logging.error(f"Table {table_id} not found")
        return False

    # Check if data already exists
    query = f"SELECT COUNT(*) as count FROM `{table_id}`"
    query_job = client.query(query)
    results = query_job.result()

    for row in results:
        if row.count > 0:
            if overwrite:
                logging.info(
                    f"Table already contains {row.count} rows. For demo, will recreate table to avoid streaming buffer..."
                )

                # Drop and recreate table to avoid streaming buffer issues
                try:
                    client.delete_table(table_id)
                    logging.info("Old table deleted")

                    # Recreate the table
                    create_orders_table(client)
                    logging.info("Table recreated with fresh schema")

                except Exception as recreate_error:
                    logging.warning(
                        f"Could not recreate table: {recreate_error}"
                    )
                    logging.info("Proceeding with existing table...")
            else:
                logging.info(
                    f"Table already contains {row.count} rows. Skipping sample data insertion."
                )
                return True

    # Sample data to insert
    current_time = datetime.now().isoformat()
    sample_orders = [
        {
            "order_id": "ORD12345",
            "order_number": "ORD12345",
            "customer_email": "johnlara@google.com",
            "customer_name": "John Doe",
            "customer_phone": "+1-555-0123",
            "order_items": [
                {
                    "item_name": "Chocolate Chip",
                    "quantity": 12,
                    "unit_price": 2.50,
                },
                {
                    "item_name": "Oatmeal Raisin",
                    "quantity": 6,
                    "unit_price": 2.75,
                },
                {
                    "item_name": "Snickerdoodle",
                    "quantity": 12,
                    "unit_price": 2.60,
                },
            ],
            "delivery_address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "12345",
                "country": "USA",
            },
            "delivery_location": "123 Main St, Anytown, CA 12345, USA",
            "delivery_request_date": "2025-09-10",
            "delivery_time_preference": "morning",
            "order_status": "order_placed",
            "total_amount": 63.50,
            "order_date": current_time,
            "special_instructions": "Please ring doorbell twice",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "order_id": "ORD12346",
            "order_number": "ORD12346",
            "customer_email": "jane.smith@example.com",
            "customer_name": "Jane Smith",
            "customer_phone": "+1-555-0124",
            "order_items": [
                {
                    "item_name": "Double Chocolate",
                    "quantity": 24,
                    "unit_price": 3.00,
                },
                {
                    "item_name": "Sugar Cookie",
                    "quantity": 12,
                    "unit_price": 2.25,
                },
            ],
            "delivery_address": {
                "street": "456 Oak Ave",
                "city": "Springfield",
                "state": "CA",
                "zip_code": "67890",
                "country": "USA",
            },
            "delivery_location": "456 Oak Ave, Springfield, CA 67890, USA",
            "delivery_request_date": "2025-09-11",
            "delivery_time_preference": "afternoon",
            "order_status": "order_placed",
            "total_amount": 99.00,
            "order_date": current_time,
            "special_instructions": "Leave at front door",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "order_id": "ORD12347",
            "order_number": "ORD12347",
            "customer_email": "bob.wilson@example.com",
            "customer_name": "Bob Wilson",
            "customer_phone": "+1-555-0125",
            "order_items": [
                {
                    "item_name": "Peanut Butter",
                    "quantity": 18,
                    "unit_price": 2.80,
                }
            ],
            "delivery_address": {
                "street": "789 Pine Ln",
                "city": "Riverside",
                "state": "CA",
                "zip_code": "54321",
                "country": "USA",
            },
            "delivery_location": "789 Pine Ln, Riverside, CA 54321, USA",
            "delivery_request_date": "2025-09-12",
            "delivery_time_preference": "evening",
            "order_status": "confirmed",
            "total_amount": 50.40,
            "order_date": current_time,
            "special_instructions": "Call upon arrival",
            "created_at": current_time,
            "updated_at": current_time,
        },
    ]

    logging.info(f"Inserting {len(sample_orders)} sample orders...")

    try:
        # Get a fresh reference to the table (important after recreation)
        table = client.get_table(table_id)
        errors = client.insert_rows_json(table, sample_orders)

        if errors:
            logging.error(f"Failed to insert sample data: {errors}")
            return False
        else:
            logging.info("Sample data inserted successfully")
            return True

    except Exception as e:
        logging.error(f"Error inserting sample data: {e}")
        return False


def main():
    """Main setup function."""
    print("========================================")
    print("BigQuery Environment Setup")
    print("========================================")

    # Check environment
    if not PROJECT_ID:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable not set")
        print("Please set it with: export GOOGLE_CLOUD_PROJECT=your-project-id")
        sys.exit(1)

    print(f"Setting up BigQuery environment for project: {PROJECT_ID}")

    try:
        # Initialize BigQuery client
        client = bigquery.Client(project=PROJECT_ID)

        # Create dataset
        if not create_dataset(client):
            print("Failed to create dataset")
            sys.exit(1)

        # Create table
        if not create_orders_table(client):
            print("Failed to create orders table")
            sys.exit(1)

        # Insert sample data
        if not insert_sample_data(client, overwrite=True):
            print("Failed to insert sample data")
            sys.exit(1)

        print("\n========================================")
        print("BigQuery environment setup completed successfully!")
        print("========================================")
        print(f"Dataset: {PROJECT_ID}.{DATASET_ID}")
        print(f"Table: {PROJECT_ID}.{DATASET_ID}.{ORDERS_TABLE}")
        print("Sample orders: 3 orders inserted")

        # Show final count
        query = f"SELECT COUNT(*) as count FROM `{PROJECT_ID}.{DATASET_ID}.{ORDERS_TABLE}`"
        query_job = client.query(query)
        results = query_job.result()

        for row in results:
            print(f"Total rows in table: {row.count}")

    except Exception as e:
        logging.error(f"Setup failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
