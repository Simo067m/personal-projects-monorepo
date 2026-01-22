import sqlite3
import os

from contextlib import contextmanager

from .utils import convert_currency

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
# Path to instance folder
INSTANCE_FOLDER = os.path.join(PROJECT_ROOT, "instance")
# Database file
DB_FILE = os.path.join(INSTANCE_FOLDER, "investment.db")

# SQL Schemas
CREATE_ASSETS_TABLE = """
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    currency TEXT NOT NULL
);
"""

CREATE_TRANSACTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    date TEXT NOT NULL,
    quantity REAL NOT NULL,
    price_per_unit REAL NOT NULL,
    fees REAL DEFAULT 0.0,
    FOREIGN KEY (asset_id) REFERENCES assets (id)
);
"""

CREATE_PRICE_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets (id),
    UNIQUE(asset_id, date) -- Ensures one price per asset per day (EOD price)
);
"""

@contextmanager
def get_db_connection():
    """Creates a connection to the database.
    Uses context manager to ensure proper closing of connection.
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
    """

    # Connect to database file
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)

        # Yield the connection object
        yield conn

    except sqlite3.Error as e:
            print(f"An error occurred: {e}")
    
    finally:
        # Make sure connection is closed
        if conn:
            conn.close()

def initialize_database():
    """Creates the database file and tables.
    Checks if tables already exist.
    """

    if not os.path.exists(INSTANCE_FOLDER):
        os.makedirs(INSTANCE_FOLDER)
        print(f"Created instance folder at {INSTANCE_FOLDER}.")
    
    try:
        with get_db_connection() as conn:
            print(f"Checking database at: {DB_FILE}")
            cursor = conn.cursor()
            
            cursor.execute(CREATE_ASSETS_TABLE)
            cursor.execute(CREATE_TRANSACTIONS_TABLE)
            cursor.execute(CREATE_PRICE_HISTORY_TABLE)
            
            conn.commit()
            print("Database tables verified/created successfully.")

    except sqlite3.Error as e:
        print(f"Database initialization failed: {e}")

def add_asset(symbol : str, name : str, asset_type : str, currency : str):
    """Adds an asset to the assets table."""

    INSERT_ASSET = """
    INSERT INTO assets (symbol, name, asset_type, currency)
    VALUES (?, ?, ?, ?);
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            parameters = (symbol, name, asset_type, currency)
            cursor.execute(INSERT_ASSET, parameters)
            print(f"""Added asset:
                Name: {name}
                Symbol: {symbol}
                Asset type: {asset_type}
                Currency: {currency}""")

            conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred in add_asset: {e}")

def add_transaction(asset_id : int, transaction_type : str, date : str,
                    quantity : float, price_per_unit : float, fees : float):
    """Adds a transaction to the transactions table."""

    INSERT_TRANSACTION = """
    INSERT INTO transactions (asset_id, transaction_type, 
    date, quantity, price_per_unit, fees)
    VALUES (?, ?, ?, ?, ?, ?);
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            parameters = (asset_id, transaction_type, date, quantity, price_per_unit, fees)
            cursor.execute(INSERT_TRANSACTION, parameters)
            print(f"""Added transaction:
                Asset ID: {asset_id}
                Transaction type: {transaction_type}
                Date: {date}
                Quantity: {quantity}
                Price per unit: {price_per_unit}
                Fees (DKK): {fees}""")

            conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred in add_transaction: {e}")

def add_price_to_history(asset_id : int, date : str, price : float):
    """Adds and EOD price to an asset's history."""

    INSERT_PRICE_HISTORY = """
    INSERT INTO price_history (asset_id, date, price)
    VALUES (?, ?, ?);
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            parameters = (asset_id, date, price)
            cursor.execute(INSERT_PRICE_HISTORY, parameters)
            print(f"""Added price:
                Asset ID: {asset_id}
                Date: {date}
                Price: {price}""")

            conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred in add_price_to_history: {e}")

def get_all_assets():
    """Read all the assets in the assets table."""

    SELECT_ASSETS = """
    SELECT * FROM assets; 
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(SELECT_ASSETS)

            return cursor.fetchall()

    except sqlite3.Error as e:
        print(f"An error occurred in get_all_assets: {e}")
        return []

