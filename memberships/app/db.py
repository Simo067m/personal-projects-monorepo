import sqlite3
import os

from contextlib import contextmanager
from datetime import date, timedelta
from flask import current_app, has_app_context

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
INSTANCE_FOLDER = os.path.join(PROJECT_ROOT, "instance")
DB_FILE = os.path.join(INSTANCE_FOLDER, "memberships.db")

CREATE_MEMBERSHIPS_TABLE = """
CREATE TABLE IF NOT EXISTS memberships (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    organization       TEXT    NOT NULL,
    description        TEXT,
    membership_type    TEXT    NOT NULL,
    member_since       TEXT    NOT NULL,
    is_paid            INTEGER NOT NULL DEFAULT 0,
    payment_frequency  TEXT,
    price_per_period   REAL,
    currency           TEXT,
    renewal_date       TEXT
);
"""


@contextmanager
def get_db_connection():
    """Creates a connection to the memberships database.
    Uses context manager to ensure proper closing of connection.
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
    """

    conn = None
    try:
        db_path = current_app.config.get("MEMBERSHIPS_DATABASE", DB_FILE) if has_app_context() else DB_FILE
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        yield conn

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if conn:
            conn.close()


def initialize_database():
    """Creates the database file and tables.
    Checks if tables already exist.

    Also runs lightweight column migrations so existing databases
    are updated without destroying data.

    Skips instance folder creation when using an in-memory database,
    since ':memory:' is not a real file path.
    """

    db_path = current_app.config.get("MEMBERSHIPS_DATABASE", DB_FILE) if has_app_context() else DB_FILE

    if db_path != ":memory:":
        if not os.path.exists(INSTANCE_FOLDER):
            os.makedirs(INSTANCE_FOLDER)
            print(f"Created instance folder at {INSTANCE_FOLDER}.")

    try:
        with get_db_connection() as conn:
            print(f"Checking database at: {db_path}")
            cursor = conn.cursor()
            cursor.execute(CREATE_MEMBERSHIPS_TABLE)
            conn.commit()

            # Migration: add renewal_date to existing databases that predate the column.
            # ALTER TABLE fails silently if the column already exists.
            try:
                cursor.execute("ALTER TABLE memberships ADD COLUMN renewal_date TEXT;")
                conn.commit()
                print("Migration applied: added renewal_date column.")
            except sqlite3.OperationalError:
                pass  # Column already exists — nothing to do.

            print("Database tables verified/created successfully.")

    except sqlite3.Error as e:
        print(f"Database initialization failed: {e}")


# --- CREATE ---

def add_membership(organization: str, description: str, membership_type: str,
                   member_since: str, is_paid: bool,
                   payment_frequency: str = None, price_per_period: float = None,
                   currency: str = None, renewal_date: str = None):
    """Adds a membership to the memberships table."""

    INSERT_MEMBERSHIP = """
    INSERT INTO memberships (organization, description, membership_type,
    member_since, is_paid, payment_frequency, price_per_period, currency, renewal_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            parameters = (organization, description, membership_type,
                          member_since, int(is_paid),
                          payment_frequency, price_per_period, currency, renewal_date)
            cursor.execute(INSERT_MEMBERSHIP, parameters)
            conn.commit()
            print(f"Added membership: {organization}")

    except sqlite3.Error as e:
        print(f"An error occurred in add_membership: {e}")


# --- READ ---

def get_all_memberships():
    """Read all memberships, ordered by paid first, then alphabetically."""

    SELECT_ALL = """
    SELECT * FROM memberships
    ORDER BY is_paid DESC, organization ASC;
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(SELECT_ALL)
            return cursor.fetchall()

    except sqlite3.Error as e:
        print(f"An error occurred in get_all_memberships: {e}")
        return []


