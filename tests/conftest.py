"""
Shared test fixtures and configuration for FastAPI tests
"""

import pytest
from fastapi.testclient import TestClient
import importlib
import sys

# Import the app module
import src.app


@pytest.fixture
def client():
    """
    Provide a TestClient instance for API testing.
    Each test gets a fresh client with a reset database to ensure isolation.
    """
    # Reload the app module to get a fresh in-memory database
    importlib.reload(src.app)
    from src.app import app
    return TestClient(app)
