from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.schemas import meetup_schema
from app.core.ai_service import ai_engine

router = APIRouter()

@router.post("/")
def get_ai_match(request: meetup_schema.MatchRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
        
    meetups = db.query(models.Meetup).all()
    if not meetups:
        raise HTTPException(status_code=404, detail="No active meetups available")
        
    meetup_desc = [f"{m.title}: {m.description}" for m in meetups]
    recommendation = ai_engine.generate_meetup_match(user.interests, meetup_desc)
    
    return {"user_id": user.id, "match_insight": recommendation}
