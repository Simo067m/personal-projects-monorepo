import sys
import os
import platform # To check if we are on Windows or Linux

from flask import Flask

# Import blueprints
from portal.routes import portal_bp
from finance.routes import finance_bp
from investment_tracker.app.routes_web import web as investment_web
from investment_tracker.app.routes_api import api as investment_api
from memberships.app.routes_web import web as memberships_web

# Import database modules
from investment_tracker.app import db as investment_db
from memberships.app import db as memberships_db

# Path setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)


def create_app(config_object=None):
    """Application factory. Creates and configures the Flask app.
    
    Args:
        config_object: Optional config class to load. If None, loads
                       the default config.py file. Pass a config class
                       during testing to get an isolated app instance.
    Usage:
        # Production (Gunicorn, direct run)
        app = create_app()

        # Testing
        app = create_app(TestConfig)
    """

    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Load config: use the provided object, or fall back to config.py
    if config_object is not None:
        app.config.from_object(config_object)
    else:
        import config
        app.secret_key = config.FLASK_SECRET
        # Point database at the real database file
        app.config["DATABASE"] = investment_db.DB_FILE

    # Register blueprints
    app.register_blueprint(portal_bp)
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(investment_web, url_prefix="/finance/investments")
    app.register_blueprint(investment_api, url_prefix="/finance/investments/api")
    app.register_blueprint(memberships_web, url_prefix="/finance/memberships")
    # Initialize database inside the app context
    with app.app_context():
        investment_db.initialize_database()
        memberships_db.initialize_database()

    return app


# Module-level app instance for Gunicorn and direct execution.
# Gunicorn expects a module-level `app` variable: `gunicorn -w 2 run:app`
#
# Tests and import-based tooling can opt out of import-time app creation
# (and the associated config/database side effects) by setting
# RUN_SKIP_APP_INIT=1 before importing this module.
app = None
if os.environ.get("RUN_SKIP_APP_INIT") != "1":
    app = create_app()

if __name__ == "__main__":
    if app is None:
        app = create_app()
    app.run(debug=True, port=5000)