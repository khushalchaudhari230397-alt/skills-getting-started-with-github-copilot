import os
import sys
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

# Ensure src is importable
SYS_PATH = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, SYS_PATH)

from app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # Check a known activity exists
    assert "Basketball" in data


def test_signup_and_unregister_flow(client):
    activity = "Chess Club"
    email = "pytest.user@example.com"

    # Ensure email not already present; attempt to unregister if it exists
    client.delete(f"/activities/{quote(activity)}/unregister", params={"email": email})

    # Signup
    signup = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert signup.status_code == 200
    assert "Signed up" in signup.json().get("message", "")

    # Verify participant present
    res = client.get("/activities")
    participants = res.json()[activity]["participants"]
    assert email in participants

    # Unregister
    unreg = client.delete(f"/activities/{quote(activity)}/unregister", params={"email": email})
    assert unreg.status_code == 200
    assert "Unregistered" in unreg.json().get("message", "")

    # Verify removed
    res2 = client.get("/activities")
    participants2 = res2.json()[activity]["participants"]
    assert email not in participants2
