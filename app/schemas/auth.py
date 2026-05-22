import uuid
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserCreate(BaseModel):
    username: EmailStr = Field(..., description="User email used as username")
    password: str = Field(..., min_length=8, description="Raw text password")

class UserResponse(BaseModel):
    id: uuid.UUID
    username: EmailStr

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class MessageResponse(BaseModel):
    message: str