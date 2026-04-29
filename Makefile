.PHONY: dev dev-backend dev-frontend build test lint install migrate

dev:
	docker-compose up

dev-backend:
	cd backend && uv run uvicorn api.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

build:
	docker-compose build

install:
	cd backend && uv sync --extra dev
	cd frontend && npm install

test:
	cd backend && SECRET_KEY=test-secret-key JWT_SECRET=test-jwt-secret uv run python -m pytest --cov=src --cov=api --cov-report=term-missing
	cd frontend && npm run test

lint:
	cd backend && uv run ruff check . && uv run mypy src/
	cd frontend && npm run lint && npm run type-check

migrate:
	cd backend && uv run alembic upgrade head

db-revision:
	cd backend && uv run alembic revision --autogenerate -m "$(msg)"

clean:
	docker-compose down -v
