# MCP Servers - Organized Structure

This directory contains Model Context Protocol (MCP) servers that provide external integrations for the cookie delivery agent.

## Directory Structure

```
cookie_scheduler_agent/
├── mcp-servers/
│   └── calendar/
│       ├── calendar_mcp_server.py          # Google Calendar MCP Server
│       ├── calendar_credentials.json       # OAuth credentials (not in git)
│       ├── calendar_token.json            # Access tokens (not in git)
│       └── test_calendar_functions.py     # Direct function tests
├── start_calendar_mcp.py                  # Convenience runner script
├── test_organized_structure.py            # Structure validation test
└── agent.py                              # Main agent (will integrate with MCP)
```

## Quick Start

### Start Calendar MCP Server
```bash
# From the main cookie_scheduler_agent directory
python start_calendar_mcp.py
```

### Test Calendar Functions
```bash
# Test from organized structure
cd mcp-servers/calendar
python test_calendar_functions.py
```

## MCP Server Status

| Service | Status | Location | Functionality |
|---------|--------|----------|---------------|
| **Google Calendar** | Working | `mcp-servers/calendar/` | Read/Write events, check availability |
| **Gmail** | Planned | `mcp-servers/gmail/` | Send emails, templates |
| **BigQuery** | Could migrate | `../bigquery_tools.py` | Order data management |

## Testing

The organized structure maintains all functionality while providing better organization:

-  **Authentication**: Works with Google Calendar API
-  **Event Creation**: Can create calendar events
-  **Event Reading**: Can retrieve calendar events  
-  **Availability Checking**: Can check for scheduling conflicts
-  **Event Updates**: Can modify existing events

## Integration Guide

When updating `agent.py` to use the organized MCP servers:

```python
# Instead of dummy data functions, import from organized structure
import sys
import os

# Add calendar MCP to path
calendar_path = os.path.join(os.path.dirname(__file__), 'mcp-servers', 'calendar')
sys.path.append(calendar_path)

from calendar_mcp_server import CalendarManager

# Use real calendar instead of dummy data
calendar_manager = CalendarManager()
```

This organized structure makes your cookie delivery agent more maintainable and production-ready! 🍪
