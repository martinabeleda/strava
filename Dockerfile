FROM --platform=linux/amd64 python:3.11

WORKDIR /app/

RUN apt-get update && \
    apt-get install -yqq libgeos-dev libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ln -s /root/.local/bin/uv /usr/local/bin/uv

COPY pyproject.toml /app/

RUN uv sync --no-dev

COPY ./strava /app/strava
COPY ./alembic /app/alembic
COPY alembic.ini /app/alembic.ini

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "strava.main:app", "--host", "0.0.0.0", "--port", "8080"]
