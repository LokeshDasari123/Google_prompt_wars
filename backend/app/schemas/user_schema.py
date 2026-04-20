from pydantic import BaseModel, Field

class UserBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Lokesh"}, description="The user's full name")
    interests: str = Field(..., json_schema_extra={"example": "AI, Hiking, Hackathons"}, description="Comma-separated interests")

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
