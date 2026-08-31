from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversationId: Optional[str] = None
    collectionId: Optional[str] = None
    department: Optional[str] = None
    category: Optional[str] = None
    language: Optional[str] = "English"  # "English", "Hindi", "Telugu"

class SourceResponse(BaseModel):
    documentId: Optional[str] = None
    title: str
    fileName: Optional[str] = None
    pageNumber: Optional[int] = 1
    section: Optional[str] = None
    category: Optional[str] = None
    snippet: str
    score: Optional[float] = None

class ChatResponse(BaseModel):
    conversationId: str
    messageId: str
    answer: str
    sources: List[SourceResponse] = []
    isUnknown: bool = False
    retrievalScore: Optional[float] = 0.0

class ConversationCreateRequest(BaseModel):
    title: Optional[str] = "New Conversation"
    collectionId: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    conversationId: str
    role: str
    content: str
    sources: List[SourceResponse] = []
    retrievalMetadata: Dict[str, Any] = {}
    feedback: Optional[Dict[str, Any]] = None
    createdAt: str

class ConversationDetailResponse(BaseModel):
    id: str
    userId: str
    title: str
    collectionId: Optional[str] = None
    createdAt: str
    updatedAt: str
    messages: List[MessageResponse] = []
