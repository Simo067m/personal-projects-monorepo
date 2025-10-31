import sqlite3
import os

# Define instance folder path
INSTANCE_FOLDER = os.path.join(os.path.dirname(__file__), 'instance')
# Define database name
DB_NAME = os.path.join(INSTANCE_FOLDER, "investment.db")

# SQL Commands to create tables
CREATE_ASSETS_TABLE = """
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    asset_type TEXT NOT NULL
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

def initialize_database():
    """Creates the database file and the tables."""

    # conn is the database connection
    conn = None
    try:
        # Create the database if it does not exist
        conn = sqlite3.connect(DB_NAME)

        cursor = conn.cursor()

        print("Database connected.")

        # Execute SQL commands
        cursor.execute(CREATE_ASSETS_TABLE)
        print("Created 'assets' table (or it already exists).")
        
        cursor.execute(CREATE_TRANSACTIONS_TABLE)
        print("Created 'transactions' table (or it already exists).")

        # Commit changes
        conn.commit()
        print("Database initialized successfully.")

    except sqlite3.Error as e:
        print(f"An error occured: {e}")
    finally:
        # Close connection
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    initialize_database()