import logging
import os
from typing import Optional

from flask import Flask, send_from_directory
from flask.helpers import locked_cached_property
from jinja2 import ChoiceLoader, FileSystemLoader
from werkzeug.exceptions import NotFound

import superset
from superset.initialization import SupersetAppInitializer

logger = logging.getLogger(__name__)


def create_app(superset_config_module: Optional[str] = None) -> Flask:
    app = CustomSupersetApp(__name__)

    try:
        # Allow user to override our config completely
        config_module = superset_config_module or os.environ.get(
            "SUPERSET_CONFIG", "superset.config"
        )
        app.config.from_object(config_module)

        app_initializer = app.config.get("APP_INITIALIZER", SupersetAppInitializer)(app)
        app_initializer.init_app()

        app.config["EXPLAIN_TEMPLATE_LOADING"] = True

        return app

    # Make sure that bootstrap errors ALWAYS get logged
    except Exception as ex:
        logger.exception("Failed to create app")
        raise ex


class CustomSupersetApp(Flask):

    template_paths = [superset.__path__[0] + "/templates"]
    static_paths = [superset.__path__[0] + "/static"]

    def send_static_file(self, filename):
        if not self.has_static_folder:
            raise RuntimeError("'static_folder' must be set to serve static_files.")

        # send_file only knows to call get_send_file_max_age on the app,
        # call it here so it works for blueprints too.
        max_age = self.get_send_file_max_age(filename)

        l = self.static_paths[:]
        l.append(self.static_folder)

        print("--------> STATIC", l)

        for path in l:
            try:
                return send_from_directory(path, filename, max_age=max_age)
            except NotFound:
                continue

        raise NotFound()


    @locked_cached_property
    def jinja_loader(self):
        parent_loader = super(CustomSupersetApp, self).jinja_loader
        loaders = [parent_loader]
        loaders += [FileSystemLoader(path) for path in self.template_paths]
        print("--------> PARENT", [l.searchpath for l in loaders])

        return ChoiceLoader(loaders)
