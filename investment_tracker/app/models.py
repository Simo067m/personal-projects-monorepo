import sqlite3
import os

from .utils import convert_currency

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

        # Return the connection object
        return conn

    except sqlite3.Error as e:
            print(f"An error occured: {e}")

def add_asset(symbol : str, name : str, asset_type : str, currency : str):
    """Adds an asset to the assets table."""

    # Get database connection
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return
    
    try:
        cursor = conn.cursor()

        # Define insert command
        INSERT_ASSET = """
        INSERT INTO assets (symbol, name, asset_type, currency)
        VALUES (?, ?, ?, ?);
        """

        # Execute command
        parameters = (symbol, name, asset_type, currency)
        cursor.execute(INSERT_ASSET, parameters)
        print(f"""Added asset:
            Name: {name}
            Symbol: {symbol}
            Asset type: {asset_type}
            Currency: {currency}
To the asset table.
        """)

        # Commit to the database
        conn.commit()
        print("Successfully commited to database.")

    except sqlite3.Error as e:
        print(f"An error occurred in add_asset: {e}")

    finally:
        if conn:    
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
    
    try:
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
            Price per unit: {price_per_unit}
            Fees (DKK): {fees}
To the transactions table.
        """)

        # Commit to the database
        conn.commit()
        print("Successfully commited to database.")

    except sqlite3.Error as e:
        print(f"An error occurred in add_transaction: {e}")

    finally:
        if conn:    
            # Close the connection
            conn.close()
            print("Database connection closed.")

def add_price_to_history(asset_id : int, date : str, price : float):
    """Adds and EOD price to an asset's history."""

    # Get database connection
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return
    
    try: 
        cursor = conn.cursor()

        # Define insert command
        INSERT_PRICE_HISTORY = """
        INSERT INTO price_history (asset_id, date, price)
        VALUES (?, ?, ?);
        """

        # Execute command
        parameters = (asset_id, date, price)
        cursor.execute(INSERT_PRICE_HISTORY, parameters)
        print(f"""Added price:
            Asset ID: {asset_id}
            Date: {date}
            Price: {price}
To the price_history table.
        """)

        # Commit to the database
        conn.commit()
        print("Successfully commited to database.")

    except sqlite3.Error as e:
        print(f"An error occurred in add_price_to_history: {e}")

    finally:
        if conn:    
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
    
    # Initialize assets list
    assets = []

    try:
        cursor = conn.cursor()

        # Define select command
        SELECT_ASSETS = """
        SELECT * FROM assets; 
    """

        # Execute the command
        cursor.execute(SELECT_ASSETS)

        # Fetch the results
        assets = cursor.fetchall()

    except sqlite3.Error as e:
        print(f"An error occurred in get_all_assets: {e}")

    finally:
        if conn:    
            # Close the connection
            conn.close()

    return assets

def get_all_transactions_for_asset(asset_id : int):
    """Read all the transactions in the transactions table
    for a specific asset ID."""

    # Get database connection
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return
    
    # Initialize return list
    transactions = []

    try:
        cursor = conn.cursor()

        # Define select command
        SELECT_TRANSACTIONS_FOR_ASSET = """
        SELECT * FROM transactions
        WHERE transactions.asset_id = (?); 
    """

        # Execute the command
        parameters = (asset_id,)
        cursor.execute(SELECT_TRANSACTIONS_FOR_ASSET, parameters)

        # Fetch the results
        transactions = cursor.fetchall()

    except sqlite3.Error as e:
        print(f"An error occurred in get_all_transactions_for_asset: {e}")

    finally:
        if conn:    
            # Close the connection
            conn.close()

    return transactions

def get_latest_price(asset_id : int):
    """Get the latest price for a specific asset ID."""

    # Get database connection
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return
    
    # Initialize return value
    price = None

    try:
        cursor = conn.cursor()

        # Define select command
        SELECT_LATEST_PRICE_FOR_ASSET = """
        SELECT price FROM price_history
        WHERE price_history.asset_id = (?)
        ORDER BY date DESC
        LIMIT 1
    """

        # Execute the command
        parameters = (asset_id,)
        cursor.execute(SELECT_LATEST_PRICE_FOR_ASSET, parameters)

        # Fetch the result
        price_result_tuple = cursor.fetchone()
        
        # Return None if no result
        if price_result_tuple is None:
            return None
        
        price = price_result_tuple[0]

    except sqlite3.Error as e:
        print(f"An error occurred in get_latest_price: {e}")

    finally:
        if conn:    
            # Close the connection
            conn.close()

    return price

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
    
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return None
    
    # Initialize return value
    asset_id = None
    
    try:
        cursor = conn.cursor()
        
        # Define select command
        SELECT_ASSET_ID = """
        SELECT id FROM assets
        WHERE symbol = ?;"""

        # Execute the command
        parameters = (symbol.upper(),)
        cursor.execute(SELECT_ASSET_ID, parameters)

        result_tuple = cursor.fetchone()
        
        if result_tuple:
            asset_id = result_tuple[0]
            
    except sqlite3.Error as e:
        print(f"An error occurred in get_asset_id_by_symbol: {e}")
    
    finally:
        if conn:
            conn.close()
    
    return asset_id

def get_price_history(asset_id):
    """Gets all registered prices for a single asset ID"""

    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return
    
    # Initialize return list
    prices = []

    try:
        cursor = conn.cursor()

        # Define select command
        SELECT_PRICE_HISTORY = """
        SELECT date, price FROM price_history
        WHERE asset_id = ?
        ORDER BY date ASC;
        """

        # Execute the command
        parameters = (asset_id,)
        cursor.execute(SELECT_PRICE_HISTORY, parameters)

        prices = cursor.fetchall()
    
    except sqlite3.Error as e:
        print(f"An error occurred in get_price_history: {e}")
    
    finally:
        if conn:
            conn.close()
    
    return prices