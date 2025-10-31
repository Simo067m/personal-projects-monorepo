from flask import Flask, render_template

from .models import get_portfolio_summary

app = Flask(__name__)

# Define global variable to store holdings
holdings = {}

@app.route("/")
def index():
    holdings = get_portfolio_summary()
    return render_template("index.html", holdings = holdings)