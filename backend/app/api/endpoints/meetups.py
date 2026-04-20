"""
Meetup management endpoints for the Nexus Event Companion API.

Provides CRUD operations for physical conference meetup events
that are surfaced to attendees via AI-powered recommendations.
"""
import logging
from fastapi import APIRouter, HTTPException, status
from app.db.database import SessionLocal
from app.db import models
from app.schemas.meetup_schema import MeetupCreate, MeetupResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/meetups", tags=["Meetups"])


@router.post(
    "/",
    response_model=MeetupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new meetup event",
    description="Register a new physical meetup that the AI engine can recommend to attendees.",
)
def create_meetup(meetup: MeetupCreate) -> MeetupResponse:
    """
    Create a new physical conference meetup.

    Args:
        meetup: A MeetupCreate schema with title and description.

    Returns:
        MeetupResponse with the assigned ID and submitted fields.

    Raises:
        HTTPException 500: If the database write fails.
    """
    db = SessionLocal()
    try:
        db_meetup = models.Meetup(title=meetup.title, description=meetup.description)
        db.add(db_meetup)
        db.commit()
        db.refresh(db_meetup)
        logger.info(f"Meetup created: id={db_meetup.id}, title='{db_meetup.title}'")
        return db_meetup
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create meetup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist meetup record.",
        )
    finally:
        db.close()


@router.get(
    "/",
    response_model=list[MeetupResponse],
    summary="List all active meetups",
    description="Returns all currently registered meetup events available for AI matching.",
)
def get_meetups() -> list[MeetupResponse]:
    """
    Retrieve all active conference meetups.

    Returns:
        A list of MeetupResponse objects representing all stored events.
        Returns an empty list if no meetups have been seeded yet.
    """
    db = SessionLocal()
    try:
        meetups = db.query(models.Meetup).all()
        logger.info(f"Retrieved {len(meetups)} meetups.")
        return meetups
    finally:
        db.close()


@router.get(
    "/{meetup_id}",
    response_model=MeetupResponse,
    summary="Retrieve a specific meetup",
    description="Fetch a single meetup event by its unique ID.",
)
def get_meetup(meetup_id: int) -> MeetupResponse:
    """
    Retrieve a specific meetup by ID.

    Args:
        meetup_id: The integer primary key of the meetup to retrieve.

    Returns:
        MeetupResponse for the specified meetup.

    Raises:
        HTTPException 404: If no meetup with the given ID exists.
    """
    db = SessionLocal()
    try:
        meetup = db.query(models.Meetup).filter(models.Meetup.id == meetup_id).first()
        if not meetup:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meetup with id={meetup_id} not found.",
            )
        return meetup
    finally:
        db.close()