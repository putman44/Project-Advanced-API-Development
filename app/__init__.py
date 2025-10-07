from flask import Flask

# from app.extensions import ma / absolute path
from .extensions import ma, limiter, cache
from .models import db
from .blueprints.customers import customers_bp
from .blueprints.mechanics import mechanics_bp
from .blueprints.service_tickets import service_tickets_bp
from .blueprints.inventories import inventories_bp
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = "/api/docs"  # URL for exposing Swagger UI (without trailing '/')
API_URL = "/static/swagger_build/merged.yaml"  # Our API URL (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Your API's Name"}
)


def create_app(config_name):
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config.from_object(f"config.{config_name}")

    # initialize extensions
    ma.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # Register Blueprints
    app.register_blueprint(
        swaggerui_blueprint, url_prefix=SWAGGER_URL
    )  # Registering our swagger blueprint
    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
    app.register_blueprint(service_tickets_bp, url_prefix="/service_tickets")
    app.register_blueprint(inventories_bp, url_prefix="/inventories")

    return app
