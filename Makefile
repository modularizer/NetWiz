# NetWiz Makefile for running tests and development commands

.PHONY: help test test-backend test-frontend test-integration test-e2e test-all install dev clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

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
	python -m pytest tests/integration/ -v

test-e2e: ## Run end-to-end tests (requires selenium)
	python -m pytest tests/e2e/ -v

test-all: test-backend test-frontend test-integration ## Run all tests

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	cd frontend && rm -rf node_modules build coverage
	cd backend && rm -rf .pytest_cache htmlcov

docker-test: ## Run tests in Docker containers
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

docker-dev: ## Start development environment with Docker
	docker-compose up --build