def get_membership_by_id(membership_id: int):
    """Read a single membership by its ID."""

    SELECT_BY_ID = """
    SELECT * FROM memberships
    WHERE id = ?;
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(SELECT_BY_ID, (membership_id,))
            return cursor.fetchone()

    except sqlite3.Error as e:
        print(f"An error occurred in get_membership_by_id: {e}")
        return None


def get_paid_memberships():
    """Read only memberships where is_paid is true."""

    SELECT_PAID = """
    SELECT * FROM memberships
    WHERE is_paid = 1
    ORDER BY organization ASC;
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(SELECT_PAID)
            return cursor.fetchall()

    except sqlite3.Error as e:
        print(f"An error occurred in get_paid_memberships: {e}")
        return []


def get_free_memberships():
    """Read only memberships where is_paid is false."""

    SELECT_FREE = """
    SELECT * FROM memberships
    WHERE is_paid = 0
    ORDER BY organization ASC;
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(SELECT_FREE)
            return cursor.fetchall()

    except sqlite3.Error as e:
        print(f"An error occurred in get_free_memberships: {e}")
        return []


def get_upcoming_renewals(days: int = 30):
    """Returns paid memberships with a renewal_date within the next N days,
    ordered by renewal_date ascending. Each result is enriched with a
    days_until integer for display urgency.
    """

    today = date.today()
    cutoff = today + timedelta(days=days)

    SELECT_UPCOMING = """
    SELECT * FROM memberships
    WHERE renewal_date IS NOT NULL
    AND renewal_date BETWEEN ? AND ?
    ORDER BY renewal_date ASC;
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(SELECT_UPCOMING, (today.isoformat(), cutoff.isoformat()))
            rows = cursor.fetchall()

        enriched = []
        for row in rows:
            renewal = date.fromisoformat(row["renewal_date"])
            days_until = (renewal - today).days
            enriched.append({"membership": row, "days_until": days_until})

        return enriched

    except sqlite3.Error as e:
        print(f"An error occurred in get_upcoming_renewals: {e}")
        return []


def get_total_monthly_cost():
    """Calculates total monthly cost across all paid memberships, keyed by currency.

    Frequency conversion rates:
        weekly     → multiply by 4.33  (avg weeks per month)
        monthly    → multiply by 1
        quarterly  → divide by 3
        yearly     → divide by 12
    """

    paid = get_paid_memberships()

    FREQUENCY_TO_MONTHLY = {
        "weekly":    4.33,
        "monthly":   1.0,
        "quarterly": 1 / 3,
        "yearly":    1 / 12,
    }

    totals = {}
    for row in paid:
        freq = row["payment_frequency"]
        price = row["price_per_period"]
        curr = row["currency"]

        if not (freq and price and curr):
            continue

        multiplier = FREQUENCY_TO_MONTHLY.get(freq.lower())
        if multiplier is None:
            continue

        monthly_equivalent = price * multiplier
        totals[curr] = totals.get(curr, 0.0) + monthly_equivalent

    return totals


# --- UPDATE ---

def update_membership(membership_id: int, organization: str, description: str,
                      membership_type: str, member_since: str, is_paid: bool,
                      payment_frequency: str = None, price_per_period: float = None,
                      currency: str = None, renewal_date: str = None):
    """Updates all fields of an existing membership by ID."""

    UPDATE_MEMBERSHIP = """
    UPDATE memberships
    SET organization = ?, description = ?, membership_type = ?,
        member_since = ?, is_paid = ?, payment_frequency = ?,
        price_per_period = ?, currency = ?, renewal_date = ?
    WHERE id = ?;
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            parameters = (organization, description, membership_type,
                          member_since, int(is_paid),
                          payment_frequency, price_per_period, currency,
                          renewal_date, membership_id)
            cursor.execute(UPDATE_MEMBERSHIP, parameters)
            conn.commit()
            print(f"Updated membership ID {membership_id}.")

    except sqlite3.Error as e:
        print(f"An error occurred in update_membership: {e}")
        raise e


# --- DELETE ---

def delete_membership_by_id(membership_id: int):
    """Deletes a membership by its ID."""

    DELETE_MEMBERSHIP = "DELETE FROM memberships WHERE id = ?;"

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(DELETE_MEMBERSHIP, (membership_id,))
            conn.commit()
            print(f"Deleted membership ID {membership_id}.")

    except sqlite3.Error as e:
        print(f"An error occurred in delete_membership_by_id: {e}")
        raise e