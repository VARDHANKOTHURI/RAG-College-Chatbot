from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: str = Field(default="", alias="_id")
    name: str
    email: str
    passwordHash: str
    role: str = "student"  # "student" or "admin"
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    lastLogin: Optional[str] = None

    class Config:
        populate_by_name = True
