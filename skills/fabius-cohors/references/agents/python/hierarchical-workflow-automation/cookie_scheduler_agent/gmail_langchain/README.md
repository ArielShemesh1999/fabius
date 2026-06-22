# Gmail LangChain Integration

This module provides Gmail functionality for the cookie delivery agent using the LangChain Community Gmail toolkit.

## Features

- **Email Sending**: Send HTML and plain text emails via Gmail API
- **Message Search**: Search Gmail with powerful query syntax
- **Message Retrieval**: Get specific emails and thread details
- **OAuth2 Authentication**: Secure authentication with automatic token refresh
- **Error Handling**: Graceful fallback when Gmail is not configured

## File Structure

```
gmail-langchain/
├── __init__.py                 # Package initialization and exports
├── gmail_manager.py           # Main LangChain Gmail manager class
├── email_utils.py             # Utility functions for agent integration
├── test_gmail_integration.py  # Test script for Gmail functionality
├── gmail_credentials.json     # OAuth2 credentials (you create)
├── gmail_token.json          # Auto-generated tokens
└── README.md                 # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install langchain-community langchain-core
```

### 2. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Gmail API
3. Go to "Credentials" section
4. Click "Create Credentials" > "OAuth 2.0 Client ID"
5. Choose "Desktop Application"
6. Download the JSON file
7. Save it as `gmail_credentials.json` in this directory

### 3. Configure Environment

Add to your `.env` file:

```bash
USE_GMAIL_LANGCHAIN=true
BUSINESS_EMAIL=deliveries@yourbusiness.com
```

### 4. Test the Integration

```bash
python test_gmail_integration.py
```

This will trigger the OAuth2 authentication flow on first run.

## Usage

### In Agent Code

```python
from gmail_langchain import gmail_manager, send_confirmation_email_langchain

# Check availability
if gmail_manager.is_available():
    # Send email
    result = send_confirmation_email_langchain(
        to="customer@example.com",
        subject="Your Cookie Delivery is Scheduled!",
        body="<html>...</html>"
    )
    print(f"Email sent: {result['status']}")
```

### Direct Manager Usage

```python
from gmail_langchain.gmail_manager import gmail_manager

# Send email
result = gmail_manager.send_email(
    to="customer@example.com",
    subject="Test Subject",
    body="<h1>Test Email</h1>",
    body_type="html"
)

# Search messages
search_result = gmail_manager.search_messages("from:me", max_results=5)

# Get message details
message = gmail_manager.get_message("message_id_here")
```

## Integration with Agent

The Gmail integration is designed to work seamlessly with the agent workflow:

1. **Agent checks availability**: Uses `USE_GMAIL_LANGCHAIN` environment variable
2. **Real Gmail**: If configured, sends actual emails via LangChain
3. **Fallback**: If not configured, uses dummy email data
4. **Logging**: Comprehensive logging shows which method is being used

## OAuth2 Scopes

The integration uses these Gmail API scopes:

- `gmail.send`: Send emails
- `gmail.readonly`: Read emails and threads
- `gmail.compose`: Compose emails
- `gmail.modify`: Modify email labels and properties

## Error Handling

The integration includes robust error handling:

- **Missing credentials**: Falls back to dummy data
- **Network issues**: Retries with exponential backoff
- **Authentication errors**: Provides clear setup instructions
- **API limits**: Respects Gmail API quotas and limits

## Security Considerations

- **Credentials**: Never commit `gmail_credentials.json` or `gmail_token.json`
- **Scopes**: Uses minimal required permissions
- **Tokens**: Automatic refresh prevents expired token issues
- **Business Account**: Designed for dedicated business Gmail account

## Troubleshooting

### Common Issues

1. **"LangChain Gmail toolkit not available"**
   - Install: `pip install langchain-community`

2. **"Gmail credentials file not found"**
   - Create `gmail_credentials.json` from Google Cloud Console

3. **"OAuth2 flow failed"**
   - Check Gmail API is enabled
   - Verify credentials file is valid
   - Ensure OAuth2 consent screen is configured

4. **"Failed to send email"**
   - Check internet connection
   - Verify Gmail API quotas
   - Check business email permissions

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

1. **Test First**: Always run `test_gmail_integration.py` before production use
2. **Business Account**: Use dedicated business Gmail account
3. **Environment Variables**: Keep configuration in `.env` file
4. **Error Handling**: Always check return status before assuming success
5. **Rate Limits**: Respect Gmail API quotas in production

## Integration Status

This Gmail integration follows the same architecture pattern as the Calendar MCP:
- Real service when configured
- Graceful fallback when not available
- Comprehensive error handling and logging
- Professional email formatting with business branding
