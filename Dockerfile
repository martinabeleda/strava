FROM --platform=linux/amd64 python:3.13-slim

WORKDIR /app/

RUN apt-get update && \
    apt-get install -yqq \
        gcc \
        libgeos-dev \
        libpq-dev \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ln -s /root/.local/bin/uv /usr/local/bin/uv

# Install third-party dependencies first for better layer caching
COPY pyproject.toml README.md /app/
RUN uv sync --no-dev --no-install-project

# Copy the application code and install the project itself
COPY ./strava /app/strava
COPY ./alembic /app/alembic
COPY alembic.ini /app/alembic.ini
RUN uv sync --no-dev

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "strava.main:app", "--host", "0.0.0.0", "--port", "8080"]
