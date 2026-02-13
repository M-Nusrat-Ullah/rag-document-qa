.PHONY: install run test lint docker-build docker-run clean

# Install dependencies
install:
	pip install -r requirements.txt

# Install dev dependencies
install-dev:
	pip install -r requirements.txt -r requirements-dev.txt

# Run application
run:
	python -m src.api.main

# Run with uvicorn (hot reload)
dev:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	pytest tests/ -v --cov=src --cov-report=html

# Lint code
lint:
	black src/ tests/
	isort src/ tests/
	flake8 src/ tests/

# Docker build
docker-build:
	docker build -t rag-document-qa:latest -f docker/Dockerfile .

# Docker run
docker-run:
	docker-compose -f docker/docker-compose.yml up

# Clean
clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +