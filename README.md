# ecospheres-catalog-dokku

Deploys a Metabase instance on dokku, for `ecospheres-catalog`.

Accessible via https://ecospheres-catalog.app.france.sh/.

This uses a dedicated postgres DB for metabase, identified by `DATABASE_URL`. The sole custom logic here is to map `DATABASE_URL` to `MB_DB_CONNECTION_URI` and build the original metabase image.

Another DB is used and managed by `ecospheres-catalog`, identified in this project by `DOKKU_POSTGRES_AQUA_URL`.


```shell
dokku postgres:link ecospheres-metabase ecospheres-catalog # internal data, this app
dokku postgres:link ecospheres-catalog ecospheres-catalog # business data, managed by ../ecospheres-catalog
dokku ports:add http:80:3000
```
