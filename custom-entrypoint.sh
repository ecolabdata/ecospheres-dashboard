#!/bin/sh

# map db config var
export MB_DB_CONNECTION_URI=$DATABASE_URL

# Call the original ENTRYPOINT
/app/run_metabase.sh "$@"
