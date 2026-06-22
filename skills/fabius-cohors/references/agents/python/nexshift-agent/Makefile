# NexShift Agent Makefile
# ========================
# Commands for development, testing, and deployment to GCP Agent Engine

.PHONY: install lint run run-cli eval eval-agent eval-case deploy deploy-check deploy-bucket deploy-list deploy-test deploy-delete gcp-enable-apis gcp-setup clean clean-deploy clean-all help

# =============================================================================
# Configuration - All values loaded from .env (see .env.example)
# =============================================================================
-include .env
PROJECT_ID ?= $(GOOGLE_CLOUD_PROJECT)
DEPLOY_LOCATION ?= $(or $(AGENT_ENGINE_LOCATION),us-central1)
STAGING_BUCKET ?= gs://$(PROJECT_ID)-nexshift-agent-staging
AGENT_NAME ?= nexshift-agent

# =============================================================================
# Development Commands
# =============================================================================

## Install dependencies via uv sync
install:
	uv sync

## Run linters and type checker
lint:
	uv sync --dev
	uv run codespell
	uv run ruff check .
	uv run ty check

## Run the agent in ADK web UI (default port 8001)
run:
	uv run adk web --port 8001

## Run the agent in CLI mode (interactive terminal)
run-cli:
	uv run adk run nexshift_agent

# =============================================================================
# Evaluation Commands
# =============================================================================

## Run all evaluation tests
eval:
	uv run pytest eval/test_agent_eval.py -v

## Run evaluation for a specific agent (e.g., make eval-agent AGENT=compliance)
AGENT ?= ""
eval-agent:
	uv run pytest eval/test_agent_eval.py -v -k "$(AGENT)"

## Run a specific test case (e.g., make eval-case CASE=validate_roster_with_explicit_id)
CASE ?= ""
eval-case:
	uv run pytest eval/test_agent_eval.py -v -k "$(CASE)"

# =============================================================================
# GCP Agent Engine Deployment Commands
# =============================================================================

## Check deployment dependencies
deploy-check:
	@echo "🔍 Checking deployment dependencies..."
	uv run python deployment/deploy.py check
	@echo ""
	@echo "🔍 Checking GCP authentication..."
	@gcloud auth application-default print-access-token > /dev/null 2>&1 && echo "✅ GCP authenticated" || (echo "❌ Not authenticated. Run: gcloud auth application-default login" && exit 1)
	@echo ""
	@echo "🔍 Checking project configuration..."
	@echo "   PROJECT_ID: $(PROJECT_ID)"
	@echo "   LOCATION: $(DEPLOY_LOCATION)"
	@if [ -z "$(AGENT_ENGINE_LOCATION)" ]; then \
		echo "   ⚠️  DEPLOY_LOCATION not set, using default: us-central1"; \
		echo "   📖 To change, see README.md for configuration instructions."; \
	fi
	@echo "   STAGING_BUCKET: $(STAGING_BUCKET)"
	@echo "   AGENT_NAME: $(AGENT_NAME)"

## Create staging bucket if it doesn't exist
deploy-bucket:
	@echo "🪣 Creating staging bucket $(STAGING_BUCKET)..."
	@gsutil ls $(STAGING_BUCKET) 2>/dev/null || gsutil mb -p $(PROJECT_ID) -l $(DEPLOY_LOCATION) $(STAGING_BUCKET)
	@echo "✅ Staging bucket ready"

## Deploy agent to GCP Agent Engine
deploy: deploy-check deploy-bucket
	@echo ""
	@echo "🚀 Deploying $(AGENT_NAME) to GCP Agent Engine..."
	uv run python deployment/deploy.py deploy \
		--project $(PROJECT_ID) \
		--location $(DEPLOY_LOCATION) \
		--name $(AGENT_NAME)
		
# Alias for 'make deploy' for backward compatibility
backend: deploy

## List deployed agents
deploy-list:
	@echo "📋 Listing deployed agents..."
	uv run python deployment/deploy.py list \
		--project $(PROJECT_ID) \
		--location $(DEPLOY_LOCATION)

## Test deployed agent
deploy-test:
	@echo "🧪 Testing deployed agent..."
	uv run python deployment/deploy.py test \
		--project $(PROJECT_ID) \
		--location $(DEPLOY_LOCATION)

## Delete deployed agent
deploy-delete:
	@echo "🗑️  Deleting deployed agent..."
	uv run python deployment/deploy.py delete \
		--project $(PROJECT_ID) \
		--location $(DEPLOY_LOCATION)

# =============================================================================
# GCP Setup Commands
# =============================================================================

## Enable required GCP APIs
gcp-enable-apis:
	@echo "🔧 Enabling required GCP APIs..."
	gcloud services enable aiplatform.googleapis.com --project $(PROJECT_ID)
	gcloud services enable storage.googleapis.com --project $(PROJECT_ID)
	@echo "✅ APIs enabled"

## Full GCP setup (APIs + bucket)
gcp-setup: gcp-enable-apis deploy-bucket
	@echo ""
	@echo "✅ GCP setup complete!"
	@echo "   You can now run: make deploy"

# =============================================================================
# Cleanup Commands
# =============================================================================

## Clean Python cache files
clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

## Clean deployment artifacts
clean-deploy:
	rm -f deployment_info.json

## Full clean
clean-all: clean clean-deploy

# =============================================================================
# Help
# =============================================================================

## Show this help message
help:
	@echo "NexShift Agent - Makefile Commands"
	@echo "==================================="
	@echo ""
	@echo "Development:"
	@echo "  make install      - Install dependencies (uv sync)"
	@echo "  make run          - Run agent in ADK web UI (port 8001)"
	@echo "  make run-cli      - Run agent in CLI mode (interactive)"
	@echo "  make lint         - Run linters and type checker"
	@echo ""
	@echo "Evaluation:"
	@echo "  make eval         - Run all evaluation tests"
	@echo "  make eval-agent AGENT=compliance - Run tests for a specific agent"
	@echo "  make eval-case CASE=test_name    - Run a specific test case"
	@echo ""
	@echo "GCP Deployment:"
	@echo "  make deploy       - Deploy agent to GCP Agent Engine"
	@echo "  make deploy-check - Check deployment dependencies"
	@echo "  make deploy-bucket- Create staging bucket"
	@echo "  make deploy-list  - List deployed agents"
	@echo "  make deploy-test  - Test deployed agent"
	@echo "  make deploy-delete- Delete deployed agent"
	@echo ""
	@echo "GCP Setup:"
	@echo "  make gcp-enable-apis - Enable required APIs"
	@echo "  make gcp-setup    - Full GCP setup (APIs + bucket)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Clean Python cache files"
	@echo "  make clean-deploy - Clean deployment artifacts"
	@echo "  make clean-all    - Full clean"
	@echo ""
	@echo "Configuration (from .env - see .env.example):"
	@echo "  GOOGLE_CLOUD_PROJECT  = $(PROJECT_ID)"
	@echo "  AGENT_ENGINE_LOCATION = $(DEPLOY_LOCATION)"
	@echo "  STAGING_BUCKET        = $(STAGING_BUCKET)"
	@echo "  AGENT_NAME            = $(AGENT_NAME)"
	@echo ""
	@echo "Getting started:"
	@echo "  cp .env.example .env  # then edit .env with your values"
