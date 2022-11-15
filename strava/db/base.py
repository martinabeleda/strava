# Import all the models, so that Base has them before being
# imported by Alembic
from strava.db.base_class import Base  # noqa
from strava.models.route import Route  # noqa