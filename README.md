# ecospheres-catalog-dokku-superset

Deploys a Superset instance on dokku, for `ecospheres-catalog`.

Accessible via https://ecospheres-catalog-superset.app.france.sh/.

This uses a dedicated postgres DB for superset, identified by `DATABASE_URL`.

Another DB is used and managed by `ecospheres-catalog`, identified in this project by `DOKKU_POSTGRES_AQUA_URL`.


```shell
dokku postgres:link ecospheres-superset ecospheres-catalog-superset # internal data, this app
dokku postgres:link ecospheres-catalog ecospheres-catalog-superset # business data, managed by ../ecospheres-catalog
dokku config:set SUPERSET_CONFIG_PATH=/app/superset_config.py FLASK_APP=superset
```
