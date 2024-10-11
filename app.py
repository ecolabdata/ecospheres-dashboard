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


# from superset source code
# https://github.com/apache/superset/blob/9c12b1c7dadf461c2cd88e7aa74f15337f9ad599/superset/app.py#L29
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

        return app

    # Make sure that bootstrap errors ALWAYS get logged
    except Exception as ex:
        logger.exception("Failed to create app")
        raise ex


class CustomSupersetApp(Flask):

    # superset package paths
    template_paths = [f"{superset.__path__[0]}/templates"]
    static_paths = [f"{superset.__path__[0]}/static"]

    # base fn extract from Flask's source code
    # https://github.com/pallets/flask/blob/2fec0b206c6e83ea813ab26597e15c96fab08be7/src/flask/app.py#L301
    def send_static_file(self, filename):
        """Iterate over local static folder and superset's one when serving static file"""
        if not self.has_static_folder or not self.static_folder:
            raise RuntimeError("'static_folder' must be set to serve static_files.")

        # send_file only knows to call get_send_file_max_age on the app,
        # call it here so it works for blueprints too.
        max_age = self.get_send_file_max_age(filename)

        candidates = self.static_paths[:]
        candidates.append(self.static_folder)

        for path in candidates:
            try:
                return send_from_directory(path, filename, max_age=max_age)
            except NotFound:
                continue

        raise NotFound()

    @locked_cached_property
    def jinja_loader(self):
        """Load templates from superset's templates folder and from the app's templates folder"""
        loaders = []
        parent_loader = super(CustomSupersetApp, self).jinja_loader
        if parent_loader:
            loaders.append(parent_loader)
        loaders += [FileSystemLoader(path) for path in self.template_paths]
        return ChoiceLoader(loaders)
