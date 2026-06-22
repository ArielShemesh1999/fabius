# --- RAG Agent Garden Hooks ---
# These targets inject interactive corpus setup into the Agent Starter Pack lifecycle

.PHONY: setup_corpus grant_permissions

# We declare `setup_corpus` as a prerequisite to the standard `install` target.
# When `make install` is run (by the user or Agent Garden), it executes this first.
install: setup_corpus

# We declare `grant_permissions` to entirely override or pre-empt the standard deployment 
# so we can securely inject the env var.
backend: grant_permissions

setup_corpus:
	@echo "==============================================================================="
	@echo "| RAG Corpus Setup                                                            |"
	@echo "==============================================================================="
	@touch .env
	@if ! grep -q "^GOOGLE_CLOUD_PROJECT=" .env; then \
		PROJECT_ID=$$(gcloud config get-value project); \
		echo "GOOGLE_CLOUD_PROJECT=$$PROJECT_ID" >> .env; \
	fi
	@if ! grep -q "^GOOGLE_CLOUD_LOCATION=" .env; then \
		echo "GOOGLE_CLOUD_LOCATION=us-east1" >> .env; \
	fi
	@read -p "Do you want to deploy the sample RAG corpus for this agent? (y/n) " deploy_corpus; \
	if [ "$$deploy_corpus" = "y" ] || [ "$$deploy_corpus" = "Y" ]; then \
		echo "Deploying RAG corpus..."; \
		if [ -f "rag/shared_libraries/prepare_corpus_and_data.py" ]; then \
			uv run python rag/shared_libraries/prepare_corpus_and_data.py; \
		else \
			echo "Warning: prepare_corpus_and_data.py not found in scaffolded project."; \
		fi \
	else \
		echo "Skipping RAG corpus deployment."; \
	fi

grant_permissions:
	@echo "==============================================================================="
	@echo "| Deploying Agent Engine with RAG Corpus & Granting Permissions               |"
	@echo "==============================================================================="
	@if [ ! -z "$$RAG_CORPUS" ] || grep -q "^RAG_CORPUS=" .env 2>/dev/null; then \
		CORPUS_VAL=$${RAG_CORPUS:-$$(grep "^RAG_CORPUS=" .env | cut -d '=' -f2- | tr -d "'\"")}; \
		echo "Injecting RAG_CORPUS=$$CORPUS_VAL via --set-env-vars..."; \
		(uv export --no-hashes --no-header --no-dev --no-emit-project --no-annotate > rag/app_utils/.requirements.txt 2>/dev/null || \
		uv export --no-hashes --no-header --no-dev --no-emit-project > rag/app_utils/.requirements.txt) && \
		uv run -m rag.app_utils.deploy \
			--source-packages=./rag \
			--entrypoint-module=rag.agent_engine_app \
			--entrypoint-object=agent_engine \
			--requirements-file=rag/app_utils/.requirements.txt \
			--set-env-vars="RAG_CORPUS=$$CORPUS_VAL" \
			$(if $(AGENT_IDENTITY),--agent-identity) \
			$(if $(filter command line,$(origin SECRETS)),--set-secrets="$(SECRETS)"); \
		if [ -f "rag/shared_libraries/grant_permissions.sh" ]; then \
			bash rag/shared_libraries/grant_permissions.sh; \
		else \
			echo "Warning: rag/shared_libraries/grant_permissions.sh not found."; \
		fi \
	else \
		echo "RAG_CORPUS not found. Falling back to standard deploy..."; \
		(uv export --no-hashes --no-header --no-dev --no-emit-project --no-annotate > rag/app_utils/.requirements.txt 2>/dev/null || \
		uv export --no-hashes --no-header --no-dev --no-emit-project > rag/app_utils/.requirements.txt) && \
		uv run -m rag.app_utils.deploy \
			--source-packages=./rag \
			--entrypoint-module=rag.agent_engine_app \
			--entrypoint-object=agent_engine \
			--requirements-file=rag/app_utils/.requirements.txt \
			$(if $(AGENT_IDENTITY),--agent-identity) \
			$(if $(filter command line,$(origin SECRETS)),--set-secrets="$(SECRETS)"); \
	fi