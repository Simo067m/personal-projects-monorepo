import sys
import os
import config
import psutil
import platform # To check if we are on Windows or Linux

from flask import Flask, render_template, jsonify

# Import blueprints
from portal.routes import portal_bp as portal_bp
from investment_tracker.app.routes_web import web as investment_web
from investment_tracker.app.routes_api import api as investment_api

# Import database modules
from investment_tracker.app import db as investment_db

# Path setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

# Create Portal App
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = config.FLASK_SECRET

# Register blueprints
app.register_blueprint(portal_bp)
app.register_blueprint(investment_web, url_prefix="/investments")
app.register_blueprint(investment_api, url_prefix="/investments/api")

# Wrap the initialization in the app context so it knows WHERE to create the DB.
with app.app_context():
    investment_db.initialize_database()

if __name__ == "__main__":
    # Check database configuration
    investment_db.initialize_database()

    app.run(debug=True, port=5000)