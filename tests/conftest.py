import pytest
import tempfile
import os

from run import create_app


@pytest.fixture
def app():
    """Creates a fresh app instance backed by a temporary database file.

    We use a real temp file rather than ':memory:' because SQLite creates
    a brand new database for every call to sqlite3.connect(':memory:').
    Since each db.py function opens its own connection, ':memory:' would
    mean add_asset() and get_asset_id_by_symbol() talk to different
    databases — the second would always be empty.

    A temp file persists across connections for the duration of the test,
    then is deleted automatically in the fixture teardown.
    """

    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    class TestConfig:
        TESTING = True
        SECRET_KEY = "test-secret-key"
        DATABASE = db_path

    app = create_app(TestConfig)

    yield app

    # Teardown: close the file descriptor and delete the temp file
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for making HTTP requests against the app."""
    return app.test_client()