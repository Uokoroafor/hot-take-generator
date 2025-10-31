# Hot Take Generator Backend - Makefile

.PHONY: help install test test-unit test-integration test-external test-coverage lint format dev clean

# Variables
PYTHON = uv run python
PYTEST = uv run pytest
UVICORN = uv run uvicorn

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with UV
	uv sync

test: ## Run all tests
	$(PYTEST) -v

test-unit: ## Run only unit tests
	$(PYTEST) -v -m "unit or not external"

test-integration: ## Run integration tests
	$(PYTEST) -v -m "integration"

test-external: ## Run tests that require external APIs
	$(PYTEST) -v -m "external"

test-coverage: ## Run tests with coverage report
	$(PYTEST) --cov=app --cov-report=html --cov-report=term-missing

test-watch: ## Run tests in watch mode
	$(PYTEST) -f

lint: ## Run linting checks
	uv run ruff check app tests
	uv run black --check app tests

format: ## Format code
	uv run black app tests
	uv run ruff check --fix app tests

dev: ## Start development server
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

dev-debug: ## Start development server with debug logging
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

clean: ## Clean up cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

setup-env: ## Copy .env.example to .env
	cp .env.example .env
	@echo "Remember to add your API keys to .env"

check: ## Run all quality checks
	$(MAKE) lint
	$(MAKE) test-unit
	@echo "All checks passed!"

ci: ## Run CI pipeline (for GitHub Actions)
	$(MAKE) install
	$(MAKE) lint
	$(MAKE) test

# Development helpers
logs: ## Show development server logs
	tail -f uvicorn.log

health: ## Check if API is running
	curl -f http://localhost:8000/health || echo "API not running"

test-api: ## Test API endpoints with curl
	@echo "Testing health endpoint..."
	curl -s http://localhost:8000/health | python -m json.tool
	@echo "\nTesting agents endpoint..."
	curl -s http://localhost:8000/api/agents | python -m json.tool
	@echo "\nTesting styles endpoint..."
	curl -s http://localhost:8000/api/styles | python -m json.tool