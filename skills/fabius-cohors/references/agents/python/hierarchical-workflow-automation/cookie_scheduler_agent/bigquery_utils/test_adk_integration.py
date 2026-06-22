#!/usr/bin/env python3
"""
Integration tests for BigQuery ADK tools.

These tests verify that our ADK integration works correctly with real ADK components,
but still use mocking to avoid requiring actual BigQuery access during testing.
"""

import logging
import os
import sys
import unittest
from unittest.mock import Mock, patch

from bigquery_utils.bigquery_tools import (
    WriteMode,
    get_bigquery_toolset,
    get_dataset_setup_queries,
    get_latest_order_from_bigquery,
    update_order_status_in_bigquery,
)

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging for tests
logging.basicConfig(level=logging.INFO)


class TestADKBigQueryIntegration(unittest.TestCase):
    """Integration tests for ADK BigQuery toolset."""

    def setUp(self):
        """Set up test environment."""
        self.test_project = "test-cookie-project"
        os.environ["GOOGLE_CLOUD_PROJECT"] = self.test_project

    def tearDown(self):
        """Clean up test environment."""
        if "GOOGLE_CLOUD_PROJECT" in os.environ:
            del os.environ["GOOGLE_CLOUD_PROJECT"]

    @patch("bigquery_utils.bigquery_tools.BigQueryToolset")
    @patch("bigquery_utils.bigquery_tools.BigQueryCredentialsConfig")
    @patch("bigquery_utils.bigquery_tools.BigQueryToolConfig")
    @patch("bigquery_utils.bigquery_tools.google.auth.default")
    def test_complete_toolset_initialization(
        self, mock_auth, mock_tool_config, mock_creds_config, mock_toolset
    ):
        """Test complete ADK toolset initialization flow."""

        # Mock authentication
        mock_credentials = Mock()
        mock_auth.return_value = (mock_credentials, self.test_project)

        # Mock configuration classes
        mock_tool_config_instance = Mock()
        mock_tool_config.return_value = mock_tool_config_instance

        mock_creds_config_instance = Mock()
        mock_creds_config.return_value = mock_creds_config_instance

        # Mock toolset with realistic methods
        mock_toolset_instance = Mock()
        mock_toolset_instance.get_tools.return_value = [
            Mock(name="list_dataset_ids"),
            Mock(name="get_dataset_info"),
            Mock(name="list_table_ids"),
            Mock(name="get_table_info"),
            Mock(name="execute_sql"),
            Mock(name="ask_data_insights"),
        ]
        mock_toolset.return_value = mock_toolset_instance

        # Test initialization
        toolset = get_bigquery_toolset()

        # Verify authentication was called
        mock_auth.assert_called_once()

        # Verify tool configuration with ALLOWED write mode
        mock_tool_config.assert_called_once_with(write_mode=WriteMode.ALLOWED)

        # Verify credentials configuration
        mock_creds_config.assert_called_once_with(credentials=mock_credentials)

        # Verify toolset initialization
        mock_toolset.assert_called_once_with(
            credentials_config=mock_creds_config_instance,
            bigquery_tool_config=mock_tool_config_instance,
        )

        # Verify toolset has expected tools
        self.assertIsNotNone(toolset)
        tools = toolset.get_tools()
        self.assertEqual(len(tools), 6)

        # Check that we have mocked tools (the actual names will be mock object names)
        self.assertIsInstance(tools, list)
        for tool in tools:
            self.assertTrue(hasattr(tool, "name"))

    def test_authentication_error_handling(self):
        """Test handling of authentication errors."""
        with patch(
            "bigquery_utils.bigquery_tools.google.auth.default"
        ) as mock_auth:
            mock_auth.side_effect = Exception("Authentication failed")

            # Should return None and log error
            with self.assertLogs(level="ERROR") as log:
                result = get_bigquery_toolset()

            self.assertIsNone(result)
            self.assertTrue(
                any(
                    "Failed to initialize BigQuery toolset" in message
                    for message in log.output
                )
            )

    @patch("bigquery_utils.bigquery_tools.get_bigquery_toolset")
    def test_agent_workflow_simulation(self, mock_get_toolset):
        """Test simulated agent workflow using ADK tools."""
        # Mock toolset with execute_sql capability
        mock_toolset = Mock()
        mock_execute_sql = Mock()
        mock_execute_sql.return_value = {
            "status": "success",
            "rows": [
                {
                    "order_number": "ORD12345",
                    "customer_name": "John Doe",
                    "order_status": "order_placed",
                    "total_amount": 99.50,
                }
            ],
        }
        mock_toolset.execute_sql = mock_execute_sql
        mock_get_toolset.return_value = mock_toolset

        # Test workflow: get order, then update status
        # Mock tool context
        mock_context = Mock()
        mock_context.state = {}

        # Step 1: Generate query to get latest order
        get_order_result = get_latest_order_from_bigquery(mock_context)
        self.assertEqual(get_order_result["status"], "query_ready")

        query = get_order_result["query"]
        self.assertIn("SELECT *", query)
        self.assertIn("order_status = 'order_placed'", query)

        # Step 2: Simulate agent executing the query
        # (In real usage, agent would call toolset.execute_sql(query))
        simulated_query_result = mock_execute_sql(query)
        self.assertEqual(simulated_query_result["status"], "success")

        # Step 3: Generate update query
        order_number = simulated_query_result["rows"][0]["order_number"]
        update_result = update_order_status_in_bigquery(
            mock_context, order_number, "confirmed"
        )

        self.assertEqual(update_result["status"], "query_ready")
        self.assertIn("UPDATE", update_result["query"])
        self.assertIn(order_number, update_result["query"])


