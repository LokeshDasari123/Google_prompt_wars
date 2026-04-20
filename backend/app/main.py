import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
# FIXED: Removed .v1 because your folder is app/api/endpoints
from app.api.endpoints import endpoints 
from app.db.database import engine, SessionLocal
from app.db import models
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Recreate tables and seed
models.Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()
    try:
        if db.query(models.Meetup).count() == 0:
            initial_meetups = [
                models.Meetup(title="GenAI Architecture Boardroom", description="Senior engineers whiteboarding LLM scaling and RAG architectures. Room 402."),
                models.Meetup(title="Seed Round Speed Dating", description="3-minute pitches with active angel investors looking for AI startups. VIP Lounge."),
                models.Meetup(title="Board Games & Pizza", description="Catan, Avalon, and cold pizza. Dining Hall.")
            ]
            db.bulk_save_objects(initial_meetups)
            db.commit()
    finally:
        db.close()

seed_database()

app = FastAPI(title="Nexus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# IMPORTANT: API Routes
app.include_router(endpoints.router, prefix="/api/v1")

# IMPORTANT: Serve Frontend
# This ensures index.html is served at the base URL
frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))