# ecospheres-dashboard

Deploys a Superset instance on dokku.

This uses a dedicated postgres DB for superset, identified by `DATABASE_URL`.

Another DB is used and managed by `ecospheres-dashboard-backend`, identified in this project by `DOKKU_POSTGRES_AQUA_URL`.


```shell
dokku postgres:create dashboard
dokku postgres:link dashboard dashboard # internal data, this app
dokku postgres:link dashboard-backend dashboard # business data, managed by ../ecospheres-dashboard-backend
dokku config:set SUPERSET_CONFIG_PATH=/app/superset_config.py FLASK_APP=superset
```
