import pytest
import tempfile
import os

from run import create_app


@pytest.fixture
def app():
    """Creates a fresh app instance backed by temporary database files.

    One temp file per database so each module's connections stay isolated.
    Both are deleted automatically in teardown.
    """

    inv_fd, inv_path = tempfile.mkstemp(suffix=".db")
    mem_fd, mem_path = tempfile.mkstemp(suffix=".db")
    os.close(inv_fd)
    os.close(mem_fd)

    class TestConfig:
        TESTING = True
        SECRET_KEY = "test-secret-key"
        INVESTMENT_DATABASE = inv_path
        MEMBERSHIPS_DATABASE = mem_path

    app = create_app(TestConfig)

    yield app

    os.unlink(inv_path)
    os.unlink(mem_path)


@pytest.fixture
def client(app):
    """A test client for making HTTP requests against the app."""
    return app.test_client()