.PHONY: venv format check test acceptance-test itest coverage load-test load-test-report run build-docker clean
.DEFAULT_GOAL := venv

LOAD_TEST_REPORT_DIR ?= loadtest/reports
LOAD_TEST_REPORT_PREFIX ?= $(LOAD_TEST_REPORT_DIR)/locust

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

# Run locust with dashboard. Go to LOCUST_HOST to configure/run
load-test: venv
	uv run locust \
		--locustfile loadtest/locustfile.py \
		--host $${LOCUST_HOST:-http://localhost:8080} \

# Run locust in headless mode and generate reports locally
load-test-report: venv
	mkdir -p $(LOAD_TEST_REPORT_DIR)
	uv run locust \
		--headless \
		--locustfile loadtest/locustfile.py \
		--host $${LOCUST_HOST:-http://localhost:8080} \
		--users $${LOCUST_USERS:-10} \
		--spawn-rate $${LOCUST_SPAWN_RATE:-2} \
		--run-time $${LOCUST_RUN_TIME:-1m} \
		--html $(LOAD_TEST_REPORT_PREFIX).html \
		--csv $(LOAD_TEST_REPORT_PREFIX)

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
