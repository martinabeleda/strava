.PHONY: venv format test itest coverage run build-docker clean
.DEFAULT_GOAL := venv

venv:
	uv sync --frozen --dev

format:
	uv run ruff format .
	uv run ruff check --fix .

test: venv format
	uv run pytest tests -v --ignore=tests/acceptance --cov=strava --cov-report=term-missing

coverage: test

itest: test
	docker compose -f docker-compose.test.yml down -v || true
	docker compose -f docker-compose.test.yml up --build --wait
	uv run pytest tests/acceptance -v --cov=strava --cov-report=term-missing --cov-append; \
	docker compose -f docker-compose.test.yml down -v

run:
	docker compose down -v || true
	docker compose up --build

build-docker:
	docker build -t martinabeleda/strava .

clean:
	uv cache clean
	rm -rf .venv
	docker compose down -v || true
	docker compose -f docker-compose.test.yml down -v || true
	docker builder prune -f
