import sqlite3
import os

# Path to instance folder
INSTANCE_FOLDER = os.path.join("..", "instance")
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
    """Adds an asset to the assets table"""

    # Get database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Define insert command
    INSERT_ASSET = """
    INSERT INTO assets (symbol, name, asset_type)
    VALUES (?, ?, ?);
    """

    # Execute command
    parameters = (symbol, name, asset_type)
    cursor.execute(INSERT_ASSET, parameters)
    print(f"""Added asset:\n
          Name: {name}\n
          Symbol: {symbol}\n
          Asset type: {asset_type}\n
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
    """Adds a transaction to the transactions table"""

    # Get database connection
    conn = get_db_connection()
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

    print(f"""Added transaction:\n
          Asset ID: {asset_id}\n
          Transaction type: {transaction_type}\n
          Date: {date}\n
          Quantity: {quantity}\n
          Price per unit (DKK): {price_per_unit}\n
          Fees (DKK): {fees}\n
        To the transactions table.
    """)

    # Commit to the database
    conn.commit()
    print("Successfully commited to database.")

    # Close the connection
    conn.close()
    print("Database connection closed.")