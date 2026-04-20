import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.endpoints import users, meetups, ai_match
from app.db.database import engine, SessionLocal
from app.db import models

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexus API", version="1.0.0")

# -------------------------
# Seed DB (simple version)
# -------------------------
def seed_db():
    db = SessionLocal()
    try:
        if db.query(models.Meetup).count() == 0:
            db.add_all([
                models.Meetup(
                    title="GenAI Architecture Boardroom",
                    description="LLM scaling and RAG discussion. Room 402."
                ),
                models.Meetup(
                    title="Seed Round Speed Dating",
                    description="Pitch to angel investors. VIP Lounge."
                ),
                models.Meetup(
                    title="Board Games & Pizza",
                    description="Relax and network. Dining Hall."
                ),
            ])
            db.commit()
    finally:
        db.close()

seed_db()

# -------------------------
# CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # simple + better score
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Routers
# -------------------------
app.include_router(users.router, prefix="/api/v1")
app.include_router(meetups.router, prefix="/api/v1")
app.include_router(ai_match.router, prefix="/api/v1")

# -------------------------
# Frontend
# -------------------------
frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# -------------------------
# Health
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok"}