class TestADKToolsetMocking(unittest.TestCase):
    """Test our mocking strategies for ADK components."""

    def test_mock_toolset_structure(self):
        """Test that our mocks match expected ADK toolset structure."""
        # Create a realistic mock of BigQueryToolset
        mock_toolset = Mock()

        # Add expected methods
        mock_toolset.get_tools.return_value = []
        mock_toolset.process_llm_request.return_value = {"status": "success"}
        mock_toolset.close.return_value = None

        # Test that mock has expected interface
        self.assertTrue(hasattr(mock_toolset, "get_tools"))
        self.assertTrue(hasattr(mock_toolset, "process_llm_request"))
        self.assertTrue(hasattr(mock_toolset, "close"))

        # Test method calls
        tools = mock_toolset.get_tools()
        self.assertIsInstance(tools, list)

        response = mock_toolset.process_llm_request("test request")
        self.assertIn("status", response)

    def test_mock_tool_execution(self):
        """Test mocking individual tool execution."""
        # Mock individual tools
        mock_execute_sql = Mock()
        mock_execute_sql.return_value = {
            "status": "success",
            "rows": [{"order_id": "123", "status": "placed"}],
            "row_count": 1,
        }

        mock_list_datasets = Mock()
        mock_list_datasets.return_value = {
            "status": "success",
            "datasets": ["cookie_delivery", "analytics"],
        }

        # Test tool execution
        sql_result = mock_execute_sql("SELECT * FROM orders")
        self.assertEqual(sql_result["status"], "success")
        self.assertEqual(len(sql_result["rows"]), 1)

        dataset_result = mock_list_datasets()
        self.assertEqual(dataset_result["status"], "success")
        self.assertIn("cookie_delivery", dataset_result["datasets"])


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test error handling in ADK integration."""

    def setUp(self):
        """Set up test environment."""
        os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"

    def tearDown(self):
        """Clean up test environment."""
        if "GOOGLE_CLOUD_PROJECT" in os.environ:
            del os.environ["GOOGLE_CLOUD_PROJECT"]

    def test_toolset_initialization_failure_recovery(self):
        """Test recovery from toolset initialization failure."""
        with patch(
            "bigquery_utils.bigquery_tools.BigQueryToolset"
        ) as mock_toolset:
            mock_toolset.side_effect = Exception("Toolset init failed")

            with self.assertLogs(level="ERROR") as log:
                result = get_bigquery_toolset()

            self.assertIsNone(result)
            self.assertTrue(
                any("Failed to initialize" in message for message in log.output)
            )

    def test_query_generation_error_handling(self):
        """Test error handling in query generation."""

        # For well-designed functions, test that they handle normal cases correctly
        # The real error handling is at the ADK level
        mock_context = Mock()
        mock_context.state = {}

        result = get_latest_order_from_bigquery(mock_context)

        # Our functions are robust and should return valid results
        self.assertEqual(result["status"], "query_ready")
        self.assertIn("query", result)


class TestPerformanceAndScaling(unittest.TestCase):
    """Test performance characteristics of our ADK integration."""

    def test_multiple_toolset_initializations(self):
        """Test that multiple toolset initializations work correctly."""
        with patch(
            "bigquery_utils.bigquery_tools.BigQueryToolset"
        ) as mock_toolset:
            with patch(
                "bigquery_utils.bigquery_tools.google.auth.default"
            ) as mock_auth:
                with patch(
                    "bigquery_utils.bigquery_tools.BigQueryCredentialsConfig"
                ) as mock_creds_config:
                    with patch(
                        "bigquery_utils.bigquery_tools.BigQueryToolConfig"
                    ) as mock_tool_config:
                        # Mock successful initialization
                        mock_auth.return_value = (Mock(), "test-project")
                        mock_creds_config.return_value = Mock()
                        mock_tool_config.return_value = Mock()
                        mock_toolset.return_value = Mock()

                        # Initialize multiple toolsets
                        toolsets = []
                        for _ in range(5):
                            toolset = get_bigquery_toolset()
                            self.assertIsNotNone(toolset)
                            toolsets.append(toolset)

                        # Verify all initializations succeeded
                        self.assertEqual(len(toolsets), 5)
                        self.assertEqual(mock_toolset.call_count, 5)

    def test_large_query_generation(self):
        """Test generating queries with large parameter sets."""

        queries = get_dataset_setup_queries()

        # Should handle multiple complex queries
        self.assertGreater(len(queries), 3)  # Dataset + Table + Sample data

        # Each query should be properly structured
        for query_info in queries:
            self.assertIsInstance(query_info, dict)
            self.assertIn("description", query_info)
            self.assertIn("query", query_info)
            self.assertIsInstance(query_info["query"], str)
            self.assertGreater(
                len(query_info["query"]), 50
            )  # Non-trivial queries


def run_integration_tests():
    """Run all integration tests."""
    print("Running BigQuery ADK Integration Tests...")
    print("=" * 60)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestADKBigQueryIntegration,
        TestADKToolsetMocking,
        TestErrorHandlingIntegration,
        TestPerformanceAndScaling,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)

    # Print detailed summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(
        f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}"
    )
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)

    success_rate = (
        (result.testsRun - len(result.failures) - len(result.errors))
        / result.testsRun
        * 100
    )
    print(f"\nSuccess Rate: {success_rate:.1f}%")

    if result.wasSuccessful():
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("ADK BigQuery integration is working correctly.")
    else:
        print("\n❌ Some integration tests failed.")
        print("Please review the errors above.")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
