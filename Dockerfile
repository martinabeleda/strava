FROM --platform=linux/amd64 python:3.9

WORKDIR /app/

RUN apt-get update && \
    apt-get install -yqq libgeos-dev libpq-dev

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-root --no-dev

COPY ./strava /app/strava

EXPOSE 8080

CMD ["uvicorn", "strava.main:app", "--host", "0.0.0.0", "--port", "8080"]
