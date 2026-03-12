.PHONY: sync format test itest run build-docker

sync:
	uv sync --frozen --dev

format:
	uv run ruff format .
	uv run ruff check --fix .

test:
	uv run pytest

itest:
	docker compose -f docker-compose.test.yml up --build --wait
	uv run pytest tests/acceptance -v; \
	docker compose -f docker-compose.test.yml down -v

run:
	docker compose up

build-docker:
	docker build -t martinabeleda/strava .
