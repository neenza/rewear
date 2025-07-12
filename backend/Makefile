.PHONY: help dev-setup migrate run test docker-up docker-down lint format

help:
	@echo "Available commands:"
	@echo "  make dev-setup    - Set up development environment"
	@echo "  make migrate      - Run database migrations"
	@echo "  make run          - Run the FastAPI server"
	@echo "  make test         - Run tests"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make lint         - Run linting"
	@echo "  make format       - Format code"

dev-setup:
	@echo "Setting up development environment..."
	python -m venv venv
	@echo "Virtual environment created."
	@echo "To activate, run:"
	@echo "  On Windows: .\\venv\\Scripts\\activate"
	@echo "  On Unix/Mac: source venv/bin/activate"
	@echo "Then run: pip install -r requirements.txt"

migrate:
	@echo "Running database migrations..."
	alembic upgrade head

run:
	@echo "Starting FastAPI server..."
	uvicorn app.main:app --reload

test:
	@echo "Running tests..."
	pytest -v

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

lint:
	@echo "Running linting..."
	flake8 app tests

format:
	@echo "Formatting code..."
	black app tests
