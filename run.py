import sys
import os
import config

from flask import Flask, render_template

# Import database modules
from investment_tracker.app import db as investment_db

# Path setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

# Create Portal App
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = config.FLASK_SECRET

# Import blueprints
from investment_tracker.app.routes_web import web as investment_web
from investment_tracker.app.routes_api import api as investment_api

# Register blueprints
app.register_blueprint(investment_web, url_prefix="/investments")
app.register_blueprint(investment_api, url_prefix="/investments/api")

# Define portal homepage
@app.route("/")
def portal_home():
    # This data could eventually come from a database
    my_apps = [
        {
            "name": "Investment Tracker",
            "description": "Manage portfolio, view graphs, and track assets.",
            "endpoint": "investment.index",
            "status": "active",
            "style": "primary"
        },
        {
            "name": "Crypto Bot",
            "description": "Automated trading algorithms.",
            "endpoint": "#", # No link yet
            "status": "disabled",
            "style": "secondary"
        }
    ]
    
    # We pass 'apps=my_apps' to the template so HTML can see it
    return render_template("portal_home.html", apps=my_apps)

if __name__ == "__main__":
    # Check database configuration
    investment_db.initialize_database()

    app.run(debug=True, port=5000)

    # When launching on pi
    # app.run(host='0.0.0.0', port=5000)