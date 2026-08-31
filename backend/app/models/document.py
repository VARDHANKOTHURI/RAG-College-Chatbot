from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class Document(BaseModel):
    id: str = Field(default="", alias="_id")
    title: str
    fileName: str
    description: Optional[str] = ""
    category: str = "General FAQ"
    department: Optional[str] = "All"
    academicYear: Optional[str] = "2026"
    version: int = 1
    status: str = "processing"  # "processing", "ready", "failed"
    uploadedBy: str = "admin"
    fileUrl: str
    totalPages: int = 1
    totalChunks: int = 0
    errorMessage: Optional[str] = None
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        populate_by_name = True
