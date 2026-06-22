#!/bin/bash

# BigQuery Setup Script for Cookie Delivery System
# This script sets up the BigQuery environment with tables and sample data

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required environment variables are set
check_environment() {
    print_status "Checking environment configuration..."
    
    # Try to load from .env if it exists
    if [ -f ".env" ]; then
        print_status "Loading environment variables from .env file..."
        export $(cat .env | grep -v '^#' | xargs)
    elif [ -f ".env" ]; then
        print_status "Loading environment variables from .env file..."
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
        print_error "GOOGLE_CLOUD_PROJECT environment variable is not set"
        print_status "Please set it in .env or run:"
        print_status "  export GOOGLE_CLOUD_PROJECT=your-project-id"
        exit 1
    fi
    
    print_success "Environment variables are configured"
    print_status "Using project: $GOOGLE_CLOUD_PROJECT"
}

# Check if gcloud is installed and authenticated
check_gcloud() {
    print_status "Checking Google Cloud CLI..."
    
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed"
        print_status "Please install it from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Not authenticated with Google Cloud"
        print_status "Please run: gcloud auth application-default login"
        exit 1
    fi
    
    # Set the project
    gcloud config set project $GOOGLE_CLOUD_PROJECT
    
    print_success "Google Cloud CLI is configured"
}

# Enable required APIs
enable_apis() {
    print_status "Enabling required Google Cloud APIs..."
    
    gcloud services enable bigquery.googleapis.com
    gcloud services enable logging.googleapis.com
    gcloud services enable discoveryengine.googleapis.com
    gcloud services enable dialogflow.googleapis.com
    gcloud services enable aiplatform.googleapis.com
    gcloud services enable cloudfunctions.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable aiplatform.googleapis.com            #Vertex AI API
    gcloud services enable analyticshub.googleapis.com          #Analytics Hub API
    gcloud services enable appoptimize.googleapis.com           #App Optimize API
    gcloud services enable artifactregistry.googleapis.com      #Artifact Registry API
    gcloud services enable bigquery.googleapis.com              #BigQuery API
    gcloud services enable bigqueryconnection.googleapis.com    #BigQuery Connection API
    gcloud services enable bigquerydatapolicy.googleapis.com    #BigQuery Data Policy API
    gcloud services enable bigquerymigration.googleapis.com     #BigQuery Migration API
    gcloud services enable bigqueryreservation.googleapis.com   #BigQuery Reservation API
    gcloud services enable bigquerystorage.googleapis.com       #BigQuery Storage API
    gcloud services enable calendar-json.googleapis.com         #Google Calendar API
    gcloud services enable loudaicompanion.googleapis.com      #Gemini for Google Cloud API
    gcloud services enable cloudapis.googleapis.com             #Google Cloud APIs
    gcloud services enable cloudasset.googleapis.com            #Cloud Asset API
    gcloud services enable cloudbuild.googleapis.com            #Cloud Build API
    gcloud services enable cloudresourcemanager.googleapis.com  #Cloud Resource Manager API
    gcloud services enable cloudtrace.googleapis.com            #Cloud Trace API
    gcloud services enable compute.googleapis.com               #Compute Engine API
    gcloud services enable containerregistry.googleapis.com     #Container Registry API
    gcloud services enable dataform.googleapis.com              #Dataform API
    gcloud services enable dataplex.googleapis.com              #Cloud Dataplex API
    gcloud services enable datastore.googleapis.com             #Cloud Datastore API
    gcloud services enable dialogflow.googleapis.com            #Dialogflow API
    gcloud services enable discoveryengine.googleapis.com       #Discovery Engine API
    gcloud services enable geminicloudassist.googleapis.com     #Gemini Cloud Assist API
    gcloud services enable iam.googleapis.com                   #Identity and Access Management (IAM) API
    gcloud services enable iamcredentials.googleapis.com        #IAM Service Account Credentials API
    gcloud services enable logging.googleapis.com               #Cloud Logging API
    gcloud services enable monitoring.googleapis.com            #Cloud Monitoring API
    gcloud services enable oslogin.googleapis.com               #Cloud OS Login API
    gcloud services enable pubsub.googleapis.com                #Cloud Pub/Sub API
    gcloud services enable recommender.googleapis.com           #Recommender API
    gcloud services enable servicemanagement.googleapis.com     #Service Management API
    gcloud services enable serviceusage.googleapis.com          #Service Usage API
    gcloud services enable sql-component.googleapis.com         #Cloud SQL
    gcloud services enable storage-api.googleapis.com           #Google Cloud Storage JSON API
    gcloud services enable storage-component.googleapis.com     #Cloud Storage
    gcloud services enable storage.googleapis.com               #Cloud Storage API

    print_success "APIs enabled successfully"
}

