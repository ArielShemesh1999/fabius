#!/usr/bin/env python3
"""
Convenience script to start the Calendar MCP Server from the organized structure.
Run this from the main cookie_scheduler_agent directory.
"""

import os
import subprocess
import sys


def start_calendar_mcp_server():
    """Start the Calendar MCP Server from the organized location."""

    # Get the path to the calendar MCP server
    calendar_mcp_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "calendar"
    )

    server_script = os.path.join(calendar_mcp_path, "calendar_mcp_server.py")

    print(" Starting Calendar MCP Server...")
    print(f" Location: {calendar_mcp_path}")
    print(f" Script: {server_script}")
    print("=" * 60)

    if not os.path.exists(server_script):
        print(f" Calendar MCP server not found at: {server_script}")
        return False

    try:
        # Change to the calendar directory and run the server
        os.chdir(calendar_mcp_path)
        subprocess.run([sys.executable, "calendar_mcp_server.py"], check=False)

    except KeyboardInterrupt:
        print("\n Calendar MCP Server stopped by user")
    except Exception as e:
        print(f" Error starting Calendar MCP Server: {e}")
        return False

    return True


if __name__ == "__main__":
    start_calendar_mcp_server()
