from investment_tracker.app.db import (
    add_asset,
    get_asset_id_by_symbol,
    add_transaction,
    add_price_to_history,
    calculate_holdings,
    get_latest_price,
    get_portfolio_summary,
    delete_asset_by_id,
)


# --- Asset Tests ---

def test_add_and_retrieve_asset(app):
    with app.app_context():
        add_asset("AAPL", "Apple Inc.", "Stock", "USD")
        asset_id = get_asset_id_by_symbol("AAPL")
        assert asset_id is not None

def test_get_asset_id_is_case_insensitive(app):
    """Symbols should resolve regardless of the case passed in."""
    with app.app_context():
        add_asset("TSLA", "Tesla", "Stock", "USD")
        assert get_asset_id_by_symbol("tsla") is not None
        assert get_asset_id_by_symbol("TSLA") is not None

def test_get_asset_id_returns_none_for_unknown_symbol(app):
    with app.app_context():
        assert get_asset_id_by_symbol("UNKNOWN") is None


# --- Holdings / Transaction Tests ---

def test_calculate_holdings_after_buy(app):
    with app.app_context():
        add_asset("NOVO", "Novo Nordisk", "Stock", "DKK")
        asset_id = get_asset_id_by_symbol("NOVO")
        add_transaction(asset_id, "buy", "2024-01-01", 10.0, 500.0, 0.0)
        assert calculate_holdings(asset_id) == 10.0

def test_calculate_holdings_after_buy_and_sell(app):
    with app.app_context():
        add_asset("NOVO", "Novo Nordisk", "Stock", "DKK")
        asset_id = get_asset_id_by_symbol("NOVO")
        add_transaction(asset_id, "buy", "2024-01-01", 10.0, 500.0, 0.0)
        add_transaction(asset_id, "sell", "2024-06-01", 4.0, 600.0, 0.0)
        assert calculate_holdings(asset_id) == 6.0

def test_calculate_holdings_is_zero_with_no_transactions(app):
    with app.app_context():
        add_asset("NOVO", "Novo Nordisk", "Stock", "DKK")
        asset_id = get_asset_id_by_symbol("NOVO")
        assert calculate_holdings(asset_id) == 0


# --- Price History Tests ---

def test_get_latest_price_returns_most_recent(app):
    """Latest price should be the most recent by date, not insertion order."""
    with app.app_context():
        add_asset("AAPL", "Apple Inc.", "Stock", "USD")
        asset_id = get_asset_id_by_symbol("AAPL")
        add_price_to_history(asset_id, "2024-01-01", 180.0)
        add_price_to_history(asset_id, "2024-01-02", 185.0)
        assert get_latest_price(asset_id) == 185.0

def test_get_latest_price_returns_none_with_no_history(app):
    with app.app_context():
        add_asset("AAPL", "Apple Inc.", "Stock", "USD")
        asset_id = get_asset_id_by_symbol("AAPL")
        assert get_latest_price(asset_id) is None


# --- Portfolio Summary Tests ---

def test_portfolio_summary_excludes_fully_sold_assets(app):
    """An asset with net zero holdings should not appear in the summary."""
    with app.app_context():
        add_asset("AAPL", "Apple Inc.", "Stock", "USD")
        asset_id = get_asset_id_by_symbol("AAPL")
        add_transaction(asset_id, "buy", "2024-01-01", 5.0, 180.0, 0.0)
        add_transaction(asset_id, "sell", "2024-06-01", 5.0, 200.0, 0.0)

        summary = get_portfolio_summary()
        assert "AAPL" not in summary

def test_portfolio_summary_includes_held_assets(app):
    with app.app_context():
        add_asset("AAPL", "Apple Inc.", "Stock", "USD")
        asset_id = get_asset_id_by_symbol("AAPL")
        add_transaction(asset_id, "buy", "2024-01-01", 5.0, 180.0, 0.0)

        summary = get_portfolio_summary()
        assert "AAPL" in summary
        assert summary["AAPL"]["asset_holdings"] == 5.0


# --- Delete Tests ---

def test_delete_asset_removes_asset_and_all_records(app):
    """Deleting an asset should cascade to its transactions and price history."""
    with app.app_context():
        add_asset("AAPL", "Apple Inc.", "Stock", "USD")
        asset_id = get_asset_id_by_symbol("AAPL")
        add_transaction(asset_id, "buy", "2024-01-01", 5.0, 180.0, 0.0)
        add_price_to_history(asset_id, "2024-01-01", 180.0)

        delete_asset_by_id(asset_id)

        assert get_asset_id_by_symbol("AAPL") is None
        assert calculate_holdings(asset_id) == 0
        assert get_latest_price(asset_id) is None