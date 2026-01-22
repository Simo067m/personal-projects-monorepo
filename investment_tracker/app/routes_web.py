# All HTML-related routes for investment_tracker

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from .db import (
    get_portfolio_summary,
    get_portfolio_value,
    get_all_assets,
    get_asset_id_by_symbol,
    add_asset,
    add_transaction,
    add_price_to_history
)

# Define the blueprint
web = Blueprint('investment_web', __name__,
                template_folder='templates',
                static_folder='static')

@web.route("/")
def index():
    """Homepage for investment_tracker."""
    try:
        holdings = get_portfolio_summary()
        total_value_dkk = get_portfolio_value()
    except Exception as e:
        flash(f"Error: {e}", "error")
        holdings = {}
        total_value_dkk = 0.0
    
    return render_template("investment/index.html", holdings=holdings, total_value_dkk=total_value_dkk)

@web.route("/manage")
def manage():
    """Mnagement page."""
    try:
        assets = get_all_assets()
    except Exception as e:
        flash(f"Error: {e}", "error")
        assets = []
    
    return render_template("investment/manage.html", assets=assets)

@web.route("/add-asset", methods=["POST"])
def handle_add_asset():
    """Handles adding assets to the database."""

    symbol = request.form.get("symbol", "").strip().upper()
    name = request.form.get("name").strip()
    asset_type = request.form.get("asset_type")
    currency = request.form.get("currency").strip().upper()

    if not (symbol and name and asset_type and currency):
        flash("All fields are required to add an asset.", "warning")
        return redirect(url_for("investment_web.manage"))

    try:
        if get_asset_id_by_symbol(symbol):
            flash(f"Asset '{symbol}' already exists.", "warning")
        else:
            add_asset(symbol, name, asset_type, currency)
            flash(f"Successfully added asset '{symbol}'.", "success")

    except Exception as e:
        flash(f"Database error: {e}", "error")
    
    return redirect(url_for("investment_web.manage"))

@web.route("/add-transaction", methods=["POST"])
def handle_add_transaction():
    """Handles adding transactions to the database."""

    symbol = request.form.get("symbol", "").strip().upper()
    transaction_type = request.form.get("transaction_type")
    date = request.form.get("date")
    
    # Raw strings for math conversion
    raw_qty = request.form.get("quantity")
    raw_price = request.form.get("price_per_unit")
    raw_fees = request.form.get("fees")

    if not (symbol and transaction_type and date and raw_qty and raw_price):
        flash("Missing required fields.", "warning")
        return redirect(url_for("investment_web.manage"))

    try:
        # Data Conversion
        quantity = float(raw_qty)
        price = float(raw_price)
        fees = float(raw_fees) if raw_fees else 0.0

        asset_id = get_asset_id_by_symbol(symbol)
        if not asset_id:
            flash(f"Asset '{symbol}' not found. Please create it first.", "error")
            return redirect(url_for("investment_web.manage"))

        add_transaction(asset_id, transaction_type, date, quantity, price, fees)
        flash(f"Recorded {transaction_type} for {symbol}.", "success")

    except ValueError:
        # Catches "ten" instead of "10"
        flash("Invalid numbers. Please check Quantity, Price, and Fees.", "error")
    except Exception as e:
        # Catches Database errors
        flash(f"System error: {e}", "error")
    
    return redirect(url_for("investment_web.manage"))

@web.route("/add-price", methods=["POST"])
def handle_add_price():
    """Form Handler: Manual price history entry."""
    symbol = request.form.get("symbol", "").strip().upper()
    date = request.form.get("date")
    raw_price = request.form.get("price")

    if not (symbol and date and raw_price):
        flash("Symbol, Date, and Price are required.", "warning")
        return redirect(url_for("investment_web.manage"))

    try:
        price = float(raw_price)
        asset_id = get_asset_id_by_symbol(symbol)

        if not asset_id:
            flash(f"Asset '{symbol}' not found.", "error")
            return redirect(url_for("investment_web.manage"))

        add_price_to_history(asset_id, date, price)
        flash(f"Price updated for {symbol}.", "success")

    except ValueError:
        flash("Price must be a valid number.", "error")
    except Exception as e:
        if "UNIQUE constraint" in str(e):
            flash(f"Price for {symbol} on {date} already exists.", "warning")
        else:
            flash(f"Error: {e}", "error")

    return redirect(url_for("investment_web.manage"))