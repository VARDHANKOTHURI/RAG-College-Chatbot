from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class DocumentResponse(BaseModel):
    id: str
    title: str
    fileName: str
    description: Optional[str] = ""
    category: str
    department: Optional[str] = "All"
    academicYear: Optional[str] = "2026"
    version: int
    status: str
    uploadedBy: str
    fileUrl: str
    totalPages: int
    totalChunks: int
    errorMessage: Optional[str] = None
    createdAt: str
    updatedAt: str

class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    academicYear: Optional[str] = None
    version: Optional[int] = None

class FeedbackCreateRequest(BaseModel):
    messageId: str
    rating: int  # 1 for thumbs up, -1 for thumbs down
    reason: Optional[str] = ""  # e.g., "Incorrect information", "Irrelevant source", "Answer not clear"
    comment: Optional[str] = ""

class FeedbackResponse(BaseModel):
    id: str
    userId: str
    messageId: str
    rating: int
    reason: Optional[str] = ""
    comment: Optional[str] = ""
    createdAt: str

class CollectionCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    department: Optional[str] = "All"
    accessRules: List[str] = ["student", "admin"]

class CollectionResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    department: Optional[str] = "All"
    accessRules: List[str] = ["student", "admin"]
    createdAt: str

class AnalyticsResponse(BaseModel):
    totalDocuments: int
    processedDocuments: int
    failedDocuments: int
    totalChunks: int
    totalQuestions: int
    answeredQuestions: int
    unansweredQuestions: int
    activeUsers: int
    positiveFeedbackCount: int
    negativeFeedbackCount: int
    popularQuestions: List[Dict[str, Any]]
    recentActivity: List[Dict[str, Any]]
