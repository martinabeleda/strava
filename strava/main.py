from fastapi import FastAPI

from strava.routes import routes

app = FastAPI()

app.include_router(routes.router)
