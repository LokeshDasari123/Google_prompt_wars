import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.db.database import SessionLocal
from app.db import models
from app.core.ai_service import ai_engine

logger = logging.getLogger(__name__)
router = APIRouter()


class UserCreate(BaseModel):
    """Schema for creating a new user profile."""
    name: str = Field(..., example="Lokesh", description="The attendee's full name")
    interests: str = Field(..., example="AI and coffee", description="Natural language description of what the user wants to experience")


class MatchRequest(BaseModel):
    """Schema for requesting an AI-powered meetup match."""
    user_id: int = Field(..., example=1, description="The ID of the user profile to match")


@router.post("/users/", status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: UserCreate) -> dict:
    """
    Create a new attendee profile.

    Persists the user's name and natural language interest description
    to the database for subsequent AI matchmaking.

    Args:
        user: UserCreate schema containing name and interests.

    Returns:
        A dict with the created user's id, name, and interests.

    Raises:
        HTTPException: 500 if the database transaction fails.
    """
    db = SessionLocal()
    try:
        db_user = models.User(name=user.name, interests=user.interests)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Created user profile: id={db_user.id}, name={db_user.name}")
        return {"id": db_user.id, "name": db_user.name, "interests": db_user.interests}
    except Exception as e:
        db.rollback()
        logger.error(f"User creation failed: {e}")
        raise HTTPException(status_code=500, detail="Database transaction failed")
    finally:
        db.close()


@router.post("/match/", status_code=status.HTTP_200_OK, tags=["Matchmaking"])
def generate_match(request: MatchRequest) -> dict:
    """
    Generate an AI-powered meetup recommendation for a user.

    Fetches the user profile and all active meetups, then uses the
    Vertex AI engine to produce a personalized matchmaking recommendation
    using Chain-of-Thought reasoning.

    Args:
        request: MatchRequest schema containing the user_id.

    Returns:
        A dict with 'match_insight' containing 'title', 'location', and 'insight'.

    Raises:
        HTTPException: 404 if the user or meetups are not found.
    """
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        meetups = db.query(models.Meetup).all()
        if not meetups:
            raise HTTPException(status_code=404, detail="No active meetups available")

        meetup_descriptions = [f"{m.title}: {m.description}" for m in meetups]
        match_insight = ai_engine.generate_meetup_match(user.interests, meetup_descriptions)

        logger.info(f"Match generated for user_id={user.id}: {match_insight.get('title')}")
        return {"user_id": user.id, "match_insight": match_insight}
    finally:
        db.close()