# Check if Python dependencies are installed
check_python_deps() {
    print_status "Checking Python dependencies..."
    
    if ! python3 -c "import google.cloud.bigquery" 2>/dev/null; then
        print_error "google-cloud-bigquery is not installed"
        print_status "Installing Python dependencies..."
        if [ -f "cookie_scheduler_agent/requirements.txt" ]; then
            pip3 install -r cookie_scheduler_agent/requirements.txt
        elif [ -f "requirements.txt" ]; then
            pip3 install -r requirements.txt
        else
            pip3 install google-cloud-bigquery google-auth
        fi
    fi
    
    print_success "Python dependencies are available"
}

# Create BigQuery dataset and tables
setup_bigquery() {
    print_status "Setting up BigQuery environment..."
    
    # Run the Python setup script from the bigquery-setup directory
    python3 bigquery-setup/create_bigquery_environment.py
    
    if [ $? -eq 0 ]; then
        print_success "BigQuery environment created successfully"
    else
        print_error "Failed to setup BigQuery environment"
        exit 1
    fi
}

# Verify the setup
verify_setup() {
    print_status "Verifying BigQuery setup..."
    
    # Check if dataset exists using bq command
    if bq show --dataset $GOOGLE_CLOUD_PROJECT:cookie_delivery &> /dev/null; then
        print_success "Dataset 'cookie_delivery' exists"
    else
        print_error "Dataset 'cookie_delivery' not found"
        exit 1
    fi
    
    # Check if table exists and has data
    ROW_COUNT=$(bq query --use_legacy_sql=false --format=csv "SELECT COUNT(*) as count FROM \`$GOOGLE_CLOUD_PROJECT.cookie_delivery.orders\`" 2>/dev/null | tail -n 1)
    
    if [ "$ROW_COUNT" -gt 0 ] 2>/dev/null; then
        print_success "Table 'orders' exists with $ROW_COUNT rows of sample data"
    else
        print_warning "Table 'orders' exists but may not have sample data"
    fi
}

# Show sample data
show_sample_data() {
    print_status "Sample data in the orders table:"
    
    bq query --use_legacy_sql=false --format=prettyjson --max_rows=3 "
    SELECT 
        order_number,
        customer_name,
        customer_email,
        order_status,
        total_amount,
        delivery_request_date
    FROM \`$GOOGLE_CLOUD_PROJECT.cookie_delivery.orders\`
    ORDER BY created_at DESC
    LIMIT 3
    " 2>/dev/null || print_warning "Could not display sample data"
}

# Test the integration
test_integration() {
    print_status "Testing BigQuery integration..."
    
    if [ -f "bigquery-setup/test_bigquery.py" ]; then
        cd bigquery-setup
        python3 test_bigquery.py
        cd ..
        print_success "Integration test completed"
    else
        print_warning "Test script not found, skipping integration test"
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "Cookie Delivery BigQuery Setup Script"
    echo "=========================================="
    echo
    
    check_environment
    check_gcloud
    enable_apis
    check_python_deps
    setup_bigquery
    verify_setup
    show_sample_data
    test_integration
    
    echo
    print_success "BigQuery setup completed successfully!"
    echo
    print_status "Next steps:"
    print_status "1. Edit .env and set USE_BIGQUERY=true"
    print_status "2. Run the agent: cd cookie_scheduler_agent && python agent.py"
    echo
    print_status "To view your data in BigQuery, visit:"
    print_status "  https://console.cloud.google.com/bigquery?project=$GOOGLE_CLOUD_PROJECT"
    echo
}

# Run the main function
main "$@"



