import logging
from flask import Flask
from app.config import Config
from app.models import db

def create_app(config_class=Config):
    """Orchestrates application initialization factory pipelines."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize structured diagnostic logger patterns
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    # Initialize persistent ORM database layers
    db.init_app(app)

    # Register decoupled route clusters using blueprints
    from app.routes.core import core_bp
    app.register_blueprint(core_bp)

    return app

