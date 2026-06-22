# Load environment variables
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# Derived Database Configuration
NAVALLIST_DB_USER ?= navallist_user
NAVALLIST_DB_PASS ?= password
NAVALLIST_DB_NAME ?= navallistdb
NAVALLIST_DB_CONTAINER_NAME ?= navallist-db
NAVALLIST_DB_PORT ?= 5434
NAVALLIST_MIGRATE_PATH ?= migrations
NAVALLIST_MIGRATE_IMAGE ?= migrate/migrate

NAVALLIST_DB_CONNECTION_STRING ?= postgres://$(NAVALLIST_DB_USER):$(NAVALLIST_DB_PASS)@localhost:$(NAVALLIST_DB_PORT)/$(NAVALLIST_DB_NAME)?sslmode=disable

SHELL := /bin/bash

.PHONY: db-start db-stop db-status db-refresh db-console \
	migrate-up migrate-down migrate-reset migrate-create \
	run \
	test test-all dev

# -----------------------------------------------------------------------------
# Database Management
# -----------------------------------------------------------------------------
db-start:
	@if [ "$$(uname)" = "Darwin" ]; then \
		if ! podman info >/dev/null 2>&1; then \
			echo "Podman engine not reachable. Trying to start machine..."; \
			podman machine start 2>/dev/null || true; \
		fi; \
	fi
	@if [ ! "$$(podman ps -a --filter name=^$(NAVALLIST_DB_CONTAINER_NAME)$$ --format '{{.Names}}')" ]; then \
		echo "Creating and starting database container..."; \
		podman run --name $(NAVALLIST_DB_CONTAINER_NAME) -e POSTGRES_USER=$(NAVALLIST_DB_USER) -e POSTGRES_PASSWORD=$(NAVALLIST_DB_PASS) -e POSTGRES_DB=$(NAVALLIST_DB_NAME) -p $(NAVALLIST_DB_PORT):5432 -d postgres:15-alpine; \
	elif [ "$$(podman container inspect $(NAVALLIST_DB_CONTAINER_NAME) --format '{{.State.Running}}')" = "false" ]; then \
		echo "Starting existing database container..."; \
		podman start $(NAVALLIST_DB_CONTAINER_NAME); \
	else \
		echo "Database container is already running."; \
	fi
	@echo "Waiting for database to be ready..."
	@for i in {1..10}; do \
		if podman exec $(NAVALLIST_DB_CONTAINER_NAME) pg_isready -U $(NAVALLIST_DB_USER) -d $(NAVALLIST_DB_NAME) >/dev/null 2>&1; then \
			echo "Database is ready."; \
			$(MAKE) migrate-up; \
			exit 0; \
		fi; \
		echo "Waiting... ($$i/10)"; \
		sleep 2; \
	done; \
	echo "Error: Database failed to become ready in time."; \
	exit 1

db-stop:
	podman stop $(NAVALLIST_DB_CONTAINER_NAME) 2>/dev/null || true
	podman rm $(NAVALLIST_DB_CONTAINER_NAME) 2>/dev/null || true

db-status:
	@podman ps -a --filter name=^$(NAVALLIST_DB_CONTAINER_NAME)$$

db-console:
	podman exec -it $(NAVALLIST_DB_CONTAINER_NAME) psql -U $(NAVALLIST_DB_USER) -d $(NAVALLIST_DB_NAME)

# -----------------------------------------------------------------------------
# Migrations
# -----------------------------------------------------------------------------

migrate-up:
	@echo "--- [DEV] Migrating UP ---"
	podman run --rm -v $(PWD)/$(NAVALLIST_MIGRATE_PATH):/migrations --network host $(NAVALLIST_MIGRATE_IMAGE) \
		-path=/migrations -database "$(NAVALLIST_DB_CONNECTION_STRING)" up

migrate-down:
	@echo "--- [DEV] Migrating DOWN ---"
	podman run --rm -v $(PWD)/$(NAVALLIST_MIGRATE_PATH):/migrations --network host $(NAVALLIST_MIGRATE_IMAGE) \
		-path=/migrations -database "$(NAVALLIST_DB_CONNECTION_STRING)" down 1

migrate-reset:
	@echo "--- [DEV] Resetting Database ---"
	podman run --rm -v $(PWD)/$(NAVALLIST_MIGRATE_PATH):/migrations --network host $(NAVALLIST_MIGRATE_IMAGE) \
		-path=/migrations -database "$(NAVALLIST_DB_CONNECTION_STRING)" drop -f
	$(MAKE) migrate-up

migrate-create:
	@read -p "Enter migration name: " name; \
	podman run --rm -v $(PWD)/$(NAVALLIST_MIGRATE_PATH):/migrations $(NAVALLIST_MIGRATE_IMAGE) \
		create -ext sql -dir /migrations -seq $$name

# -----------------------------------------------------------------------------
# Runtime & Development
# -----------------------------------------------------------------------------

# Run everything locally
run: db-start
	@echo "Starting Main Backend (with Embedded Agent) on :8080..."
	mkdir -p data/artifacts
	NAVALLIST_DB_PORT=$(NAVALLIST_DB_PORT) \
	NAVALLIST_DB_USER=$(NAVALLIST_DB_USER) \
	NAVALLIST_DB_PASS=$(NAVALLIST_DB_PASS) \
	NAVALLIST_DB_NAME=$(NAVALLIST_DB_NAME) \
	NAVALLIST_FRONTEND_DIR=web \
	NAVALLIST_ARTIFACT_STORAGE=data/artifacts \
	NAVALLIST_SITE_URL=http://localhost:8080 \
	go run cmd/server/main.go

# -----------------------------------------------------------------------------
# Testing
# -----------------------------------------------------------------------------

test:
	@echo "--- Testing Backend ---"
	go test ./internal/... ./cmd/... -cover -count=1

test-all:
	@echo "--- Testing Backend (All) ---"
	NAVALLIST_DB_CONNECTION_STRING="$(NAVALLIST_DB_CONNECTION_STRING)" go test -tags integration ./... -cover
