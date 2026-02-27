from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

web = Blueprint('health_web', __name__,
                template_folder='templates',
                static_folder='static')

@web.route("/")
def index():
    """Homepage for health_tracker."""
    return render_template("health/index.html")