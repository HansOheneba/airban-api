from flask import Flask
from flask_cors import CORS
from config import Config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per minute", "30 per second"],
    storage_uri="memory://",
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize CORS
    CORS(app)  # Allow all origins for now

    # Initialize rate limiter
    limiter.init_app(app)

    # Initialize database pool after app creation
    with app.app_context():
        from .models import init_db_pool

        init_db_pool()

    # Register blueprints
    from .routes import main

    app.register_blueprint(main)

    return app
