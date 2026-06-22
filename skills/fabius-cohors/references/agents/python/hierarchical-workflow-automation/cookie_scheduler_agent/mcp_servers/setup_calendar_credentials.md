# Google Calendar API Setup Instructions

## 1. Get Google Calendar API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Give it a name like "Cookie Delivery Calendar"
   - Click "Create"

5. Download the JSON file and save it as:
   ```
   /Users/johnlara/Google_Projects/adk-multi-tool-use/cookie_scheduler_agent/calendar_credentials.json
   ```

## 2. Required File Structure

After setup, you should have these files:
- `calendar_credentials.json` (downloaded from Google Cloud Console)
- `calendar_token.json` (will be created automatically during first OAuth flow)

## 3. Security Note

Never commit `calendar_credentials.json` or `calendar_token.json` to version control!
Add them to your .gitignore file.
