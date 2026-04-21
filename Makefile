.PHONY: install run dev test lint docker-build docker-run docker-dev docker-down clean

# ==================
# Local Development
# ==================

install:
	pip install -r requirements.txt

run:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=src --cov-report=html

lint:
	black src/ tests/
	isort src/ tests/

# ==================
# Docker - Production
# ==================

docker-build:
	docker compose -f docker/docker-compose.yml build

docker-run:
	docker compose -f docker/docker-compose.yml up -d
	@echo "Waiting for services to start..."
	@sleep 10
	@echo "RAG API: http://localhost:8000/docs"
	@echo "Ollama: http://localhost:11434"

docker-down:
	docker compose -f docker/docker-compose.yml down

docker-logs:
	docker compose -f docker/docker-compose.yml logs -f

docker-status:
	docker compose -f docker/docker-compose.yml ps

# ==================
# Docker - Development
# ==================

docker-dev:
	docker compose -f docker/docker-compose.dev.yml up --build

docker-dev-down:
	docker compose -f docker/docker-compose.dev.yml down

# ==================
# Cleanup
# ==================

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf data/chroma_db

docker-clean:
	docker compose -f docker/docker-compose.yml down -v --rmi local
	docker system prune -f