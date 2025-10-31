import sqlite3
import os

# Path to instance folder
INSTANCE_FOLDER = os.path.join(os.path.dirname(__file__), "..", "instance")
# Database file
DB_FILE = os.path.join(INSTANCE_FOLDER, "investment.db")


def get_db_connection():
    """Creates a connection to the database."""

    # Connect to database file
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)

        print("Database connected.")

        # Return the connection object
        return conn

    except sqlite3.Error as e:
            print(f"An error occured: {e}")

def add_asset(symbol : str, name : str, asset_type : str):
    """Adds an asset to the assets table."""

    # Get database connection
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return
    cursor = conn.cursor()

    # Define insert command
    INSERT_ASSET = """
    INSERT INTO assets (symbol, name, asset_type)
    VALUES (?, ?, ?);
    """

    # Execute command
    parameters = (symbol, name, asset_type)
    cursor.execute(INSERT_ASSET, parameters)
    print(f"""Added asset:
          Name: {name}
          Symbol: {symbol}
          Asset type: {asset_type}
To the asset table.
    """)

    # Commit to the database
    conn.commit()
    print("Successfully commited to database.")

    # Close the connection
    conn.close()
    print("Database connection closed.")

def add_transaction(asset_id : int, transaction_type : str, date : str,
                    quantity : float, price_per_unit : float, fees : float):
    """Adds a transaction to the transactions table."""

    # Get database connection
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return
    cursor = conn.cursor()

    # Define insert command
    INSERT_TRANSACTION = """
    INSERT INTO transactions (asset_id, transaction_type, 
    date, quantity, price_per_unit, fees)
    VALUES (?, ?, ?, ?, ?, ?);
    """

    # Execute command
    parameters = (asset_id, transaction_type, date, quantity, price_per_unit, fees)
    cursor.execute(INSERT_TRANSACTION, parameters)

    print(f"""Added transaction:
          Asset ID: {asset_id}
          Transaction type: {transaction_type}
          Date: {date}
          Quantity: {quantity}
          Price per unit (DKK): {price_per_unit}
          Fees (DKK): {fees}
To the transactions table.
    """)

    # Commit to the database
    conn.commit()
    print("Successfully commited to database.")

    # Close the connection
    conn.close()
    print("Database connection closed.")

def get_all_assets():
    """Read all the assets in the assets table."""

    # Get database connection
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return
    cursor = conn.cursor()

    # Define select command
    SELECT_ASSETS = """
    SELECT * FROM assets; 
"""

    # Execute the command
    cursor.execute(SELECT_ASSETS)

    # Fetch the results
    assets = cursor.fetchall()

    # Close the connection
    conn.close()
    print("Database connection closed.")

    return assets

def get_all_transactions_for_asset(asset_id : int):
    """Read all the transactions in the transactions table
    for a specific asset ID."""

    # Get database connection
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return
    cursor = conn.cursor()

    # Define select command
    SELECT_TRANSACTIONS_FOR_ASSET = """
    SELECT * FROM transactions
    WHERE transactions.asset_id == (?); 
"""

    # Execute the command
    parameters = (asset_id,)
    cursor.execute(SELECT_TRANSACTIONS_FOR_ASSET, parameters)

    # Fetch the results
    assets = cursor.fetchall()

    # Close the connection
    conn.close()
    print("Database connection closed.")

    return assets

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

    # Get all assets from the assets table
    assets = get_all_assets()

    # Get all current holdings
    holdings_dict = {}
    for asset in assets:
        asset_id = asset[0]
        asset_symbol = asset[1]
        asset_type = asset[3]
        asset_holdings = calculate_holdings(asset_id)
        if asset_holdings > 0.0:
            holdings_dict[asset_symbol] = {
                "asset_holdings" : asset_holdings,
                "asset_type" : asset_type
            }
    
    return holdings_dict