from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class DocumentChunk(BaseModel):
    id: str = Field(default="", alias="_id")
    documentId: str
    chunkIndex: int
    text: str
    pageNumber: int = 1
    section: Optional[str] = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    vectorId: str = ""

    class Config:
        populate_by_name = True
