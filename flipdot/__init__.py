import os
import json

from flask_openapi3 import Info, OpenAPI
from flask_swagger_ui import get_swaggerui_blueprint
from flask import send_file, Response
from flipdot import connector, fonts, clock
from apscheduler.schedulers.background import BackgroundScheduler

SWAGGER_URL = '/swagger'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/openapi.json'

def create_app(test_config=None):
    # create and configure the app
    app = OpenAPI(
        __name__,
        info=Info(title="Pixel Flipdot API", version="1.0"),
        doc_ui=False,
        instance_relative_config=True,
        static_url_path='/static',
    )
    # flask-swagger-ui 4 only renders documents whose version is openapi 3.0.n.
    app.openapi_version = "3.0.3"
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_file("config.json", load=json.load, silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    app.config.from_prefixed_env()

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.errorhandler(connector.UnknownDisplayError)
    def unknown_display(_error):
        return Response("No such display id", status=404)

    fonts.initialize()
    connector.start_pixel(
        app.config.get('PIXEL_PORT', '/dev/serial0'),
        app.config.get('PIXEL_PIN', 18),
        app.config.get('PIXEL_USE_MOCK', False),
        app.config.get('DISPLAY_IDS', [0]),
        eth_host=app.config.get('PIXEL_ETH_HOST'),
        eth_port=app.config.get('PIXEL_ETH_PORT'),
        baud=app.config.get('PIXEL_BAUD', 4800),
        controller_name=app.config.get('PIXEL_CONTROLLER', '8051'),
        controller_overrides_value=app.config.get('PIXEL_CONTROLLERS'),
        encoding_name=app.config.get('PIXEL_ENCODING'),
        color_mode_name=app.config.get('PIXEL_COLOR_MODE', 'mono'),
        rts_toggle=app.config.get('PIXEL_RTS_TOGGLE', False),
        rs485=app.config.get('PIXEL_RS485', False),
    )
    
    def tick():
        clock.tick()
    
    scheduler = BackgroundScheduler()
    if app.config.get('CLOCK', False):
        scheduler.add_job(id='clock-job', func=tick, trigger='interval', seconds=15)
    scheduler.start()
    
    @app.route("/openapi.json")
    @app.route("/swagger.json")
    def openapi_json():
        return app.api_doc
    
    @app.route("/")
    def index():
        return send_file("static/index.html")
    
    @app.route("/icons/<path:path>")
    def icon(path):
        return send_file(f"../icons/{path}.png")

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "Pixel Flipdot"
        },
    )
    app.register_blueprint(swaggerui_blueprint)

    from . import actions, info, display, text_helpers # needs to stay here (after connector.startpixel) because of python modules
    app.register_api(info.bp)
    app.register_api(display.bp)
    app.register_api(actions.bp)
    app.register_api(text_helpers.bp)

    return app