.PHONY: up down restart logs seed test dev-api dev-web build clean

# Start all services
up:
	docker compose up -d

# Stop all services
down:
	docker compose down

# Restart all services
restart:
	docker compose down && docker compose up -d

# View logs
logs:
	docker compose logs -f

# Seed demo data
seed:
	cd services/api && python seed.py

# Run all tests
test:
	cd services/api && python -m pytest
	cd services/agents && python -m pytest

# Development servers
dev-api:
	cd services/api && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-web:
	cd web && npm run dev

# Build all Docker images
build:
	docker compose build

# Clean up volumes and data
clean:
	docker compose down -v
	rm -rf pgdata redis-data qdrant-data kafka-data zookeeper-data minio-data

# Pull Ollama models
ollama-setup:
	docker compose exec ollama ollama pull llama3:70b-instruct-q4_K_M
	docker compose exec ollama ollama pull mistral:7b-instruct-v0.3
	docker compose exec ollama ollama pull bge-m3

# Run agent evaluation
agent-eval:
	cd tests/agent-evals && python eval_full_pipeline.py
