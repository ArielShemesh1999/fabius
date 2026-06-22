# Makefile for Retail AI Location Strategy Agent
# Compatible with agent-starter-pack deployment

.PHONY: install dev playground ag-ui ag-ui-install lint test clean help

# ============================================================================
# LOCAL DEVELOPMENT
# ============================================================================

## Install dependencies
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $$HOME/.local/bin/env; }
	uv sync

## Run agent locally with ADK web UI
dev:
	uv run adk web . --port 8501

## Alias for dev
playground: dev

# ============================================================================
# AG-UI FRONTEND (Interactive Dashboard)
# ============================================================================

## Install AG-UI frontend dependencies
ag-ui-install:
	@echo "Installing AG-UI backend dependencies..."
	pip install -r app/frontend/backend/requirements.txt
	@echo "Installing AG-UI frontend dependencies..."
	cd app/frontend && npm install
	@if [ ! -f app/frontend/.env.local ]; then \
		cp app/frontend/.env.local.example app/frontend/.env.local; \
		echo "Created app/frontend/.env.local from example"; \
	fi
	@echo "AG-UI dependencies installed!"

## Run AG-UI frontend (backend + Next.js frontend)
ag-ui:
	@echo "Starting AG-UI servers..."
	@echo "Backend will run at http://localhost:8000"
	@echo "Frontend will run at http://localhost:3000"
	@echo ""
	@trap 'kill 0' INT; \
	(cd app/frontend/backend && python main.py) & \
	(cd app/frontend && npm run dev) & \
	wait

# ============================================================================
# CODE QUALITY
# ============================================================================

## Run linters (ruff, mypy, codespell)
lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .

# ============================================================================
# TESTING & UTILITIES
# ============================================================================

## Run tests
test:
	uv sync --dev
	uv run pytest tests/

## Clean build artifacts
clean:
	rm -rf .venv __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

## Show help
help:
	@echo "Retail AI Location Strategy Agent - Makefile Commands"
	@echo ""
	@echo "LOCAL DEVELOPMENT:"
	@echo "  make install     - Install dependencies with uv"
	@echo "  make dev         - Run agent locally with ADK web UI (port 8501)"
	@echo "  make playground  - Alias for 'make dev'"
	@echo ""
	@echo "AG-UI FRONTEND (Interactive Dashboard):"
	@echo "  make ag-ui-install - Install AG-UI frontend dependencies"
	@echo "  make ag-ui         - Run AG-UI frontend (backend:8000 + frontend:3000)"
	@echo ""
	@echo "CODE QUALITY:"
	@echo "  make lint        - Run linters (ruff, mypy, codespell)"
	@echo ""
	@echo "TESTING & UTILITIES:"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean build artifacts"
	@echo ""
	@echo "DEPLOYMENT:"
	@echo "  Use agent-starter-pack for deployment:"
	@echo "    pip install agent-starter-pack"
	@echo "    agent-starter-pack create my-agent -a adk@retail-ai-location-strategy"
	@echo ""
	@echo "AUTHENTICATION SETUP:"
	@echo "  For AI Studio (default):"
	@echo "    echo 'GOOGLE_GENAI_USE_VERTEXAI=FALSE' >> app/.env"
	@echo "    echo 'GOOGLE_API_KEY=your_key' >> app/.env"
	@echo "    echo 'MAPS_API_KEY=your_maps_key' >> app/.env"
	@echo ""
	@echo "  For Vertex AI:"
	@echo "    echo 'GOOGLE_GENAI_USE_VERTEXAI=TRUE' >> app/.env"
	@echo "    echo 'GOOGLE_CLOUD_PROJECT=your_project' >> app/.env"
	@echo "    echo 'GOOGLE_CLOUD_LOCATION=us-central1' >> app/.env"
	@echo "    echo 'MAPS_API_KEY=your_maps_key' >> app/.env"
