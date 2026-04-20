"""
User management endpoints for the Nexus Event Companion API.

Handles creation and retrieval of attendee profiles that are
subsequently used for AI-powered meetup matchmaking.
"""
import logging
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import models
from app.schemas.user_schema import UserCreate, UserResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


def get_db() -> Session:
    """Provide a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new attendee profile",
    description="Creates a persistent user profile with natural language interests for AI matchmaking.",
)
def create_user(user: UserCreate) -> UserResponse:
    """
    Register a new conference attendee.

    Persists the user's name and natural language interest description
    to the database. The stored profile is later consumed by the
    AI matchmaking engine to generate personalized recommendations.

    Args:
        user: A UserCreate schema containing name and free-text interests.

    Returns:
        UserResponse with the assigned database ID and submitted fields.

    Raises:
        HTTPException 500: If the database transaction fails or rolls back.
    """
    db = SessionLocal()
    try:
        db_user = models.User(name=user.name, interests=user.interests)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User profile created: id={db_user.id}, name='{db_user.name}'")
        return db_user
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database transaction failed. Please retry.",
        )
    finally:
        db.close()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Retrieve an attendee profile",
    description="Fetch a previously registered user profile by their unique ID.",
)
def get_user(user_id: int) -> UserResponse:
    """
    Retrieve a specific attendee profile by ID.

    Args:
        user_id: The integer primary key of the user to retrieve.

    Returns:
        UserResponse containing the user's stored profile data.

    Raises:
        HTTPException 404: If no user with the given ID exists.
    """
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id={user_id} not found.",
            )
        return user
    finally:
        db.close()