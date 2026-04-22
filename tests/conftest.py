"""
Pytest configuration and shared fixtures for FastAPI tests.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app


# Default test data
DEFAULT_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}


@pytest.fixture
def client(monkeypatch):
    """
    Arrange: Create a TestClient and fresh activities data for each test.
    """
    # Reset activities to default state
    fresh_activities = deepcopy(DEFAULT_ACTIVITIES)
    monkeypatch.setattr("src.app.activities", fresh_activities)
    
    # Create and return the test client
    return TestClient(app)
