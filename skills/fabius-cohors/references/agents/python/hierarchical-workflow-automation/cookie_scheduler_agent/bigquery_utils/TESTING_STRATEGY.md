# BigQuery ADK Testing Strategy

## Overview

This document explains the comprehensive testing strategy for BigQuery ADK tools, designed specifically for first-party Google ADK integration.

## Testing Philosophy for First-Party ADK Integration

### What We DON'T Test (ADK's Responsibility)
- **BigQuery Connection Logic**: ADK handles connection pooling, authentication, and networking
- **Query Execution Engine**: Google's BigQuery service execution is tested by Google
- **Authentication Mechanisms**: ADC (Application Default Credentials) is managed by Google Cloud SDK
- **Retry Logic & Backoff**: ADK implements robust retry strategies
- **BigQuery API Specifics**: Rate limiting, quota management, etc.

### What We DO Test (Our Application Logic)
- **Tool Configuration**: Proper ADK toolset initialization
- **SQL Query Generation**: Our business logic that creates SQL queries
- **Parameter Validation**: Input validation for our functions
- **Agent Integration**: How our tools integrate with ADK agent framework
- **Error Handling**: Application-specific error scenarios
- **Workflow Logic**: Business process flows using ADK tools

## Test Categories

### 1. Unit Tests (`test_adk_bigquery_unit.py`)

**Purpose**: Test individual functions and components in isolation.

#### Test Classes:

**TestBigQueryADKConfiguration**
- Toolset initialization with mocked ADK components
- Environment variable configuration
- Authentication failure handling
- Configuration object creation

**TestSQLQueryGeneration**
- SQL query generation for latest orders
- Update query generation with parameters
- Analytics query generation with date ranges
- Dataset setup query generation

**TestParameterValidation**
- Input validation for order numbers, statuses
- Special character handling in parameters
- Date range validation for analytics
- Error handling for invalid inputs

**TestMockAgentWorkflow**
- Complete order processing workflows
- Analytics reporting workflows
- State management in agent context

**TestAgentIntegration**
- Integration patterns with ADK agent system
- Query generation suitable for agent execution
- Structured result formats

### 2. Integration Tests (`test_adk_integration.py`)

**Purpose**: Test how our components work together with mocked ADK services.

#### Test Classes:

**TestADKBigQueryIntegration**
- Complete toolset initialization flow
- Authentication error handling
- Simulated agent workflows with mocked ADK responses

**TestADKToolsetMocking**
- Verification that our mocks match ADK interfaces
- Mock tool execution patterns
- Realistic ADK response simulation

**TestErrorHandlingIntegration**
- Recovery from toolset initialization failures
- Query generation error handling
- Integration error scenarios

**TestPerformanceAndScaling**
- Multiple toolset initialization
- Large query generation
- Performance characteristics

## Testing Patterns for ADK Tools

### 1. Mocking Strategy

```python
# Mock ADK components, not BigQuery services
@patch('bigquery_utils.bigquery_tools.BigQueryToolset')
@patch('bigquery_utils.bigquery_tools.BigQueryCredentialsConfig')
def test_toolset_init(self, mock_config, mock_toolset):
    # Test our initialization logic
    toolset = get_bigquery_toolset()
    self.assertIsNotNone(toolset)
```

### 2. Query Generation Testing

```python
def test_query_generation(self):
    # Test that we generate correct SQL
    result = get_latest_order_from_bigquery(mock_context)
    
    # Verify structure
    self.assertEqual(result["status"], "query_ready")
    self.assertIn("query", result)
    
    # Verify SQL content
    query = result["query"]
    self.assertIn("SELECT *", query)
    self.assertIn("WHERE order_status = 'order_placed'", query)
```

### 3. Agent Workflow Testing

```python
def test_agent_workflow(self):
    # Test complete business processes
    
    # Step 1: Generate query
    query_result = get_latest_order_from_bigquery(context)
    
    # Step 2: Simulate agent execution (mocked)
    execution_result = mock_agent_execute(query_result["query"])
    
    # Step 3: Verify workflow completion
    self.assertEqual(execution_result["status"], "success")
```

## Test File Organization

```
bigquery_utils/
├── test_adk_bigquery_unit.py     # Unit tests for individual functions
├── test_adk_integration.py       # Integration tests with mocked ADK
├── test_bigquery.py              # Legacy tests (reference only)
├── TESTING_STRATEGY.md           # This documentation
└── bigquery_tools.py             # Implementation under test
```

## Running Tests

### Unit Tests
```bash
cd bigquery_utils
python test_adk_bigquery_unit.py
```

### Integration Tests
```bash
cd bigquery_utils  
python test_adk_integration.py
```

### All Tests
```bash
cd bigquery_utils
python -m pytest test_adk_*.py -v
```

## Test Data Strategy

### Mock Data Patterns
- **Order Data**: Realistic order structures for testing workflows
- **Query Results**: Typical BigQuery response formats
- **Error Scenarios**: Common error conditions and edge cases

### Environment Setup
- Mock `GOOGLE_CLOUD_PROJECT` environment variable
- Mock ADK credentials and authentication
- Mock tool context with realistic state

## Assertions and Validations

### Query Structure Validation
```python
# Verify SQL syntax elements
self.assertIn("SELECT", query)
self.assertIn("FROM", query) 
self.assertIn("WHERE", query)

# Verify business logic
self.assertIn("order_status = 'order_placed'", query)
self.assertIn("ORDER BY created_at DESC", query)
```

### Integration Response Validation
```python
# Verify response structure
self.assertIn("status", result)
self.assertIn("query", result)

# Verify agent execution compatibility
self.assertEqual(result["status"], "query_ready")
self.assertIn("instruction", result)
```

## Error Testing Strategy

### Application Error Scenarios
- Invalid input parameters
- Missing environment variables
- Query generation failures
- Context state corruption

### ADK Error Simulation
- Authentication failures
- Toolset initialization errors
- Configuration errors
- Network/service unavailability

## Test Coverage Goals

### Functional Coverage
- All public functions tested
- All query generation paths tested
- All error conditions tested
- All integration patterns tested

### Code Coverage Targets
- **Unit Tests**: >90% line coverage
- **Integration Tests**: >80% workflow coverage
- **Combined**: >95% of application logic

## Continuous Integration

### Test Automation
- Run unit tests on every commit
- Run integration tests on pull requests
- Performance tests on releases

### Test Requirements
- All tests must pass before merge
- New features require corresponding tests
- Bug fixes require regression tests

## Best Practices

### Test Design
1. **Test One Thing**: Each test should verify one specific behavior
2. **Clear Names**: Test names should describe what is being tested
3. **Independent Tests**: Tests should not depend on each other
4. **Fast Execution**: Unit tests should run quickly
5. **Realistic Mocks**: Mocks should match real ADK behavior

### Maintenance
1. **Update Tests with Code**: Keep tests in sync with implementation
2. **Review Test Failures**: Investigate and fix failing tests promptly
3. **Refactor Tests**: Keep test code clean and maintainable
4. **Document Changes**: Update test documentation when patterns change


### Integration with ADK Updates
- Monitor ADK release notes for breaking changes
- Update mocks when ADK interfaces change
- Test compatibility with new ADK versions
- Maintain backwards compatibility where possible

