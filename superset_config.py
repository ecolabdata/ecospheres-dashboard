import os

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
SECRET_KEY = "Ccdivw2Cmz53oUtXGPromUcEeGKkXM8H"
PUBLIC_ROLE_LIKE = "Gamma"

# does not work
# HTTP_HEADERS = {'X-Frame-Options': 'ALLOWALL'}
# OVERRIDE_HTTP_HEADERS = {'X-Frame-Options': 'ALLOWALL'}

# disable talisman to disable restrictive X-Frame-Options
TALISMAN_ENABLED = False
