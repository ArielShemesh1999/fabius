# Install dependencies using uv package manager
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev
# Launch local dev playground
playground:
	@echo "==============================================================================="
	@echo "| 🚀 Starting your agent playground...                                        |"
	@echo "|                                                                             |"
	@echo "| 🔍 IMPORTANT: Select the 'app' folder to interact with your agent.          |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# Deploy the agent remotely
# Usage: make backend [PORT=8080] - Set IAP=true to enable Identity-Aware Proxy, PORT to specify container port
backend:
	PROJECT_ID=$$(gcloud config get-value project) && \
	gcloud beta run deploy short-movie-agents \
		--source . \
		--memory "4Gi" \
		--project $$PROJECT_ID \
		--region "europe-west4" \
		--no-cpu-throttling \
		--labels "created-by=adk,dev-tutorial=sample-short-movie-agents" \
		--allow-unauthenticated \
		--env-vars-file .env \
		$(if $(PORT),--port=$(PORT))

# Launch local development server with hot-reload
local-backend:
	uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload

# Run unit and integration tests
test:
	uv run pytest tests/unit && uv run pytest tests/integration

# Run code quality checks (codespell, ruff, mypy)
lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .