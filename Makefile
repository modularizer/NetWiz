# NetWiz Makefile for running tests and development commands

.PHONY: help test test-backend test-frontend test-integration test-e2e test-all install dev clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	cd backend && pip install -e .[dev]
	cd backend && pre-commit install
	cd frontend && npm install

install-backend: ## Install backend in development mode
	cd backend && pip install -e .[dev]
	cd backend && pre-commit install

install-backend-prod: ## Install backend for production
	cd backend && pip install .

setup-env: ## Setup environment files from examples
	@echo "Setting up environment files..."
	@if [ ! -f .env ]; then cp env.example.main .env; echo "Created .env from env.example.main"; fi
	@if [ ! -f backend/.env ]; then cp backend/env.example.backend backend/.env; echo "Created backend/.env from env.example.backend"; fi
	@echo "✅ Environment files setup complete!"

setup-env-backend: ## Setup only backend environment file
	@echo "Setting up backend environment file..."
	@if [ ! -f backend/.env ]; then cp backend/env.example.backend backend/.env; echo "Created backend/.env from env.example.backend"; fi
	@echo "✅ Backend environment file setup complete!"

setup-env-main: ## Setup only main environment file
	@echo "Setting up main environment file..."
	@if [ ! -f .env ]; then cp env.example.main .env; echo "Created .env from env.example.main"; fi
	@echo "✅ Main environment file setup complete!"

dev: ## Start development servers
	@echo "Starting development servers..."
	@echo "Backend: http://localhost:5000"
	@echo "Frontend: http://localhost:3000"
	@echo "MongoDB: mongodb://localhost:27017"
	docker-compose up -d mongodb
	cd backend && python app.py &
	cd frontend && npm start

test-backend: ## Run backend tests
	cd backend && python -m pytest tests/ -v

test-frontend: ## Run frontend tests
	cd frontend && npm test -- --coverage --watchAll=false

test-integration: ## Run integration tests
	cd backend && python -m pytest tests/integration/ -v

test-e2e: ## Run end-to-end tests (requires selenium)
	cd backend && python -m pytest tests/e2e/ -v

test-all: test-backend test-frontend test-integration ## Run all tests

sync-metadata: ## Sync metadata and dependencies from __init__.py and requirements files to pyproject.toml
	cd backend && python scripts/sync_metadata.py

check-metadata: ## Check if metadata is in sync between __init__.py and pyproject.toml
	cd backend && python scripts/sync_metadata.py --check

generate-openapi: ## Generate OpenAPI schema from FastAPI app
	cd backend && python scripts/generate_openapi.py --pretty

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	cd frontend && rm -rf node_modules build coverage
	cd backend && rm -rf .pytest_cache htmlcov

docker-dev: ## Start development environment with Docker (using .env files)
	docker-compose -f docker-compose.dev.yml up --build

docker-prod: ## Start production environment with Docker
	docker-compose up --build

docker-backend: ## Start only backend with Docker
	docker-compose -f docker-compose.dev.yml up --build backend mongodb

docker-test: ## Run tests in Docker containers
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

docker-stop: ## Stop all Docker containers
	docker-compose -f docker-compose.dev.yml down
	docker-compose down

docker-clean: ## Clean up Docker containers and volumes
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose down -v
	docker system prune -f
