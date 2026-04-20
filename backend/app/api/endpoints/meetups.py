from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.schemas import meetup_schema

router = APIRouter()

@router.post("/", response_model=meetup_schema.MeetupResponse, status_code=status.HTTP_201_CREATED)
def create_meetup(meetup: meetup_schema.MeetupCreate, db: Session = Depends(get_db)):
    db_meetup = models.Meetup(title=meetup.title, description=meetup.description)
    db.add(db_meetup)
    db.commit()
    db.refresh(db_meetup)
    return db_meetup

@router.get("/", response_model=list[meetup_schema.MeetupResponse])
def get_meetups(db: Session = Depends(get_db)):
    return db.query(models.Meetup).all()
