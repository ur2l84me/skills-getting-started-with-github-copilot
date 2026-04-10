import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app


# Sample clean activities data for testing
CLEAN_ACTIVITIES = {
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
        "participants": ["emma@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": []
    }
}


@pytest.fixture
def activities(monkeypatch):
    """
    Fixture that provides a clean copy of activities data for each test.
    Monkeypatches app.activities to use the clean data, ensuring test isolation.
    """
    clean_copy = copy.deepcopy(CLEAN_ACTIVITIES)
    monkeypatch.setattr("src.app.activities", clean_copy)
    return clean_copy


@pytest.fixture
def client(activities):
    """
    Fixture that provides a FastAPI TestClient with isolated activities data.
    Depends on activities fixture to ensure clean data per test.
    """
    return TestClient(app)
