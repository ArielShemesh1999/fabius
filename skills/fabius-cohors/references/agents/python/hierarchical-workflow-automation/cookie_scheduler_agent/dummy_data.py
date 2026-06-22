# --- Dummy Data and Simulation Tools ---
# NOTE: these will be replaced with:
# - BigQuery integration for orders (direct connection)
# - Google Calendar MCP server for scheduling (business account)
# - Gmail MCP server for email sending (business account)

# This dictionary simulates a BigQuery table structure for orders.
# Table: `cookie_delivery.orders`
DUMMY_ORDER_DATABASE = {
    "ORD12345": {
        "order_id": "ORD12345",
        "order_number": "ORD12345",
        "customer_email": "customer@example.com",
        "customer_name": "John Doe",
        "customer_phone": "+1-555-555-5555",
        "order_items": [
            {"item_name": "Chocolate Chip", "quantity": 12, "unit_price": 2.50},
            {"item_name": "Oatmeal Raisin", "quantity": 6, "unit_price": 2.75},
            {"item_name": "Snickerdoodle", "quantity": 12, "unit_price": 2.60},
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
        "delivery_time_preference": "morning",  # morning, afternoon, evening
        "order_status": "order_placed",  # order_placed, confirmed, scheduled, in_delivery, delivered, cancelled
        "total_amount": 63.50,
        "order_date": "2025-09-04T10:30:00Z",
        "special_instructions": "Please ring doorbell twice",
        "created_at": "2025-09-04T10:30:00Z",
        "updated_at": "2025-09-04T10:30:00Z",
    }
}

# This dictionary simulates Google Calendar API responses.
DUMMY_CALENDAR = {
    "2025-09-08": [
        {
            "id": "evt_001",
            "summary": "Cookie Delivery - ORD12340",
            "description": "Delivery for John Smith - 2 dozen assorted cookies",
            "location": "456 Oak Ave, Springfield, CA",
            "start": {"dateTime": "2025-09-08T10:00:00-07:00"},
            "end": {"dateTime": "2025-09-08T10:30:00-07:00"},
            "status": "confirmed",
        }
    ],
    "2025-09-09": [
        {
            "id": "evt_002",
            "summary": "Cookie Delivery - ORD12342",
            "description": "Delivery for Jane Doe - 1 dozen chocolate chip",
            "location": "789 Pine Ln, Springfield, CA",
            "start": {"dateTime": "2025-09-09T14:00:00-07:00"},
            "end": {"dateTime": "2025-09-09T14:30:00-07:00"},
            "status": "confirmed",
        }
    ],
}
