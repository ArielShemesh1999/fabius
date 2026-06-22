#!/bin/bash

BASEURL="http://localhost:8081"
APPNAME="boat_agent"
USER="testuser"
SESSION="testsession"

# Endpoint for starting off the adk session
ENDPOINT_SESSION="${BASEURL}/api/apps/${APPNAME}/users/${USER}/sessions/${SESSION}"

# Make the curl call to start the session
curl -X POST "$ENDPOINT_SESSION"

# Endpoint for querying the boat agent
ENDPOINT_QUERY="${BASEURL}/api/run"

# Sample boat query, note the session info embedded in it. 
QUERY="{
    \"appName\": \"${APPNAME}\",
    \"userId\": \"${USER}\",
    \"sessionId\": \"${SESSION}\",
    \"newMessage\": {
        \"role\": \"user\",
        \"parts\": [{
        \"text\": \"Sun Odyssey 349\"
        }]
    }
}"

# Make the curl call
curl -X POST \
     -H "Content-Type: application/json" \
     -d "$QUERY" \
     "$ENDPOINT_QUERY" | jq .

