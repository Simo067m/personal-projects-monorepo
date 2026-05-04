from flask import Blueprint, render_template

finance_bp = Blueprint('finance', __name__,
                       template_folder='templates')

@finance_bp.route("/")
def index():
    return render_template("finance/index.html")