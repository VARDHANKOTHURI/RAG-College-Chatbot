import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG-Based College Chatbot"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # MongoDB Configuration
    MONGODB_URI: str = Field(default="mongodb://localhost:27017", env="MONGODB_URI")
    DATABASE_NAME: str = Field(default="college_rag_chatbot", env="DATABASE_NAME")
    
    # Authentication & JWT
    JWT_SECRET: str = Field(default="super-secret-college-chatbot-key-2026-xyz-rag", env="JWT_SECRET")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Vector Database - Qdrant
    QDRANT_URL: Optional[str] = Field(default=None, env="QDRANT_URL")
    QDRANT_API_KEY: Optional[str] = Field(default=None, env="QDRANT_API_KEY")
    QDRANT_COLLECTION_NAME: str = Field(default="college_knowledge_base", env="QDRANT_COLLECTION_NAME")
    QDRANT_PATH: str = Field(default="./data/qdrant_storage", env="QDRANT_PATH")
    
    # LLM Configuration
    GEMINI_API_KEY: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    LLM_MODEL: str = Field(default="gemini-1.5-flash", env="LLM_MODEL")
    LLM_TEMPERATURE: float = 0.2
    
    # Embeddings Configuration
    EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    EMBEDDING_DIMENSION: int = 384
    
    # RAG Search & Chunking Configuration
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100
    TOP_K: int = 4
    SIMILARITY_THRESHOLD: float = 0.28
    ENABLE_RERANKING: bool = True
    
    # Storage & Uploads
    UPLOAD_DIR: str = Field(default="./data/uploads", env="UPLOAD_DIR")
    STATIC_DIR: str = Field(default="./static", env="STATIC_DIR")
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "txt", "png", "jpg", "jpeg"]
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
