# Calendar MCP Server Setup Guide

## Overview
This guide will help you set up the Google Calendar MCP server to connect your cookie delivery agent with your Google Calendar.

## Prerequisites
Python environment with required packages (already installed)
Google Cloud Project (you have: `agents-starter-patterns`)
MCP server code (already created)

## Step-by-Step Setup

### 1. Google Cloud Console Setup

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Select your project**: `agents-starter-patterns`
3. **Enable Google Calendar API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click on it and press "Enable"

### 2. Create OAuth 2.0 Credentials

1. **Navigate to Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"

2. **Configure OAuth Consent Screen** (if prompted):
   - Choose "External" user type
   - Fill in required fields:
     - App name: "Cookie Delivery Service"
     - User support email: your email
     - Developer contact: your email
   - Add scopes: `https://www.googleapis.com/auth/calendar`

3. **Create OAuth 2.0 Client ID**:
   - Application type: "Desktop application"
   - Name: "Cookie Delivery Calendar Client"
   - Click "Create"

4. **Download Credentials**:
   - Click the download button next to your new credential
   - Save the file as: `calendar_credentials.json` in the `cookie_scheduler_agent/` folder

### 3. Test the MCP Server

1. **Start the MCP server**:
   ```bash
   cd /Users/johnlara/Google_Projects/adk-multi-tool-use/cookie_scheduler_agent
   python calendar_mcp_server.py
   ```

2. **Complete OAuth Flow**:
   - A web browser will open
   - Sign in to your Google account
   - Grant calendar permissions
   - The server will save tokens automatically

3. **Verify Setup**:
   - Look for "Calendar API authenticated successfully" in the logs
   - The server should be running and waiting for MCP requests

### 4. Test MCP Functionality

Run the test script to see example interactions:
```bash
python test_calendar_mcp.py
```

### 5. Connect to Your Agent

The next step will be updating your `agent.py` to use the MCP server instead of dummy data.

## File Structure After Setup

```
cookie_scheduler_agent/
├── calendar_mcp_server.py          # MCP server code
├── calendar_credentials.json       # OAuth credentials (keep secret!)
├── calendar_token.json            # Access tokens (auto-generated)
├── test_calendar_mcp.py           # Test script
├── agent.py                       # Your main agent
└── setup_calendar_credentials.md  # This guide
```

## Security Notes 🔒

- `calendar_credentials.json` is in .gitignore (won't be committed)
- `calendar_token.json` is in .gitignore (won't be committed)
-  **NEVER** share these files or commit them to version control
-  Tokens auto-refresh, so you only need to do OAuth flow once

## Troubleshooting

**Error: "calendar_credentials.json not found"**
- Complete Step 2 above to download credentials

**Error: "Access blocked"**
- Make sure your OAuth consent screen is properly configured
- Add your email as a test user if using external user type

**Error: "insufficient_scope"**
- Make sure Calendar API is enabled in Google Cloud Console
- Verify the OAuth consent screen includes calendar scope

## Next Steps

1. Complete this setup
2. Test the MCP server
3. Update `agent.py` to use real calendar instead of dummy data

Let me know when you've completed the Google Cloud setup and I'll help you connect everything!
