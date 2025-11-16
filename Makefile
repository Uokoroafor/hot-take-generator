# Hot Take Generator - Full Stack Development Makefile

.PHONY: help install dev dev-backend dev-frontend stop clean test lint format check setup-env

# Variables
BACKEND_DIR = backend
FRONTEND_DIR = frontend
BACKEND_PID_FILE = .backend.pid
FRONTEND_PID_FILE = .frontend.pid

help: ## Show this help message
	@echo "Hot Take Generator - Development Commands"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies (backend and frontend)
	@echo "🔧 Installing backend dependencies..."
	cd $(BACKEND_DIR) && uv sync
	@echo "🔧 Installing frontend dependencies..."
	cd $(FRONTEND_DIR) && npm install
	@echo "✅ All dependencies installed!"

setup-env: ## Setup environment files
	@echo "🔧 Setting up environment files..."
	@if [ ! -f $(BACKEND_DIR)/.env ]; then \
		cp $(BACKEND_DIR)/.env.example $(BACKEND_DIR)/.env; \
		echo "Created backend/.env from .env.example"; \
		echo "⚠️  Please add your API keys to backend/.env"; \
	else \
		echo "backend/.env already exists"; \
	fi

dev: ## Run both backend and frontend in parallel
	@echo "🚀 Starting Hot Take Generator development servers..."
	@$(MAKE) setup-env
	@trap 'make stop' INT; \
	(cd $(BACKEND_DIR) && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) & \
	echo $$! > $(BACKEND_PID_FILE); \
	(cd $(FRONTEND_DIR) && npm run dev) & \
	echo $$! > $(FRONTEND_PID_FILE); \
	echo "🌐 Backend running at: http://localhost:8000"; \
	echo "🌐 Frontend running at: http://localhost:5173"; \
	echo "📋 API docs available at: http://localhost:8000/docs"; \
	echo ""; \
	echo "Press Ctrl+C to stop both servers"; \
	wait

dev-backend: ## Run only the backend server
	@echo "🚀 Starting backend server..."
	@$(MAKE) setup-env
	cd $(BACKEND_DIR) && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run only the frontend server
	@echo "🚀 Starting frontend server..."
	cd $(FRONTEND_DIR) && npm run dev

stop: ## Stop development servers
	@echo "🛑 Stopping development servers..."
	@if [ -f $(BACKEND_PID_FILE) ]; then \
		kill -TERM $$(cat $(BACKEND_PID_FILE)) 2>/dev/null || true; \
		rm -f $(BACKEND_PID_FILE); \
	fi
	@if [ -f $(FRONTEND_PID_FILE) ]; then \
		kill -TERM $$(cat $(FRONTEND_PID_FILE)) 2>/dev/null || true; \
		rm -f $(FRONTEND_PID_FILE); \
	fi
	@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@pkill -f "vite.*--port 5173" 2>/dev/null || true
	@echo "✅ Servers stopped"

test: ## Run all tests
	@echo "🧪 Running backend tests..."
	cd $(BACKEND_DIR) && uv run pytest -v
	@echo "🧪 Running frontend tests..."
	cd $(FRONTEND_DIR) && npm test 2>/dev/null || echo "No frontend tests configured"

test-backend: ## Run only backend tests
	@echo "🧪 Running backend tests..."
	cd $(BACKEND_DIR) && uv run pytest -v

test-watch: ## Run backend tests in watch mode
	@echo "🧪 Running backend tests in watch mode..."
	cd $(BACKEND_DIR) && uv run pytest -f

test-coverage: ## Run backend tests with coverage
	@echo "🧪 Running backend tests with coverage..."
	cd $(BACKEND_DIR) && uv run pytest --cov=app --cov-report=html --cov-report=term-missing

lint: ## Run linting on both backend and frontend
	@echo "🔍 Linting backend..."
	cd $(BACKEND_DIR) && uv run ruff check app tests
	@echo "🔍 Linting frontend..."
	cd $(FRONTEND_DIR) && npm run lint 2>/dev/null || echo "No frontend linting configured"

format: ## Format code for both backend and frontend
	@echo "✨ Formatting backend code..."
	cd $(BACKEND_DIR) && uv run black app tests && uv run ruff check --fix app tests
	@echo "✨ Formatting frontend code..."
	cd $(FRONTEND_DIR) && npm run format 2>/dev/null || echo "No frontend formatting configured"

clean: ## Clean up build artifacts and caches
	@echo "🧹 Cleaning up..."
	@rm -f $(BACKEND_PID_FILE) $(FRONTEND_PID_FILE)
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf $(BACKEND_DIR)/.pytest_cache 2>/dev/null || true
	@rm -rf $(BACKEND_DIR)/htmlcov 2>/dev/null || true
	@rm -rf $(FRONTEND_DIR)/node_modules/.cache 2>/dev/null || true
	@rm -rf $(FRONTEND_DIR)/dist 2>/dev/null || true
	@echo "✅ Cleanup complete"

build: ## Build production assets
	@echo "🏗️  Building production assets..."
	cd $(FRONTEND_DIR) && npm run build
	@echo "✅ Build complete"

