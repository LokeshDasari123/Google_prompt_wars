from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.database import SessionLocal
from app.db import models
from app.core.ai_service import ai_engine
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class UserCreate(BaseModel):
    name: str
    interests: str

class MatchRequest(BaseModel):
    user_id: int

@router.post("/users/", status_code=201)
def create_user(user: UserCreate):
    db = SessionLocal()
    try:
        db_user = models.User(name=user.name, interests=user.interests)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"id": db_user.id, "name": db_user.name, "interests": db_user.interests}
    finally:
        db.close()

@router.post("/match/")
def generate_match(request: MatchRequest):
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        meetups = db.query(models.Meetup).all()
        meetup_descriptions = [f"{m.title}: {m.description}" for m in meetups]
        
        match_insight = ai_engine.generate_meetup_match(user.interests, meetup_descriptions)
        return {"match_insight": match_insight}
    finally:
        db.close()