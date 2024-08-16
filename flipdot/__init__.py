import os
import json

from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from flask import Flask, jsonify, send_file
from . import connector

SWAGGER_URL = '/swagger'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/swagger.json'  # Our API url (can of course be a local resource)

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_file("config.json", load=json.load, silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    connector.start_pixel(app.config.get('PIXEL_PORT', '/dev/serial0'), app.config.get('PIXEL_PIN', 18), app.config.get('PIXEL_USE_MOCK', False))
    
    @app.route("/swagger.json")
    def spec():
        return send_file("swagger.json")

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "Pixel Flipdot"
        },
    )
    app.register_blueprint(swaggerui_blueprint)

    from . import actions, info, display, text_helpers # needs to stay here (after connector.startpixel) because of python modules
    app.register_blueprint(info.bp)
    app.register_blueprint(display.bp)
    app.register_blueprint(actions.bp)
    app.register_blueprint(text_helpers.bp)

    return app