# BigQuery ADK Integration Directory

This directory contains the complete BigQuery ADK toolset integration for the Cookie Delivery System using Google's first-party ADK tools, including a comprehensive testing suite designed specifically for ADK integration patterns.

## Directory Contents

### Core Implementation
- `bigquery_tools.py` - ADK BigQuery toolset implementation with Application Default Credentials
- `create_bigquery_environment.py` - Setup script for BigQuery dataset and table creation

### Comprehensive Testing Suite
- `test_adk_bigquery_unit.py` - Unit tests for application logic and SQL query generation
- `test_adk_integration.py` - Integration tests with mocked ADK components
- `run_all_tests.py` - Comprehensive test suite runner with detailed reporting
- `TESTING_STRATEGY.md` - Complete testing documentation and best practices

### Documentation
- `BIGQUERY_SETUP.md` - Comprehensive setup guide for ADK integration
- `CLEANUP_SUMMARY.md` - Documentation of legacy code removal and modernization
- `README.md` - This file

## ADK Integration Overview

The implementation uses Google's official ADK BigQuery toolset with modern best practices:

```python
from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

def get_bigquery_toolset() -> BigQueryToolset:
    """Create and configure the ADK BigQuery toolset."""
    # Uses Application Default Credentials for authentication
    # WriteMode.ALLOWED for full read/write access  
    # Synchronous operation compatible with ADK web interface
    return BigQueryToolset(credentials_config=creds_config, bigquery_tool_config=tool_config)
```

### Available ADK Tools
- `list_dataset_ids` - List all available datasets
- `get_dataset_info` - Get detailed dataset information
- `list_table_ids` - List tables in a dataset
- `get_table_info` - Get table schema and metadata
- `execute_sql` - Execute SQL queries
- `ask_data_insights` - AI-powered data insights

## Quick Start

### 1. Install Dependencies
```bash
pip install google-adk[bigquery]
```

### 2. Authentication Setup
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 3. Environment Configuration
```bash
export USE_BIGQUERY=true
export GOOGLE_CLOUD_PROJECT=your-project-id
```

### 4. Run Comprehensive Tests
```bash
# Run all tests with detailed reporting
python run_all_tests.py

# Or run individual test suites
python test_adk_bigquery_unit.py      # Unit tests
python test_adk_integration.py        # Integration tests
```

Expected output:
```
BigQuery ADK Test Suite Runner
=====================================
Unit Tests: PASSED (14/14 tests, 100.0% success rate)
Integration Tests: PASSED (9/9 tests, 100.0% success rate)
ALL TESTS PASSED! BigQuery ADK integration is working correctly.
Test Quality: EXCELLENT
```

## Testing Strategy for ADK Integration

Our testing approach is specifically designed for first-party Google ADK integration:

### What We Test (Application Logic)
**Tool Configuration**: ADK toolset initialization and setup
**Query Generation**: SQL query building for business operations  
**Parameter Validation**: Input validation and error handling
**Agent Integration**: How tools integrate with ADK agent framework
**Mock Workflows**: Business process simulations

### What We DON'T Test (ADK Responsibility)
BigQuery connection logic (ADK manages)
Authentication mechanisms (Google Cloud SDK handles)
Query execution engine (BigQuery service)  
Retry logic and backoff (ADK implements)

### Test Categories

1. **Unit Tests** (`test_adk_bigquery_unit.py`)
   - Individual function testing
   - SQL query generation validation
   - Parameter validation
   - Error handling scenarios

2. **Integration Tests** (`test_adk_integration.py`)
   - ADK toolset integration patterns
   - Mock agent workflow simulation
   - Performance and scaling tests
   - Authentication error recovery

3. **Test Runner** (`run_all_tests.py`)
   - Automated test execution
   - Comprehensive reporting
   - Success rate analysis
   - Actionable recommendations



## Key Features

- **Production Ready**: Uses Google's official first-party tools with enterprise support
- **Secure Authentication**: Application Default Credentials via Google Cloud SDK
- **Async Compatible**: Resolved async conflicts for ADK web interface usage
- **Comprehensive Testing**: 23 test cases covering all integration aspects
- **WriteMode Configuration**: Proper data access control (BLOCKED, ALLOWED, PROTECTED)
- **AI-Powered Insights**: Built-in data analytics via ask_data_insights tool
- **Professional Code Quality**: No emojis, clean error handling, proper logging

### Testing Best Practices
1. **Mock ADK components**, not BigQuery services
2. **Test application logic**, not Google's infrastructure
3. **Use realistic test data** that matches production patterns
4. **Verify SQL query structure** rather than execution results
5. **Test error handling** for application-specific scenarios

## Migration Notes

This directory has been completely modernized for ADK integration:


## Troubleshooting

### Common Issues

1. **ADK Import Errors**
   ```bash
   pip install google-adk[bigquery]
   ```

2. **Authentication Failures**
   ```bash
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Test Failures**
   ```bash
   # Check test output for specific failures
   python run_all_tests.py
   # Review TESTING_STRATEGY.md for debugging guidance
   ```

4. **Permission Denied**
   ```bash
   # Ensure proper BigQuery IAM roles
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="user:your-email@domain.com" \
     --role="roles/bigquery.dataEditor"
   ```

## Performance Characteristics

The ADK toolset provides:
- **Connection Pooling**: Automatic connection management
- **Query Optimization**: Built-in query performance improvements  
- **Rate Limiting**: Automatic quota and rate limit handling
- **Retry Logic**: Intelligent retry with exponential backoff
- **Monitoring**: Built-in metrics and logging

## Support

For issues and questions:
1. Check `TESTING_STRATEGY.md` for testing guidance
2. Review `BIGQUERY_SETUP.md` for setup instructions
3. Run `python run_all_tests.py` to validate your environment
4. Check the main project's troubleshooting section
