from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    user_id: str = Field(..., description="Unique user identifier (e.g. username or UUID)")
    name: Optional[str] = None


class UserInDB(BaseModel):
    user_id: str
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_sessions: int = 0
