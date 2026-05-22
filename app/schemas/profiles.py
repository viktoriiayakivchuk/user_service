import uuid
from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict

class ProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None

class ProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    avatar_url: str | None = None
    bio: str | None = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)