import os

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
PUBLIC_ROLE_LIKE = "Gamma"

if not SQLALCHEMY_DATABASE_URI or not SECRET_KEY:
    raise Exception("DATABASE_URL and SECRET_KEY must be set in the environment")

# does not work
# HTTP_HEADERS = {'X-Frame-Options': 'ALLOWALL'}
# OVERRIDE_HTTP_HEADERS = {'X-Frame-Options': 'ALLOWALL'}

# FIXME: move this in reverse proxy
# disable talisman to disable restrictive X-Frame-Options
TALISMAN_ENABLED = False
