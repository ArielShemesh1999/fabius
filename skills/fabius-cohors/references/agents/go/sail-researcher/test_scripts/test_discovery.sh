#!/bin/bash

BASEURL="http://localhost:8081"
APPNAME="discovery_agent"
USER="testuser"
SESSION="testsession_discovery"

SESSION_ENDPOINT="${BASEURL}/api/apps/${APPNAME}/users/${USER}/sessions/${SESSION}"

# Delete existing session to ensure fresh state
echo "Deleting existing session..."
curl -X DELETE "$SESSION_ENDPOINT"
echo ""

# Make the curl call to initialize session with state
echo "Initializing session..."
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"state": {"Month": "September"}}' \
     "$SESSION_ENDPOINT"
echo ""

# Endpoint for invoking the agent
ENDPOINT="${BASEURL}/api/run"

# Sample discovery query for September
QUERY="{
    \"appName\": \"${APPNAME}\",
    \"userId\": \"${USER}\",
    \"sessionId\": \"${SESSION}\",
    \"newMessage\": {
        \"role\": \"user\",
        \"parts\": [{
        \"text\": \"Find sailing destinations.\"
        }]
    }
}"

echo "Sending query..."
# Make the curl call
curl -X POST \
     -H "Content-Type: application/json" \
     -d "$QUERY" \
     "$ENDPOINT" | jq .