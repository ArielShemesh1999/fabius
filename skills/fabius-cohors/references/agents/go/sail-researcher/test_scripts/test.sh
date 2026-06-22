#!/bin/bash

BASEURL="http://localhost:8081"
APPNAME="researcher_agent"
USER="testuser"
SESSION="testsession"

SESSION_ENDPOINT="${BASEURL}/api/apps/${APPNAME}/users/${USER}/sessions/${SESSION}"

# Make the curl call
curl -X POST "$SESSION_ENDPOINT"

# Endpoint for invoking the resaearcher agent
ENDPOINT="${BASEURL}/api/run"

# Sample boat query
QUERY="{
    \"appName\": \"${APPNAME}\",
    \"userId\": \"${USER}\",
    \"sessionId\": \"${SESSION}\",
    \"newMessage\": {
        \"role\": \"user\",
        \"parts\": [{
        \"text\": \"Research anchorages and weather for 48.75 N, 123.22 W (Poets Cove) for July 15, 2026. Radius 5nm.\"
        }]
    }
}"

# Make the curl call
curl -X POST \
     -H "Content-Type: application/json" \
     -d "$QUERY" \
     "$ENDPOINT" | jq .
