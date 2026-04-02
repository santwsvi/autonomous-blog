.PHONY: dev infra stop test lint migrate seed openapi

infra: ## Start PostgreSQL + Redis
	podman compose --env-file /dev/null -f docker-compose.dev.yml up -d

stop: ## Stop infrastructure
	podman compose --env-file /dev/null -f docker-compose.dev.yml down

dev: infra ## Start API with hot reload
	@sleep 2
	uv run python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	uv run pytest tests/ -v

lint: ## Run linter
	uv run ruff check app/ tests/
	uv run ruff format --check app/ tests/

format: ## Format code
	uv run ruff check --fix app/ tests/
	uv run ruff format app/ tests/

migrate: ## Run database migrations
	uv run alembic upgrade head

migrate-new: ## Create new migration (usage: make migrate-new MSG="add xyz")
	uv run alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed database with initial data
	uv run python scripts/seed.py

openapi: ## Export OpenAPI spec
	uv run python scripts/generate_openapi.py
