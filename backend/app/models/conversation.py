from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Conversation(BaseModel):
    id: str = Field(default="", alias="_id")
    userId: str
    title: str = "New Conversation"
    collectionId: Optional[str] = None
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        populate_by_name = True

class SourceReference(BaseModel):
    documentId: Optional[str] = None
    title: str
    fileName: Optional[str] = None
    pageNumber: Optional[int] = 1
    section: Optional[str] = None
    category: Optional[str] = None
    snippet: str
    score: Optional[float] = None

class Message(BaseModel):
    id: str = Field(default="", alias="_id")
    conversationId: str
    role: str  # "user", "assistant", "system"
    content: str
    sources: List[SourceReference] = Field(default_factory=list)
    retrievalMetadata: Dict[str, Any] = Field(default_factory=dict)
    feedback: Optional[Dict[str, Any]] = None
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        populate_by_name = True

class Feedback(BaseModel):
    id: str = Field(default="", alias="_id")
    userId: str
    messageId: str
    rating: int  # 1 for helpful, -1 for unhelpful
    reason: Optional[str] = ""
    comment: Optional[str] = ""
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        populate_by_name = True

class Collection(BaseModel):
    id: str = Field(default="", alias="_id")
    name: str
    description: Optional[str] = ""
    department: Optional[str] = "All"
    accessRules: List[str] = Field(default_factory=lambda: ["student", "admin"])
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        populate_by_name = True

class UnansweredQuestion(BaseModel):
    id: str = Field(default="", alias="_id")
    userId: str
    question: str
    conversationId: Optional[str] = None
    retrievalScore: Optional[float] = 0.0
    status: str = "open"  # "open", "resolved", "ignored"
    adminNotes: Optional[str] = ""
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        populate_by_name = True
