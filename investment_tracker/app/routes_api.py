from flask import Blueprint, jsonify

from .db import get_price_history

# Define the blueprint
api = Blueprint('investment_tracker_api', __name__)

@api.route("/price-history/<int:asset_id>")
def get_history(asset_id):
    try:
        data = get_price_history(asset_id)
        formatted = [{"date": r[0], "price": r[1]} for r in data]
        return jsonify(formatted)
    except Exception as e:
        return jsonify({"error": str(e)}), 500