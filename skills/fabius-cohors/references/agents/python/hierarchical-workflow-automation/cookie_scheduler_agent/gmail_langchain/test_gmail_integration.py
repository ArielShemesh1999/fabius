#!/usr/bin/env python3
"""
Test script for LangChain Gmail integration.
This script tests the Gmail functionality without running the full agent workflow.
"""

import logging
import os
import sys

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from gmail_manager import gmail_manager


def test_gmail_initialization():
    """Test if LangChain Gmail toolkit initializes correctly."""
    print("=" * 60)
    print("Testing LangChain Gmail Toolkit Initialization")
    print("=" * 60)

    # Test manager creation
    print(f"Gmail Manager Available: {gmail_manager.is_available()}")
    print(f"Available Tools: {gmail_manager.get_available_tools()}")

    if gmail_manager.is_available():
        print("SUCCESS: LangChain Gmail Toolkit initialized successfully!")
        return True
    else:
        print("NOTICE: LangChain Gmail Toolkit not available")
        print("\nTo set up LangChain Gmail integration:")
        print("1. Install dependencies: pip install langchain-community")
        print("2. Create gmail_credentials.json file:")
        print("   - Go to Google Cloud Console")
        print("   - Enable Gmail API")
        print("   - Create OAuth 2.0 Client ID (Desktop Application)")
        print("   - Download and save as gmail_credentials.json")
        print("3. Run OAuth2 authentication flow")
        return False


def test_gmail_search():
    """Test Gmail search functionality."""
    if not gmail_manager.is_available():
        print("Skipping search test - Gmail not available")
        return

    print("\n" + "=" * 60)
    print("Testing Gmail Search Functionality")
    print("=" * 60)

    try:
        # Search for recent messages from yourself
        result = gmail_manager.search_messages("from:me", max_results=3)
        print(f"Search Status: {result['status']}")

        if result["status"] == "success":
            print("SUCCESS: Gmail search working!")
            print(f"Query: {result['query']}")
            # Note: We don't print the full results to avoid showing sensitive data
            print(
                "Search completed successfully (results not shown for privacy)"
            )
        else:
            print(
                f"ERROR: Search failed: {result.get('message', 'Unknown error')}"
            )

    except Exception as e:
        print(f"ERROR: Search test failed with exception: {e}")


def test_gmail_send_demo():
    """Demonstrate how email sending would work (without actually sending)."""
    print("\n" + "=" * 60)
    print("Gmail Send Function Demo (No actual email sent)")
    print("=" * 60)

    # Demo email content
    demo_email = {
        "to": "customer@example.com",
        "subject": "Your Cookie Delivery is Scheduled!",
        "body": """
        <html>
        <body>
            <h2>Cookie Delivery Confirmation</h2>
            <p>Dear Valued Customer,</p>
            
            <p>We're excited to confirm your cookie delivery!</p>
            
            <h3>Delivery Details:</h3>
            <ul>
                <li><strong>Order Number:</strong> ORD12345</li>
                <li><strong>Delivery Date:</strong> September 15, 2025</li>
                <li><strong>Time Window:</strong> 9:00 AM - 9:30 AM</li>
                <li><strong>Location:</strong> 123 Main St, Anytown, CA</li>
            </ul>
            
            <h3>Your Order:</h3>
            <ul>
                <li>12x Chocolate Chip Cookies</li>
                <li>6x Oatmeal Raisin Cookies</li>
            </ul>
            
            <h3>Special Haiku for September:</h3>
            <em>
                Autumn leaves falling<br>
                Sweet cookies warm the cool air<br>
                Joy delivered fresh
            </em>
            
            <p>Thank you for choosing our cookie delivery service!</p>
            
            <p>Best regards,<br>
            The Cookie Delivery Team<br>
            deliveries@cookiebusiness.com</p>
        </body>
        </html>
        """,
    }

    print("Demo email content:")
    print(f"To: {demo_email['to']}")
    print(f"Subject: {demo_email['subject']}")
    print("Body: HTML formatted confirmation email")

    if gmail_manager.is_available():
        print(
            "\nNOTICE: To actually send this email, uncomment the following line:"
        )
        print("# result = gmail_manager.send_email(**demo_email)")
        print("\nSUCCESS: LangChain Gmail is ready to send real emails!")
    else:
        print("\nNOTICE: Gmail not available - would fall back to dummy email")


def test_gmail_credentials_setup():
    """Test credential file setup and provide guidance."""
    print("\n" + "=" * 60)
    print("Gmail Credentials Setup Check")
    print("=" * 60)

    credentials_file = gmail_manager.credentials_file
    token_file = gmail_manager.token_file

    print(f"Credentials file path: {credentials_file}")
    print(f"Token file path: {token_file}")
    print(f"Credentials file exists: {os.path.exists(credentials_file)}")
    print(f"Token file exists: {os.path.exists(token_file)}")

    if not os.path.exists(credentials_file):
        print("\nCredential Setup Instructions:")
        print("1. Go to Google Cloud Console (console.cloud.google.com)")
        print("2. Enable Gmail API")
        print("3. Go to 'Credentials' section")
        print("4. Click 'Create Credentials' > 'OAuth 2.0 Client ID'")
        print("5. Choose 'Desktop Application'")
        print("6. Download the JSON file")
        print(f"7. Save it as: {credentials_file}")
        print("8. Run this test again to authenticate")


def main():
    """Run all Gmail tests."""
    logging.basicConfig(level=logging.INFO)

    print("LangChain Gmail Integration Test Suite")
    print("=" * 60)

    # Test 1: Initialization
    if test_gmail_initialization():
        # Test 2: Search functionality
        test_gmail_search()

    # Test 3: Email sending demo (always run to show format)
    test_gmail_send_demo()

    # Test 4: Credentials setup check
    test_gmail_credentials_setup()

    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("=" * 60)

    if gmail_manager.is_available():
        print("SUCCESS: LangChain Gmail integration is working!")
        print(
            "The agent can now send real Gmail emails when USE_GMAIL_LANGCHAIN=true"
        )
    else:
        print("NOTICE: LangChain Gmail integration needs setup")
        print("The agent will use dummy email data until Gmail is configured")


if __name__ == "__main__":
    main()
