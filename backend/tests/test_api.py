import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.db import models

client = TestClient(app)

def test_health_check():
    """Verify system is operational."""
    response = client.get("/")
    assert response.status_code == 200
    # Since we are serving HTML at root now, check for HTML content
    assert "text/html" in response.headers["content-type"]

def test_database_seeding():
    """Verify that the auto-seed function actually populated meetups."""
    # We call the get_meetups endpoint
    response = client.get("/api/v1/meetups/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "AI Hackers Mixer"

def test_full_ai_match_workflow():
    """Verify the end-to-end matchmaking logic."""
    # 1. Create a user
    user_data = {"name": "Test Engineer", "interests": "I love building AI on GCP"}
    user_res = client.post("/api/v1/users/", json=user_data)
    user_id = user_res.json()["id"]

    # 2. Request a match
    match_res = client.post("/api/v1/match/", json={"user_id": user_id})
    assert match_res.status_code == 200
    
    match_data = match_res.json()
    # Verify the structured JSON response we built earlier
    assert "match_insight" in match_data
    assert "title" in match_data["match_insight"]
    assert "location" in match_data["match_insight"]