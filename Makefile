.PHONY: help install run demo test clean docker-build docker-run docs

help:
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║          Translation API - Makefile Commands              ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "  make install       Install dependencies"
	@echo "  make run           Run the API server"
	@echo "  make demo          Run demo script"
	@echo "  make test          Run unit tests"
	@echo "  make clean         Remove cache and logs"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docker-run    Run Docker container"
	@echo "  make docker-stop   Stop Docker container"
	@echo "  make lint          Run code linting"
	@echo "  make format        Format code with black"
	@echo "  make health        Check API health"
	@echo ""

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

run:
	@echo "Starting Translation API..."
	python main.py

demo:
	@echo "Running demo script..."
	python demo.py

test:
	@echo "Running tests..."
	pip install pytest pytest-asyncio httpx
	pytest tests.py -v

clean:
	@echo "Cleaning cache and logs..."
	rm -rf __pycache__
	rm -rf logs/
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleaned"

docker-build:
	@echo "Building Docker image..."
	docker build -t translation-api .
	@echo "✓ Image built"

docker-run:
	@echo "Running Docker container..."
	docker run -p 8000:8000 --name translation-api translation-api
	@echo "✓ Container running on http://localhost:8000"

docker-stop:
	@echo "Stopping Docker container..."
	docker stop translation-api
	docker rm translation-api
	@echo "✓ Container stopped"

docker-compose-up:
	@echo "Starting with Docker Compose..."
	docker-compose up -d
	@echo "✓ API running on http://localhost:8000"

docker-compose-down:
	@echo "Stopping Docker Compose..."
	docker-compose down
	@echo "✓ Stopped"

lint:
	@echo "Linting code..."
	pip install flake8
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "✓ Linting complete"

format:
	@echo "Formatting code..."
	pip install black
	black . --line-length 88
	@echo "✓ Code formatted"

health:
	@echo "Checking API health..."
	curl -s http://localhost:8000/health | python -m json.tool
	@echo ""

docs:
	@echo "API Documentation:"
	@echo "  Swagger UI: http://localhost:8000/docs"
	@echo "  ReDoc: http://localhost:8000/redoc"
	@echo "  Full Docs: API_DOCUMENTATION.md"
	@echo "  Quick Start: QUICKSTART.md"
	@echo "  README: README.md"

logs:
	@echo "Showing recent logs..."
	tail -n 50 logs/translation_api.log

.DEFAULT_GOAL := help
