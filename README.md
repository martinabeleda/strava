# strava

A strava clone service for storing running, hiking and ski routes

## Developing

Run the service using docker-compose:

```shell
docker compose up --build
```

## Creating a new migration

To create a new migration, run the docker compose and open a shell into the service container:

```shell
docker exec -it strava-service-1 bash
```

Then use alembic's autogenerate feature:

```shell
alembic revision --autogenerate -m "Added route table"
```