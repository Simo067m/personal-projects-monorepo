import pytest
from run import create_app


class TestConfig:
    """Isolated config for the test suite.
    
    Uses an in-memory SQLite database so tests never touch
    the real investment.db file on disk.
    """
    TESTING = True
    SECRET_KEY = "test-secret-key"
    DATABASE = ":memory:"


@pytest.fixture
def app():
    """Creates a fresh app instance for each test.
    
    Because create_app() is called here rather than imported as a
    global, each test gets its own isolated Flask app and database.
    """
    app = create_app(TestConfig)
    yield app


@pytest.fixture
def client(app):
    """A test client for making HTTP requests against the app."""
    return app.test_client()