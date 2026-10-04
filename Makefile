.PHONY: dev test lint format compose-up compose-down

dev:
	uvicorn app.main:app --reload --port 8080

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

compose-up:
	docker compose up --build

compose-down:
	docker compose down

