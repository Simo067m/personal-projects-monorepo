from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify
)

from .db import (
    get_portfolio_summary,
    get_portfolio_value,
    get_all_assets,
    add_price_to_history,
    add_asset,
    add_transaction,
    get_asset_id_by_symbol,
    get_price_history
)

app = Flask(__name__)

@app.route("/")
def index():
    """Homepage."""
    # Get the data
    holdings_data = get_portfolio_summary()
    total_value_dkk = get_portfolio_value()

    # Pass data to the template
    return render_template("index.html",
                           holdings = holdings_data,
                           total_value = total_value_dkk)

@app.route("/manage")
def manage():
    """Price editing page."""
    # Get the data
    all_assets = get_all_assets()

    # Pass data to the template
    return render_template("manage.html", assets=all_assets)

@app.route("/add-asset", methods=["POST"])
def handle_add_asset():
    """Handles adding assets to the database."""

    # Get the data
    symbol = request.form.get("symbol")
    name = request.form.get("name")
    asset_type = request.form.get("asset_type")
    currency = request.form.get("currency")

    if symbol and name and asset_type and currency:
        try:
            # Check if asset already exists
            existing_asset_id = get_asset_id_by_symbol(symbol)

            if not existing_asset_id:
                add_asset(symbol.upper(), name, asset_type, currency.upper())
                print(f"Successfully added asset {symbol}.")
            else:
                print(f"Error: Asset with symbol {symbol} already exists.")

        except Exception as e:
            print(f"An error occured: {e}")
    
    return redirect(url_for("manage"))

@app.route("/add-transaction", methods=["POST"])
def handle_add_transaction():
    """Handles adding transactions to the database."""

    # Get the data
    symbol = request.form.get("symbol")
    transaction_type = request.form.get("transaction_type")
    date = request.form.get("date")
    quantity = request.form.get("quantity")
    price_per_unit = request.form.get("price_per_unit")
    fees = request.form.get("fees")

    if symbol and transaction_type and date and quantity and price_per_unit and fees:
        try:
            # Get the asset ID
            asset_id = get_asset_id_by_symbol(symbol)
            quantity_float = float(quantity)
            price_per_unit_float = float(price_per_unit)
            fees_float = float(fees)

            if asset_id:
                add_transaction(asset_id, transaction_type, date,
                                quantity_float, price_per_unit_float, fees_float)
                print(f"Successfully added transaction of {quantity_float} {symbol} for a unit price of {price_per_unit_float}.")
            else:
                print(f"Error: Asset with symbol {symbol} does not exist.")

        except Exception as e:
            print(f"An error occured: {e}")
    
    return redirect(url_for("manage"))

@app.route("/add-price", methods=["POST"])
def handle_add_price():
    """Handles adding prices to the database."""

    # Get the data
    symbol = request.form.get("symbol")
    date = request.form.get("date")
    price = request.form.get("price")

    if symbol and date and price:
        try:
            # Get the asset ID
            asset_id = get_asset_id_by_symbol(symbol)
            price_float = float(price)

            if asset_id:
                add_price_to_history(asset_id, date, price_float)
                print(f"Successfully added price {price_float} for asset {symbol.upper()} on date {date}.")
            else:
                print(f"Error: Asset with symbol {symbol} does not exist.")

        except Exception as e:
            print(f"An error occured: {e}")
    
    return redirect(url_for("manage"))

# Data-Only API route
@app.route("/api/price-history/<int:asset_id>")
def api_get_price_history(asset_id):
    """
    This route is called by JavaScript.
    Gets the price history for a single asset ID as a JSON object.
    """

    history_data = get_price_history(asset_id)

    # Convert the data from a list of tuples to JSON
    formatted_data = []
    for data in history_data:
        formatted_data.append({
            "date" : data[0],
            "price" : data[1]
        })

    # Return as JSON
    return jsonify(formatted_data)