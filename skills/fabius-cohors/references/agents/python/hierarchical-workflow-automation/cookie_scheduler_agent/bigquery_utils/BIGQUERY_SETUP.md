# BigQuery ADK Integration Guide

This guide explains how to set up and use BigQuery integration with the Cookie Delivery Agent System using Google's first-party ADK toolset.

## Overview

The system uses Google's official ADK BigQuery toolset for production-ready data access:
- **ADK BigQuery Toolset**: Uses Google's first-party tools with Application Default Credentials
- **Async Compatible**: Resolved async conflicts for seamless ADK web interface usage
- **WriteMode Configuration**: Proper data access control (BLOCKED, ALLOWED, PROTECTED)
- **Fallback Support**: Graceful degradation to dummy data when BigQuery unavailable

## Quick Setup

### 1. Prerequisites

- Google Cloud Project with BigQuery API enabled
- `gcloud` CLI installed and authenticated
- Python dependencies installed (`pip install google-adk[bigquery]`)

### 2. Authentication Setup

```bash
# Set up Application Default Credentials (ADC)
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

# Verify authentication
gcloud auth application-default print-access-token
```

### 3. Enable BigQuery Integration

Edit your `.env` file:
```bash
USE_BIGQUERY=true
GOOGLE_CLOUD_PROJECT=your-actual-project-id
```

### 4. Test the ADK Integration

```bash
# Test BigQuery ADK toolset integration
python test_bigquery_integration.py

# Expected output:
# All tests passed: toolset initialization, agent creation, async compatibility
```

## ADK BigQuery Toolset Implementation

### Architecture

The new implementation uses Google's official ADK BigQuery toolset:

```python
# bigquery_utils/bigquery_tools.py
from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
import google.auth

def get_bigquery_toolset() -> BigQueryToolset:
    """Create and configure the ADK BigQuery toolset."""
    # Tool configuration with write permissions
    tool_config = BigQueryToolConfig(write_mode=WriteMode.ALLOWED)
    
    # Use Application Default Credentials
    application_default_credentials, _ = google.auth.default()
    
    # Create credentials configuration
    credentials_config = BigQueryCredentialsConfig(
        credentials=application_default_credentials
    )
    
    # Initialize the BigQuery toolset
    bigquery_toolset = BigQueryToolset(
        credentials_config=credentials_config,
        bigquery_tool_config=tool_config
    )
    
    return bigquery_toolset
```

### Available ADK Tools

The BigQuery ADK toolset provides these tools:
- **list_dataset_ids**: List all available datasets in the project
- **get_dataset_info**: Get detailed information about a specific dataset
- **list_table_ids**: List all tables within a dataset
- **get_table_info**: Get schema and metadata for a specific table
- **execute_sql**: Execute SQL queries against BigQuery
- **ask_data_insights**: Get AI-powered insights about your data

### WriteMode Configuration

- **WriteMode.BLOCKED**: Read-only access to BigQuery data
- **WriteMode.ALLOWED**: Full read/write access for order management (current setting)
- **WriteMode.PROTECTED**: Temporary data access only

### New ADK Approach 

The ADK toolset approach is synchronous and compatible:
```python
def get_bigquery_toolset() -> BigQueryToolset:
    # Synchronous initialization compatible with ADK web interface
    return bigquery_toolset
```

## Database Schema (Compatible with ADK Toolset)

The BigQuery schema is designed to work seamlessly with the ADK toolset:

### Dataset: `cookie_delivery`
### Table: `orders`

| Field | Type | Mode | Description |
|-------|------|------|-------------|
| order_id | STRING | REQUIRED | Unique order identifier |
| order_number | STRING | REQUIRED | Human-readable order number |
| customer_email | STRING | REQUIRED | Customer email address |
| customer_name | STRING | REQUIRED | Customer full name |
| customer_phone | STRING | NULLABLE | Customer phone number |
| order_items | RECORD | REPEATED | Array of ordered items |
| delivery_address | RECORD | NULLABLE | Structured delivery address |
| delivery_location | STRING | NULLABLE | Formatted delivery address |
| delivery_request_date | DATE | NULLABLE | Requested delivery date |
| delivery_time_preference | STRING | NULLABLE | morning/afternoon/evening |
| order_status | STRING | REQUIRED | Current order status |
| total_amount | FLOAT | NULLABLE | Total order amount |
| order_date | TIMESTAMP | NULLABLE | When order was placed |
| special_instructions | STRING | NULLABLE | Customer delivery notes |
| created_at | TIMESTAMP | NULLABLE | Record creation time |
| updated_at | TIMESTAMP | NULLABLE | Last update time |

### Order Status Values