def get_all_transactions_for_asset(asset_id : int):
    """Read all the transactions in the transactions table
    for a specific asset ID."""

    SELECT_TRANSACTIONS_FOR_ASSET = """
    SELECT * FROM transactions
    WHERE transactions.asset_id = (?); 
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            parameters = (asset_id,)
            cursor.execute(SELECT_TRANSACTIONS_FOR_ASSET, parameters)
            return cursor.fetchall()

    except sqlite3.Error as e:
        print(f"An error occurred in get_all_transactions_for_asset: {e}")
        return []

def get_latest_price(asset_id : int):
    """Get the latest price for a specific asset ID."""

    SELECT_LATEST_PRICE_FOR_ASSET = """
    SELECT price FROM price_history
    WHERE price_history.asset_id = (?)
    ORDER BY date DESC
    LIMIT 1
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            parameters = (asset_id,)
            cursor.execute(SELECT_LATEST_PRICE_FOR_ASSET, parameters)

            result = cursor.fetchone()
            
            return result[0] if result else None

    except sqlite3.Error as e:
        print(f"An error occurred in get_latest_price: {e}")

def calculate_holdings(asset_id : int):
    """Get current holdings for a specific asset ID."""

    # Get all transactions for the asset
    transactions = get_all_transactions_for_asset(asset_id)

    # Count holdings in the transactions
    total_holdings = 0
    for transaction in transactions:
        transaction_type = transaction[2]
        quantity = transaction[4]
        if transaction_type == "buy":
            total_holdings += quantity
        else:
            total_holdings -= quantity
    
    return total_holdings

def get_portfolio_summary():
    """Gets a summary of all current holdings."""

    # Get all assets
    all_assets = get_all_assets()

    # Get value of all current holdings
    holdings_dict = {}
    for asset in all_assets:
        asset_id = asset[0]
        asset_symbol = asset[1]
        asset_type = asset[3]
        asset_currency = asset[4]

        asset_holdings = calculate_holdings(asset_id)

        # Only add if asset is held
        if asset_holdings > 0.0:

            asset_latest_price = get_latest_price(asset_id)

            asset_dkk_price = None

            if asset_latest_price is not None:
                asset_dkk_price = convert_currency(asset_latest_price, asset_currency, "DKK")

            holdings_dict[asset_symbol] = {
                "asset_id" : asset_id,
                "asset_holdings" : asset_holdings,
                "asset_type" : asset_type.capitalize(),
                "latest_price" : asset_latest_price,
                "asset_currency" : asset_currency,
                "asset_dkk_price" : asset_dkk_price
            }
    
    return holdings_dict


def get_portfolio_value():
    """Gets the total accumulated value of all current holdings."""

    # Get current holdings and summary
    holdings_dict = get_portfolio_summary()

    # Compute total value of holdings
    total_value_dkk = 0.0
    for _, data in holdings_dict.items():
        if data["asset_holdings"] > 0.0:
            if data["asset_dkk_price"] is not None:
                asset_value = data["asset_holdings"] * data["asset_dkk_price"]

                total_value_dkk += asset_value

    return total_value_dkk

def get_asset_id_by_symbol(symbol : str):
    """Finds an asset's database ID based on its symbol."""
    
    SELECT_ASSET_ID = """
    SELECT id FROM assets
    WHERE symbol = ?;
    """
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            parameters = (symbol.upper(),)
            cursor.execute(SELECT_ASSET_ID, parameters)

            result = cursor.fetchone()
            
            return result[0] if result else None
            
    except sqlite3.Error as e:
        print(f"An error occurred in get_asset_id_by_symbol: {e}")

def get_price_history(asset_id):
    """Gets all registered prices for a single asset ID"""

    SELECT_PRICE_HISTORY = """
    SELECT date, price FROM price_history
    WHERE asset_id = ?
    ORDER BY date ASC;
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            parameters = (asset_id,)
            cursor.execute(SELECT_PRICE_HISTORY, parameters)

            return cursor.fetchall()
    
    except sqlite3.Error as e:
        print(f"An error occurred in get_price_history: {e}")