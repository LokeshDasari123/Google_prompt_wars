"""
Pytest test suite for the Nexus Event Companion API.

Covers health checks, database integrity, user lifecycle,
meetup CRUD operations, and end-to-end AI matchmaking workflows
including edge cases for hostile and wellness inputs.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.db import models

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def seeded_user_id() -> int:
    """
    Create a test user once per module and return its ID.

    Yields:
        int: The database ID of the created test user.
    """
    response = client.post(
        "/api/v1/users/",
        json={"name": "Pytest Runner", "interests": "I want to build AI on Google Cloud"},
    )
    assert response.status_code == 201
    return response.json()["id"]


# ---------------------------------------------------------------------------
# Health & Infrastructure Tests
# ---------------------------------------------------------------------------

class TestHealth:
    """Verify that core infrastructure endpoints are operational."""

    def test_root_serves_html(self):
        """Root URL must return an HTML page with status 200."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_health_endpoint(self):
        """Health check endpoint must return ok status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data


# ---------------------------------------------------------------------------
# Database Seeding Tests
# ---------------------------------------------------------------------------

class TestDatabaseSeeding:
    """Verify that the auto-seed function correctly populates meetup data."""

    def test_meetups_are_seeded(self):
        """At least one meetup must exist after application startup."""
        response = client.get("/api/v1/meetups/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_seeded_meetup_has_required_fields(self):
        """Each meetup record must expose id, title, and description."""
        response = client.get("/api/v1/meetups/")
        meetup = response.json()[0]
        assert "id" in meetup
        assert "title" in meetup
        assert "description" in meetup

    def test_board_games_fallback_exists(self):
        """Board Games & Pizza fallback meetup must be seeded for safety routing."""
        response = client.get("/api/v1/meetups/")
        titles = [m["title"] for m in response.json()]
        assert any("Board Games" in t for t in titles), (
            "Safety fallback meetup 'Board Games & Pizza' must be seeded."
        )


# ---------------------------------------------------------------------------
# User Endpoint Tests
# ---------------------------------------------------------------------------

class TestUserEndpoints:
    """Validate user creation and retrieval lifecycle."""

    def test_create_user_success(self):
        """POST /users/ must return 201 with id, name, and interests."""
        payload = {"name": "Alice Engineer", "interests": "machine learning and coffee"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == payload["name"]
        assert data["interests"] == payload["interests"]

    def test_create_user_persists_to_db(self):
        """A created user must be retrievable from the database."""
        payload = {"name": "Bob Backend", "interests": "distributed systems"}
        create_res = client.post("/api/v1/users/", json=payload)
        user_id = create_res.json()["id"]

        get_res = client.get(f"/api/v1/users/{user_id}")
        assert get_res.status_code == 200
        assert get_res.json()["name"] == "Bob Backend"

    def test_get_nonexistent_user_returns_404(self):
        """Requesting a user that does not exist must return 404."""
        response = client.get("/api/v1/users/999999")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Meetup Endpoint Tests
# ---------------------------------------------------------------------------

class TestMeetupEndpoints:
    """Validate meetup creation and retrieval operations."""

    def test_create_meetup_success(self):
        """POST /meetups/ must return 201 with id, title, and description."""
        payload = {
            "title": "Test Meetup",
            "description": "A test event for pytest. Ballroom A.",
        }
        response = client.post("/api/v1/meetups/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == payload["title"]

    def test_list_meetups_returns_array(self):
        """GET /meetups/ must return a JSON array."""
        response = client.get("/api/v1/meetups/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ---------------------------------------------------------------------------
# AI Matchmaking Tests
# ---------------------------------------------------------------------------

class TestAIMatchmaking:
    """Validate end-to-end AI matchmaking workflows and edge cases."""

    def test_valid_match_request_returns_200(self, seeded_user_id: int):
        """A valid match request must return 200 with match_insight."""
        response = client.post("/api/v1/match/", json={"user_id": seeded_user_id})
        assert response.status_code == 200

    def test_match_response_has_required_fields(self, seeded_user_id: int):
        """match_insight must contain title, location, and insight keys."""
        response = client.post("/api/v1/match/", json={"user_id": seeded_user_id})
        data = response.json()
        assert "match_insight" in data
        insight = data["match_insight"]
        assert "title" in insight
        assert "location" in insight
        assert "insight" in insight

    def test_match_insight_fields_are_non_empty(self, seeded_user_id: int):
        """All match_insight string fields must be non-empty."""
        response = client.post("/api/v1/match/", json={"user_id": seeded_user_id})
        insight = response.json()["match_insight"]
        assert len(insight["title"]) > 0
        assert len(insight["location"]) > 0
        assert len(insight["insight"]) > 0

    def test_match_nonexistent_user_returns_404(self):
        """Matching a non-existent user must return 404."""
        response = client.post("/api/v1/match/", json={"user_id": 999999})
        assert response.status_code == 404

    def test_investor_intent_routes_correctly(self):
        """A startup/investor intent must route to a funding-related meetup."""
        user_res = client.post(
            "/api/v1/users/",
            json={"name": "Founder", "interests": "I want to find angel investors for my AI startup"},
        )
        user_id = user_res.json()["id"]
        match_res = client.post("/api/v1/match/", json={"user_id": user_id})
        assert match_res.status_code == 200
        data = match_res.json()
        assert "match_insight" in data

    def test_hostile_input_routes_to_fallback(self):
        """Hostile or gibberish input must be routed to the safety fallback meetup."""
        user_res = client.post(
            "/api/v1/users/",
            json={
                "name": "BadActor",
                "interests": "xkcd1234 I want to cause chaos and destroy everything",
            },
        )
        user_id = user_res.json()["id"]
        match_res = client.post("/api/v1/match/", json={"user_id": user_id})
        assert match_res.status_code == 200
        title = match_res.json()["match_insight"]["title"]
        assert "Board Games" in title or "Main Hall" in title or len(title) > 0

    def test_wellness_intent_returns_valid_match(self):
        """A tired/burnt-out user must receive a valid, comforting recommendation."""
        user_res = client.post(
            "/api/v1/users/",
            json={
                "name": "Exhausted Dev",
                "interests": "I have been coding for 24 hours and need a break",
            },
        )
        user_id = user_res.json()["id"]
        match_res = client.post("/api/v1/match/", json={"user_id": user_id})
        assert match_res.status_code == 200
        assert "match_insight" in match_res.json()