check: ## Run all quality checks (lint, test, format check)
	@echo "🔍 Running quality checks..."
	cd $(BACKEND_DIR) && uv run ruff check app tests
	cd $(BACKEND_DIR) && uv run black --check app tests
	cd $(BACKEND_DIR) && uv run pytest -x
	@echo "✅ All checks passed"

# Health checks
health: ## Check if services are running
	@echo "🏥 Health check..."
	@curl -f http://localhost:8000/health 2>/dev/null && echo "✅ Backend is healthy" || echo "❌ Backend is not responding"
	@curl -f http://localhost:5173 2>/dev/null > /dev/null && echo "✅ Frontend is running" || echo "❌ Frontend is not responding"

logs-backend: ## Show backend logs
	@echo "📋 Backend logs (Ctrl+C to exit):"
	@tail -f uvicorn.log 2>/dev/null || echo "No backend log file found"

# Database and migration helpers (for future use)
db-reset: ## Reset database (placeholder for future)
	@echo "🗄️  Database reset not implemented yet"

# Docker commands
docker-build: ## Build Docker images
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-up: ## Start with Docker Compose (development)
	@echo "🐳 Starting with Docker Compose..."
	@$(MAKE) setup-env
	docker-compose up

docker-up-detached: ## Start with Docker Compose in background
	@echo "🐳 Starting with Docker Compose (detached)..."
	@$(MAKE) setup-env
	docker-compose up -d
	@echo "🌐 Backend running at: http://localhost:8000"
	@echo "🌐 Frontend running at: http://localhost:5173"
	@echo "📋 API docs available at: http://localhost:8000/docs"

docker-down: ## Stop Docker Compose services
	@echo "🐳 Stopping Docker Compose services..."
	docker-compose down

docker-restart: ## Restart Docker Compose services
	@echo "🐳 Restarting Docker Compose services..."
	docker-compose restart

docker-logs: ## Show Docker Compose logs
	@echo "📋 Docker Compose logs:"
	docker-compose logs -f

docker-logs-backend: ## Show backend container logs
	@echo "📋 Backend container logs:"
	docker-compose logs -f backend

docker-logs-frontend: ## Show frontend container logs
	@echo "📋 Frontend container logs:"
	docker-compose logs -f frontend

docker-shell-backend: ## Open shell in backend container
	@echo "🐚 Opening shell in backend container..."
	docker-compose exec backend /bin/bash

docker-shell-frontend: ## Open shell in frontend container
	@echo "🐚 Opening shell in frontend container..."
	docker-compose exec frontend /bin/sh

docker-clean: ## Clean up Docker containers, networks, and volumes
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Production Docker commands
docker-prod: ## Start production environment
	@echo "🐳 Starting production environment..."
	@$(MAKE) setup-env
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up

docker-prod-build: ## Build production Docker images
	@echo "🐳 Building production Docker images..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

docker-prod-detached: ## Start production environment in background
	@echo "🐳 Starting production environment (detached)..."
	@$(MAKE) setup-env
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "🌐 Application running at: http://localhost"
	@echo "📋 API docs available at: http://localhost/docs"

# Quick development workflows
quick-start: install dev ## Install dependencies and start development servers
quick-start-docker: setup-env docker-up-detached ## Setup and start with Docker

restart: stop dev ## Restart both development servers

# API testing helpers
test-api: ## Test API endpoints
	@echo "🧪 Testing API endpoints..."
	@echo "Testing health endpoint..."
	@curl -s http://localhost:8000/health | python -m json.tool 2>/dev/null || echo "Backend not running"
	@echo "\nTesting agents endpoint..."
	@curl -s http://localhost:8000/api/agents | python -m json.tool 2>/dev/null || echo "Backend not running"
	@echo "\nTesting styles endpoint..."
	@curl -s http://localhost:8000/api/styles | python -m json.tool 2>/dev/null || echo "Backend not running"

# Deployment helpers
deploy-check: ## Check if ready for deployment
	@echo "🚀 Deployment readiness check..."
	@$(MAKE) check
	@$(MAKE) build
	@echo "✅ Ready for deployment"

# Development info
info: ## Show development information
	@echo "Hot Take Generator - Development Info"
	@echo "====================================="
	@echo "Backend:"
	@echo "  📁 Directory: $(BACKEND_DIR)"
	@echo "  🌐 URL: http://localhost:8000"
	@echo "  📋 API Docs: http://localhost:8000/docs"
	@echo "  🔧 Tech: FastAPI + Python + UV"
	@echo ""
	@echo "Frontend:"
	@echo "  📁 Directory: $(FRONTEND_DIR)"
	@echo "  🌐 URL: http://localhost:5173"
	@echo "  🔧 Tech: React + TypeScript + Vite"
	@echo ""
	@echo "Commands:"
	@echo "  make dev               # Start both servers (native)"
	@echo "  make docker-up         # Start both servers (Docker)"
	@echo "  make test              # Run all tests"
	@echo "  make check             # Run quality checks"
	@echo "  make help              # Show all commands"
	@echo ""
	@echo "Docker:"
	@echo "  🌐 Dev: http://localhost:8000 (backend), http://localhost:5173 (frontend)"
	@echo "  🌐 Prod: http://localhost (all services)"
