"""
AI matchmaking endpoint for the Nexus Event Companion API.

Orchestrates the core intelligence of Nexus: consuming a user profile
and all active meetups, then delegating to the Vertex AI engine to
produce a personalized, Chain-of-Thought-powered recommendation.
"""
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.db.database import SessionLocal
from app.db import models
from app.core.ai_service import ai_engine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/match", tags=["Matchmaking"])


class MatchRequest(BaseModel):
    """Request schema for the AI meetup matchmaking endpoint."""

    user_id: int = Field(
        ...,
        example=1,
        description="The unique ID of the attendee profile to generate a match for.",
    )


class MatchResponse(BaseModel):
    """Response schema for a successful AI matchmaking result."""

    user_id: int = Field(..., description="The ID of the matched user.")
    match_insight: dict = Field(
        ...,
        description="AI-generated match containing 'title', 'location', and 'insight'.",
    )


@router.post(
    "/",
    response_model=MatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate an AI-powered meetup recommendation",
    description=(
        "Uses Google Cloud Vertex AI (gemini-2.5-flash) with Chain-of-Thought reasoning "
        "to analyze a user's intent and recommend the single most relevant meetup. "
        "Handles hostile and gibberish inputs by routing safely to a fallback event."
    ),
)
def generate_match(request: MatchRequest) -> MatchResponse:
    """
    Generate a personalized meetup recommendation for an attendee.

    Fetches the user's stored interest profile and all active meetup
    descriptions, then passes them to the Vertex AI engine for
    intent analysis and semantic matching.

    The AI applies Chain-of-Thought reasoning to:
    - Decode the user's underlying goal (networking, funding, relaxation, etc.)
    - Evaluate every active meetup against that goal
    - Select the single best match with a personalized explanation
    - Safely route hostile or off-topic inputs to a decompression zone

    Args:
        request: MatchRequest containing the target user_id.

    Returns:
        MatchResponse with user_id and a match_insight dict containing
        'title', 'location', and 'insight' keys.

    Raises:
        HTTPException 404: If the user ID does not exist in the database.
        HTTPException 404: If no active meetups are available to match against.
    """
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == request.user_id).first()
        if not user:
            logger.warning(f"Match requested for non-existent user_id={request.user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id={request.user_id} not found.",
            )

        meetups = db.query(models.Meetup).all()
        if not meetups:
            logger.error("Match requested but no meetups exist in database.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active meetups available for matching.",
            )

        meetup_descriptions: list[str] = [
            f"{m.title}: {m.description}" for m in meetups
        ]

        logger.info(
            f"Generating AI match for user_id={user.id} "
            f"against {len(meetups)} meetups."
        )
        match_insight: dict = ai_engine.generate_meetup_match(
            user.interests, meetup_descriptions
        )

        logger.info(
            f"Match generated for user_id={user.id}: '{match_insight.get('title')}'"
        )
        return {"user_id": user.id, "match_insight": match_insight}
    finally:
        db.close()