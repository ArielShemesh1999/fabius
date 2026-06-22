#!/usr/bin/env python3
"""
Direct test of Calendar MCP Server functionality in the new organized structure.
"""

import json
import logging
import os
import sys
import traceback
from datetime import datetime, timedelta

from calendar_mcp_server import CalendarManager

# Add the calendar MCP server directory to Python path
calendar_mcp_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "mcp-servers", "calendar"
)
sys.path.append(calendar_mcp_path)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def test_calendar_functions():
    """Test the Calendar MCP server functions in the new organized structure."""

    print(" Testing Calendar MCP Server Functions (Organized Structure)")
    print("=" * 70)
    print(f" Calendar MCP Path: {calendar_mcp_path}")
    print()

    try:
        # Import the CalendarManager from the MCP server

        # Create calendar manager instance
        print("Creating CalendarManager instance...")
        calendar_manager = CalendarManager()

        if not calendar_manager.service:
            print(" Calendar service not authenticated properly")
            return False

        print(" Calendar service authenticated successfully!")
        print()

        # Test 1: Get events for the next 7 days
        print("  Testing get_events (next 7 days)...")
        now = datetime.now()
        week_later = now + timedelta(days=7)

        time_min = now.isoformat() + "Z"
        time_max = week_later.isoformat() + "Z"

        events_result = calendar_manager.get_events(time_min, time_max)
        print(f"Events Result: {json.dumps(events_result, indent=2)}")

        if events_result["status"] == "success":
            print(f" Found {events_result['count']} events")
        else:
            print(
                f" Failed to get events: {events_result.get('message', 'Unknown error')}"
            )
        print()

        # Test 2: Check availability for tomorrow afternoon
        print("  Testing check_availability (tomorrow 2-3 PM)...")
        tomorrow = now + timedelta(days=1)
        start_time = tomorrow.replace(
            hour=14, minute=0, second=0, microsecond=0
        )
        end_time = start_time + timedelta(hours=1)

        start_iso = start_time.isoformat() + "Z"
        end_iso = end_time.isoformat() + "Z"

        availability_result = calendar_manager.check_availability(
            start_iso, end_iso
        )
        print(
            f" Availability Result: {json.dumps(availability_result, indent=2)}"
        )

        if availability_result["status"] == "success":
            if availability_result["available"]:
                print(" Time slot is available!")
            else:
                print(
                    f" Time slot has conflicts: {len(availability_result['conflicts'])} conflicts"
                )
        else:
            print(
                f"Failed to check availability: {availability_result.get('message', 'Unknown error')}"
            )
        print()

        # Test 3: Create a test event (only if the time slot is available)
        if availability_result.get(
            "status"
        ) == "success" and availability_result.get("available"):
            print(" Testing create_event (Organized Structure Test)...")

            create_result = calendar_manager.create_event(
                summary="MCP Organized Structure Test",
                description="This test event verifies the organized MCP server structure is working correctly. Created from mcp-servers/calendar/ subfolder.",
                location="456 Organized Drive, Clean Code City, CA",
                start_datetime=start_iso,
                end_datetime=end_iso,
            )

            print(f"Create Event Result: {json.dumps(create_result, indent=2)}")

            if create_result["status"] == "success":
                print(
                    "Test event created successfully from organized structure!"
                )
                print(f"Event ID: {create_result.get('event_id')}")
                print(f"Event Link: {create_result.get('event_link', 'N/A')}")

            else:
                print(
                    f"Failed to create event: {create_result.get('message', 'Unknown error')}"
                )
        else:
            print(
                "Skipping create_event test (time slot not available or availability check failed)"
            )

        print()
        print("Organized Calendar MCP Server Test Complete!")
        print()
        print("Structure Benefits:")
        print("- Clean separation of MCP servers")
        print("- Credentials isolated in calendar subfolder")
        print("- Easy to add more MCP servers (Gmail, etc.)")
        print("- Better organization for production deployment")

        return True

    except ImportError as e:
        print(f"Failed to import CalendarManager: {e}")
        print(f"Make sure calendar_mcp_server.py is in: {calendar_mcp_path}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_calendar_functions()

    if success:
        print("\nNext Steps with Organized Structure:")
        print("1. MCP servers are now cleanly organized")
        print("2. Update agent.py to import from new MCP server locations")
        print("3. Create similar structure for Gmail MCP server")
        print("4. Deploy with better separation of concerns")
    else:
        print("\nTroubleshooting:")
        print("1. Check if files were moved correctly to mcp-servers/calendar/")
        print("2. Verify credentials and token files are in the right location")
        print("3. Test import paths from the new structure")