- `order_placed`: New order, ready for processing
- `confirmed`: Order confirmed, ready for scheduling
- `scheduled`: Delivery scheduled
- `in_delivery`: Out for delivery
- `delivered`: Successfully delivered
- `cancelled`: Order cancelled

## ADK Agent Integration

### Agent Implementation

The new agents use the BigQuery ADK toolset:

```python
# agents.py
from google.adk import Agent
from bigquery_utils.bigquery_tools import get_bigquery_toolset

def store_database_agent():
    """Agent for managing store inventory and customer data in BigQuery."""
    bigquery_toolset = get_bigquery_toolset()
    
    agent = Agent(
        name="store_database_agent",
        model="gemini-2.0-flash-exp",
        description="Manages store inventory and customer data using BigQuery ADK toolset",
        instruction="""You can query BigQuery databases for order management, 
        inventory tracking, and customer service using the ADK toolset.""",
        tools=[bigquery_toolset]
    )
    
    return agent
```

### Usage Examples

Agents can now directly use BigQuery tools:

```sql
-- Example queries agents can execute via execute_sql tool

-- Get latest orders
SELECT * FROM `your-project.cookie_delivery.orders` 
WHERE order_status = 'order_placed' 
ORDER BY created_at DESC LIMIT 5;

-- Update order status
UPDATE `your-project.cookie_delivery.orders` 
SET order_status = 'scheduled', updated_at = CURRENT_TIMESTAMP() 
WHERE order_number = 'ORD12345';

-- Get order analytics
SELECT 
  order_status,
  COUNT(*) as order_count,
  AVG(total_amount) as avg_amount,
  SUM(total_amount) as total_revenue
FROM `your-project.cookie_delivery.orders`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY order_status;
```

## Error Handling

The BigQuery ADK integration includes comprehensive error handling:

- **Authentication errors**: Uses Application Default Credentials with clear error messages
- **Toolset initialization**: Graceful fallback when BigQuery unavailable
- **ADK compatibility**: Resolved async conflicts for web interface usage
- **Credential management**: Automatic token refresh and validation

## Testing

### Integration Tests

```bash
# Run comprehensive ADK integration tests
python test_bigquery_integration.py

# Expected output:
# BigQuery ADK Integration Test Suite
# All tests passed: toolset initialization, agent creation, async compatibility
```

### Manual Testing

```bash
# Test individual components
python -c "from bigquery_utils.bigquery_tools import get_bigquery_toolset; print('Toolset:', get_bigquery_toolset())"
python -c "from agents import store_database_agent; print('Agent:', store_database_agent())"
```

## Monitoring

### Query Performance
```sql
-- Check query history in BigQuery console
SELECT 
  job_id,
  query,
  total_bytes_processed,
  total_slot_ms,
  creation_time
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_USER
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
ORDER BY creation_time DESC;
```

### Data Quality
```sql
-- Check for data quality issues
SELECT 
  order_status,
  COUNT(*) as count,
  COUNT(DISTINCT customer_email) as unique_customers
FROM `your-project.cookie_delivery.orders`
GROUP BY order_status;
```

## Troubleshooting

### Common Issues

1. **ADK BigQuery Import Error**
   ```bash
   # Install ADK with BigQuery support
   pip install google-adk[bigquery]
   
   # Verify installation
   python -c "from google.adk.tools.bigquery import BigQueryToolset; print('ADK BigQuery available')"
   ```

2. **Authentication Error**
   ```bash
   # Set up Application Default Credentials
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   
   # Verify credentials
   gcloud auth application-default print-access-token
   ```

3. **Permission Denied**
   ```bash
   # Ensure required IAM roles
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="user:your-email@domain.com" \
     --role="roles/bigquery.dataEditor"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="user:your-email@domain.com" \
     --role="roles/bigquery.jobUser"
   ```

4. **Async Compatibility Issues**
   ```bash
   # This should be resolved with ADK toolset
   # If you encounter async errors, verify you're using the new implementation:
   python test_bigquery_integration.py
   ```

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
python test_bigquery.py
```

### Verify Setup

```bash
# Check dataset exists
bq ls --project_id=YOUR_PROJECT_ID

# Check table schema
bq show your-project:cookie_delivery.orders

# Check sample data
bq query --use_legacy_sql=false "SELECT COUNT(*) FROM \`your-project.cookie_delivery.orders\`"
```

## Cost Optimization

- Use partitioned tables for large datasets
- Implement table clustering on frequently queried columns
- Monitor query costs in BigQuery console
- Set up billing alerts

## Security

- Use IAM roles with minimal required permissions
- Enable audit logging
- Consider field-level encryption for sensitive data
- Regular access reviews

## Production Considerations

- Set up monitoring and alerting
- Implement backup strategies
- Use separate datasets for different environments
- Configure appropriate retention policies
