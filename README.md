# ecospheres-catalog-dokku

Deploys a Metabase instance on dokku, for `ecospheres-catalog`.

This uses a dedicated postgres DB for metabase, identified by `DATABASE_URL`. The sole custom logic here is to map `DATABASE_URL` to `MB_DB_CONNECTION_URI` and build the original metabase image.

Another DB is used and managed by `ecospheres-catalog`, identified in this project by `DOKKU_POSTGRES_AQUA_URL`.
