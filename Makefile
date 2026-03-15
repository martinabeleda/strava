.PHONY: sync format test itest run build-docker clean

sync:
	uv sync --frozen --dev

format:
	uv run ruff format .
	uv run ruff check --fix .

test: sync format
	uv run pytest

itest: test
	docker compose -f docker-compose.test.yml down -v || true
	docker compose -f docker-compose.test.yml up --build --wait
	uv run pytest tests/acceptance -v; \
	docker compose -f docker-compose.test.yml down -v

run:
	docker compose up

build-docker:
	docker build -t martinabeleda/strava .

clean:
	uv cache clean
	rm -rf .venv
