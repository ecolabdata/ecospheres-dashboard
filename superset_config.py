import os
from pathlib import Path

from flask import Response

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
REDIS_URL = os.getenv("REDIS_URL")

if not SQLALCHEMY_DATABASE_URI or not SECRET_KEY or not REDIS_URL:
    raise Exception("DATABASE_URL, SECRET_KEY and REDIS_URL must be set in the environment")

# https://superset.apache.org/docs/security/#public
PUBLIC_ROLE_LIKE = "Gamma"

# add caching like in https://github.com/apache/superset/blob/master/docker/pythonpath_dev/superset_config.py
CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_URL": REDIS_URL,
}
DATA_CACHE_CONFIG = CACHE_CONFIG

FEATURE_FLAGS = {
    # Required to filter on array fields, see https://github.com/ecolabdata/ecospheres/issues/541
    "ENABLE_TEMPLATE_PROCESSING": True,
}


def FLASK_APP_MUTATOR(app):
    @app.route("/robots.txt")
    def robots():
        robots_path = Path(__file__).parent / "robots.txt"
        return Response(robots_path.read_text(), mimetype="text/plain")
