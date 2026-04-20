from pydantic import BaseModel, Field

class MeetupBase(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Tech Enthusiasts Mixer"}, description="Title of the physical meetup")
    description: str = Field(..., json_schema_extra={"example": "Casual meetup at the main stage."}, description="Details of the event")

class MeetupCreate(MeetupBase):
    pass

class MeetupResponse(MeetupBase):
    id: int

    class Config:
        from_attributes = True

class MatchRequest(BaseModel):
    user_id: int = Field(..., json_schema_extra={"example": 1}, description="ID of the user seeking a match")
