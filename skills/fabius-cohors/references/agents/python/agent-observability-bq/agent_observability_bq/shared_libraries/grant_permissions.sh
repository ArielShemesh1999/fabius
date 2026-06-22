#!/bin/bash
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Script to grant BigQuery dataset access permissions to Default Compute Service Account

set -e

# Load environment variables from .env file
SCRIPT_DIR="$(dirname "$0")"

# Prioritize .env in the current working directory (e.g., when run inside a scaffolded project)
if [ -f "$PWD/.env" ]; then
  ENV_FILE="$PWD/.env"
elif [ -f "${SCRIPT_DIR}/../../.env" ]; then
  ENV_FILE="${SCRIPT_DIR}/../../.env"
else
  echo "Warning: .env file not found"
fi

# Security: Parse variables instead of sourcing to avoid arbitrary code execution
if [ -n "$ENV_FILE" ] && [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
  GOOGLE_CLOUD_PROJECT=$(grep "^GOOGLE_CLOUD_PROJECT=" "$ENV_FILE" | cut -d= -f2- | tr -d "'\"")
fi
export GOOGLE_CLOUD_PROJECT

# Get the project ID from environment variable
PROJECT_ID="$GOOGLE_CLOUD_PROJECT"
if [ -z "$PROJECT_ID" ]; then
  PROJECT_ID=$(gcloud config get-value project)
fi

if [ -z "$PROJECT_ID" ]; then
  echo "No project ID found. Please set your project ID."
  exit 1
fi

PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
if [ -z "$PROJECT_NUMBER" ]; then
  echo "Failed to retrieve project number for project $PROJECT_ID"
  exit 1
fi

# Agents deployed to Agent Engine or Cloud Run use the Default Compute Service Account
# if no explicit service account is provided via Terraform.
SERVICE_ACCOUNT_COMPUTE="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
SERVICE_ACCOUNT_RE="service-${PROJECT_NUMBER}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"

# Note: roles/bigquery.dataEditor is broad at project level, but standard for this sample setup.
echo "Granting BigQuery permissions to Default Compute Service Account ($SERVICE_ACCOUNT_COMPUTE)..."

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_COMPUTE" \
  --role="roles/bigquery.dataEditor" > /dev/null

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_COMPUTE" \
  --role="roles/bigquery.jobUser" > /dev/null

echo "Granting BigQuery permissions to Agent Engine Service Agent ($SERVICE_ACCOUNT_RE)..."

# Guard: The Agent Engine service agent might not exist if it hasn't been initialized
if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT_RE" --project="$PROJECT_ID" > /dev/null 2>&1; then
    echo "Info: Agent Engine service agent not found. Skipping permissions for it (it will be created on first deploy)."
else
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
      --member="serviceAccount:$SERVICE_ACCOUNT_RE" \
      --role="roles/bigquery.dataEditor" > /dev/null

    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
      --member="serviceAccount:$SERVICE_ACCOUNT_RE" \
      --role="roles/bigquery.jobUser" > /dev/null
fi

echo "✅ BigQuery permissions granted successfully for both service accounts."
