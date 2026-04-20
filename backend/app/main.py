"""
Nexus Event Companion - Main Application Entry Point.

Initializes the FastAPI application, configures middleware, mounts
static files, registers API routers, and seeds the database with
initial meetup data on first startup.
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.endpoints import endpoints, users, meetups, ai_match
from app.db.database import engine, SessionLocal
from app.db import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create all database tables on startup
models.Base.metadata.create_all(bind=engine)

CLOUD_RUN_URL = "https://nexus-app-1016175435508.asia-south1.run.app"


def seed_database() -> None:
    """
    Seed the database with initial meetup data if the table is empty.

    Runs once on application startup. Populates three default meetup
    events covering technical, funding, and wellness use cases to
    ensure the AI matchmaking engine always has candidates to evaluate.
    """
    db = SessionLocal()
    try:
        if db.query(models.Meetup).count() == 0:
            initial_meetups = [
                models.Meetup(
                    title="GenAI Architecture Boardroom",
                    description="Senior engineers whiteboarding LLM scaling and RAG architectures. Room 402."
                ),
                models.Meetup(
                    title="Seed Round Speed Dating",
                    description="3-minute pitches with active angel investors looking for AI startups. VIP Lounge."
                ),
                models.Meetup(
                    title="Board Games & Pizza",
                    description="Catan, Avalon, and cold pizza. Dining Hall."
                ),
            ]
            db.bulk_save_objects(initial_meetups)
            db.commit()
            logger.info("Database seeded with 3 initial meetups.")
    except Exception as e:
        db.rollback()
        logger.error(f"Database seeding failed: {e}")
    finally:
        db.close()


seed_database()

app = FastAPI(
    title="Nexus API",
    description=(
        "Enterprise-grade AI matchmaking agent for tech conference and hackathon attendees. "
        "Powered by Google Cloud Vertex AI (gemini-2.5-flash) with Chain-of-Thought reasoning."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Security Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CLOUD_RUN_URL, "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# ---------------------------------------------------------------------------
# API Routers
# ---------------------------------------------------------------------------
app.include_router(users.router, prefix="/api/v1")
app.include_router(meetups.router, prefix="/api/v1")
app.include_router(ai_match.router, prefix="/api/v1")
app.include_router(endpoints.router, prefix="/api/v1")  # legacy compat

# ---------------------------------------------------------------------------
# Static Frontend
# ---------------------------------------------------------------------------
frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")


# ---------------------------------------------------------------------------
# Core Routes
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"], include_in_schema=False)
async def read_index() -> FileResponse:
    """Serve the Nexus frontend single-page application."""
    return FileResponse(os.path.join(frontend_path, "index.html"))


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Lightweight liveness probe for Google Cloud Run uptime monitoring.",
)
async def health_check() -> dict:
    """
    Return service health status.

    Used by Google Cloud Run as a liveness and readiness probe.
    Returns service name, version, and operational status.

    Returns:
        dict: Health status payload with 'status', 'service', and 'version'.
    """
    return {"status": "ok", "service": "Nexus API", "version": "1.0.0"}