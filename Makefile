# ============================================
# DevOps Agent — Makefile
# ============================================

.PHONY: help install run test docker-up docker-down clean lint

help: ## Show this help message
	@echo "DevOps Agent - Available Commands:"
	@echo "=================================="
	@echo "  make install      Install dependencies"
	@echo "  make run          Start the API server"
	@echo "  make run-agent    Run agent with a task"
	@echo "  make test         Run all tests"
	@echo "  make test-cov     Run tests with coverage"
	@echo "  make docker-up    Start all services with Docker"
	@echo "  make docker-down  Stop all Docker services"
	@echo "  make clean        Remove cache and temp files"
	@echo "  make lint         Run code linting"
	@echo "  make db-init      Initialize the database"

install: ## Install all dependencies
	pip install -r requirements.txt

run: ## Start the FastAPI server
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

run-agent: ## Run the agent with a task (usage: make run-agent TASK="your task")
	python -m agent.core "$(TASK)"

test: ## Run all tests
	pytest tests/ -v

test-cov: ## Run tests with coverage report
	pytest tests/ -v --cov=agent --cov=tools --cov=api --cov-report=html

docker-up: ## Start all services with Docker Compose
	docker-compose up -d --build

docker-down: ## Stop all Docker services
	docker-compose down

clean: ## Remove cache, temp files, and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage build dist *.egg-info

lint: ## Run code linting
	python -m py_compile agent/core.py
	python -m py_compile api/main.py

db-init: ## Initialize the database
	python -c "from api.models.database import init_db; init_db()"

worker: ## Start Celery worker
	celery -A workers.celery_app worker --loglevel=info

format: ## Format code
	black agent/ tools/ api/ workers/ safety/ tests/
	isort agent/ tools/ api/ workers/ safety/ tests/
