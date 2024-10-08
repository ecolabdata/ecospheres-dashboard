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

## chartsgouv / dsfr

On applique les personnalisations de https://github.com/etalab-ia/chartsgouv/, mais notre installation est basée sur Pypi plutôt que Docker. Il faut donc les adapter.

`app.py` est un wrapper autour de `superset.app.Superset` qui permet de définir de spécifier :
- le chemin "local" `templates` pour les surcharges de templates, ainsi que le chemin `templates` du package `superset`
- le chemin "local" `static` pour les surcharges de templates, ainsi que le chemin `static` du package `superset`

Ce comportement n'est pas directement prévu par `Flask`, il faut donc attaquer les méthodes `send_static_file` et `jinja_loader`.

On retrouve ensuite les personnalisations de `chartsgouv` :
- surcharges de templates dans `templates/*`
- surcharges de styles dans `static/*`
- inclusion du DSFR dans `static/dsfr/*`
- modification de `superset_config.py` afin de paraméter les couleurs de thème
