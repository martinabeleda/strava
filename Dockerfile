FROM python:3.13-slim AS builder

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
ENV UV_PROJECT_ENVIRONMENT=${VIRTUAL_ENV}

WORKDIR /app

RUN apt-get update && \
    apt-get install -yqq \
        gcc \
        libgeos-dev \
        libpq-dev \
        curl && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv "${VIRTUAL_ENV}"

# Install uv only in the builder image so the runtime stays close to production.
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ln -s /root/.local/bin/uv /usr/local/bin/uv

COPY pyproject.toml uv.lock README.md /app/
RUN uv sync --frozen --no-dev --no-install-project

COPY ./strava /app/strava
COPY ./alembic /app/alembic
COPY alembic.ini /app/alembic.ini
RUN uv sync --frozen --no-dev

FROM python:3.13-slim AS runtime

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

WORKDIR /app

RUN apt-get update && \
    apt-get install -yqq \
        libgeos-dev \
        libpq-dev \
        curl && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/strava /app/strava
COPY --from=builder /app/alembic /app/alembic
COPY --from=builder /app/alembic.ini /app/alembic.ini
COPY README.md /app/README.md

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "strava.main:app", "--host", "0.0.0.0", "--port", "8080"]
