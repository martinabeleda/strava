.PHONY: venv format check test acceptance-test itest coverage load-test run build-docker clean
.DEFAULT_GOAL := venv

venv:
	uv sync --frozen --dev

format:
	uv run ruff format .
	uv run ruff check --fix .

check: venv
	uv run ruff format --check .
	uv run ruff check .
	uv run ty check

test: check
	uv run pytest tests -v --ignore=tests/acceptance --cov=strava --cov-report=term-missing

coverage: test

acceptance-test: check
	docker compose -f docker-compose.test.yml down -v || true
	docker compose -f docker-compose.test.yml up --build --wait
	uv run pytest tests/acceptance -v --cov=strava --cov-report=term-missing --cov-append; \
	docker compose -f docker-compose.test.yml down -v

itest: acceptance-test

load-test: venv
	uv run locust -f loadtest/locustfile.py --host $${LOCUST_HOST:-http://localhost:8080}

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
